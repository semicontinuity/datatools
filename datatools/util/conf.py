import json
import os

from datatools.util.logging import debug


FD_METADATA_IN = 104
FD_METADATA_OUT = 105

FD_PRESENTATION_IN = 106
FD_PRESENTATION_OUT = 107

FD_STATE_IN = 108
FD_STATE_OUT = 109


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
