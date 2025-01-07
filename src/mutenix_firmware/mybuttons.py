from __future__ import annotations

from hardware import hardware_variant
from button import Button


"""Buttons for enabling special boot modes."""
BOOT_USB_BUTTON = 0
BOOT_SERIAL_BUTTON = 1

buttons = [Button(i, pin) for i, pin in enumerate(hardware_variant.buttons)]


def read_buttons():
    for b in buttons:
        b.read()


def boot_button_usb_pressed():
    return buttons[BOOT_USB_BUTTON].pressed


def boot_button_serial_pressed():
    return buttons[BOOT_SERIAL_BUTTON].pressed
