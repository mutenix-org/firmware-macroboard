import time

class EventTime:
    def __init__(self, name=None):
        self.name = name
        self._last = 0.0
        self._current = 0.0

    def trigger(self, value=None):
        self._last = self._current
        self._current = value or time.monotonic()

    @property
    def diff(self):
        return self._current - self._last