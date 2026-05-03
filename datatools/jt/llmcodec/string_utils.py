import json
import re

RE_IDENT = re.compile(r"[A-Za-z0-9_.-]+")


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


def identifier_counts(
    text: str,
    pattern: re.Pattern = RE_IDENT,
    counts: dict[str, int] | None = None,
) -> dict[str, int]:
    """Count occurrences of each match of *pattern* in *text*.

    If *counts* is provided, tallies are accumulated into it and it is returned
    as-is (no filtering).  Otherwise a new dict is created and only entries
    with count > 1 are returned.
    """
    if counts is None:
        counts = {}
    for m in pattern.finditer(text):
        key = m.group()
        counts[key] = counts.get(key, 0) + 1
    return counts


def value_to_str(v) -> str:
    """Convert a JSON value to a string for compression."""
    if isinstance(v, str):
        return v
    return json.dumps(v, ensure_ascii=False)


def tokenize_normal(text: str) -> list[str]:
    tokens = []
    i = 0
    n = len(text)
    while i < n:
        is_alnum = _is_alnum(text[i])
        j = i + 1
        while j < n and _is_alnum(text[j]) == is_alnum:
            j += 1
        tokens.append(text[i:j])
        i = j
    return tokens


def tokenize_meta(text: str) -> list[str]:
    tokens = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c in ("~", "#"):
            j = i + 1
            while j < n and text[j].isalnum():
                j += 1
            if j < n and text[j] == c:
                tokens.append(text[i:j + 1])
                i = j + 1
                continue
        elif c == "!":
            j = i + 1
            while j < n and text[j].isalnum():
                j += 1
            if j < n and text[j] == "!":
                tokens.append(text[i:j + 1])
                i = j + 1
                continue
        is_alnum = _is_alnum(c)
        j = i + 1
        while j < n:
            nc = text[j]
            if is_alnum:
                if not _is_alnum(nc):
                    break
            else:
                if _is_alnum(nc) or nc in ("~", "#", "!"):
                    break
            j += 1
        tokens.append(text[i:j])
        i = j
    return tokens


def split_normal(text: str) -> tuple[list[str], list[str]]:
    """Split on ~tag~ (or #tag#) separators, returning (parts, seps)."""
    parts = []
    seps = []
    i = 0
    last_end = 0
    n = len(text)
    while i < n:
        if text[i] in ("~", "#"):
            delim = text[i]
            j = i + 1
            while j < n and text[j].isalnum():
                j += 1
            if n > j > i + 1 and text[j] == delim:
                parts.append(text[last_end:i])
                seps.append(text[i:j + 1])
                last_end = j + 1
                i = j + 1
                continue
        i += 1
    parts.append(text[last_end:])
    return parts, seps


def split_meta(text: str) -> tuple[list[str], list[str]]:
    """Split on newlines."""
    parts = []
    seps = []
    last_end = 0
    for i, c in enumerate(text):
        if c == "\n":
            parts.append(text[last_end:i])
            seps.append("\n")
            last_end = i + 1
    parts.append(text[last_end:])
    return parts, seps


def _is_alnum(c: str) -> bool:
    return c.isalnum() or c == "_"
