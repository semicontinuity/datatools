import os
from pathlib import Path


def create_ctx_reference_chain(ctx, referring_path: Path, referenced_path: Path):
    for part in ctx.parts:
        referenced_path = referenced_path / part
        if not referenced_path.exists():
            return False

        referring_path = referring_path / part
        os.makedirs(referring_path, exist_ok=True)
        os.chmod(str(referring_path), os.stat(str(referenced_path)).st_mode)

        ref = os.path.relpath(
            path=str(referenced_path),
            start=str(referring_path),
        )

        context_pointer = referring_path / '._'
        if not context_pointer.exists():
            os.symlink(ref, context_pointer)

    return True


def create_context_pointers_chain(created_context_dir, referenced_context_dir):
    os.makedirs(created_context_dir, exist_ok=True)
    # Calculate the realm reference
    realm_ref = os.path.relpath(
        referenced_context_dir,
        start=created_context_dir
    )
    # Check if the context pointer file exists, create a symlink if not
    context_pointer = Path(f"{created_context_dir}/._")
    if not context_pointer.exists():
        os.symlink(realm_ref, context_pointer)


def write_entity_parts(entity_path, query_str, content):
    with Path(f"{entity_path}/.query").open('w') as f:
        f.write(query_str)
    if content is not None:
        with Path(f"{entity_path}/content.jsonl").open('w+b') as f:
            f.write(content)
