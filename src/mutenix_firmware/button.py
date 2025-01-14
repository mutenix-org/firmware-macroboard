import digitalio  # type: ignore
from utils import EventTime

DOUBLETAP_TIME_MS = 200


class Button:
    def __init__(self, id: int, pin=None):
        self._pin = digitalio.DigitalInOut(pin)
        self._pin.direction = digitalio.Direction.INPUT
        self._pin.pull = digitalio.Pull.UP
        self._state = not self._pin.value
        self._doubletap = False
        self._pressed = self._state
        self._released = not self._state
        self._triggered = False
        self._press_handled = False
        self._changed_state = False
        self._pushEventTime = EventTime()
        self._id = id
        self._counter = 0

    @property
    def state(self):
        return self._state

    @property
    def id(self):
        return self._id

    @property
    def doubletapped(self):
        difftime = self._pushEventTime.diff
        return difftime < DOUBLETAP_TIME_MS / 1000.0

    def read(self):
        value = not self._pin.value
        if self._state != value:
            self._changed_state = True
            self._state = value
            if value:
                self._pushEventTime.trigger()
                self._pressed = True
                self._released = False
                self._press_handled = False
                self._counter += 1
            else:
                self._released = True
                self._pressed = False
                if not self._press_handled:
                    self._triggered = True
        return self._pressed

    @property
    def triggered(self):
        retval = self._triggered
        self._triggered = False
        return retval

    @property
    def pressed(self):
        retval = self._pressed
        return retval

    @property
    def released(self):
        retval = self._released
        return retval

    @property
    def changed_state(self):
        retval = self._changed_state
        self._changed_state = False
        return retval

    @property
    def counter(self):
        return self._counter

    def handled(self):
        self._press_handled = True
