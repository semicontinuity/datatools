import os
import subprocess
from typing import Dict, List


def exe(cwd: str, args: List[str], env: Dict[str, str], stdin: bytes = None):
    env = os.environ | env
    proc = subprocess.Popen(
        args,
        cwd=cwd,
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate(stdin)
    if proc.returncode != 0:
        raise Exception((proc.returncode, err))
    return out.decode()
