# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Matthias Bilger <matthias@bilger.info>
import time

import digitalio  # type: ignore

LONGPRESS_TIME_MS = 400


class Button:
    def __init__(self, id: int, pin=None):
        self._pin = digitalio.DigitalInOut(pin)
        self._pin.direction = digitalio.Direction.INPUT
        self._pin.pull = digitalio.Pull.UP
        self._state = not self._pin.value
        self._longpress = False
        self._pressed = self._state
        self._released = not self._state
        self._triggered = False
        self._changed_state = False
        self._last = 0.0
        self._id = id
        self._counter = 0

    @property
    def state(self):
        return self._state

    @property
    def id(self):
        return self._id

    @property
    def longpressed(self):
        return self._longpress

    def read(self):
        value = not self._pin.value
        if self._state != value:
            self._changed_state = True
            self._state = value
            if value:
                self._last = time.monotonic()
                self._longpress = False
                self._pressed = True
                self._released = False
                self._counter += 1
            else:
                self._longpress = (
                    self._last + LONGPRESS_TIME_MS / 1000 < time.monotonic()
                )
                self._released = True
                self._pressed = False
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
