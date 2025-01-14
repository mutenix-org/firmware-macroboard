import debug_on


def log(*args, **kwargs):
    if debug_on.debug:
        print(*args, **kwargs)
