import usb_hid
import time
from leds import ColorLeds, Rainbow
from protocol import InMessage, OutMessage, Ping, SetColor, Unknown
import microcontroller
from mybuttons import buttons

COMBO_ACTIVATION_TIME = 500_000_000

macropad = usb_hid.devices[0]
led = ColorLeds()


def do_reset():
    microcontroller.reset()


last_communication = 0
rainbow = Rainbow(led, 1, 5)
combo_matched_time = {}


def handle_received_report(data):
    print("Data received")
    p = OutMessage.from_buffer(data)
    if isinstance(p, Ping):
        InMessage.initialize().send(macropad)
        print("ping")
    elif isinstance(p, SetColor):
        if p.buttonid < 5 and p.buttonid >= 0:
            led[5-p.buttonid] = p.color
        print(f"led {p.buttonid} set to {p.color}")
    elif isinstance(p, Unknown):
        print(f"Unknown message {p.data}")


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


combos = Combos({
    (0, 1, 4): do_reset,
})

while True:
    data = macropad.get_last_received_report()
    try:
        if data:
            last_communication = time.monotonic()
            handle_received_report(data)

        if (time.monotonic() - last_communication) > 1:
            led[0] = ColorLeds.purple
            rainbow.next()

        for b in buttons:
            b.read()
            if b.changed_state:
                print(f"Button {b._pin} changed, send status")
                InMessage.button(b).send(macropad)
        combos.check()

    except OSError as e:
        print(f"USB send not working, but who cares {e}")
