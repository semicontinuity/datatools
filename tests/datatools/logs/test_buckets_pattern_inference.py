from datatools.logs.buckets import Bucket
from datatools.logs.buckets_pattern_inference import infer_pattern, scan_column, scan_columns

DATA_0 = [
    ['1'],
    ['2'],
    ['3'],
]


def test__0():
    bucket = Bucket()

    for i, tokens in enumerate(DATA_0):
        bucket.append(i, tokens)

    pattern = infer_pattern(bucket.tokenized_strings)
    assert pattern == [None]


DATA_1 = [
    ['q', 't1', '-', '1', 'x'],
    ['q', 't1', '-', '2', 'y'],
    ['q', 't1', '-', '3', 'z'],
    ['x', 't1', '-', '1', 'q'],
    ['y', 't1', '-', '2', 'q'],
    ['z', 't1', '-', '3', 'q'],
]


def test__1__infer_pattern():
    bucket = Bucket()

    for i, tokens in enumerate(DATA_1):
        bucket.append(i, tokens)

    assert infer_pattern(bucket.tokenized_strings) == [None, 't1', '-', None]


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

    assert infer_pattern(bucket.tokenized_strings) == ['t1', '-', None]


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

    assert infer_pattern(bucket.tokenized_strings) == ['t1', None, '-']


# Global milestones are: t1, t2, t3. x is not (not unique in string), but between t1..t2, t2..t3 it is
DATA_4 = [
    ['t1', 'x', '1', 't2', 'a', 'x', 'h', 't3'],
    ['t1', 'x', '2', 't2', 'b', 'x', 'i', 't3'],
    ['t1', 'x', '3', 't2', 'c', 'x', 'j', 't3'],
    ['t1', 'x', '4', 't2', 'd', 'x', 'k', 't3'],
    ['t1', 'x', '5', 't2', 'e', 'x', 'l', 't3'],
    ['t1', 'x', '6', 't2', 'f', 'x', 'm', 't3'],
]


def test__4():
    bucket = Bucket()

    for i, tokens in enumerate(DATA_4):
        bucket.append(i, tokens)

    pattern = infer_pattern(bucket.tokenized_strings)
    assert pattern == ['t1', 'x', None, 't2', None, 'x', None, 't3']


DATA_5 = [
    ['fill', '-', 'ID1', '-', '1'],
    ['fill', '-', 'ID1', '-', '1'],
    ['fill', '-', 'ID2', '-', '1'],
    ['fill', '-', 'ID2', '-', '1'],
    ['fill', '-', 'ID3', '-', '1'],
    ['fill', '-', 'ID3', '-', '1'],
]


def test__5__scan_column():
    assert scan_column(DATA_5, 0, False) == 'fill'
    assert scan_column(DATA_5, 1, False) == '-'
    assert scan_column(DATA_5, 2, False) == None
    assert scan_column(DATA_5, 3, False) == '-'
    assert scan_column(DATA_5, 4, False) == '1'

    assert scan_column(DATA_5, 0, True) == '1'
    assert scan_column(DATA_5, 1, True) == '-'
    assert scan_column(DATA_5, 2, True) == None
    assert scan_column(DATA_5, 3, True) == '-'
    assert scan_column(DATA_5, 4, True) == 'fill'


def test__5__scan_column2():
    assert scan_columns(DATA_5, False) == ['fill', '-']
    assert scan_columns(DATA_5, True) == ['-', '1']


def test__5():
    bucket = bucket_of(DATA_5)
    assert infer_pattern(bucket.tokenized_strings) == ['fill', '-', None, '-', '1']


DATA_6 = [
    ['main'],
    ['main'],
    ['main'],
]


def test__6():
    bucket = bucket_of(DATA_6)
    pattern = infer_pattern(bucket.tokenized_strings)
    assert pattern == ['main']


def bucket_of(data):
    bucket = Bucket()
    for i, tokens in enumerate(data):
        bucket.append(i, tokens)
    return bucket
