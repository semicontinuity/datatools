#!/usr/bin/env python3
"""Decompress output produced by ndjson_log_compress back to NDJSON."""

import json
import re
import sys

RE_LEGEND_ENTRY = re.compile(r"^([#!&][0-9a-zA-Z]+[#!]?)\s*=\s*(.*)$")
RE_DUP = re.compile(r"^\s+\.\.\. x(\d+)$")
RE_TOKEN = re.compile(
    r"&[0-9a-zA-Z]+:[#!][0-9a-zA-Z]+[#!]"
    r"|#[0-9a-zA-Z]+#"
    r"|![0-9a-zA-Z]+!"
    r"|&[0-9a-zA-Z]+"
)
RE_MACRO_TAG = re.compile(r"^(&[0-9a-zA-Z]+):([#!][0-9a-zA-Z]+[#!])$")

# Matches  <tag>  or  <tag prefix='...' [n='N']>
# prefix value uses single quotes; only \' needs escaping inside.
RE_OPEN_TAG = re.compile(
    r"^<([A-Za-z0-9_]+)"
    r"(?:\s+prefix='((?:[^'\\]|\\.)*)')?"
    r"(?:\s+n='(\d+)')?"
    r">\s*$"
)
RE_CLOSE_TAG = re.compile(r'^</([A-Za-z0-9_]+)>\s*$')
# Incomplete-columns section
RE_OPEN_INC = re.compile(r'^<>\s*$')
RE_CLOSE_INC = re.compile(r'^</>\s*$')
RE_LEGEND_OPEN = re.compile(r'^<LEGEND>\s*$')
RE_LEGEND_CLOSE = re.compile(r'^</LEGEND>\s*$')
RE_COLUMNS_MARKER = re.compile(r'^<COLUMNS>\s*$')


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == "'" and value[-1] == "'":
        return value[1:-1]
    return value


def _expand(text: str, table: dict[str, str], depth: int = 0) -> str:
    if depth > 50:
        return text

    def replace(m: re.Match) -> str:
        tok = m.group()
        mt = RE_MACRO_TAG.match(tok)
        if mt:
            macro_tok, tag_tok = mt.group(1), mt.group(2)
            if macro_tok in table:
                expanded_tag = _expand(tag_tok, table, depth + 1)
                expanded_template = table[macro_tok].replace("?", expanded_tag, 1)
                return _expand(expanded_template, table, depth + 1)
            return tok
        if tok in table:
            return _expand(table[tok], table, depth + 1)
        return tok

    return RE_TOKEN.sub(replace, text)


def _expand_lines(
    raw_lines: list[str],
    table: dict[str, str],
    prefix: str,
) -> list[str]:
    """Expand compressed lines back to original values, restoring duplicates."""
    result: list[str] = []
    last_nonempty = ""

    for raw in raw_lines:
        dup_m = RE_DUP.match(raw)
        if dup_m:
            count = int(dup_m.group(1))
            for _ in range(count - 1):
                result.append(last_nonempty)
            continue

        expanded = prefix + _expand(raw, table)
        result.append(expanded)
        if expanded:
            last_nonempty = expanded

    return result


def _parse_legend(legend_lines: list[str]) -> dict[str, str]:
    table: dict[str, str] = {}
    for line in legend_lines:
        m = RE_LEGEND_ENTRY.match(line)
        if m:
            table[m.group(1)] = _unquote(m.group(2))
    return table


def _unescape_prefix(pfx: str) -> str:
    """Reverse _escape_prefix: \\' → '."""
    return pfx.replace("\\'", "'")


def _parse_inc_pair(pair: str) -> tuple[str, object]:
    """Parse  "key":value  into (key, parsed_value)."""
    colon = pair.index(":")
    raw_key = pair[:colon].strip()
    raw_val = pair[colon + 1:].strip()
    key = json.loads(raw_key)
    val = json.loads(raw_val)
    return key, val


def _strip_columns_markers(lines: list[str]) -> list[str]:
    """Remove leading and trailing <COLUMNS> marker lines."""
    start = 0
    end = len(lines) - 1
    while start <= end and RE_COLUMNS_MARKER.match(lines[start]):
        start += 1
    while end >= start and RE_COLUMNS_MARKER.match(lines[end]):
        end -= 1
    return lines[start:end + 1]


def _read_legend_block(lines: list[str], i: int, n: int) -> tuple[list[str], int]:
    """If lines[i] is <LEGEND>, consume until </LEGEND> and return (legend_lines, new_i)."""
    if i < n and RE_LEGEND_OPEN.match(lines[i]):
        i += 1
        legend_lines: list[str] = []
        while i < n and not RE_LEGEND_CLOSE.match(lines[i]):
            legend_lines.append(lines[i])
            i += 1
        i += 1  # skip </LEGEND>
        return legend_lines, i
    return [], i


