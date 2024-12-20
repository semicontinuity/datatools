import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Iterator, Dict, Hashable, Sequence, List, Tuple, Set

from datatools.util.logging import debug


@dataclass
class Stat:
    token: str
    quality: float
    count: int
    support: int
    selected: bool


def compute_stats_for_tokenized(tokenized_strings: Sequence[Sequence[str]], ratio=0.5) -> Iterator[Stat]:
    size = len(tokenized_strings)
    debug(f"Computing stats for {size} lines")
    token2lines = defaultdict(list)  # or better just set of line indices!
    for tokenized_string in tokenized_strings:
        token_set = set(tokenized_string)
        for token in token_set:
            token2lines[token].append(tokenized_string)

    token2count = compute_token_counts((token for tokenized_string in tokenized_strings for token in tokenized_string))

    token2quality = {}
    total_quality = 0

    # total_count = 0
    # for token, count in token2count.items():
    #     total_count += count

    # total_support = 0

    for token, count in token2count.items():
        quality = len(token2lines[token]) * len(token2lines[token]) / count

        # tf = count / total_count
        # idf = math.log(size / len(token2lines[token]))
        # quality = 1 / (tf * idf)
        # quality = tf * idf

        token2quality[token] = quality
        total_quality += quality
    debug("compute_stats_for_tokenized", total_quality=total_quality)

        # total_support += len(token2lines[token])

    # total_count = 0
    # for count in f.values():
    #     total_count += count

    limit = ratio * total_quality
    total = 0
    prev_support = 0
    prev_quality = 0
    prev_selected = True
    i = 0
    n_selected = 0
    by_quality = sorted(token2quality.items(), key=lambda item: -item[1])

    for token, quality in by_quality:
        # count = f[token]
        support = len(token2lines[token])
        # and i < len(s)
        selected = prev_selected and support > 1 and (
                # total < limit or quality == prev_quality or support >= prev_support)
                total < limit or support == size)
        if selected:
            n_selected += 1
        total += quality
        prev_quality = quality
        prev_support = support
        prev_selected = selected
        i += 1

        # yield Stat(token=token, quality=quality, count=token2count[token], support=support, selected=selected)
        yield Stat(token=token, quality=math.log(quality), count=token2count[token], support=support, selected=selected)

    debug(f"Computed stats for {size} lines: selected {n_selected} tokens")


def compute_token_counts(tokens: Iterable[Hashable]) -> Dict[Hashable, int]:
    d = defaultdict(int)
    for token in tokens:
        d[token] += 1
    return {token: count for token, count in sorted(d.items(), key=lambda item: -item[1])}


def raw_pattern_and_milestone_offsets(tokens: Iterable[str], selected: Set[str]) -> Tuple[List[str], List[int]]:
    raw_pattern = []
    milestone_offsets = []
    for offset, token in enumerate(tokens):
        if token in selected:
            raw_pattern.append(token)
            milestone_offsets.append(offset)
        else:
            raw_pattern.append(None)
    return raw_pattern, milestone_offsets
