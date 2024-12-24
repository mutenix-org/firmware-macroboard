import board # type: ignore
import digitalio # type: ignore
from button import Button
import hardware

def is_ten_button_variant(pin):
    pin = digitalio.DigitalInOut(pin)
    pin.direction = digitalio.Direction.INPUT
    pin.pull = digitalio.Pull.UP
    return not pin.value


if hardware.HW_VERSION == hardware.FIVE_BUTTON_USB:
    buttons = [
        Button(1, board.GP0),
        Button(2, board.GP1),
        Button(3, board.GP2),
        Button(4, board.GP3),
        Button(5, board.GP4),
    ]
elif hardware.HW_VERSION == hardware.TEN_BUTTON_USB_V2 or hardware.HW_VERSION == hardware.TEN_BUTTON_BT:
    buttons = [
        Button(1, board.GP11),
        Button(2, board.GP10),
        Button(3, board.GP9),
        Button(4, board.GP8),
        Button(5, board.GP7),
    ]
    if hardware.HW_VERSION == hardware.TEN_BUTTON_USB_V2:
        buttons.extend([
            Button(6, board.GP6),
            Button(7, board.GP3),
            Button(8, board.GP2),
            Button(9, board.GP1),
            Button(10, board.GP0),
        ])
elif hardware.HW_VERSION == hardware.FIVE_BUTTON_BT or hardware.HW_VERSION == hardware.TEN_BUTTON_BT:
    buttons = [
        Button(1, board.P1_04),
        Button(2, board.P1_06),
        Button(3, board.P0_09),
        Button(4, board.P0_10),
        Button(5, board.P1_11),
    ]
    if hardware.HW_VERSION == hardware.TEN_BUTTON_BT:
        buttons.extend([
            Button(6, board.P1_13),
            Button(7, board.P1_15),
            Button(8, board.P0_02),
            Button(9, board.P0_29),
            Button(10, board.P0_31),
        ])
