#!/usr/bin/env python3

import json
import sys

from datatools.jt.llmcodec.ndjson import NDJson, make_ndjson
from datatools.jt.llmcodec.token_registry import TokenRegistry
from .compressor import Compressor, _render_legend_block, section
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
    shared_idents: dict,
) -> list[str]:
    """Compress one complete column and return its output lines."""
    attrs, text = extract_column_text(key, ndjson)
    if text is None:
        return section(tag=key, body=[], attrs=attrs)

    frequent_ident_counts = {p: c for p, c in identifier_counts(text).items() if c > 1}
    registry = TokenRegistry(frequent_ident_counts, shared_idents, shared_idents=True)
    legend_lines, data_lines = Compressor(registry).compress_text(text)
    return section(tag=key, body=[*_render_legend_block(legend_lines), *data_lines], attrs=attrs)


def extract_column_text(key, ndjson):
    values = [value_to_str(rec[key]) for rec in ndjson.records]
    n = len(values)
    # All values identical → encode as prefix + count, empty body.
    if len(set(values)) == 1:
        return f"prefix='{_escape_prefix(values[0])}' n='{n}'", None
    pfx = find_common_prefix(values)
    if pfx:
        attrs = f"prefix='{_escape_prefix(pfx)}'"
        text = "\n".join(v[len(pfx):] for v in values)
    else:
        attrs = ""
        text = "\n".join(values)
    return attrs, text


def compress_incomplete_columns(
    ndjson: NDJson,
    shared_idents: dict,
) -> list[str]:
    """Compress all incomplete columns together and return their output lines.

    One line is emitted per record (empty string for records that have none of
    the incomplete keys).  This preserves positional alignment so the
    decompressor can reconstruct which values belong to which record.
    """
    incomplete_columns_text = extract_incomplete_columns_text(ndjson)
    frequent_ident_counts = {p: c for p, c in identifier_counts(incomplete_columns_text).items() if c > 1}
    registry = TokenRegistry(frequent_ident_counts, shared_idents, shared_idents=True)
    legend_lines, data_lines = Compressor(registry).compress_text(incomplete_columns_text)
    return ["<>", *_render_legend_block(legend_lines), *data_lines, "</>"]


def extract_incomplete_columns_text(ndjson):
    incomplete_columns_lines: list[str] = []
    for rec in ndjson.records:
        pairs = [
            f'"{k}":{json.dumps(rec[k], ensure_ascii=False)}'
            for k in ndjson.incomplete_column_keys
            if k in rec
        ]
        incomplete_columns_lines.append(",".join(pairs))
    return "\n".join(incomplete_columns_lines)


def compress_ndjson(ndjson: NDJson) -> str:
    """Compress a list of NDJSON records into the column-based format.

    A single shared ident dict is used across all columns so that #N# always
    refers to the same string regardless of which column it appears in.
    Per-column inline/meta/macro tokens are independent (each column has its
    own legend section).
    """
    # Shared ident dict: mutated in-place as columns are compressed so every
    # column sees the same pat→index assignments.
    shared_idents: dict[str, int] = dict(ndjson.ident_counts)

    body: list[str] = []
    for key in ndjson.complete_column_keys:
        body.extend(compress_complete_column(key, ndjson, shared_idents))

    if ndjson.incomplete_column_keys:
        body.extend(compress_incomplete_columns(ndjson, shared_idents))

    return "".join(line + '\n' for line in section("COLUMNS", body))


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
