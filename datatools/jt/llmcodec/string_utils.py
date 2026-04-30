import re
from collections import defaultdict


RE_IDENT = re.compile(r"[A-Za-z0-9_-]+")


def common_prefix(strings: list[str]) -> str:
    """Return the longest common prefix of a list of strings."""
    if not strings:
        return ""
    prefix = strings[0]
    for s in strings[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix


def find_common_prefix(values: list[str]) -> str:
    """Find common prefix among values; return '' if no savings."""
    if len(values) < 2:
        return ""
    pfx = common_prefix(values)
    if not pfx:
        return ""
    # Only introduce prefix if it saves space:
    # savings = len(pfx) * len(values) - len(pfx) - overhead(attr ~10 chars)
    overhead = len(pfx) + 10  # prefix="..." attribute overhead
    savings = len(pfx) * len(values) - overhead
    if savings <= 0:
        return ""
    return pfx


def pattern_counts(text: str, pattern: re.Pattern = RE_IDENT) -> dict[str, int]:
    """Count occurrences of each match of *pattern* in *text*.

    Only entries with count > 1 are included (single occurrences cannot be
    compressed).
    """
    counts: dict[str, int] = defaultdict(int)
    for m in pattern.finditer(text):
        counts[m.group()] += 1
    return {p: c for p, c in counts.items() if c > 1}
