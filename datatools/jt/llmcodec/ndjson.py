import json
from dataclasses import dataclass

from datatools.jt.llmcodec.ndjson_utils import classify_keys
from datatools.jt.llmcodec.string_utils import value_to_str, find_common_prefix, identifier_counts


@dataclass
class NDJson:
    records: list[dict]
    ordered_complete: list[str]
    incomplete_keys: list[str]
    unified_counts: dict[str, int]
    idents: dict[str, int]


def make_ndjson(records: list[dict]) -> NDJson:
    """Build the NDJson for a list of records."""
    ordered_complete, incomplete_keys = classify_keys(records)
    unified_counts = _build_unified_identifier_counts(ordered_complete, incomplete_keys, records)
    idents = _build_idents(unified_counts)
    return NDJson(
        records=records,
        ordered_complete=ordered_complete,
        incomplete_keys=incomplete_keys,
        unified_counts=unified_counts,
        idents=idents,
    )


def _build_idents(ident_counts: dict[str, int]) -> dict[str, int]:
    """Build a pat→index mapping sorted by descending frequency (count > 1 only)."""
    sorted_tokens = sorted(
        (k for k, c in ident_counts.items() if c > 1),
        key=lambda k: -ident_counts[k],
    )
    return {pat: idx for idx, pat in enumerate(sorted_tokens)}


def _build_unified_identifier_counts(
    ordered_complete: list[str],
    incomplete_keys: list[str],
    records: list[dict],
) -> dict[str, int]:
    """Build a unified identifier_counts dict across all columns."""
    counts: dict[str, int] = {}

    for key in ordered_complete:
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

    if incomplete_keys:
        for rec in records:
            pairs = [
                f'"{k}":{json.dumps(rec[k], ensure_ascii=False)}'
                for k in incomplete_keys
                if k in rec
            ]
            identifier_counts(",".join(pairs), counts=counts)

    return counts
