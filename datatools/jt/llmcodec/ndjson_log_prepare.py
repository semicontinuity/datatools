#!/usr/bin/env python3
"""Reformat NDJSON: complete columns first (in order of first appearance),
incomplete columns last.  Recursively applied to dict-valued columns.
Output is valid NDJSON, one JSON object per line.
"""

import json
import sys
from collections import defaultdict


def parse_ndjson(text: str) -> tuple[list[dict], list[str]]:
    """Parse NDJSON text and return (records, errors).

    Each non-empty line must be a JSON object.  Parse errors and non-object
    lines are collected in *errors* rather than raising.
    """
    records: list[dict] = []
    errors: list[str] = []
    for lineno, line in enumerate(text.splitlines(), 1):
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
    return records, errors


def _classify_keys(records: list[dict]) -> tuple[list[str], list[str]]:
    """Return (ordered_complete_keys, ordered_incomplete_keys).

    Ordering within each group follows first-appearance across all records.
    """
    total = len(records)
    key_counts: dict[str, int] = defaultdict(int)
    first_seen: dict[str, int] = {}

    for rec in records:
        for k in rec:
            key_counts[k] += 1
            if k not in first_seen:
                first_seen[k] = len(first_seen)

    complete = sorted(
        (k for k, cnt in key_counts.items() if cnt == total),
        key=lambda k: first_seen[k],
    )
    incomplete = sorted(
        (k for k, cnt in key_counts.items() if cnt < total),
        key=lambda k: first_seen[k],
    )
    return complete, incomplete


def _collect_sub_dicts(records: list[dict], key: str) -> list[dict] | None:
    """Return the list of dict values for key across all records, or None if
    any value is not a dict (or key is absent in some record).
    """
    sub: list[dict] = []
    for rec in records:
        v = rec.get(key)
        if not isinstance(v, dict):
            return None
        sub.append(v)
    return sub


def _reorder_value(value, sub_records: list[dict] | None):
    """Recursively reorder a dict value using sub_records as the column set."""
    if not isinstance(value, dict) or sub_records is None:
        return value
    return _reorder_record(value, sub_records)


def _reorder_record(rec: dict, all_records: list[dict]) -> dict:
    """Return rec with keys reordered (complete first, incomplete last),
    recursively reordering dict-valued keys.
    """
    complete, incomplete = _classify_keys(all_records)
    key_order = complete + incomplete
    new_rec: dict = {}
    for k in key_order:
        if k not in rec:
            continue
        sub_dicts = _collect_sub_dicts(all_records, k)
        new_rec[k] = _reorder_value(rec[k], sub_dicts)
    return new_rec


def prepare_ndjson(records: list[dict]) -> list[dict]:
    """Return records with keys reordered recursively."""
    if not records:
        return []
    return [_reorder_record(rec, records) for rec in records]


def main() -> None:
    raw = sys.stdin.read()
    records, errors = parse_ndjson(raw)

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    for rec in prepare_ndjson(records):
        print(json.dumps(rec, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
