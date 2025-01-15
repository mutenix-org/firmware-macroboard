# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Matthias Bilger <matthias@bilger.info>
import time


class EventTime:
    def __init__(self, name=None):
        self.name = name
        self._last = 0.0
        self._current = 0.0
        self.triggered = 0

    def trigger(self, value=None):
        self._last = self._current
        self._current = value or time.monotonic()
        self.triggered += 1

    @property
    def diff(self):
        return self._current - self._last if self.triggered >= 2 else float("inf")
