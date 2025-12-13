from pathlib import Path


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
