from insight.logic.singletons import global_singletons


DATA_1 = [
    ['q', 't1', '-', '1', 'x'],
    ['q', 't1', '-', '2', 'y'],
    ['q', 't1', '-', '3', 'z'],
    ['x', 't1', '-', '1', 'q'],
    ['y', 't1', '-', '2', 'q'],
    ['z', 't1', '-', '3', 'q'],
]


def test__1():
    assert global_singletons(DATA_1) == {'t1', '-', 'q'}
