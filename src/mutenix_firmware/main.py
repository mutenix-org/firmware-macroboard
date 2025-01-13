import time

import supervisor  # type: ignore
import usb_hid  # type: ignore
from hardware import hardware_variant
from log import log
from protocol import InMessage
from protocol import OutMessage
from protocol import Ping
from protocol import PrepareUpdate
from protocol import Reset
from protocol import SetColor
from protocol import Unknown
from protocol import UpdateConfig
from update import do_update

COMBO_ACTIVATION_TIME = 500_000_000
COMMUNICATION_TIMEOUT = 5.5

update_mode = False
macropad = usb_hid.devices[0]


def do_reset():  # pragma: no cover
    import microcontroller  # type: ignore

    microcontroller.reset()


last_communication: float = 0.0


def update_config(update):
    with open("/debug_on.py", "r") as f:
        lines = f.readlines()

    with open("/debug_on.py", "w") as f:
        for line in lines:
            if "=" not in line:
                f.write(line)
                continue
            name, value = map(str.strip, line.split("="))
            if name == "debug" and update.update_debug is not None:
                value = str(update.activate_debug)
            if name == "filesystem" and update.update_filesystem is not None:
                value = str(update.activate_filesystem)
            f.write(f"{name} = {value}\n")


def handle_received_report(data):
    log("Data received")
    p = OutMessage.from_buffer(data)
    if isinstance(p, Ping):
        InMessage.initialize().send(macropad)
        log("ping")
    elif isinstance(p, SetColor):
        if p.buttonid < 6 and p.buttonid >= 1:
            hardware_variant.leds[p.buttonid] = p.color
        log(f"led {p.buttonid} set to {p.color}")
    elif isinstance(p, PrepareUpdate):
        log("Prepare update")
        global update_mode
        update_mode = True
    elif isinstance(p, Reset):
        log("Reset")
        do_reset()
    elif isinstance(p, UpdateConfig):
        log(f"Update config {p.activate_debug}, {p.activate_filesystem}")
        update_config(p)
    elif isinstance(p, Unknown):
        log(f"Unknown message {p.data}")


class Combos:
    def __init__(self, combos):
        self.combos = combos
        self.combo_matched_time = {}

    def check(self):
        for c, f in self.combos.items():
            if all([hardware_variant.buttons[i].pressed for i in c]):
                if self.combo_matched_time[c] == 0:
                    self.combo_matched_time[c] = time.monotonic_ns()
                if (
                    time.monotonic_ns() - self.combo_matched_time[c]
                    > COMBO_ACTIVATION_TIME
                ):
                    f()
                    for i in c:
                        hardware_variant.buttons[i].handled()
                    self.combo_matched_time = {}
            else:
                self.combo_matched_time[c] = 0


combos = Combos(
    {
        (0, 1, 4): do_reset,
    },
)

hardware_variant.setup_bluetooth()

while True:
    data = None
    if hardware_variant.bluetooth_connected:
        try:
            data = hardware_variant.read_bluetooth_hid()
            if data:
                log("data from bt", data)
        except Exception as e:
            log(f"Bluetooth receiving not working, but who cares {e}")
    elif supervisor.runtime.usb_connected:
        try:
            data = macropad.get_last_received_report(1)
            if data:
                log("data from usb", data)
        except Exception as e:
            log(f"USB receiving not working, but who cares {e}")
    try:
        if data:
            # hardware_variant.leds.rainbow_off()
            if last_communication == 0:
                if hardware_variant.bluetooth_connected:
                    log("send bt")
                    hardware_variant.send_bluetooth_hid(
                        InMessage.status_request()._data,
                    )
                elif supervisor.runtime.usb_connected:
                    log("send usb")
                    InMessage.status_request().send(macropad)
            last_communication = time.monotonic()
            handle_received_report(data)
            hardware_variant.leds[0] = "green"

        if (time.monotonic() - last_communication) > COMMUNICATION_TIMEOUT:
            hardware_variant.leds[0] = "red"
            # hardware_variant.leds.rainbow_next()
            last_communication = 0

        for b in hardware_variant.buttons:
            b.read()
            if b.changed_state:
                log(f"Button {b._pin} changed")
                if hardware_variant.bluetooth_connected:
                    log("send bt")
                    hardware_variant.send_bluetooth_hid(InMessage.button(b)._data)
                elif supervisor.runtime.usb_connected:
                    log("send usb")
                    InMessage.button(b).send(macropad)
        combos.check()

    except OSError as e:
        log(f"USB send not working, but who cares {e}")

    hardware_variant.check_bluetooth()

    if supervisor.runtime.usb_connected:
        if update_mode:
            do_update(hardware_variant)
            update_mode = False
