#!/usr/bin/env python3

import sys

from datatools.jt.llmcodec.global_token_registry import GlobalTokenRegistry
from datatools.jt.llmcodec.ndjson import NDJson, analyze_ndjson
from datatools.jt.llmcodec.token_registry import TokenRegistry
from .compressor import Compressor
from .ndjson_log_prepare import parse_ndjson


def _section(tag: str, body: list[str], attrs: str = "") -> list[str]:
    """Wrap body lines with <tag attrs>...</tag>."""
    open_tag = f"<{tag}{' ' + attrs if attrs else ''}>"
    return [open_tag, *body, f"</{tag}>"]


def _render_legend_block(legend_lines: list[str]) -> list[str]:
    """Wrap legend lines in <LEGEND>...</LEGEND> if non-empty."""
    if not legend_lines:
        return []
    return _section("LEGEND", legend_lines)


def compress_complete_column(
    key: str,
    ndjson: NDJson,
    global_registry: "GlobalTokenRegistry"
) -> list[str]:
    """Compress one complete column and return its output lines."""
    attrs, text = ndjson.extract_column_text(key)
    if text is None:
        return _section(tag=key, body=[], attrs=attrs)

    registry = TokenRegistry(global_registry)
    registry.populate_frequent_idents_from_text(text)
    legend_lines, data_lines = Compressor(registry).compress_text(text)
    return _section(tag=key, body=[*_render_legend_block(legend_lines), *data_lines], attrs=attrs)


def compress_incomplete_columns(
    ndjson: NDJson,
    global_registry: "GlobalTokenRegistry"
) -> list[str]:
    """Compress all incomplete columns together and return their output lines.

    One line is emitted per record (empty string for records that have none of
    the incomplete keys).  This preserves positional alignment so the
    decompressor can reconstruct which values belong to which record.
    """
    incomplete_columns_text = ndjson.extract_incomplete_columns_text()
    registry = TokenRegistry(global_registry)
    registry.populate_frequent_idents_from_text(incomplete_columns_text)
    legend_lines, data_lines = Compressor(registry).compress_text(incomplete_columns_text)
    return ["<>", *_render_legend_block(legend_lines), *data_lines, "</>"]


def compress_ndjson(ndjson: NDJson, global_registry: "GlobalTokenRegistry") -> str:
    """Compress a list of NDJSON records into the column-based format.

    ``global_registry.ident_index`` (built by :meth:`GlobalTokenRegistry.init`)
    is used as the shared ident dict so that ``#N#`` tokens are consistent
    across all columns and files.  Per-column inline/meta/macro tokens are
    independent (each column has its own legend section).
    """
    shared_idents: dict[str, int] = global_registry.ident_index

    body: list[str] = []
    for key in ndjson.complete_column_keys:
        body.extend(compress_complete_column(key, ndjson, global_registry))

    if ndjson.incomplete_column_keys:
        body.extend(compress_incomplete_columns(ndjson, global_registry))

    return "".join(line + '\n' for line in _section("COLUMNS", body))


def main():
    data = sys.stdin.read()
    records, errors = parse_ndjson(data)

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    if not records:
        sys.exit(0)

    global_registry = GlobalTokenRegistry()
    ndjson = analyze_ndjson(records, global_registry)
    global_registry.init()
    print(compress_ndjson(ndjson, global_registry))


if __name__ == "__main__":
    main()
