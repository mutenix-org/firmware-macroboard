import storage
import usb_hid
import myhid
import supervisor
import usb_cdc
from mybuttons import buttons
from mode import device_mode
from debug_on import debug

supervisor.set_usb_identification("m42e.de", "macropad", pid=8323)
usb_hid.enable(
    (myhid.stupid_macroboard, myhid.stupid_keyboard)
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
