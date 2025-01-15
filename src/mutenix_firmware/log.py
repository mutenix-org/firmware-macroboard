# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Matthias Bilger <matthias@bilger.info>
import debug_on


def log(*args, **kwargs):
    if debug_on.debug:
        print(*args, **kwargs)
