from __future__ import annotations

import sys
from unittest import mock
from unittest.mock import MagicMock
from unittest.mock import patch
from unittest.mock import PropertyMock

import pytest

sys.modules["supervisor"] = mock.Mock()
sys.modules["usb_hid"] = mock.MagicMock()
sys.modules["storage"] = mock.Mock()
sys.modules["board"] = mock.MagicMock()

from mutenix_firmware.update import (  # noqa: E402
    FileTransport,
    FILE_TRANSPORT_START,
    FILE_TRANSPORT_DATA,
    FILE_TRANSPORT_END,
    FILE_TRANSPORT_FINISH,
    FILE_TRANSPORT_DELETE,
    LedStatus,
    File,
    do_update,
)


def test_filetransport_initialization():
    data = (
        FILE_TRANSPORT_START.to_bytes(2, "little")
        + (1).to_bytes(2, "little")
        + (10).to_bytes(2, "little")
        + (0).to_bytes(2, "little")
        + b"filename.txt"
    )
    ft = FileTransport(data)
    assert ft.type_ == FILE_TRANSPORT_START
    assert ft.id == 1
    assert ft.total_packages == 10
    assert ft.package == 0
    assert ft.content == b"filename.txt"


def test_filetransport_is_valid():
    valid_data = (
        FILE_TRANSPORT_START.to_bytes(2, "little")
        + (1).to_bytes(2, "little")
        + (10).to_bytes(2, "little")
        + (0).to_bytes(2, "little")
        + b"filename.txt"
    )
    invalid_data = (9999).to_bytes(2, "little") + b"\x00" * 6
    ft_valid = FileTransport(valid_data)
    ft_invalid = FileTransport(invalid_data)
    assert ft_valid.is_valid() is True
    assert ft_invalid.is_valid() is False


def test_filetransport_as_start():
    data = (
        FILE_TRANSPORT_START.to_bytes(2, "little")
        + (1).to_bytes(2, "little")
        + (10).to_bytes(2, "little")
        + (0).to_bytes(2, "little")
        + b"\x0cfilename.txt\x04\x00\x00\x10"
    )
    ft = FileTransport(data)
    filename, total_size = ft.as_start()
    assert filename == "filename.txt"
    assert total_size == 1048576


def test_filetransport_is_end():
    data = (
        FILE_TRANSPORT_END.to_bytes(2, "little")
        + (1).to_bytes(2, "little")
        + (10).to_bytes(2, "little")
        + (0).to_bytes(2, "little")
        + b""
    )
    ft = FileTransport(data)
    assert ft.is_end() is True


def test_filetransport_is_finish():
    data = (
        FILE_TRANSPORT_FINISH.to_bytes(2, "little")
        + (1).to_bytes(2, "little")
        + (10).to_bytes(2, "little")
        + (0).to_bytes(2, "little")
        + b""
    )
    ft = FileTransport(data)
    assert ft.is_finish() is True


def test_file_initialization():
    data = (
        FILE_TRANSPORT_START.to_bytes(2, "little")
        + (1).to_bytes(2, "little")
        + (10).to_bytes(2, "little")
        + (0).to_bytes(2, "little")
        + b"\x0cfilename.txt\x04\x00\x00\x10"
    )
    ft = FileTransport(data)
    file = File(ft)
    assert file.filename == "filename.txt"
    assert file.total_size == 1048576
    assert file.id == 1
    assert file.packages == list(range(11))
    assert len(file.content) == 1048576


def test_file_write():
    start_data = (
        FILE_TRANSPORT_START.to_bytes(2, "little")
        + (1).to_bytes(2, "little")
        + (10).to_bytes(2, "little")
        + (0).to_bytes(2, "little")
        + b"\x0cfilename.txt\x04\x00\x00\x10"
    )
    ft_start = FileTransport(start_data)
    file = File(ft_start)

    data = (
        FILE_TRANSPORT_DATA.to_bytes(2, "little")
        + (1).to_bytes(2, "little")
        + (10).to_bytes(2, "little")
        + (1).to_bytes(2, "little")
        + b"12345678"
    )
    ft_data = FileTransport(data)
    file.write(ft_data)
    assert (
        file.content[FileTransport.content_length : FileTransport.content_length + 8]
        == b"12345678"
    )
    assert 1 not in file.packages


