import board
import digitalio

HW_VERSION = 0x00
FIVE_BUTTON_USB = 0x02
FIVE_BUTTON_BT = 0x03
TEN_BUTTON_USB = 0x04
TEN_BUTTON_BT = 0x05

if board.board_id == "waveshare_rp2040_zero":
    variant_pin = digitalio.DigitalInOut(board.GP29)
    variant_pin.direction = digitalio.Direction.INPUT
    variant_pin.pull = digitalio.Pull.UP
    
    if variant_pin.value:
        HW_VERSION = FIVE_BUTTON_USB
    else:
        HW_VERSION = TEN_BUTTON_USB
elif board.board_id == "supermini_nrf52840":
    variant_pin = digitalio.DigitalInOut(board.P0_17)
    variant_pin.direction = digitalio.Direction.INPUT
    variant_pin.pull = digitalio.Pull.UP
    
    if variant_pin.value:
        HW_VERSION = FIVE_BUTTON_BT
    else:
        HW_VERSION = TEN_BUTTON_BT

    