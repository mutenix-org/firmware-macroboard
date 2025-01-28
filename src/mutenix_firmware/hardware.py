# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Matthias Bilger <matthias@bilger.info>
import os
import time

import adafruit_ble  # type: ignore
import board
import device_info
import digitalio
import myhid
import neopixel_write  # type: ignore
import version
from _bleio import adapter  # type: ignore
from adafruit_ble.advertising import Advertisement  # type: ignore
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement  # type: ignore
from adafruit_ble.services.standard import BatteryService  # type: ignore
from adafruit_ble.services.standard.device_info import DeviceInfoService  # type: ignore
from adafruit_ble.services.standard.hid import HIDService  # type: ignore
from adafruit_ble.services.standard.hid import ReportIn  # type: ignore
from adafruit_ble.services.standard.hid import ReportOut  # type: ignore
from button import Button
from log import log


FIVE_BUTTON_USB = 0x02
FIVE_BUTTON_BT = 0x03
FIVE_BUTTON_USB_V2 = 0x04
TEN_BUTTON_USB_V2 = 0x05
TEN_BUTTON_BT = 0x06


def file_or_dir_exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False


def mix_color(color1, color2, descriminant, divisor):
    if isinstance(color1, str):
        color1 = LedColors[color1]
    if isinstance(color2, str):
        color2 = LedColors[color2]
    return bytearray(
        [
            int(
                (color1[i] * descriminant + color2[i] * (divisor - descriminant))
                / divisor,
            )
            for i in range(4)
        ],
    )


GRBW = 0
GRB = 1

LedColors = {
    "red": bytearray([10, 0, 0, 0]),
    "green": bytearray([0, 10, 0, 0]),
    "blue": bytearray([0, 0, 10, 0]),
    "white": bytearray([10, 10, 10, 0]),
    "black": bytearray([0, 0, 0, 0]),
    "yellow": bytearray([10, 10, 0, 0]),
    "cyan": bytearray([0, 10, 10, 0]),
    "magenta": bytearray([10, 0, 10, 0]),
    "orange": bytearray([10, 5, 0, 0]),
    "purple": bytearray([5, 0, 5, 0]),
    "pink": bytearray([10, 5, 5, 0]),
    "turquoise": bytearray([0, 10, 5, 0]),
}


class Rainbow:
    def __init__(self, led, selected, speed=0.1):
        self.led = led
        self.speed = speed
        self._hue = 0
        self._selected = selected
        self._time = time.monotonic()
        self._was_active = True

    def next(self):
        if time.monotonic() - self._time < self.speed:
            return
        self._was_active = True
        self._time = time.monotonic()
        self._hue = (self._hue + self.speed) % 1
        for i in self._selected:
            self.led[i] = self._color(i)

    def was_active(self):
        return self._was_active

    def off(self):
        self._was_active = False
        for i in self._selected:
            self.led[i] = bytearray([0, 0, 0, 0])

    def _color(self, i):
        r, g, b = self._hsv_to_rgb(self._hue, 1, 1)
        return bytearray([int(g * 10), int(r * 10), int(b * 10), 0])

    def _hsv_to_rgb(self, h, s, v):
        i = int(h * 6)
        f = (h * 6) - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)

        if i % 6 == 0:
            r, g, b = v, t, p
        elif i % 6 == 1:
            r, g, b = q, v, p
        elif i % 6 == 2:
            r, g, b = p, v, t
        elif i % 6 == 3:
            r, g, b = p, q, v
        elif i % 6 == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q

        return r, g, b


