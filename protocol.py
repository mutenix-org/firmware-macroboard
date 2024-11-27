import version as v
from button import Button

OUT_REPORT_LENGTH = 8


class OutMessage:
    SETCOLOR = 0x1
    PING = 0xF0

    @classmethod
    def from_buffer(cls, buffer):
        type = buffer[0]
        if type == cls.PING:
            return Ping(buffer[1:OUT_REPORT_LENGTH])
        elif type == cls.SETCOLOR:
            return SetColor(buffer[1:OUT_REPORT_LENGTH])
        return Unknown(buffer[0:OUT_REPORT_LENGTH])


class Ping(OutMessage):
    def __init__(self, _):
        pass


class Unknown(OutMessage):
    def __init__(self, data):
        self._data = data

    @property
    def data(self):
        return self._data


class SetColor(OutMessage):
    def __init__(self, data):
        self._buttonid = data[0]
        self._color = bytearray(data[1:5])

    @property
    def color(self):
        return self._color

    @property
    def buttonid(self):
        return self._buttonid


class InMessage:
    INITIALIZE = 0x99
    STATUS = 0x1

    def __init__(self, data):
        self._data = bytearray(data + [0] * (OUT_REPORT_LENGTH - len(data)))

    @classmethod
    def initialize(cls):
        return cls([cls.INITIALIZE, v.MAJOR, v.MINOR, v.PATCH])

    @classmethod
    def button(cls, button: Button):
        return cls([cls.STATUS, button.id, button.triggered, button.doubletapped, button.pressed, button.released])

    def send(self, device):
        print(f"Sending {len(self._data)} bytes: {self._data}")
        device.send_report(self._data, 1)
