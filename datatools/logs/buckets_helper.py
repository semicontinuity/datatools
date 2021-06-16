import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Iterator, Dict, Hashable, Sequence

from datatools.util.logging import debug


@dataclass
class Stat:
    token: str
    quality: float
    count: int
    support: int
    selected: bool


def compute_stats_for_tokenized(tokenized_strings: Sequence[Sequence[str]]) -> Iterator[Stat]:
    size = len(tokenized_strings)
    debug(f"Computing stats for {size} lines")
    token2lines = defaultdict(list)  # or better just set of line indices!
    for tokenized_string in tokenized_strings:
        token_set = set(tokenized_string)
        for token in token_set:
            token2lines[token].append(tokenized_string)

    f = compute_token_counts((token for tokenized_string in tokenized_strings for token in tokenized_string))

    token2quality = {}
    total_quality = 0
    # total_support = 0
    for token, count in f.items():
        quality = len(token2lines[token]) * len(token2lines[token]) / count
        token2quality[token] = quality
        total_quality += quality
        # total_support += len(token2lines[token])

    # total_count = 0
    # for count in f.values():
    #     total_count += count

    limit = 0.65 * total_quality
    total = 0
    prev_support = 0
    prev_quality = 0
    prev_selected = True
    i = 0
    for token, quality in sorted(token2quality.items(), key=lambda item: -item[1]):
        # count = f[token]
        support = len(token2lines[token])
        # and i < len(s)
        selected = prev_selected and support > 1 and (
                # total < limit or quality == prev_quality or support >= prev_support)
                total < limit or support == size)

        total += quality
        prev_quality = quality
        prev_support = support
        prev_selected = selected
        i += 1

        yield Stat(token=token, quality=math.log(quality), count=f[token], support=support, selected=selected)

    debug(f"Computed stats for {size} lines")


def compute_token_counts(tokens: Iterable[Hashable]) -> Dict[Hashable, int]:
    d = defaultdict(int)
    for token in tokens:
        d[token] += 1
    return {token: count for token, count in sorted(d.items(), key=lambda item: -item[1])}
