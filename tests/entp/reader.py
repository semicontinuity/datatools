import os
import sys

from entp.pipe_peer_env_var import get_pipe_peer_env_var, get_pipe_peer_pids

if __name__ == '__main__':
    print(f'reader: my pid is {os.getpid()}', file=sys.stderr)
    print("reader's peers", get_pipe_peer_pids(os.getpid(), 0), file=sys.stderr)
    print("reader' peer is cool", get_pipe_peer_env_var('PRODUCES_ENTP', 0), file=sys.stderr)
