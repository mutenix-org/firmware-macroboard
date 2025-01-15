# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Matthias Bilger <matthias@bilger.info>
import time

from mutenix_firmware.utils import EventTime


def test_eventtime_initialization():
    event_time = EventTime(name="test_event")
    assert event_time.name == "test_event"
    assert event_time._last == 0.0
    assert event_time._current == 0.0
    assert event_time.triggered == 0


def test_eventtime_trigger():
    event_time = EventTime()
    initial_time = time.monotonic()
    event_time.trigger(initial_time)
    assert event_time._last == 0.0
    assert event_time._current == initial_time
    assert event_time.triggered == 1

    new_time = initial_time + 1.0
    event_time.trigger(new_time)
    assert event_time._last == initial_time
    assert event_time._current == new_time
    assert event_time.triggered == 2


def test_eventtime_diff():
    event_time = EventTime()
    assert event_time.diff == float("inf")

    initial_time = time.monotonic()
    event_time.trigger(initial_time)
    assert event_time.diff == float("inf")

    new_time = initial_time + 1.0
    event_time.trigger(new_time)
    assert event_time.diff == 1.0
