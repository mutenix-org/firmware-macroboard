import version as v
from button import Button
from hardware import hardware_variant
from log import log

OUT_REPORT_LENGTH = 8


class OutMessage:
    """Message from the host to the device."""

    SETCOLOR = 0x1
    PREPARE_UPDATE = 0xE0
    RESET = 0xE1
    UPDATE_CONFIG = 0xE2
    PING = 0xF0

    @classmethod
    def from_buffer(cls, buffer):
        type = buffer[0]
        if type == cls.PING:
            return Ping(buffer[1:OUT_REPORT_LENGTH])
        elif type == cls.SETCOLOR:
            return SetColor(buffer[1:OUT_REPORT_LENGTH])
        elif type == cls.PREPARE_UPDATE:
            return PrepareUpdate()
        elif type == cls.RESET:
            return Reset()
        elif type == cls.UPDATE_CONFIG:
            return UpdateConfig(buffer[1:OUT_REPORT_LENGTH])
        return Unknown(buffer[0:OUT_REPORT_LENGTH])


class Ping(OutMessage):
    """Ping message to signal that the host is alive."""

    def __init__(self, _):
        pass


class Unknown(OutMessage):
    """Unknown message."""

    def __init__(self, data):
        self._data = data

    @property
    def data(self):
        return self._data


class SetColor(OutMessage):
    """Set the color of a led."""

    def __init__(self, data):
        self._buttonid = data[0]
        self._color = bytearray(data[1:5])

    @property
    def color(self):
        return self._color

    @property
    def buttonid(self):
        return self._buttonid


class PrepareUpdate(OutMessage):
    """Prepare the device for a firmware update."""

    def __init__(self):
        pass


class Reset(OutMessage):
    """Reset the device."""

    def __init__(self):
        pass


class UpdateConfig(OutMessage):
    """Set the color of a led."""

    def __init__(self, data):
        self._update_debug = data[0]
        self._update_filesystem = data[0]

    @property
    def update_filesystem(self):
        return self._update_filesystem != 0

    @property
    def activate_filesystem(self):
        return self._update_filesystem == 2

    @property
    def update_debug(self):
        return self._update_debug != 0

    @property
    def activate_debug(self):
        return self._update_debug == 2


class InMessage:
    """Message from the device to the host."""

    INITIALIZE = 0x99
    STATUS = 0x1
    STATUS_REQUEST = 0x2

    def __init__(self, data):
        self._data = bytearray(data + [0] * (OUT_REPORT_LENGTH - len(data)))

    @classmethod
    def initialize(cls):
        return cls(
            [
                cls.INITIALIZE,
                v.MAJOR,
                v.MINOR,
                v.PATCH,
                hardware_variant.hardware_variant,
            ],
        )

    @classmethod
    def button(cls, button: Button):
        return cls(
            [
                cls.STATUS,
                button.id,
                button.triggered,
                button.doubletapped,
                button.pressed,
                button.released,
                button.counter,
            ],
        )

    @classmethod
    def status_request(cls):
        return cls([cls.STATUS_REQUEST])

    def send(self, device):
        log(f"Sending {len(self._data)} bytes: {self._data}")
        device.send_report(self._data, 1)
