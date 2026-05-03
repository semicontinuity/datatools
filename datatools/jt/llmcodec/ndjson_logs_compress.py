#!/usr/bin/env python3
"""Find all data.jsonl files under the current directory and compress each one
to a sibling data.jsonl.compact file using ndjson_log_prepare + ndjson_log_compress.
"""

import os
import sys

from datatools.jt.llmcodec.ndjson_log_compress import make_ndjson, compress_ndjson
from datatools.jt.llmcodec.ndjson_log_prepare import parse_ndjson, prepare_ndjson


def compress_file(src: str) -> None:
    """Compress src (data.jsonl) → src + '.compact'."""
    dst = src + ".compact"
    print(f"Processing {src}", flush=True)

    with open(src, encoding="utf-8") as fh:
        text = fh.read()

    records, errors = parse_ndjson(text)
    if errors:
        for err in errors:
            print(f"  ERROR in {src}: {err}", file=sys.stderr)
        print(f"  Skipping {src} due to errors.", file=sys.stderr)
        return

    if not records:
        print(f"  {src} is empty, writing empty compact file.")
        open(dst, "w").close()
        return

    prepared = prepare_ndjson(records)
    compressed = compress_ndjson(make_ndjson(prepared))

    with open(dst, "w", encoding="utf-8") as fh:
        fh.write(compressed)

    src_size = os.path.getsize(src)
    dst_size = os.path.getsize(dst)
    ratio = dst_size / src_size * 100 if src_size else 0
    print(f"  {src_size} → {dst_size} bytes ({ratio:.1f}%)")


def main() -> None:
    found = False
    for dirpath, _dirnames, filenames in os.walk("."):
        for name in filenames:
            if name == "data.jsonl":
                found = True
                compress_file(os.path.join(dirpath, name))

    if not found:
        print("No data.jsonl files found.")

    print("Log compression completed.")


if __name__ == "__main__":
    main()
