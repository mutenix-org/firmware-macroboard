import board # type: ignore
import debug_on
import hardware
import microcontroller # type: ignore
import myhid
import time
import usb_hid # type: ignore

from leds import ColorLeds, Rainbow
from mybuttons import buttons
from protocol import InMessage, OutMessage, Ping, PrepareUpdate, SetColor, Unknown, Reset
from update import do_update

COMBO_ACTIVATION_TIME = 500_000_000
COMMUNICATION_TIMEOUT = 5.5

update_mode = False
macropad = usb_hid.devices[0]

if hardware.HW_VERSION == hardware.FIVE_BUTTON_USB:
    led_pin = board.GP7
    led_count = 6
elif hardware.HW_VERSION == hardware.TEN_BUTTON_USB_V2 or hardware.HW_VERSION == hardware.FIVE_BUTTON_USB_V2:
    led_pin = board.GP15
    led_count = 13
elif hardware.HW_VERSION == hardware.FIVE_BUTTON_BT or hardware.HW_VERSION == hardware.TEN_BUTTON_BT:
    led_pin = board.P0_20
    led_count = 13
led = ColorLeds(led_pin, led_count)


def log(*args, **kwargs):
    if debug_on.debug:
        print(*args, **kwargs)


def do_reset():
    microcontroller.reset()


last_communication: float = 0.0
rainbow = Rainbow(led, 1, 5, 0.025)


def handle_received_report(data):
    log("Data received")
    p = OutMessage.from_buffer(data)
    if isinstance(p, Ping):
        InMessage.initialize().send(macropad)
        log("ping")
    elif isinstance(p, SetColor):
        if p.buttonid < 6 and p.buttonid >= 1:
            led[6-p.buttonid] = p.color
        log(f"led {p.buttonid} set to {p.color}")
    elif isinstance(p, PrepareUpdate):
        log("Prepare update")
        global update_mode
        update_mode = True
    elif isinstance(p, Reset):
        log("Reset")
        do_reset()
    elif isinstance(p, Unknown):
        log(f"Unknown message {p.data}")


class Combos:
    def __init__(self, combos):
        self.combos = combos
        self.combo_matched_time = {}

    def check(self):
        for c, f in self.combos.items():
            if all([buttons[i].pressed for i in c]):
                if self.combo_matched_time[c] == 0:
                    self.combo_matched_time[c] = time.monotonic_ns()
                if time.monotonic_ns() - self.combo_matched_time[c] > COMBO_ACTIVATION_TIME:
                    f()
                    for i in c:
                        buttons[i].handled()
                    self.combo_matched_time = {}
            else:
                self.combo_matched_time[c] = 0

def send_url():
    keyboard = myhid.stupid_keyboard
    url = "https://mutenix.de"
    for char in url:
        report = [0x00] * 8
        if 'a' <= char <= 'z':
            report[2] = ord(char) - ord('a') + 0x04
        elif 'A' <= char <= 'Z':
            report[0] = 0x02  # Left Shift
            report[2] = ord(char) - ord('A') + 0x04
        elif char == ':':
            report[0] = 0x02  # Left Shift
            report[2] = 0x33  # Colon
        elif char == '/':
            report[2] = 0x38  # Slash
        elif char == '.':
            report[2] = 0x37  # Period
        keyboard.send_report(bytearray(report), 3)
        keyboard.send_report(bytearray([0x00] * 8), 3)  # Release key

combos = Combos({
    (0, 1, 4): do_reset,
    (3, 4): send_url,
})

while True:
    try:
        data = macropad.get_last_received_report(1)
    except Exception as e:
        log(f"USB receiving not working, but who cares {e}")
    try:
        if data:
            log('data', data)
            if last_communication == 0:
                InMessage.status_request().send(macropad)
            last_communication = time.monotonic()
            handle_received_report(data)
            led[0] = ColorLeds.green

        if (time.monotonic() - last_communication) > COMMUNICATION_TIMEOUT:
            led[0] = ColorLeds.purple
            rainbow.next()
            last_communication = 0

        for b in buttons:
            b.read()
            if b.changed_state:
                log(f"Button {b._pin} changed, send status")
                InMessage.button(b).send(macropad)
        combos.check()

    except OSError as e:
        log(f"USB send not working, but who cares {e}")

    if update_mode:
        do_update(led)
        update_mode = False
