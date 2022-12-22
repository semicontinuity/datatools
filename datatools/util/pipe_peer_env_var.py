import os
import subprocess


def get_pipe_peer_env_var(name):
    pid = os.getpid()
    pipe_id = os.readlink(f'/proc/{pid}/fd/1').removeprefix("pipe:[").removesuffix("]")
    pgid = os.getpgid(pid)
    peer_pid = get_pipe_peer_pid(pgid, pipe_id)
    return get_env_var(peer_pid, name)


def get_pipe_peer_pid(pgid, pipe_id):
    try:
        out = subprocess.check_output(['lsof', '-g', str(pgid)], stderr=subprocess.DEVNULL)
    except:
        pass
    else:
        lines = out.strip().split(b'\n')
        for line in lines:
            parts = line.split()
            if parts[5] != b'FIFO' or parts[8] != bytes(str(pipe_id), 'utf-8') or parts[4][-1] != 114:  # 'r'=read end
                continue
            return int(parts[1])


def get_env_var(pid: int, name: str):
    with open(f'/proc/{pid}/environ') as f:
        for s in f.readline().split('\x00'):
            if s == '':
                continue
            (k, v) = s.split('=', maxsplit=1)
            if k == name:
                return v
