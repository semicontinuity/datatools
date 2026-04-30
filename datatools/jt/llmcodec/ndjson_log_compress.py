#!/usr/bin/env python3

import json
import sys

from .compressor import Compressor
from .ndjson_utils import classify_keys


def compress_ndjson(records: list[dict]) -> str:
    """Compress a list of NDJSON records into the column-based format."""
    if not records:
        return ""

    ordered_complete, incomplete_keys = classify_keys(records)
    comp = Compressor()
    output_parts: list[str] = ["<COLUMNS>"]

    for key in ordered_complete:
        output_parts.extend(comp.compress_complete_column(key, records))

    if incomplete_keys:
        output_parts.extend(comp.compress_incomplete_columns(incomplete_keys, records))

    output_parts.append("<COLUMNS>")
    return "".join(line + '\n' for line in output_parts)


def main():
    data = sys.stdin.read()
    records: list[dict] = []
    errors: list[str] = []

    for lineno, line in enumerate(data.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            errors.append(f"Line {lineno}: {e}")
            continue
        if not isinstance(obj, dict):
            errors.append(f"Line {lineno}: expected JSON object, got {type(obj).__name__}")
            continue
        records.append(obj)

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    if not records:
        sys.exit(0)

    print(compress_ndjson(records))


if __name__ == "__main__":
    main()
