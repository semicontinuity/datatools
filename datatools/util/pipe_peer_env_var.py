import os
import subprocess
from typing import List


def get_pipe_peer_env_var(name: str):
    """
    Returns the value of the given env variable, if present from some of pipe peers
    """
    pid = os.getpid()
    pipe_id = os.readlink(f'/proc/{pid}/fd/1').removeprefix("pipe:[").removesuffix("]")
    pgid = os.getpgid(pid)
    peer_pids = get_pipe_peer_pids(pgid, pipe_id)
    if len(peer_pids) == 0:
        return None
    for peer_pid in peer_pids:
        value = get_env_var(peer_pid, name)
        if value is not None:
            return value


def get_pipe_peer_pids(pgid, pipe_id) -> List[int]:
    """
    Returns all PIDs of the given PGID, reading the specified pipe.
    """
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
            if parts[5] != b'FIFO' or parts[8] != bytes(str(pipe_id), 'utf-8') or parts[4][-1] != 114:  # 'r'=read end
                continue
            pids.append(int(parts[1]))
        return pids


def get_env_var(pid: int, name: str):
    with open(f'/proc/{pid}/environ') as f:
        for s in f.readline().split('\x00'):
            if s == '':
                continue
            (k, v) = s.split('=', maxsplit=1)
            if k == name:
                return v
