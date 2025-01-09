from __future__ import annotations

import time

import digitalio  # type: ignore
import neopixel_write  # type: ignore


def mix_color(color1, color2, descriminant, divisor):
    return bytearray(
        [
            int(
                (color1[i] * descriminant + color2[i] * (divisor - descriminant))
                / divisor,
            )
            for i in range(4)
        ],
    )


class ColorLeds:
    blue = bytearray([0, 0, 10, 0])
    purple = bytearray([0, 10, 10, 0])
    red = bytearray([0, 10, 0, 0])
    green = bytearray([10, 00, 0, 0])
    yellow = bytearray([10, 10, 0, 0])
    off = bytearray([0, 0, 0, 0])

    def __init__(self, pin=None, count=6):
        self.pin = digitalio.DigitalInOut(pin)
        self.pin.direction = digitalio.Direction.OUTPUT
        self.colors = bytearray(count * 4)
        self.count = count

    def __getitem__(self, key):
        return self.colors[key * 4 : key * 4 + 4]

    def __setitem__(self, key, value):
        if not isinstance(value, (bytes, bytearray)):
            raise ValueError("Value must be a bytes or bytearray object")
        if len(value) != 4:
            raise ValueError("Value must be exactly 4 bytes long")
        self.colors[key * 4 : key * 4 + 4] = value
        neopixel_write.neopixel_write(self.pin, self.colors)


class Rainbow:
    def __init__(self, led, start, end, speed=0.1):
        self.led = led
        self.speed = speed
        self._hue = 0
        self._start = start
        self._end = end
        self._time = time.monotonic()
        self._was_active = True

    def next(self):
        if time.monotonic() - self._time < self.speed:
            return
        self._was_active = True
        self._time = time.monotonic()
        self._hue = (self._hue + self.speed) % 1
        for i in range(self._start, self._end + 1):
            self.led[i] = self._color(i)

    def was_active(self):
        return self._was_active

    def off(self):
        self._was_active = False
        for i in range(self._start, self._end + 1):
            self.led[i] = (0, 0, 0, 0)

    def _color(self, i):
        r, g, b = self._hsv_to_rgb(self._hue, 1, 1)
        return bytearray([int(g * 10), int(r * 10), int(b * 10), 0])

    def _hsv_to_rgb(self, h, s, v):
        i = int(h * 6)
        f = (h * 6) - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)

        if i % 6 == 0:
            r, g, b = v, t, p
        elif i % 6 == 1:
            r, g, b = q, v, p
        elif i % 6 == 2:
            r, g, b = p, v, t
        elif i % 6 == 3:
            r, g, b = p, q, v
        elif i % 6 == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q

        return r, g, b