def test_file_is_complete():
    start_data = (
        FILE_TRANSPORT_START.to_bytes(2, "little")
        + (1).to_bytes(2, "little")
        + (10).to_bytes(2, "little")
        + (0).to_bytes(2, "little")
        + b"\x0cfilename.txt\x04\x00\x00\x10"
    )
    ft_start = FileTransport(start_data)
    file = File(ft_start)

    for i in range(11):
        data = (
            FILE_TRANSPORT_DATA.to_bytes(2, "little")
            + (1).to_bytes(2, "little")
            + (10).to_bytes(2, "little")
            + (i).to_bytes(2, "little")
            + b"12345678"
        )
        ft_data = FileTransport(data)
        file.write(ft_data)

    assert file.is_complete() is True


def test_ledstatus_initialization():
    led = [bytearray((0, 0, 0, 0)) for _ in range(6)]
    led_status = LedStatus(led)
    assert led_status.led_status == 0
    assert led_status.led == led


@pytest.mark.skip
def test_ledstatus_update():
    led = [bytearray((0, 0, 0, 0)) for _ in range(6)]
    led_status = LedStatus(led)

    for _ in range(101):
        led_status.update()

    assert led_status.led_status == 1
    assert led[1] == bytearray((9, 0, 1, 0))
    assert led[2] == bytearray((9, 0, 1, 0))

    for _ in range(9):
        led_status.update()

    assert led_status.led_status == 10
    assert led[1] == bytearray((1, 0, 9, 0))
    assert led[2] == bytearray((10, 0, 0, 0))

    for _ in range(10):
        led_status.update()

    assert led_status.led_status == 20
    assert led[1] == bytearray((1, 0, 9, 0))
    assert led[2] == bytearray((1, 0, 9, 0))

    for _ in range(70):
        led_status.update()

    assert led_status.led_status == 90
    assert led[5] == bytearray((0, 0, 10, 0))

    for _ in range(10):
        led_status.update()

    assert led_status.led_status == 0
    assert led[1] == bytearray((10, 0, 0, 0))


@pytest.mark.skip
def test_do_update_successful_update():
    led = [bytearray((0, 0, 0, 0)) for _ in range(6)]
    patch("storage.remount")
    patch("supervisor.runtime.autoreload", new_callable=PropertyMock)
    patch("time.monotonic", side_effect=[0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5])
    device_mock = MagicMock()
    sys.modules["usb_hid"].devices = [device_mock]
    device_mock.get_last_received_report = mock.Mock(
        side_effect=[
            None,
            FILE_TRANSPORT_START.to_bytes(2, "little")
            + (1).to_bytes(2, "little")
            + (0).to_bytes(2, "little")
            + (0).to_bytes(2, "little")
            + b"\x0cfilename.txt\x04\x08\x00\x00\x00",
            FILE_TRANSPORT_DATA.to_bytes(2, "little")
            + (1).to_bytes(2, "little")
            + (0).to_bytes(2, "little")
            + (0).to_bytes(2, "little")
            + b"12345678",
            FILE_TRANSPORT_END.to_bytes(2, "little")
            + (1).to_bytes(2, "little")
            + (0).to_bytes(2, "little")
            + (0).to_bytes(2, "little")
            + b"",
            FILE_TRANSPORT_FINISH.to_bytes(2, "little")
            + (1).to_bytes(2, "little")
            + (0).to_bytes(2, "little")
            + (0).to_bytes(2, "little")
            + b"",
            None,
        ],
    )
    mock_open = mock.mock_open()
    with patch("builtins.open", mock_open):
        with patch("mutenix_firmware.update.TIMEOUT_TRANSFER", 0.1):
            with patch("mutenix_firmware.update.TIMEOUT_UPDATE", 0.1):
                do_update(led)

    assert led[0] == bytearray((10, 0, 0, 0))
    assert led[1] == bytearray((10, 0, 0, 0))
    assert led[2] == bytearray((10, 0, 0, 0))
    assert led[3] == bytearray((10, 0, 0, 0))
    assert led[4] == bytearray((10, 0, 0, 0))
    assert led[5] == bytearray((10, 0, 0, 0))
    mock_open.assert_called_once_with("filename.txt", "wb")
    mock_open().write.assert_called_once_with(
        b"12345678",
    )


