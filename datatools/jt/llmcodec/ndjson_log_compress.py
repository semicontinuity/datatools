#!/usr/bin/env python3

import argparse
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


def _compress_text(text: str, global_registry: "GlobalTokenRegistry") -> tuple[list[str], list[str]]:
    """Compress *text* and return (legend_lines, data_lines)."""
    registry = TokenRegistry(global_registry)
    registry.populate_frequent_idents_from_text(text)
    return Compressor(registry).compress_text(text)


def compress_complete_column(
    key: str,
    ndjson: NDJson,
    global_registry: "GlobalTokenRegistry"
) -> tuple[list[str], list[str]]:
    """Compress one complete column; return (legend_lines, section_lines)."""
    attrs, text = ndjson.extract_column_text(key)
    if text is None:
        return [], _section(tag=key, body=[], attrs=attrs)

    legend_lines, data_lines = _compress_text(text, global_registry)
    return legend_lines, _section(tag=key, body=data_lines, attrs=attrs)


def compress_incomplete_columns(
    ndjson: NDJson,
    global_registry: "GlobalTokenRegistry"
) -> tuple[list[str], list[str]]:
    """Compress all incomplete columns; return (legend_lines, section_lines).

    One line is emitted per record (empty string for records that have none of
    the incomplete keys).  This preserves positional alignment so the
    decompressor can reconstruct which values belong to which record.
    """
    text = ndjson.extract_incomplete_columns_text()
    legend_lines, data_lines = _compress_text(text, global_registry)
    return legend_lines, ["<>", *data_lines, "</>"]


_LEGEND_ORDER = {'#': 0, '~': 1, '!': 2, '&': 3}


def _legend_sort_key(line: str) -> tuple[int, int, str]:
    """Sort key: token type order (#, ~, !, &), then token length, then lexicographic."""
    token = line.split(' = ', 1)[0]
    return _LEGEND_ORDER.get(line[0], 9), len(token), token


def _merge_legends(all_legend_lines: list[list[str]]) -> list[str]:
    """Merge multiple legend line lists into one deduplicated list sorted by processing order."""
    return sorted({line for lines in all_legend_lines for line in lines}, key=_legend_sort_key)


def compress_ndjson(
    ndjson: NDJson,
    global_registry: "GlobalTokenRegistry",
    column_legends: bool = False,
) -> str:
    """Compress a list of NDJSON records into the column-based format.

    When *column_legends* is False (default), a single merged <LEGEND> block
    is emitted before <COLUMNS>.  When True, each column section gets its own
    <LEGEND> block (legacy behaviour).
    """
    all_legends: list[list[str]] = []
    body: list[str] = []

    for key in ndjson.complete_column_keys:
        legend_lines, section_lines = compress_complete_column(key, ndjson, global_registry)
        if column_legends:
            # section_lines = [open_tag, *data, close_tag] — insert legend after open tag
            body.extend([section_lines[0], *_render_legend_block(legend_lines), *section_lines[1:]])
        else:
            all_legends.append(legend_lines)
            body.extend(section_lines)

    if ndjson.incomplete_column_keys:
        legend_lines, section_lines = compress_incomplete_columns(ndjson, global_registry)
        if column_legends:
            # section_lines = ["<>", *data, "</>"] — insert legend after "<>"
            body.extend([section_lines[0], *_render_legend_block(legend_lines), *section_lines[1:]])
        else:
            all_legends.append(legend_lines)
            body.extend(section_lines)

    if column_legends:
        output_lines = _section("COLUMNS", body)
    else:
        merged_legend = _merge_legends(all_legends)
        output_lines = [*_render_legend_block(merged_legend), *_section("COLUMNS", body)]
    return "".join(line + '\n' for line in output_lines)


def main():
    parser = argparse.ArgumentParser(description="Compress NDJSON log to column format")
    parser.add_argument(
        "--column-legends",
        action="store_true",
        default=False,
        help="Embed a <LEGEND> block inside each column section instead of a single unified legend",
    )
    args = parser.parse_args()

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
    print(compress_ndjson(ndjson, global_registry, column_legends=args.column_legends))


if __name__ == "__main__":
    main()
