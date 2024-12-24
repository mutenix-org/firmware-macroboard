from __future__ import annotations
class DeviceMode:
    def __init__(self):
        self.storage_enabled = False
        self.serial_enabled = False

    @property
    def usb_storage_active(self):
        return self.storage_enabled

    @property
    def usb_serial_active(self):
        return self.serial_enabled

device_mode = DeviceMode()
