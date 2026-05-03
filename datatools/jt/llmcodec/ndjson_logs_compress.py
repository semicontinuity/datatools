#!/usr/bin/env python3
"""Find all data.jsonl files under the current directory and compress each one
to a sibling data.jsonl.compact file using ndjson_log_prepare + ndjson_log_compress.
"""

import os
import sys

from datatools.jt.llmcodec.global_token_registry import GlobalTokenRegistry
from datatools.jt.llmcodec.ndjson import NDJson, make_ndjson
from datatools.jt.llmcodec.ndjson_log_compress import compress_ndjson
from datatools.jt.llmcodec.ndjson_log_prepare import parse_ndjson, prepare_ndjson


def _load_ndjson(src: str, global_registry: GlobalTokenRegistry) -> NDJson | None:
    """Parse, prepare and build NDJson for src, accumulating ident counts.

    Returns None and prints an error if the file cannot be parsed.
    """
    with open(src, encoding="utf-8") as fh:
        text = fh.read()

    records, errors = parse_ndjson(text)
    if errors:
        for err in errors:
            print(f"  ERROR in {src}: {err}", file=sys.stderr)
        print(f"  Skipping {src} due to errors.", file=sys.stderr)
        return None

    prepared = prepare_ndjson(records)
    if not prepared:
        return None

    return make_ndjson(prepared, global_registry)


def main() -> None:
    global_registry = GlobalTokenRegistry()

    # First pass: build NDJson for every data.jsonl, accumulating ident counts.
    ndjson_map: dict[str, NDJson] = {}
    for dirpath, _dirnames, filenames in os.walk("."):
        for name in filenames:
            if name != "data.jsonl":
                continue
            src = os.path.join(dirpath, name)
            print(f"Scanning {src}", flush=True)
            ndjson = _load_ndjson(src, global_registry)
            if ndjson is not None:
                ndjson_map[src] = ndjson

    if not ndjson_map:
        print("No data.jsonl files found.")
        return

    # Build the shared ident index from accumulated counts.
    global_registry.init()

    # Second pass: compress each file using the already-built NDJson objects.
    for src, ndjson in ndjson_map.items():
        dst = src + ".compact"
        print(f"Compressing {src}", flush=True)

        compressed = compress_ndjson(ndjson, global_registry)

        with open(dst, "w", encoding="utf-8") as fh:
            fh.write(compressed)

        src_size = os.path.getsize(src)
        dst_size = os.path.getsize(dst)
        ratio = dst_size / src_size * 100 if src_size else 0
        print(f"  {src_size} → {dst_size} bytes ({ratio:.1f}%)")

    print("Log compression completed.")


if __name__ == "__main__":
    main()
