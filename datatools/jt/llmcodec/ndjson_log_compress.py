#!/usr/bin/env python3

import json
import sys

from datatools.jt.llmcodec.ndjson import NDJson, make_ndjson
from .compressor import Compressor, _render_legend_block, wrap_with
from .ndjson_log_prepare import parse_ndjson
from .string_utils import find_common_prefix, identifier_counts, value_to_str


def _escape_prefix(pfx: str) -> str:
    """Escape prefix for use inside a single-quoted attribute.
    Only ' needs escaping (as \\').
    """
    return pfx.replace("'", "\\'")


def compress_complete_column(
    key: str,
    ndjson: NDJson,
) -> list[str]:
    """Compress one complete column and return its output lines."""
    values = [value_to_str(rec[key]) for rec in ndjson.records]
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

    col_counts = {p: c for p, c in identifier_counts(text).items() if c > 1}
    legend_lines, data_lines = Compressor(col_counts, ndjson.idents).compress_text(text)
    return wrap_with(key, [*_render_legend_block(legend_lines), *data_lines], attrs)


def compress_incomplete_columns(
    ndjson: NDJson,
) -> list[str]:
    """Compress all incomplete columns together and return their output lines.

    One line is emitted per record (empty string for records that have none of
    the incomplete keys).  This preserves positional alignment so the
    decompressor can reconstruct which values belong to which record.
    """
    inc_lines: list[str] = []
    for rec in ndjson.records:
        pairs = [
            f'"{k}":{json.dumps(rec[k], ensure_ascii=False)}'
            for k in ndjson.incomplete_keys
            if k in rec
        ]
        inc_lines.append(",".join(pairs))

    joined = "\n".join(inc_lines)
    col_counts = {p: c for p, c in identifier_counts(joined).items() if c > 1}
    legend_lines, data_lines = Compressor(col_counts, ndjson.idents).compress_text(joined)
    return ["<>", *_render_legend_block(legend_lines), *data_lines, "</>"]


def compress_ndjson(ndjson: NDJson) -> str:
    """Compress a list of NDJSON records into the column-based format."""
    body: list[str] = []

    for key in ndjson.ordered_complete:
        body.extend(compress_complete_column(key, ndjson))

    if ndjson.incomplete_keys:
        body.extend(compress_incomplete_columns(ndjson))

    return "".join(line + '\n' for line in wrap_with("COLUMNS", body))


def main():
    data = sys.stdin.read()
    records, errors = parse_ndjson(data)

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    if not records:
        sys.exit(0)

    print(compress_ndjson(make_ndjson(records)))


if __name__ == "__main__":
    main()
