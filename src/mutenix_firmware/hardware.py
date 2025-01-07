from __future__ import annotations

import os

import board
import digitalio

FIVE_BUTTON_USB = 0x02
FIVE_BUTTON_BT = 0x03
FIVE_BUTTON_USB_V2 = 0x04
TEN_BUTTON_USB_V2 = 0x05
TEN_BUTTON_BT = 0x06


class HardwareOptions:
    def __init__(self):
        self.board_id = board.board_id
        self.led_count = 13
        if self.board_id == "waveshare_rp2040_zero":
            if os.path.exists("/version1"):
                self.led_pin = board.GP7
                self.led_count = 6
                self.hardware_variant = FIVE_BUTTON_USB
            else:
                self.variant_pin = board.GP29
                self.led_pin = board.GP15
                if self._is_ten_button_variant():
                    self.hardware_variant = TEN_BUTTON_USB_V2
                else:
                    self.hardware_variant = FIVE_BUTTON_USB
        elif self.board_id == "supermini_nrf52840":
            self.variant_pin = board.P0_17
            self.led_pin = board.P0_20
            if self._is_ten_button_variant():
                self.hardware_variant = TEN_BUTTON_BT
            else:
                self.hardware_variant = FIVE_BUTTON_BT

        self._set_buttons()

    def _set_buttons(self):
        if self.hardware_variant == FIVE_BUTTON_USB:
            self.buttons = [
                board.GP0,
                board.GP1,
                board.GP2,
                board.GP3,
                board.GP4,
            ]
        elif self.hardware_variant in [TEN_BUTTON_USB_V2, FIVE_BUTTON_USB_V2]:
            self.buttons = [
                board.GP11,
                board.GP10,
                board.GP9,
                board.GP8,
                board.GP7,
            ]
            if self.hardware_variant == TEN_BUTTON_USB_V2:
                self.buttons.extend(
                    [
                        board.GP6,
                        board.GP3,
                        board.GP2,
                        board.GP1,
                        board.GP0,
                    ]
                )
        elif self.hardware_variant in [FIVE_BUTTON_BT, TEN_BUTTON_BT]:
            self.buttons = [
                board.P1_04,
                board.P1_06,
                board.P0_09,
                board.P0_10,
                board.P1_11,
            ]
            if self.hardware_variant == TEN_BUTTON_BT:
                self.buttons.extend(
                    [
                        board.P1_13,
                        board.P1_15,
                        board.P0_02,
                        board.P0_29,
                        board.P0_31,
                    ]
                )

    def _is_ten_button_variant(self):
        variant = digitalio.DigitalInOut(self.variant_pin)
        variant.direction = digitalio.Direction.INPUT
        variant.pull = digitalio.Pull.UP
        return not variant.value


hardware_variant = HardwareOptions()
