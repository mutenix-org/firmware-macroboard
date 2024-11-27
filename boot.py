import storage
import usb_hid
import myhid
import supervisor
import microcontroller
import usb_cdc
from mybuttons import buttons

supervisor.set_usb_identification("m42e.de", "macropad", pid=8323)
usb_hid.enable(
    (myhid.stupid_macroboard, )
)

# Read the buttons in case a boot option button has been pressed
for b in buttons:
    b.read()

if buttons[0].released:
    storage.disable_usb_drive()  # disable CIRCUITPY drive

if buttons[1].released:
    usb_cdc.disable()
