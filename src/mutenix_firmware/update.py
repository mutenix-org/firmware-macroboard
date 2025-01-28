# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Matthias Bilger <matthias@bilger.info>
import os
import time

import storage  # type: ignore
import supervisor  # type: ignore
import usb_hid  # type: ignore
from hardware import hardware_variant
from hardware import mix_color
from log import log

FILE_TRANSPORT_START = 1
FILE_TRANSPORT_DATA = 2
FILE_TRANSPORT_END = 3
FILE_TRANSPORT_FINISH = 4
FILE_TRANSPORT_DELETE = 5

CHUNK_SIZE = 60
HEADER_SIZE = 8

TIMEOUT_TRANSFER = 10
TIMEOUT_UPDATE = 180
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

    def _get_filename(self):
        filename_length = self.content[0]
        filename = self.content[1 : 1 + filename_length].decode("utf-8")
        log("Filename[", filename_length, "]:", filename)
        return filename_length, filename

    def as_start(self) -> tuple[str, int]:
        if self.type_ != FILE_TRANSPORT_START:
            raise ValueError("Not a start packet")
        filename_length, filename = self._get_filename()
        size_length = self.content[1 + filename_length]
        total_size = int.from_bytes(
            self.content[2 + filename_length : 2 + filename_length + size_length],
            "little",
        )
        return filename, total_size

    def as_delete(self) -> str:
        if self.type_ != FILE_TRANSPORT_DELETE:
            raise ValueError("Not a delete packet")
        return self._get_filename()[1]

    def is_end(self):
        return self.type_ == FILE_TRANSPORT_END

    def is_finish(self):
        return self.type_ == FILE_TRANSPORT_FINISH

    def is_delete(self):
        return self.type_ == FILE_TRANSPORT_DELETE

    def is_start(self):
        return self.type_ == FILE_TRANSPORT_START

    def is_data(self):
        return self.type_ == FILE_TRANSPORT_DATA


class File:
    def __init__(self, first_element: FileTransport):
        if not first_element.is_start():
            raise ValueError("First element must be start")
        self.filename, self.total_size = first_element.as_start()
        self.id = first_element.id
        self.packages = list(range(first_element.total_packages + 1))
        self._file = None  # type: ignore  # noqa

    def write(self, data: FileTransport):
        if not data.is_data():
            log("Not a data packet")
            return
        if self._file is None:
            self._file = open(self.filename, "wb")  # type: ignore  # noqa
        if data.package == data.total_packages:
            length = self.total_size % FileTransport.content_length
        else:
            length = FileTransport.content_length
        if data.package not in self.packages:
            log("Package already received")
            return

        self._file.write(data.content[:length])  # type: ignore  # noqa
        self.packages.remove(data.package)
        if self.is_complete():
            self._file.close()  # type: ignore  # noqa

    def is_complete(self):
        return len(self.packages) == 0

    def __str__(self):
        return f"File: {self.filename}, Size: {self.total_size}, Missing: {len(self.packages)}"


def send_report(macropad, data: bytearray):
    data = data + b"\0" * (36 - len(data))
    macropad.send_report(
        data,
        2,
    )


def confirm_chunk(macropad, filetransport: FileTransport):
    send_report(
        macropad,
        (
            bytearray("AK", "utf-8")
            + filetransport.id.to_bytes(2, "little")
            + filetransport.package.to_bytes(2, "little")
            + filetransport.type_.to_bytes(1, "little")
        ),
    )


def notify_error(macropad, info: str):
    info_bytes = info.encode()[:33]
    send_report(
        macropad,
        (bytearray("ER", "utf-8") + len(info_bytes).to_bytes(1, "little") + info_bytes),
    )


def send_mode(macropad):
    send_report(macropad, bytearray("MO", "utf-8") + (1).to_bytes(1, "little"))


class LedStatus:
    def __init__(self, led):
        self.led = led
        self.led_status = 0
        self.counter = 0

    def update(self):
        self.led_status = (self.led_status + 1) % 100
        for i in range(1, len(self.led)):
            if self.led_status // 10 in [(i - 1), (i - 1 + 5)]:
                color1, color2 = (
                    ("blue", "green")
                    if self.led_status // 10 == (i - 1)
                    else ("green", "blue")
                )
                self.led[i] = mix_color(color1, color2, self.led_status % 10, 10)

    def running(self):
        self.led[0] = "purple" if (self.counter // 100) % 2 == 0 else "yellow"
        self.counter += 1

    def error(self):
        self.led.fill("red")

    def success(self):
        self.led.fill("green")


def do_update():
    special_protected_files = ["update.py", "boot.py"]
    hardware = hardware_variant
    led_status = LedStatus(hardware.leds)
    macropad = usb_hid.devices[0]
    try:
        storage.remount("/", readonly=False)
    except RuntimeError:
        led_status.error()
        notify_error(macropad, "filsystem")
        time.sleep(TIME_SHOW_FINAL_STATUS)
        return
    supervisor.runtime.autoreload = False
    files = {}
    last_transfer = time.monotonic()
    start_time = last_transfer

    invalid_data_ignore_counter = 5

    log("Prepared for update")
    send_mode(macropad)
    finished = False
    while True:
        data = macropad.get_last_received_report(2)
        led_status.running()
        if data:
            log("Data received", last_transfer)
            ft = FileTransport(data)
            if not ft.is_valid():
                invalid_data_ignore_counter -= 1
                if invalid_data_ignore_counter == 0:
                    log("Cannot recover from invalid data, aborting")
                    led_status.error()
                    time.sleep(TIME_SHOW_FINAL_STATUS)
                    break
                log(
                    f"Invalid data received {data}, ignoring it {invalid_data_ignore_counter} more times",
                )
                continue
            confirm_chunk(macropad, ft)

            last_transfer = time.monotonic()
            led_status.update()
            if ft.is_delete():
                log("Delete file {ft.name}")
                filename = ft.as_delete()
                try:
                    os.unlink(filename)
                except OSError:
                    log("File not found")
                continue
            if ft.is_finish():
                log("Update completed")
                finished = True
                break
            if ft.is_end():
                if ft.id in files:
                    log("File complete")
                    del files[ft.id]
                else:
                    log("File not found")
                continue
            if ft.id not in files:
                # to ensure that we do not overwrite the update file, while updating,
                # we fake the name here
                files[ft.id] = File(ft)
                if files[ft.id].filename in special_protected_files:
                    files[ft.id].filename = f"{files[ft.id].filename}.tmp"
                log("New file", files[ft.id])
            else:
                files[ft.id].write(ft)
            log(f"{files[ft.id].filename}[{ft.id}]", ft.package, "/", ft.total_packages)

        if (
            time.monotonic() - last_transfer > TIMEOUT_TRANSFER
            or time.monotonic() - start_time > TIMEOUT_UPDATE
        ):
            log("Transfer timed out")
            notify_error(macropad, "timeout")
            led_status.error()
            time.sleep(TIME_SHOW_FINAL_STATUS)
            break

    if finished:
        log("Update finished")
        for file in os.listdir("/"):
            if file.endswith(".tmp"):
                # we need to revert the update.py trick here, this is the critical part in the update and
                # worst case these lines would brick the device (not really as you could enter the file mode)
                os.rename(file, file[:-4])
        led_status.success()
    supervisor.runtime.autoreload = True
    supervisor.set_next_code_file("main.py")
    supervisor.reload()


do_update()