def _parse_complete_column(
    lines: list[str], i: int, n: int, key: str, pfx: str, count: int | None
) -> tuple[tuple[str, list[str]], int]:
    """Parse a complete column block starting after its open tag.
    Returns ((key, expanded_values), new_i).
    count: value of n= attribute (all values equal prefix), or None.
    """
    legend_lines, i = _read_legend_block(lines, i, n)
    data_lines: list[str] = []
    close_pat = re.compile(rf"^</{re.escape(key)}>\s*$")
    while i < n and not close_pat.match(lines[i]):
        data_lines.append(lines[i])
        i += 1
    i += 1  # skip </key>

    # All-same case: body is empty, reconstruct N copies of the prefix.
    if count is not None and not data_lines:
        expanded = [pfx] * count
        return (key, expanded), i

    table = _parse_legend(legend_lines)
    expanded = _expand_lines(data_lines, table, pfx)
    return (key, expanded), i


def _parse_incomplete_section(
    lines: list[str], i: int, n: int
) -> tuple[list[str], int]:
    """Parse a <> ... </> block starting after the <> tag.
    Returns (expanded_lines, new_i).
    """
    legend_lines, i = _read_legend_block(lines, i, n)
    data_lines: list[str] = []
    while i < n and not RE_CLOSE_INC.match(lines[i]):
        data_lines.append(lines[i])
        i += 1
    i += 1  # skip </>
    table = _parse_legend(legend_lines)
    expanded = _expand_lines(data_lines, table, "")
    return expanded, i


def _parse_column_blocks(
    lines: list[str],
) -> tuple[list[tuple[str, list[str]]], list[str]]:
    """Parse all column blocks from inner lines.
    Returns (complete_columns, incomplete_lines).
    complete_columns: list of (key, expanded_values)
    incomplete_lines: expanded lines from the <> section (empty list if absent)
    """
    complete: list[tuple[str, list[str]]] = []
    incomplete: list[str] = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        open_m = RE_OPEN_TAG.match(line)
        if open_m:
            key = open_m.group(1)
            pfx_raw = open_m.group(2)
            pfx = _unescape_prefix(pfx_raw) if pfx_raw is not None else ""
            count_raw = open_m.group(3)
            count = int(count_raw) if count_raw is not None else None
            col, i = _parse_complete_column(lines, i + 1, n, key, pfx, count)
            complete.append(col)
            continue
        if RE_OPEN_INC.match(line):
            incomplete, i = _parse_incomplete_section(lines, i + 1, n)
            continue
        i += 1

    return complete, incomplete


def _assemble_records(
    complete: list[tuple[str, list[str]]],
    incomplete: list[str],
) -> list[dict]:
    """Reconstruct NDJSON records from parsed column data."""
    if not complete:
        return []
    n_records = len(complete[0][1])
    records: list[dict] = [{} for _ in range(n_records)]

    for key, vals in complete:
        for idx, raw_val in enumerate(vals):
            records[idx][key] = _parse_column_value(raw_val)

    # incomplete is positionally aligned: one entry per record (empty = no inc keys)
    for idx, line_val in enumerate(incomplete[:n_records]):
        if line_val.strip():
            _parse_inc_line(line_val, records[idx])

    return records


def decompress_ndjson(text: str) -> list[dict]:
    """Parse <COLUMNS>...</COLUMNS> format and return list of dicts."""
    lines = _strip_columns_markers(text.splitlines())
    complete, incomplete = _parse_column_blocks(lines)
    return _assemble_records(complete, incomplete)


def _parse_column_value(raw: str) -> object:
    """Try to parse as JSON; fall back to string."""
    stripped = raw.strip()
    if not stripped:
        return raw
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return raw


def _parse_inc_line(line: str, rec: dict) -> None:
    """Parse  "key1":val1,"key2":val2,...  into rec."""
    # Use a simple state machine to split on top-level commas.
    depth = 0
    in_str = False
    escape = False
    start = 0
    pairs: list[str] = []

    for idx, ch in enumerate(line):
        if escape:
            escape = False
            continue
        if ch == "\\" and in_str:
            escape = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch in ("{", "["):
            depth += 1
        elif ch in ("}", "]"):
            depth -= 1
        elif ch == "," and depth == 0:
            pairs.append(line[start:idx])
            start = idx + 1

    pairs.append(line[start:])

    for pair in pairs:
        pair = pair.strip()
        if not pair:
            continue
        try:
            key, val = _parse_inc_pair(pair)
            rec[key] = val
        except (ValueError, json.JSONDecodeError):
            pass


def main() -> None:
    text = sys.stdin.read()
    records = decompress_ndjson(text)
    for rec in records:
        print(json.dumps(rec, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
