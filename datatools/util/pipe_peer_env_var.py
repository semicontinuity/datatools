import os
import subprocess
import sys
from typing import List


def get_pipe_peer_env_var(name: str, fd=1):
    """
    Returns the value of the given env variable, if present in some of the pipe peers if the current process
    """
    return get_process_pipe_peer_env_var(os.getpid(), name, fd)


def get_process_pipe_peer_env_var(pid, name: str, fd=1):
    """
    Returns the value of the given env variable, if present in some pipe peers of given process
    """
    peer_pids = get_pipe_peer_pids(pid, fd)
    if len(peer_pids) == 0:
        return None
    for peer_pid in peer_pids:
        value = get_env_var(peer_pid, name)
        if value is not None:
            return value


def get_pipe_peer_pids(pid: int, fd: int):
    pipe_id = os.readlink(f'/proc/{pid}/fd/{fd}').removeprefix("pipe:[").removesuffix("]")
    pgid = os.getpgid(pid)
    return get_pg_pipe_pids(pgid, pipe_id, fd)


def get_pg_pipe_pids(pgid, pipe_id, fd) -> List[int]:
    """
    Returns all PIDs of the given PGID, reading the specified pipe.
    """

    # 'r'=read end; 'w'=write end
    peer_fd = 1 - fd
    direction = ord('r') if peer_fd == 0 else ord('w')

    try:
        # lsof output format: COMMAND PID PGID USER FD TYPE DEVICE SIZE/OFF NODE NAME
        out = subprocess.check_output(['lsof', '-g', str(pgid)], stderr=subprocess.DEVNULL)
    except:
        pass
    else:
        pids = []
        lines = out.strip().split(b'\n')
        for line in lines:
            parts = line.split()
            if parts[5] != b'FIFO' or parts[8] != bytes(str(pipe_id), 'utf-8') or parts[4][-1] != direction:
                continue
            if parts[4][0] != ord(str(peer_fd)):
                continue
            print(parts[4][0], ord(str(peer_fd)), parts[4][0] == ord(str(peer_fd)), file=sys.stderr)
            pids.append(int(parts[1]))
        return pids


def get_env_var(pid: int, name: str):
    try:
        with open(f'/proc/{pid}/environ') as f:
            for s in f.readline().split('\x00'):
                if s == '':
                    continue
                (k, v) = s.split('=', maxsplit=1)
                if k == name:
                    return v
    except:
        return None


if __name__ == '__main__':
    if len(sys.argv) > 2:
        __pid = int(sys.argv[1])
        __var_name = sys.argv[2]
        __var = get_process_pipe_peer_env_var(__pid, __var_name)
        if __var:
            print(__var)
