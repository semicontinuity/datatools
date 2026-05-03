import json
from dataclasses import dataclass

from datatools.jt.llmcodec.global_token_registry import GlobalTokenRegistry
from datatools.jt.llmcodec.ndjson_utils import classify_keys
from datatools.jt.llmcodec.string_utils import value_to_str, find_common_prefix, identifier_counts


@dataclass
class NDJson:
    records: list[dict]
    complete_column_keys: list[str]
    incomplete_column_keys: list[str]


def analyze_ndjson(records: list[dict], global_registry: GlobalTokenRegistry) -> NDJson:
    """Build the NDJson for a list of records.

    Identifier occurrences are counted directly into
    ``global_registry.ident_counts`` so that frequencies accumulate across
    multiple calls.  The resulting NDJson receives a :func:`_select_frequent`
    view of the global table at the time of this call.
    """
    complete_column_keys, incomplete_column_keys = classify_keys(records)
    _build_ident_counts(
        complete_column_keys,
        incomplete_column_keys,
        records,
        counts=global_registry.ident_counts,
    )
    return NDJson(
        records=records,
        complete_column_keys=complete_column_keys,
        incomplete_column_keys=incomplete_column_keys,
    )


def _build_ident_counts(
    complete_column_keys: list[str],
    incomplete_column_keys: list[str],
    records: list[dict],
    counts: dict[str, int],
) -> None:
    """Accumulate identifier counts across all columns into *counts*."""
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
