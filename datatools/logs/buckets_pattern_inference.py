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
    milestones_list = infer_milestones(tokenized_strings)
    if milestones_list is None:
        pattern_sink.append(None)
        return

    temp_bucket = Bucket()
    temp_bucket.tokenized_strings = tokenized_strings
    apply_milestones(temp_bucket, milestones_list)
    do_infer_pattern_for(temp_bucket, milestones_list, pattern_sink)


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
            # if len(milestone_offsets) == 0:
            #     return None
            bucket.init_alignment_offsets(len(milestone_offsets))
        if len(milestone_offsets) > len(bucket.alignment_offsets):
            raise ValueError(tokenized_string, milestone_offsets)
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
