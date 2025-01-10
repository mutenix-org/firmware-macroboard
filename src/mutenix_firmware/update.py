from __future__ import annotations

import os
import time

import storage  # type: ignore
import supervisor  # type: ignore
import usb_hid  # type: ignore
from leds import ColorLeds
from leds import mix_color

FILE_TRANSPORT_START = 1
FILE_TRANSPORT_DATA = 2
FILE_TRANSPORT_END = 3
FILE_TRANSPORT_FINISH = 4
FILE_TRANSPORT_DELETE = 5

CHUNK_SIZE = 60
HEADER_SIZE = 8

TIMEOUT_TRANSFER = 10
TIMEOUT_UPDATE = 60
TIME_SHOW_FINAL_STATUS = 4
TIMEOUT_TRANSFER_REQUEST = 1


class FileTransport:
    content_length = CHUNK_SIZE - HEADER_SIZE

    def __init__(self, data: bytes):
        self.parse(data)

    def parse(self, data: bytes):
        self.type_ = int.from_bytes(data[0:2], "little")
        self.id = int.from_bytes(data[2:4], "little")
        self.total_packages = int.from_bytes(data[4:6], "little")
        self.package = int.from_bytes(data[6:8], "little")
        self.content = data[8:]

    def is_valid(self):
        return self.type_ in [
            FILE_TRANSPORT_START,
            FILE_TRANSPORT_DATA,
            FILE_TRANSPORT_END,
            FILE_TRANSPORT_DELETE,
            FILE_TRANSPORT_FINISH,
        ]

    def as_start(self) -> tuple[str, int]:
        if self.type_ != FILE_TRANSPORT_START:
            raise ValueError("Not a start packet")
        filename_length = self.content[0]
        print("Filename length", filename_length)
        filename = self.content[1 : 1 + filename_length].decode("utf-8")
        print("Filename", filename)
        size_length = self.content[1 + filename_length]
        total_size = int.from_bytes(
            self.content[2 + filename_length : 2 + filename_length + size_length],
            "little",
        )
        return filename, total_size

    def as_delete(self) -> str:
        if self.type_ != FILE_TRANSPORT_DELETE:
            raise ValueError("Not a delete packet")
        filename_length = self.content[0]
        print("Filename length", filename_length)
        filename = self.content[1 : 1 + filename_length].decode("utf-8")
        return filename

    def is_end(self):
        return self.type_ == FILE_TRANSPORT_END

    def is_finish(self):
        return self.type_ == FILE_TRANSPORT_FINISH

    def is_delete(self):
        return self.type_ == FILE_TRANSPORT_DELETE


class File:
    def __init__(self, first_element: FileTransport):
        if first_element.type_ != FILE_TRANSPORT_START:
            raise ValueError("First element must be start")
        self.filename, self.total_size = first_element.as_start()
        self.id = first_element.id
        self.packages = list(range(first_element.total_packages + 1))
        self.content = bytearray((0,) * self.total_size)

    def write(self, data: FileTransport):
        if data.package == data.total_packages:
            length = self.total_size % FileTransport.content_length
        else:
            length = FileTransport.content_length
        self.content[
            data.package * FileTransport.content_length : data.package
            * FileTransport.content_length
            + length
        ] = data.content[:length]
        self.packages.remove(data.package)

    def is_complete(self):
        return len(self.packages) == 0

    def __str__(self):
        return f"File: {self.filename}, Size: {self.total_size}, Missing: {len(self.packages)}"


def request_chunk(macropad, file):
    macropad.send_report(
        bytearray("RQ", "utf-8")
        + file.id.to_bytes(2, "little")
        + file.packages[0].to_bytes(2, "little")
        + b"\0" * 18,
        2,
    )


def confirm_chunk(macropad, file):
    macropad.send_report(
        bytearray("AK", "utf-8")
        + file.id.to_bytes(2, "little")
        + file.package.to_bytes(2, "little")
        + b"\0" * 18,
        2,
    )


class LedStatus:
    def __init__(self, led):
        self.led = led
        self.led_status = 0
        self.counter = 0

    def update(self):
        self.led_status += 1
        if self.led_status >= 100:
            self.led_status = 0
        for i in range(1, 6):
            if self.led_status // 10 == (i - 1):
                self.led[i] = mix_color(
                    ColorLeds.blue,
                    ColorLeds.green,
                    self.led_status % 10,
                    10,
                )
            if self.led_status // 10 == (i - 1 + 5):
                self.led[i] = mix_color(
                    ColorLeds.green,
                    ColorLeds.blue,
                    self.led_status % 10,
                    10,
                )

    def running(self):
        if int(self.counter // 100) % 2 == 0:
            self.led[0] = ColorLeds.blue
        else:
            self.led[0] = ColorLeds.green
        self.counter += 1

    def error(self):
        for i in range(0, 6):
            self.led[i] = ColorLeds.red

    def success(self):
        for i in range(0, 6):
            self.led[i] = ColorLeds.green


def do_update(led):
    led_status = LedStatus(led)
    try:
        storage.remount("/", readonly=False)
    except RuntimeError:
        led_status.error()
        time.sleep(TIME_SHOW_FINAL_STATUS)
        return
    supervisor.runtime.autoreload = False
    files = {}
    macropad = usb_hid.devices[0]
    last_transfer = time.monotonic()
    requested = False
    start_time = last_transfer

    invalid_data_ignore_counter = 5

    print("Prepared for update")
    while True:
        data = macropad.get_last_received_report(2)
        led_status.running()
        if data:
            print("Data received", last_transfer)
            ft = FileTransport(data)
            if not ft.is_valid():
                invalid_data_ignore_counter -= 1
                if invalid_data_ignore_counter == 0:
                    print("Cannot recover from invalid data, aborting")
                    led_status.error()
                    time.sleep(TIME_SHOW_FINAL_STATUS)
                    break
                print(
                    f"Invalid data received {data}, ignoring it {invalid_data_ignore_counter} more times",
                )
                continue
            confirm_chunk(macropad, ft)

            last_transfer = time.monotonic()
            led_status.update()
            requested = False
            if ft.is_delete():
                print("Delete file {ft.name}")
                filename = ft.as_delete()
                os.unlink(filename)
                continue
            if ft.is_finish():
                print("Update completed")
                break
            if ft.is_end():
                if ft.id in files:
                    print("File complete")
                    del files[ft.id]
                else:
                    print("File not found")
                continue
            if ft.id not in files:
                files[ft.id] = File(ft)
                print("New file", files[ft.id])
            else:
                files[ft.id].write(ft)
            print(f"{files[ft.id].filename}[ft.id]", ft.package, "/", ft.total_packages)
            if files[ft.id].is_complete():
                print("File complete, writing", files[ft.id].filename)
                with open(files[ft.id].filename, "wb") as f:
                    f.write(files[ft.id].content)
                del files[ft.id]

        if (
            time.monotonic() - last_transfer > TIMEOUT_TRANSFER_REQUEST
            and not requested
        ):
            if len(files) > 0:
                file = next(files.values())
                print("request file", file.id)
                request_chunk(file)
                requested = True
        if (
            requested and time.monotonic() - last_transfer > TIMEOUT_TRANSFER
        ) or time.monotonic() - start_time > TIMEOUT_UPDATE:
            print("Update timed out")
            led_status.error()
            break
    led_status.success()
    supervisor.runtime.autoreload = True
