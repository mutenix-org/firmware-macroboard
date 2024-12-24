from __future__ import annotations

import sys
from unittest import mock

import digitalio
import pytest

sys.modules['neopixel_write'] = mock.Mock()

from mutenix_firmware.leds import ColorLeds # noqa: E402

@pytest.fixture
def mock_digitalio():
    with mock.patch('digitalio.DigitalInOut') as mock_digitalinout:
        yield mock_digitalinout

@pytest.fixture
def mock_neopixel_write():
    with mock.patch('neopixel_write.neopixel_write') as mock_neopixel:
        yield mock_neopixel

def test_colorleds_initialization(mock_digitalio):
    pin = mock.Mock()
    leds = ColorLeds(pin=pin, count=6)
    assert leds.count == 6
    assert len(leds.colors) == 24
    mock_digitalio.assert_called_once_with(pin)
    assert mock_digitalio.return_value.direction == digitalio.Direction.OUTPUT

def test_colorleds_getitem(mock_digitalio):
    pin = mock.Mock()
    leds = ColorLeds(pin=pin, count=6)
    leds.colors[0:4] = ColorLeds.red
    assert leds[0] == ColorLeds.red

def test_colorleds_setitem(mock_digitalio, mock_neopixel_write):
    pin = mock.Mock()
    leds = ColorLeds(pin=pin, count=6)
    leds[0] = ColorLeds.green
    assert leds[0] == ColorLeds.green
    mock_neopixel_write.assert_called_once_with(mock_digitalio.return_value, leds.colors)

def test_colorleds_setitem_invalid_value(mock_digitalio):
    pin = mock.Mock()
    leds = ColorLeds(pin=pin, count=6)
    with pytest.raises(ValueError):
        leds[0] = [10, 0, 0]  # Not a bytes or bytearray object
    with pytest.raises(ValueError):
        leds[0] = bytearray([10, 0, 0])  # Not exactly 4 bytes long
