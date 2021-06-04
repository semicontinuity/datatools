import json
import os

from datatools.util.logging import debug


def read_fd_or_default(fd, default):
    try:
        with os.fdopen(fd, 'r') as f:
            debug(f'Reading from FD {fd}')
            return json.load(f)
    except Exception:
        return default


def write_fd_or_pass(fd, value):
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(value, f)
    except Exception:
        pass


def fd_exists(fd):
    return os.path.islink(f'/proc/self/fd/{fd}')
