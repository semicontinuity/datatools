import json
import os
import sys

from datatools.json.util import to_jsonisable
from datatools.util.fd import fd_exists

FD_DEBUG = 101
FD_TRACE = 102

DEBUG_FD_OPEN = fd_exists(FD_DEBUG)
DEBUG = os.getenv('DEBUG') or DEBUG_FD_OPEN
DEBUG_FILE = os.fdopen(FD_DEBUG, 'w') if DEBUG_FD_OPEN else sys.stderr

TRACE_FD_OPEN = fd_exists(FD_TRACE)
TRACE = os.getenv('TRACE') or TRACE_FD_OPEN
TRACE_FILE = os.fdopen(FD_TRACE, 'w') if TRACE_FD_OPEN else sys.stderr


def stderr_print(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)


def debug(msg, **kwargs):
    if DEBUG == 'json':
        j = {k: to_jsonisable(v) for k, v in kwargs.items()}
        j["message"] = msg
        print(json.dumps(j), file=DEBUG_FILE)
    elif DEBUG:
        print(msg, str(kwargs), file=DEBUG_FILE)


def trace(value, title=''):
    value = to_jsonisable(value)
    if TRACE:
        if TRACE == 'browser':  # upgrade
            if title:
                print(f"X-Title:{title}", file=TRACE_FILE)
            print(file=TRACE_FILE)
            json.dump(value, TRACE_FILE)
            print(file=TRACE_FILE, flush=True)
        else:
            json.dump(value, TRACE_FILE)
            print(file=TRACE_FILE, flush=True)


def traced(title):
    def decorator(function):
        def wrapper(*args, **kwargs):
            result = function(*args, **kwargs)
            trace(result, title)
            return result
        return wrapper
    return decorator
