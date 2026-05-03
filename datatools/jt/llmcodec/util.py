import sys


def debug(*args, **kwargs) -> None:
    """Print a debug message to stderr."""
    print(*args, file=sys.stderr, **kwargs)
