#!/usr/bin/env python3

import json
import sys

from .compressor import Compressor, _render_legend_block, _value_to_str, wrap_with
from .ndjson_utils import classify_keys
from .string_utils import find_common_prefix, pattern_counts


def _escape_prefix(pfx: str) -> str:
    """Escape prefix for use inside a single-quoted attribute.
    Only ' needs escaping (as \\').
    """
    return pfx.replace("'", "\\'")


def compress_complete_column(key: str, records: list[dict]) -> list[str]:
    """Compress one complete column and return its output lines."""
    values = [_value_to_str(rec[key]) for rec in records]
    n = len(values)

    # All values identical → encode as prefix + count, empty body.
    if len(set(values)) == 1:
        return wrap_with(key, [], f"prefix='{_escape_prefix(values[0])}' n='{n}'")

    pfx = find_common_prefix(values)
    if pfx:
        attrs = f"prefix='{_escape_prefix(pfx)}'"
        text = "\n".join(v[len(pfx):] for v in values)
    else:
        attrs = ""
        text = "\n".join(values)

    legend_lines, data_lines = Compressor(pattern_counts(text)).compress_text(text)
    return wrap_with(key, [*_render_legend_block(legend_lines), *data_lines], attrs)


def compress_incomplete_columns(incomplete_keys: list[str], records: list[dict]) -> list[str]:
    """Compress all incomplete columns together and return their output lines.

    One line is emitted per record (empty string for records that have none of
    the incomplete keys).  This preserves positional alignment so the
    decompressor can reconstruct which values belong to which record.
    """
    inc_lines: list[str] = []
    for rec in records:
        pairs = [
            f'"{k}":{json.dumps(rec[k], ensure_ascii=False)}'
            for k in incomplete_keys
            if k in rec
        ]
        inc_lines.append(",".join(pairs))

    joined = "\n".join(inc_lines)
    legend_lines, data_lines = Compressor(pattern_counts(joined)).compress_text(joined)
    return ["<>", *_render_legend_block(legend_lines), *data_lines, "</>"]


def compress_ndjson(records: list[dict]) -> str:
    """Compress a list of NDJSON records into the column-based format."""
    if not records:
        return ""

    ordered_complete, incomplete_keys = classify_keys(records)
    body: list[str] = []

    for key in ordered_complete:
        body.extend(compress_complete_column(key, records))

    if incomplete_keys:
        body.extend(compress_incomplete_columns(incomplete_keys, records))

    return "".join(line + '\n' for line in wrap_with("COLUMNS", body))


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
