from __future__ import annotations

import os

import board
import digitalio

HW_VERSION = 0x00
FIVE_BUTTON_USB = 0x02
FIVE_BUTTON_BT = 0x03
FIVE_BUTTON_USB_V2 = 0x04
TEN_BUTTON_USB_V2 = 0x05
TEN_BUTTON_BT = 0x06


def is_ten_button_variant(variant):
    variant = digitalio.DigitalInOut(variant)
    variant.direction = digitalio.Direction.INPUT
    variant.pull = digitalio.Pull.UP
    return not variant.value


if board.board_id == "waveshare_rp2040_zero":
    if os.path.exists("/version1"):
        HW_VERSION = FIVE_BUTTON_USB
    else:
        if is_ten_button_variant(board.GP29):
            HW_VERSION = TEN_BUTTON_USB_V2
        else:
            HW_VERSION = FIVE_BUTTON_USB

elif board.board_id == "supermini_nrf52840":
    if is_ten_button_variant(board.P0_17):
        HW_VERSION = TEN_BUTTON_BT
    else:
        HW_VERSION = FIVE_BUTTON_BT
