from __future__ import annotations

import myhid
import storage # type: ignore
import supervisor # type: ignore
import usb_cdc # type: ignore
import usb_hid # type: ignore
from debug_on import debug
from mode import device_mode
from mybuttons import buttons

def do_init():
    supervisor.set_usb_identification("m42e.de", "macropad", pid=8323)
    usb_hid.enable(
        (myhid.stupid_macroboard, myhid.stupid_keyboard),
    )

    # Read the buttons in case a boot option button has been pressed
    for b in buttons:
        b.read()

    if buttons[0].released:
        storage.disable_usb_drive()  # disable CIRCUITPY drive
    else:
        device_mode.storage_enabled = True

    if buttons[1].released and not debug:
        usb_cdc.disable()
    else:
        device_mode.serial_enabled = True

if supervisor.runtime.run_reason in [supervisor.RunReason.STARTUP, supervisor.RunReason.AUTO_RELOAD, supervisor.RunReason.SUPERVISOR_RELOAD, supervisor.RunReason.REPL_RELOAD]:
    # If we are running because of a soft reboot, we need to reset the device
    # mode to the default, as the device mode is not saved across reboots
    do_init()
