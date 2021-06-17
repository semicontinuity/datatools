from typing import *

from datatools.logs.text_classifier import raw_pattern_and_milestone_offsets
from datatools.util.logging import debug
from insight.logic.singletons import global_singletons
from insight.logic.transitions import Transitions, pruned


def infer_pattern(bucket):
    debug("")
    debug("INFER PATTERN")

    milestones_list = infer_milestones(bucket)
    debug(milestones_list)

    apply_milestones(bucket, milestones_list)
    return do_infer_pattern(bucket, milestones_list)


def infer_milestones(bucket):
    singletons: Set[str] = global_singletons(bucket.tokenized_strings)
    debug(singletons)
    transitions = Transitions(singletons)
    for tokenized_string in bucket.tokenized_strings:
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


def do_infer_pattern(bucket, milestones_list):
    pattern = []
    if not milestone_is_adjacent_to_previous(
            len(bucket), lambda y: -1, lambda y: bucket.alignment_offsets[0][y]):
        pattern.append(None)
    pattern.append(milestones_list[0])
    for x in range(1, len(milestones_list)):
        if not milestone_is_adjacent_to_previous(
                len(bucket), lambda y: bucket.alignment_offsets[x - 1][y], lambda y: bucket.alignment_offsets[x][y]):
            pattern.append(None)
        pattern.append(milestones_list[x])
    if not milestone_is_adjacent_to_previous(
            len(bucket), lambda y: bucket.alignment_offsets[len(milestones_list) - 1][y],
            lambda y: len(bucket.tokenized_strings[y])):
        pattern.append(None)
    return pattern


def milestone_is_adjacent_to_previous(length: int, prev_offset_f: Callable[[int], int], offset_f: Callable[[int], int]):
    for i in range(length):
        if offset_f(i) != prev_offset_f(i) + 1:
            return False
    return True
