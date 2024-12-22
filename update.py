import supervisor # type: ignore
import time
import usb_hid # type: ignore
import storage # type: ignore

FILE_TRANSPORT_START = 1
FILE_TRANSPORT_DATA = 2
FILE_TRANSPORT_END = 3
FILE_TRANSPORT_FINISH = 4

CHUNK_SIZE = 60
HEADER_SIZE = 8


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
            self.content[
                2 + filename_length : 2 + filename_length + size_length
            ],
            "little",
        )
        return filename, total_size

    def is_end(self):
        return self.type_ == FILE_TRANSPORT_END

    def is_finish(self):
        return self.type_ == FILE_TRANSPORT_FINISH


class File:
    def __init__(self, first_element: FileTransport):
        if first_element.type_ != FILE_TRANSPORT_START:
            raise ValueError("First element must be start")
        self.filename, self.total_size = first_element.as_start()
        self.id = first_element.id
        self.packages = list(range(first_element.total_packages+1))
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


class LedStatus:
    def __init__(self, led):
        self.led = led
        self.led_status = 0

    def update(self):
        self.led_status += 1
        if self.led_status > 100:
            self.led_status = 0
        for i in range(1, 6):
            if self.led_status // 10 == (i - 1):
                self.led[i] = bytearray((10 - self.led_status % 10, self.led_status % 10, 0, 0))
            if self.led_status // 10 == (i - 1 + 5):
                self.led[i] = bytearray((self.led_status % 10, 10 - self.led_status % 10, 0, 0))


def do_update(led):
    try:
        storage.remount("/", readonly=False)
    except RuntimeError:
        for i in range(1, 6):
            led[i] = bytearray((0, 10, 0, 0))
        time.sleep(4)
        return
    supervisor.runtime.autoreload = False
    files = {}
    macropad = usb_hid.devices[0]
    last_transfer = time.monotonic()
    requested = False
    led_status = LedStatus(led)
    start_time = time.monotonic()

    print("Prepared for update")
    counter = 0
    while True:
        data = macropad.get_last_received_report(2)
        if int(counter // 100) % 2 == 0:
            led[0] = bytearray((0, 0, 10, 0))
        else:
            led[0] = bytearray((10, 0, 0, 0))
        counter += 1
        if data:
            print("Data received")
            ft = FileTransport(data)
            if not ft.is_valid():
                print("Invalid data")
                continue

            last_transfer = time.monotonic()
            led_status.update()
            requested = False
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
            print(f"{files[ft.id].filename}[ft.id]", ft.package, '/', ft.total_packages)
            if files[ft.id].is_complete():
                print("File complete", files[ft.id].filename)
                with open(files[ft.id].filename, "wb") as f:
                    f.write(files[ft.id].content)

        if time.monotonic() - last_transfer > 1 and not requested:
            if len(files) > 0:
                file = next(files.values())
                print("request file", file.id)
                request_chunk(file)
                requested = True
        if (requested and time.monotonic() - last_transfer > 10) or time.monotonic() - start_time > 60:
            print("Update timed out")
            break
    supervisor.runtime.autoreload = True
