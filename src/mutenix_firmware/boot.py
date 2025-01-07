from __future__ import annotations

import myhid
import storage  # type: ignore
import supervisor  # type: ignore
import usb_cdc  # type: ignore
import usb_hid  # type: ignore
from debug_on import debug
from mode import device_mode
from mybuttons import read_buttons, boot_button_usb_pressed, boot_button_serial_pressed


def check_boot_buttons():
    # Read the buttons in case a boot option button has been pressed
    read_buttons()

    device_mode.storage_enabled = boot_button_serial_pressed()
    device_mode.serial_enabled = boot_button_usb_pressed() or debug

    if not device_mode.serial_enabled:
        usb_cdc.disable()

    if not device_mode.storage_enabled:
        storage.disable_usb_drive()  # disable CIRCUITPY drive


def do_init():
    supervisor.set_usb_identification("m42e.de", "macropad", pid=8323)
    usb_hid.enable(
        (myhid.stupid_macroboard, myhid.stupid_keyboard),
    )

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
