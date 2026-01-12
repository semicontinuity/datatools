import os
import sys
from pathlib import Path

from datatools.ev.util import CONTEXT_POINTER

DEBUG = os.getenv('DEBUG')


def debug(msg, **kwargs):
    if DEBUG:
        print(msg, str(kwargs), file=sys.stderr)


def create_ctx_reference_chain(ctx: Path, referring_path: Path, referenced_path: Path):
    for part in ctx.parts:
        referenced_path = referenced_path / part
        debug('create_ctx_reference_chain', part=part, referenced_path=referenced_path)
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


def ctx_to_resources(ctx: Path, ctx_dir: Path) -> list[Path]:
    """ Resolves context to actual "resources" by following symlinks in the path, if any """
    debug('ctx_to_resource', ctx=ctx.parts)

    parts = ctx.parts
    resources = []
    path = ctx_dir

    while True:
        debug('ctx_to_resource', iteration=True, parts=parts)

        # Traverse path, starting from 'path', gradually appending 'parts'
        for i in range(len(parts)):
            sub_dir = path / parts[i]
            debug('ctx_to_resource', sub_dir=sub_dir)

            if sub_dir.is_symlink():
                debug('ctx_to_resource', sub_dir_is_symlink=True)
                target = sub_dir.readlink()
                debug('ctx_to_resource', target=target)
                target = Path(os.path.abspath(str(Path(path.joinpath(target)))))
                debug('ctx_to_resource', target=target)

                if str(target).startswith(str(ctx_dir)):
                    # "jump" detected to another context with direct symlink. repeat with new path and parts
                    debug('ctx_to_resource', target_is_under_ctx=True)
                    path = target
                    parts = parts[(i + 1):]
                    debug('ctx_to_resource', repeat=True, path=path, parts=parts)
                    break
            else:
                context_pointer = sub_dir / CONTEXT_POINTER
                if context_pointer.is_symlink() and context_pointer.is_dir():
                    # "jump" detected to another context with context pointer. repeat with new path and parts
                    resources.append(sub_dir.relative_to(ctx_dir))

                    debug('ctx_to_resource', context_pointer=True)
                    path = Path(os.path.abspath(str(Path(sub_dir.joinpath(context_pointer.readlink())))))
                    parts = parts[(i + 1):]
                    debug('ctx_to_resource', repeat=True, path=path, parts=parts)

                    break

            path = sub_dir
            debug('ctx_to_resource', path=path)
        else:
            # Regular completion without break, resolution done
            resource = path.relative_to(ctx_dir)
            resources.append(resource)
            debug('ctx_to_resource', resource=resource)
            return resources