@pytest.mark.skip
def test_do_update_timeout():
    led = [bytearray((0, 0, 0, 0)) for _ in range(6)]
    patch("storage.remount")
    patch("supervisor.runtime.autoreload", new_callable=PropertyMock)
    patch(
        "time.monotonic",
        side_effect=[0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 15],
    )
    patch("usb_hid.devices", [mock.Mock()])
    device_mock = MagicMock()
    sys.modules["usb_hid"].devices = [device_mock]
    device_mock.get_last_received_report.return_value = None

    with patch("mutenix_firmware.update.TIMEOUT_TRANSFER", 0.1):
        with patch("mutenix_firmware.update.TIMEOUT_UPDATE", 0.1):
            with patch("mutenix_firmware.update.TIME_SHOW_FINAL_STATUS", 0.1):
                do_update(led)

    assert led[0] == bytearray((10, 0, 0, 0))
    assert led[1] == bytearray((10, 0, 0, 0))
    assert led[2] == bytearray((10, 0, 0, 0))
    assert led[3] == bytearray((10, 0, 0, 0))
    assert led[4] == bytearray((10, 0, 0, 0))
    assert led[5] == bytearray((10, 0, 0, 0))


@pytest.mark.skip
def test_do_update_remount_failure():
    led = [bytearray((0, 0, 0, 0)) for _ in range(6)]
    sys.modules["storage"].remount.side_effect = RuntimeError
    patch("time.sleep")
    device_mock = MagicMock()
    sys.modules["usb_hid"].devices = [device_mock]
    device_mock.get_last_received_report.return_value = None

    with patch("mutenix_firmware.update.TIMEOUT_TRANSFER", 0.1):
        with patch("mutenix_firmware.update.TIMEOUT_UPDATE", 0.1):
            with patch("mutenix_firmware.update.TIME_SHOW_FINAL_STATUS", 0.1):
                do_update(led)

    assert led[1] == bytearray((0, 10, 0, 0))
    assert led[2] == bytearray((0, 10, 0, 0))
    assert led[3] == bytearray((0, 10, 0, 0))
    assert led[4] == bytearray((0, 10, 0, 0))
    assert led[5] == bytearray((0, 10, 0, 0))
    sys.modules["storage"].remount.side_effect = None


def test_filetransport_is_delete():
    data = (
        FILE_TRANSPORT_DELETE.to_bytes(2, "little")
        + (1).to_bytes(2, "little")
        + (10).to_bytes(2, "little")
        + (0).to_bytes(2, "little")
        + b"\x0cfilename.txt"
    )
    ft = FileTransport(data)
    assert ft.is_delete() is True
    assert ft.as_delete() == "filename.txt"


@pytest.mark.skip
def test_do_update_delete_file():
    led = [bytearray((0, 0, 0, 0)) for _ in range(6)]
    patch("storage.remount")
    patch("supervisor.runtime.autoreload", new_callable=PropertyMock)
    patch("time.monotonic", side_effect=[0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5])
    device_mock = MagicMock()
    sys.modules["usb_hid"].devices = [device_mock]
    device_mock.get_last_received_report = mock.Mock(
        side_effect=[
            None,
            FILE_TRANSPORT_DELETE.to_bytes(2, "little")
            + (1).to_bytes(2, "little")
            + (0).to_bytes(2, "little")
            + (0).to_bytes(2, "little")
            + b"\x0cfilename.txt",
            FILE_TRANSPORT_FINISH.to_bytes(2, "little")
            + (1).to_bytes(2, "little")
            + (0).to_bytes(2, "little")
            + (0).to_bytes(2, "little")
            + b"",
            None,
        ],
    )
    mock_open = mock.mock_open()
    with patch("builtins.open", mock_open):
        with patch("os.unlink") as mock_unlink:
            with patch("mutenix_firmware.update.TIMEOUT_TRANSFER", 0.1):
                with patch("mutenix_firmware.update.TIMEOUT_UPDATE", 0.1):
                    do_update(led)

    mock_unlink.assert_called_once_with("filename.txt")
    assert led[0] == bytearray((10, 0, 0, 0))
    assert led[1] == bytearray((10, 0, 0, 0))
    assert led[2] == bytearray((10, 0, 0, 0))
    assert led[3] == bytearray((10, 0, 0, 0))
    assert led[4] == bytearray((10, 0, 0, 0))
    assert led[5] == bytearray((10, 0, 0, 0))
