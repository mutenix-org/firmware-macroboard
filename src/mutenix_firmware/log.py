# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Matthias Bilger <matthias@bilger.info>
import debug_on
import hardware


def log(*args, **kwargs):
    if not debug_on.debug:
        return
    print(*args, **kwargs)
    if hardware.hardware_variant.has_bluetooth:
        text = "LD" + " ".join(map(str, args)) + " " * 36
        hardware.hardware_variant.send_bluetooth_update(text[:36])


def log_error(*args, **kwargs):
    print(*args, **kwargs)
    if hardware.hardware_variant.has_bluetooth:
        text = "LE" + " ".join(map(str, args)) + " " * 36
        hardware.hardware_variant.send_bluetooth_update(text[:36])
