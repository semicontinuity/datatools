import os, sys, json
from datatools.json.util import to_jsonisable

DEBUG = os.getenv('DEBUG')
TRACE_FD_OPEN = os.path.islink(f'/proc/self/fd/102')
TRACE = os.getenv('TRACE') or TRACE_FD_OPEN
TRACE_FILE = os.fdopen(102, 'w') if TRACE_FD_OPEN else sys.stderr


def stderr_print(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)


def debug(*args, **kwargs):
    if DEBUG:
        stderr_print(*args, **kwargs)


def trace(value, title=''):
    if TRACE:
        print(f"X-Title:{title}", file=TRACE_FILE)
        print(file=TRACE_FILE)
        json.dump(value, TRACE_FILE)
        print(file=TRACE_FILE, flush=True)


def traced(title):
    def decorator(function):
        def wrapper(*args, **kwargs):
            result = function(*args, **kwargs)
            trace(to_jsonisable(result), title)
            return result
        return wrapper
    return decorator