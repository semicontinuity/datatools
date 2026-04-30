from collections import defaultdict


def classify_keys(
    records: list[dict],
) -> tuple[list[str], list[str]]:
    """Return (ordered_complete_keys, incomplete_keys) for the record set."""
    total = len(records)
    key_counts: dict[str, int] = defaultdict(int)
    for rec in records:
        for k in rec:
            key_counts[k] += 1

    complete_set = {k for k, cnt in key_counts.items() if cnt == total}
    # Preserve insertion order from first record
    ordered_complete: list[str] = []
    seen: set[str] = set()
    for k in records[0]:
        if k in complete_set:
            ordered_complete.append(k)
            seen.add(k)
    for k in complete_set:
        if k not in seen:
            ordered_complete.append(k)

    incomplete_keys = [k for k, cnt in key_counts.items() if cnt < total]
    return ordered_complete, incomplete_keys