class ColorLeds:
    def __init__(self, pin, count, colormode=GRB, mapping=None, rainbow=None):
        self.pin = digitalio.DigitalInOut(pin)
        self.pin.direction = digitalio.Direction.OUTPUT
        self._colormode = colormode
        if colormode == GRB:
            self._size = 3
        else:
            self._size = 4
        self.colors = bytearray(count * self._size)
        self.count = count
        if mapping is None:
            self._mapping = list(range(count))
        else:
            self._mapping = mapping
        self._rainbow = Rainbow(self, rainbow or list(range(1, count)))

    def __getitem__(self, key):
        key = self._mapping[key]
        if isinstance(key, list):
            key = key[0]
        return self.colors[key * self._size : key * self._size + self._size]

    def __setitem__(self, key, value):
        if isinstance(value, str):
            value = LedColors[value]
        if not isinstance(value, (bytes, bytearray)):
            raise ValueError("Value must be a bytes or bytearray object")
        if len(value) < self._size:
            raise ValueError("Value must be exactly 4 bytes long")
        key = self._mapping[key]

        def set_color(ckey, cvalue):
            if self._colormode == GRBW:
                cvalue = bytearray([cvalue[1], cvalue[0], cvalue[2], cvalue[3]])
            if self._colormode == GRB:
                if sum(cvalue[0:3]) == 0 and len(cvalue) == 4:
                    cvalue = bytearray([cvalue[3], cvalue[3], cvalue[3]])
                else:
                    cvalue = bytearray([cvalue[1], cvalue[0], cvalue[2]])
            self.colors[ckey * self._size : ckey * self._size + self._size] = cvalue[
                0 : self._size
            ]

        if isinstance(key, list):
            for k in key:
                set_color(k, value)
        else:
            set_color(key, value)
        neopixel_write.neopixel_write(self.pin, self.colors)

    def __len__(self):
        return self.count

    def rainbow_next(self):
        self._rainbow.next()

    def rainbow_off(self):
        self._rainbow.off()

    def fill(self, color):
        for i in range(self.count):
            self[i] = color


