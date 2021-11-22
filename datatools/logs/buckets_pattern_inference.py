from typing import *

from datatools.logs.buckets import Bucket
from datatools.logs.text_classifier import raw_pattern_and_milestone_offsets
from insight.logic.singletons import global_singletons
from insight.logic.transitions import Transitions, pruned


def infer_pattern(tokenized_strings):
    pattern_sink = []
    do_infer_pattern(tokenized_strings, pattern_sink)
    return pattern_sink


def do_infer_pattern(tokenized_strings, pattern_sink):
    head_tokens = scan_columns(tokenized_strings, False)
    tail_tokens = scan_columns(tokenized_strings, True, len(head_tokens))

    pattern_sink.extend(head_tokens)

    temp_bucket = Bucket()
    temp_bucket.tokenized_strings = cut_tokens_between(tokenized_strings, len(head_tokens), len(tail_tokens))
    if temp_bucket.tokenized_strings is not None:
        milestones_list = infer_milestones(temp_bucket.tokenized_strings)
        if milestones_list is None:
            pattern_sink.append(None)
        else:
            apply_milestones(temp_bucket, milestones_list)
            do_infer_pattern_for(temp_bucket, milestones_list, pattern_sink)

    pattern_sink.extend(tail_tokens)


def cut_tokens_between(tokenized_strings, head: int, tail: int):
    """ return None if all strings are empty after cutting 'head' tokens from head and 'tail' tokens from tail """
    non_empty = False
    result = []
    for s in tokenized_strings:
        cut = s[head:len(s) - tail]
        result.append(cut)
        if len(cut) > 0:
            non_empty = True
    return result if non_empty else None


def infer_milestones(tokenized_strings):
    singletons: Set[str] = global_singletons(tokenized_strings)
    if len(singletons) == 0:
        return None

    transitions = Transitions(singletons)
    for tokenized_string in tokenized_strings:
        with transitions as tx:
            for token in tokenized_string:
                tx(token)
    milestones: Dict[str, Dict[str, int]] = pruned(transitions.singleton_transitions)
    return list(milestones.keys())


def apply_milestones(bucket, milestones_list):
    for tokenized_string in bucket.tokenized_strings:
        _, milestone_offsets = raw_pattern_and_milestone_offsets(tokenized_string, set(milestones_list))
        if bucket.alignment_offsets is None:
            bucket.init_alignment_offsets(len(milestone_offsets))
        if len(milestone_offsets) > len(bucket.alignment_offsets):
            raise ValueError(len(milestone_offsets), len(bucket.alignment_offsets), tokenized_string, milestone_offsets)
        bucket.append_milestone_offsets(milestone_offsets)


def do_infer_pattern_for(bucket, milestones_list, pattern_sink: List):
    before = tokens_between(
        lambda y: -1,
        lambda y: bucket.alignment_offsets[0][y],
        lambda y: bucket.tokenized_strings[y],
        len(bucket)
    )
    if before is not None:
        # pattern_sink.append(None)
        do_infer_pattern(before, pattern_sink)
    pattern_sink.append(milestones_list[0])

    for x in range(1, len(milestones_list)):
        between = tokens_between(
            lambda y: bucket.alignment_offsets[x - 1][y],
            lambda y: bucket.alignment_offsets[x][y],
            lambda y: bucket.tokenized_strings[y],
            len(bucket)
        )

        if between is not None:
            # pattern_sink.append(None)
            do_infer_pattern(between, pattern_sink)
        pattern_sink.append(milestones_list[x])

    after = tokens_between(
        lambda y: bucket.alignment_offsets[len(milestones_list) - 1][y],
        lambda y: len(bucket.tokenized_strings[y]),
        lambda y: bucket.tokenized_strings[y],
        len(bucket)
    )
    if after is not None:
        # pattern_sink.append(None)
        do_infer_pattern(after, pattern_sink)


def tokens_between(prev_offset_f: Callable[[int], int], offset_f: Callable[[int], int], line_f: Callable[[int], List], length: int):
    """ None if in some row milestones are adjacent: it means, that between these 'milestone columns' no sub-milestones can exist """
    result = []
    for i in range(length):
        offset = offset_f(i)
        prev_offset = prev_offset_f(i)
        if offset == prev_offset + 1:
            return None

        result.append(line_f(i)[prev_offset + 1 : offset])
    return result


def scan_columns(tokenized_strings: List[List[str]], from_tail: bool, spared_columns: int = 0):
    result = []

    x = 0
    while True:
        token = scan_column(tokenized_strings, x, from_tail, spared_columns)
        if token is None:
            return result

        if from_tail:
            result.insert(0, token)
        else:
            result.append(token)
        x += 1


def scan_column(tokenized_strings: List[List[str]], offset: int, from_tail: bool, spared_columns: int = 0):
    """ token at the column if all tokens in the column are the same; None otherwise """
    result = None
    for i in range(len(tokenized_strings)):
        tokenized_string = tokenized_strings[i]
        if from_tail:
            x = len(tokenized_string) - 1 - offset
            if x < spared_columns:
                return None
        else:
            x = offset
            if x >= len(tokenized_string) - spared_columns:
                return None

        token = tokenized_string[x]
        if result is None:
            result = token
        elif result != token:
            return None

    return result
