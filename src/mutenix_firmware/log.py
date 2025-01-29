# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Matthias Bilger <matthias@bilger.info>
import debug_on
import hardware


def log(*args, **kwargs):
    if debug_on.debug:
        print(*args, **kwargs)
    if hardware.hardware_variant.has_bluetooth:
        text = " ".join(map(str, args)) + " " * 36
        hardware.hardware_variant.send_bluetooth_update(text[:36])