class HardwareOptions:
    """Buttons for enabling special boot modes."""

    BOOT_USB_BUTTON = 0
    BOOT_SERIAL_BUTTON = 1
    BOOT_UPDATE_BUTTON = 2
    BOOT_UF2_BUTTON = 3

    def __init__(self):
        self.board_id = board.board_id
        self._bluetooth = None
        self._ble_advertising = False
        self._last_read = None
        self._battery_level = 10
        self._setup_hardware_config()
        self._set_buttons()
        self._init_leds()

    def _setup_hardware_config(self):
        self.led_count = 13
        if self.board_id == "waveshare_rp2040_zero":
            if file_or_dir_exists("/version1"):
                self.led_pin = board.GP7
                self.led_count = 6
                self.hardware_variant = FIVE_BUTTON_USB
            else:
                self.variant_pin = board.GP29
                self.led_pin = board.GP15
                if self._is_ten_button_variant():
                    self.hardware_variant = TEN_BUTTON_USB_V2
                else:
                    self.hardware_variant = FIVE_BUTTON_USB_V2
        elif self.board_id == "supermini_nrf52840":
            self.variant_pin = board.P0_17
            self.led_pin = board.P0_20
            if self._is_ten_button_variant():
                self.hardware_variant = TEN_BUTTON_BT
            else:
                self.hardware_variant = FIVE_BUTTON_BT

    def _set_buttons(self):
        if self.hardware_variant == FIVE_BUTTON_USB:
            self.button_pins = [
                board.GP0,
                board.GP1,
                board.GP2,
                board.GP3,
                board.GP4,
            ]
        elif self.hardware_variant in [TEN_BUTTON_USB_V2, FIVE_BUTTON_USB_V2]:
            self.button_pins = [
                board.GP11,
                board.GP10,
                board.GP9,
                board.GP8,
                board.GP7,
            ]
            if self.hardware_variant == TEN_BUTTON_USB_V2:
                self.button_pins.extend(
                    [
                        board.GP6,
                        board.GP3,
                        board.GP2,
                        board.GP1,
                        board.GP0,
                    ],
                )
        elif self.hardware_variant in [FIVE_BUTTON_BT, TEN_BUTTON_BT]:
            self.button_pins = [
                board.P1_04,
                board.P1_06,
                board.P0_09,
                board.P0_10,
                board.P1_11,
            ]
            if self.hardware_variant == TEN_BUTTON_BT:
                self.button_pins.extend(
                    [
                        board.P1_13,
                        board.P1_15,
                        board.P0_02,
                        board.P0_29,
                        board.P0_31,
                    ],
                )
        self.buttons = [Button(i, pin) for i, pin in enumerate(self.button_pins, 1)]

    def read_buttons(self):
        for b in self.buttons:
            b.read()

    def boot_button_usb_pressed(self):
        return self.buttons[self.BOOT_USB_BUTTON].state

    def boot_button_serial_pressed(self):
        return self.buttons[self.BOOT_SERIAL_BUTTON].state

    def boot_button_update_pressed(self):
        return self.buttons[self.BOOT_UPDATE_BUTTON].state

    def boot_button_uf2_pressed(self):
        return self.buttons[self.BOOT_UF2_BUTTON].state

    def _is_ten_button_variant(self):
        variant = digitalio.DigitalInOut(self.variant_pin)
        variant.direction = digitalio.Direction.INPUT
        variant.pull = digitalio.Pull.UP
        return variant.value

    def _init_leds(self):
        if self.hardware_variant in [TEN_BUTTON_BT, TEN_BUTTON_USB_V2]:
            self.leds = ColorLeds(
                self.led_pin,
                self.led_count,
                GRB,
                [6, 4, 3, 2, 1, 0, 8, 9, 10, 11, 12, 5, 7],
                rainbow=list(range(1, 11)),
            )
        elif self.hardware_variant in [FIVE_BUTTON_BT, FIVE_BUTTON_USB_V2]:
            self.leds = ColorLeds(
                self.led_pin,
                self.led_count,
                GRB,
                [6, [4, 8], [3, 9], [2, 10], [1, 11], [0, 12], 5, 7],
                rainbow=list(range(1, 6)),
            )
        else:
            self.leds = ColorLeds(
                self.led_pin,
                self.led_count,
                GRBW,
                [0, 5, 4, 3, 2, 1],
                rainbow=list(range(6, 1)),
            )

    @property
    def has_bluetooth(self):
        return self.hardware_variant in [FIVE_BUTTON_BT, TEN_BUTTON_BT]

    def ble(self):
        if not self.has_bluetooth:
            return None
        return self._bluetooth

    def setup_bluetooth(self):
        if self.has_bluetooth:
            self._setup_bluetooth()

    def _setup_bluetooth(self):
        adapter.name = device_info.MANUFACTURER
        self._hid = HIDService(myhid.MACROBOARD_DESCRIPTOR2)

        hardware_revision = "V1.0"

        self._device_info_service = DeviceInfoService(
            model_number=device_info.PRODUCT,
            hardware_revision=hardware_revision,
            firmware_revision=os.uname().version,
            software_revision=f"{version.MAJOR}.{version.MINOR}.{version.PATCH}",
            manufacturer=device_info.MANUFACTURER,
            pnp_id=(0x01, device_info.VID, device_info.PID, 0x0001),
        )
        self._batteryservice = BatteryService()
        self._batteryservice.level = self._battery_level

        self._advertisement = ProvideServicesAdvertisement(self._hid)
        self._advertisement.appearance = 961
        self._advertisement.short_name = device_info.MANUFACTURER
        self._scan_response = Advertisement()
        self._scan_response.complete_name = device_info.PRODUCT
        ble = adafruit_ble.BLERadio()
        ble.name = device_info.MANUFACTURER
        self._bluetooth = ble
        self._setup_hid_endpoints()
        return ble

    def check_bluetooth(self):
        if not self.has_bluetooth:
            return
        if not self._bluetooth.connected and not self._ble_advertising:
            self._bluetooth.start_advertising(self._advertisement, self._scan_response)
            self._ble_advertising = True
            log("Bluetooth advertising")

        if self._bluetooth.connected:
            self._ble_advertising = False

        if self._bluetooth.connected:
            self.leds[11] = "green"

        elif self._bluetooth.advertising:
            self.leds[11] = "blue"
        else:
            self.leds[11] = "red"

    def _setup_hid_endpoints(self):
        self._hid_communication_out = next(
            filter(
                lambda x: isinstance(x, ReportOut) and x._report_id == 1,
                self._hid.devices,
            ),
        )
        self._hid_communication_in = next(
            filter(
                lambda x: isinstance(x, ReportIn) and x._report_id == 1,
                self._hid.devices,
            ),
        )

    def read_bluetooth_hid(self):
        new_value = self._hid_communication_out.report
        if new_value == self._last_read:
            return None
        self._last_read = new_value
        return new_value

    def send_bluetooth_hid(self, data):
        self._hid_communication_in.send_report(data)
        pass

    @property
    def bluetooth_connected(self):
        if not self.has_bluetooth:
            return False
        return self._bluetooth.connected

    def set_battery_level(self, value):
        self._battery_level = value
        self._batteryservice.level = self._battery_level


hardware_variant = HardwareOptions()
