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


combos = {
    (0, 1, 4): do_reset,
}

last_communication = 0
rainbow = Rainbow(led, 1, 5)
combo_matched_time = {}


while True:
    data = macropad.get_last_received_report()
    try:
        if data:
            print("Data received")
            p = OutMessage.from_buffer(data)
            last_communication = time.monotonic()
            if isinstance(p, Ping):
                InMessage.initialize().send(macropad)
                print("ping")
            elif isinstance(p, SetColor):
                if p.buttonid < 5 and p.buttonid >= 0:
                    led[5-p.buttonid] = p.color
                print(f"led {p.buttonid} set to {p.color}")
            elif isinstance(p, Unknown):
                print(f"Unknown message {p.data}")

        if (time.monotonic() - last_communication) > 1:
            led[0] = ColorLeds.purple
            rainbow.next()

        for b in buttons:
            b.read()
            if b.changed_state:
                print(f"Button {b._pin} changed, send status")
                InMessage.button(b).send(macropad)
        for c, f in combos.items():
            if all([buttons[i].pressed for i in c]):
                if combo_matched_time[c] == 0:
                    combo_matched_time[c] = time.monotonic_ns()
                if time.monotonic_ns() - combo_matched_time[c] > COMBO_ACTIVATION_TIME:
                    f()
                    for i in c:
                        buttons[i].handled()
                    combo_matched_time = {}
            else:
                combo_matched_time[c] = 0

    except OSError as e:
        print(f"USB send not working, but who cares {e}")
