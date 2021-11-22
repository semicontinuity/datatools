import os

def fd_exists(fd: int):
    try:
        os.fstat(fd)
        return True
    except OSError:
        return False
