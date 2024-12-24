from unittest.mock import MagicMock
import sys

from circuitpython_mocks.board import board_id
from circuitpython_mocks.digitalio import DigitalInOut, Direction, Pull

pytest_plugins = ["circuitpython_mocks.fixtures"]

sys.path.append("src/mutenix_firmware")
