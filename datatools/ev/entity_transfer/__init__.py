import os
from pathlib import Path


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
    context_pointer = referring_path / '._'
    # print('context_pointer', context_pointer)
    if not context_pointer.exists():
        # print('symlink', ref, context_pointer)
        os.symlink(ref, context_pointer)


def write_entity_parts_b0(entity_path, query_str, content: bytes):
    with Path(f"{entity_path}/.query").open('w') as f:
        f.write(query_str)
    if content is not None:
        with Path(f"{entity_path}/content.jsonl").open('w+b') as f:
            f.write(content)


def write_entity_parts_s(wd: Path, query_s: str, content: str, metadata_s: str):
    write_entity_parts_b(wd, query_s.encode('utf-8'), content.encode('utf-8'), metadata_s.encode('utf-8'))


def write_entity_parts_b(wd: Path, query_b: bytes, content_b: bytes, metadata_b: bytes):
    if query_b:
        write_file_b(wd / '.query', query_b)
    if content_b:
        write_file_b(wd / 'content.jsonl', content_b)
    if metadata_b:
        write_file_b(wd / 'rs-metadata.json', metadata_b)


def write_file_b(name, b: bytes):
    with open(name, 'w+b') as f:
        f.write(b)
