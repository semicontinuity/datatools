import json
from dataclasses import dataclass

from datatools.jt.llmcodec.ndjson_utils import classify_keys
from datatools.jt.llmcodec.string_utils import value_to_str, find_common_prefix, identifier_counts


@dataclass
class NDJson:
    records: list[dict]
    complete_column_keys: list[str]
    incomplete_column_keys: list[str]
    ident_counts: dict[str, int]


def make_ndjson(records: list[dict]) -> NDJson:
    """Build the NDJson for a list of records."""
    complete_column_keys, incomplete_column_keys = classify_keys(records)
    return NDJson(
        records=records,
        complete_column_keys=complete_column_keys,
        incomplete_column_keys=incomplete_column_keys,
        ident_counts=_select_frequent(
            _build_ident_counts(
                complete_column_keys,
                incomplete_column_keys,
                records
            )
        ),
    )


def _select_frequent(ident_counts: dict[str, int]) -> dict[str, int]:
    """Build a pat→index mapping sorted by descending frequency (count > 1 only)."""
    sorted_tokens = sorted(
        (k for k, c in ident_counts.items() if c > 1),
        key=lambda k: -ident_counts[k],
    )
    return {pat: idx for idx, pat in enumerate(sorted_tokens)}


def _build_ident_counts(
    complete_column_keys: list[str],
    incomplete_column_keys: list[str],
    records: list[dict],
) -> dict[str, int]:
    """Build a identifier counts dict across all columns."""
    counts: dict[str, int] = {}

    for key in complete_column_keys:
        values = [value_to_str(rec[key]) for rec in records]
        if len(set(values)) == 1:
            continue
        pfx = find_common_prefix(values)
        if pfx:
            for v in values:
                identifier_counts(v[len(pfx):], counts=counts)
        else:
            for v in values:
                identifier_counts(v, counts=counts)

    if incomplete_column_keys:
        for rec in records:
            pairs = [
                f'"{k}":{json.dumps(rec[k], ensure_ascii=False)}'
                for k in incomplete_column_keys
                if k in rec
            ]
            identifier_counts(",".join(pairs), counts=counts)

    return counts
