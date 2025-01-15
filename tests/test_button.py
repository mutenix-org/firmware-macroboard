# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Matthias Bilger <matthias@bilger.info>
import sys
from importlib.abc import MetaPathFinder
from unittest import mock

import pytest
from mutenix_firmware.button import Button


class MockFcntl(MetaPathFinder):
    def find_spec(self, fullname, target, path=None):
        if fullname == "digitalio":
            return mock.MagicMock()


sys.meta_path.insert(0, MockFcntl())


@pytest.fixture
def mock_digitalio():
    with mock.patch("digitalio.DigitalInOut") as mock_digitalinout:
        yield mock_digitalinout


@pytest.fixture
def mock_eventtime():
    with mock.patch("utils.EventTime") as mock_eventtime:
        yield mock_eventtime


def test_button_initialization(mock_digitalio, mock_eventtime):
    pin = mock.Mock()
    button = Button(id=1, pin=pin)
    assert button.id == 1
    assert button.state != mock_digitalio.return_value.value
    assert not button.doubletapped


def test_button_read(mock_digitalio, mock_eventtime):
    pin_mock = mock.Mock()
    pin_mock.value = True
    mock_digitalio.return_value = pin_mock
    button = Button(id=1)
    button._pin.value = False
    assert button.read()
    assert button.pressed
    assert not button.released
    assert button.changed_state


def test_button_triggered(mock_digitalio, mock_eventtime):
    pin_mock = mock.Mock()
    pin_mock.value = False
    mock_digitalio.return_value = pin_mock
    button = Button(id=1)
    button.read()
    assert not button.triggered
    button._pin.value = True
    button.read()
    assert button.triggered
    assert not button.triggered


def test_button_handled(mock_digitalio, mock_eventtime):
    pin = mock.Mock()
    button = Button(id=1, pin=pin)
    button.read()
    button.handled()
    assert not button.triggered
