# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Matthias Bilger <matthias@bilger.info>
import os
import time

import debug_on
import device_info
import myhid
import storage  # type: ignore
import supervisor  # type: ignore
import usb_cdc  # type: ignore
import usb_hid  # type: ignore
from hardware import hardware_variant


def check_boot_buttons():
    # Read the buttons in case a boot option button has been pressed
    hardware_variant.read_buttons()
    time.sleep(0.2)
    hardware_variant.read_buttons()

    storage_enabled = hardware_variant.boot_button_usb_pressed() or debug_on.filesystem
    serial_enabled = hardware_variant.boot_button_serial_pressed() or debug_on.serial
    print("serial", serial_enabled)
    print("storage", storage_enabled)

    if not serial_enabled:
        usb_cdc.disable()

    if not storage_enabled:
        storage.disable_usb_drive()  # disable CIRCUITPY drive

    force_update = hardware_variant.boot_button_update_pressed()

    if force_update:
        print("Force update")
        supervisor.set_next_code_file("updae.py")


def do_init():
    try:
        supervisor.set_usb_identification(
            manufacturer=device_info.MANUFACTURER,
            product=device_info.PRODUCT,
            vid=device_info.VID,
            pid=device_info.PID,
        )
        usb_hid.enable((myhid.stupid_macroboard,))
        print("USB identification set")
        print("manufacturer", device_info.MANUFACTURER)
        print("product", device_info.PRODUCT)
        print("vid", device_info.VID)
        print("pid", device_info.PID)
    except RuntimeError:
        print("Failed to set USB identification, expected?")

    try:
        if os.stat("code.py"):
            os.unlink("code.py")
    except OSError:
        print("no code.py file found. all fine")

    check_boot_buttons()


if supervisor.runtime.run_reason in [
    supervisor.RunReason.STARTUP,
    supervisor.RunReason.AUTO_RELOAD,
    supervisor.RunReason.SUPERVISOR_RELOAD,
    supervisor.RunReason.REPL_RELOAD,
]:
    # If we are running because of a soft reboot, we need to reset the device
    # mode to the default, as the device mode is not saved across reboots
    do_init()
