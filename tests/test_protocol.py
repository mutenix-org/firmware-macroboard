from __future__ import annotations

import sys
from unittest import mock

sys.modules['hardware'] = mock.Mock()
sys.modules['hardware'].HW_VERSION = 1  # type: ignore[attr-defined]
from mutenix_firmware.protocol import OutMessage, Ping, SetColor, PrepareUpdate, Reset, Unknown, InMessage # noqa: E402
from mutenix_firmware.button import Button # noqa: E402
import version as v # noqa: E402

OUT_REPORT_LENGTH = 8

def test_outmessage_from_buffer_ping():
    buffer = bytearray([OutMessage.PING] + [0] * (OUT_REPORT_LENGTH - 1))
    message = OutMessage.from_buffer(buffer)
    assert isinstance(message, Ping)

def test_outmessage_from_buffer_setcolor():
    buffer = bytearray([OutMessage.SETCOLOR, 1, 2, 3, 4, 5, 0, 0])
    message = OutMessage.from_buffer(buffer)
    assert isinstance(message, SetColor)
    assert message.buttonid == 1
    assert message.color == bytearray([2, 3, 4, 5])

def test_outmessage_from_buffer_prepare_update():
    buffer = bytearray([OutMessage.PREPARE_UPDATE] + [0] * (OUT_REPORT_LENGTH - 1))
    message = OutMessage.from_buffer(buffer)
    assert isinstance(message, PrepareUpdate)

def test_outmessage_from_buffer_reset():
    buffer = bytearray([OutMessage.RESET] + [0] * (OUT_REPORT_LENGTH - 1))
    message = OutMessage.from_buffer(buffer)
    assert isinstance(message, Reset)

def test_outmessage_from_buffer_unknown():
    buffer = bytearray([0xFF] + [0] * (OUT_REPORT_LENGTH - 1))
    message = OutMessage.from_buffer(buffer)
    assert isinstance(message, Unknown)
    assert message.data == buffer

def test_inmessage_initialize():
    message = InMessage.initialize()
    expected_data = [InMessage.INITIALIZE, v.MAJOR, v.MINOR, v.PATCH, 1] + [0] * (OUT_REPORT_LENGTH - 5)
    assert message._data == bytearray(expected_data)

def test_inmessage_button():
    button = mock.Mock(spec=Button)
    button.id = 1
    button.triggered = True
    button.doubletapped = False
    button.pressed = True
    button.released = False
    message = InMessage.button(button)
    expected_data = [InMessage.STATUS, 1, True, False, True, False] + [0] * (OUT_REPORT_LENGTH - 6)
    assert message._data == bytearray(expected_data)

def test_inmessage_status_request():
    message = InMessage.status_request()
    expected_data = [InMessage.STATUS_REQUEST] + [0] * (OUT_REPORT_LENGTH - 1)
    assert message._data == bytearray(expected_data)

def test_inmessage_send():
    device = mock.Mock()
    data = [1, 2, 3, 4, 5, 6, 7, 8]
    message = InMessage(data)
    message.send(device)
    device.send_report.assert_called_once_with(bytearray(data), 1)
