from datatools.logs.buckets import Bucket
from datatools.logs.buckets_pattern_merger import pattern_similarity, merge_buckets_by_pattern


def test__pattern_distance__1_wildcard():
    assert pattern_similarity(['a', '-', None], ['a', '-', '1']) == 0


def test__pattern_distance__2_wildcards():
    distance = pattern_similarity([None, '-', None], ['a', '-', '1'])
    assert distance is None


def test__pattern_distance__not_equal():
    assert pattern_similarity(['a', '-', '1'], ['a', '-', '2']) is None


def test__merge_buckets_by_pattern():
    b1 = Bucket(['a', '-', None])
    b2 = Bucket(['a', '-', '1'])
    b3 = Bucket(['b', '-', '1'])
    pattern = merge_buckets_by_pattern([b1, b2, b3])
    assert pattern is None
