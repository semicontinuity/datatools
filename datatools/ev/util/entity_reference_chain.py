import os
from pathlib import Path

from datatools.ev.util import CONTEXT_POINTER


def create_ctx_reference_chain(ctx: Path, referring_path: Path, referenced_path: Path):
    for part in ctx.parts:
        referenced_path = referenced_path / part
        if not referenced_path.exists():
            return False

        referring_path = referring_path / part

        create_ctx_reference(referring_path, referenced_path)

    return True


def create_ctx_reference(referring_path: Path, referenced_path: Path):
    # print('mkdir', referring_path)
    os.makedirs(referring_path, exist_ok=True)
    st_mode = os.stat(str(referenced_path)).st_mode
    # print('st_mode', st_mode)
    os.chmod(str(referring_path), st_mode)
    ref = os.path.relpath(
        path=str(referenced_path),
        start=str(referring_path),
    )
    context_pointer = referring_path / CONTEXT_POINTER
    # print('context_pointer', context_pointer)
    if not context_pointer.exists():
        # print('symlink', ref, context_pointer)
        os.symlink(ref, context_pointer)
