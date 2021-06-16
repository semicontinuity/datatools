from datatools.logs.buckets import Bucket
from datatools.logs.buckets_pattern_inference import infer_pattern

DATA_1 = [
    ['q', 't1', '-', '1', 'x'],
    ['q', 't1', '-', '2', 'y'],
    ['q', 't1', '-', '3', 'z'],
    ['x', 't1', '-', '1', 'q'],
    ['y', 't1', '-', '2', 'q'],
    ['z', 't1', '-', '3', 'q'],
]


def test__1():
    bucket = Bucket()

    for i, tokens in enumerate(DATA_1):
        bucket.append(i, tokens)

    assert infer_pattern(bucket) == [None, 't1', '-', None]


DATA_2 = [
    ['t1', '-', '1', 'x'],
    ['t1', '-', '2', 'y'],
    ['t1', '-', '3', 'z'],
    ['t1', '-', '1', 'q'],
    ['t1', '-', '2', 'q'],
    ['t1', '-', '3', 'q'],
]


def test__2():
    bucket = Bucket()

    for i, tokens in enumerate(DATA_2):
        bucket.append(i, tokens)

    assert infer_pattern(bucket) == ['t1', '-', None]


DATA_3 = [
    ['t1', '1', 'x', '-'],
    ['t1', '2', 'y', '-'],
    ['t1', '3', 'z', '-'],
    ['t1', '1', 'q', '-'],
    ['t1', '2', 'q', '-'],
    ['t1', '3', 'q', '-'],
]


def test__3():
    bucket = Bucket()

    for i, tokens in enumerate(DATA_3):
        bucket.append(i, tokens)

    assert infer_pattern(bucket) == ['t1', None, '-']
