from typing import Dict

from insight.logic.singletons import global_singletons
from insight.logic.transitions import Transitions, pruned

DATA_1 = [
    ['q', 't1', '-', '1', 'x'],
    ['q', 't1', '-', '2', 'y'],
    ['q', 't1', '-', '3', 'z'],
    ['x', 't1', '-', '1', 'q'],
    ['y', 't1', '-', '2', 'q'],
    ['z', 't1', '-', '3', 'q'],
]


def test__1():
    singletons = global_singletons(DATA_1)
    transitions = Transitions(singletons)

    for tokens in DATA_1:
        with transitions as tx:
            for token in tokens:
                tx(token)

    milestones: Dict[str, Dict[str, int]] = pruned(transitions.singleton_transitions)
    assert milestones.keys() == {'t1', '-'}
