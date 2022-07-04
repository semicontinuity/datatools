import json
import os

import yaml

from datatools.util.logging import debug

FD_METADATA_IN = 104
FD_METADATA_OUT = 105
FD_PRESENTATION_IN = 106
FD_PRESENTATION_OUT = 107
FD_STATE_IN = 108
FD_STATE_OUT = 109

ENV_METADATA = 'METADATA'
ENV_PRESENTATION = 'PRESENTATION'
ENV_STATE = 'STATE'


def write_metadata_or_pass(metadata: dict):
    write_fd_or_pass(FD_METADATA_OUT, metadata)


def write_presentation_or_pass(presentation: dict):
    write_fd_or_pass(FD_PRESENTATION_OUT, presentation)


def write_state_or_pass(state: dict):
    write_fd_or_pass(FD_STATE_OUT, state)


def metadata_or_default(default):
    return env_or_read_fd_or_default(ENV_METADATA, FD_METADATA_IN, default)


def presentation_or_default(default, use_env=True):
    return env_or_read_fd_or_default(ENV_PRESENTATION, FD_PRESENTATION_IN, default, use_env)


def state_or_default(default):
    return env_or_read_fd_or_default(ENV_STATE, FD_STATE_IN, default)


def env_or_read_fd_or_default(env, fd, default, use_env=True):
    try:
        if use_env:
            env_var = os.environ.get(env)
            if env_var is not None:
                debug(f'Reading from ENV {env}')
                return yaml.safe_load(env_var)
        with os.fdopen(fd, 'r') as f:
            debug(f'Reading from FD {fd}')
            return yaml.safe_load(f)
    except Exception:
        return default


def write_fd_or_pass(fd, value):
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(value, f)
            # yaml.safe_dump(value, stream=f, sort_keys=False)
    except Exception:
        pass

