import pytest
from unittest import mock
from mutenix_firmware.button import Button
from utils import EventTime

@pytest.fixture
def mock_digitalio():
    with mock.patch('digitalio.DigitalInOut') as mock_digitalinout:
        yield mock_digitalinout

@pytest.fixture
def mock_eventtime():
    with mock.patch('utils.EventTime') as mock_eventtime:
        yield mock_eventtime

def test_button_initialization(mock_digitalio, mock_eventtime):
    pin = mock.Mock()
    button = Button(id=1, pin=pin)
    assert button.id == 1
    assert button.state != mock_digitalio.return_value.value
    assert not button.doubletapped

def test_button_read(mock_digitalio, mock_eventtime):
    pin = mock.Mock()
    button = Button(id=1, pin=pin)
    mock_digitalio.return_value.value = False
    assert button.read()
    assert button.pressed
    assert not button.released
    assert button.changed_state

def test_button_triggered(mock_digitalio, mock_eventtime):
    pin = mock.Mock()
    button = Button(id=1, pin=pin)
    mock_digitalio.return_value.value = False
    button.read()
    assert not button.triggered
    mock_digitalio.return_value.value = True
    button.read()
    assert button.triggered
    assert not button.triggered

def test_button_handled(mock_digitalio, mock_eventtime):
    pin = mock.Mock()
    button = Button(id=1, pin=pin)
    button.read()
    button.handled()
    assert not button.triggered