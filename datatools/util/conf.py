import json
import os

from datatools.util.logging import debug


ENV_METADATA = 'METADATA'
ENV_PRESENTATION = 'PRESENTATION'
ENV_STATE = 'STATE'

FD_METADATA_IN = 104
FD_METADATA_OUT = 105

FD_PRESENTATION_IN = 106
FD_PRESENTATION_OUT = 107

FD_STATE_IN = 108
FD_STATE_OUT = 109


def metadata_or_default(default):
    return env_or_read_fd_or_default(ENV_METADATA, FD_METADATA_IN, default)


def presentation_or_default(default):
    return env_or_read_fd_or_default(ENV_PRESENTATION, FD_PRESENTATION_IN, default)


def state_or_default(default):
    return env_or_read_fd_or_default(ENV_STATE, FD_STATE_IN, default)


def env_or_read_fd_or_default(env, fd, default):
    try:
        env_var = os.environ.get(env)
        if env_var is not None:
            debug(f'Reading from ENV {env}')
            return json.loads(env_var)

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
