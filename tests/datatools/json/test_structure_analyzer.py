from datatools.json.structure_analyzer import *


def test__array_descriptor_and_path_counts__plain_table():
    j = [
        {"a": 1, "b": 2},
        {"a": 1, "b": 2},
        {"a": 1},
    ]
    descriptor, path_of_leaf_to_count = array_descriptor_and_path_counts(j)
    assert descriptor == {'a': None, 'b': None}
    assert path_of_leaf_to_count == {('a',): 3, ('b',): 2}


def test__array_descriptor_and_path_counts__nested_table():
    j = [
        {"a": 1, "b": {"b1": 1, "b2": 2}},
        {"a": 1, "b": {"b1": 1, "b2": 2}},
    ]
    descriptor, path_of_leaf_to_count = array_descriptor_and_path_counts(j)
    assert descriptor == {'a': None, 'b': {"b1": None, "b2": None}}
    assert path_of_leaf_to_count == {('a',): 2, ('b', 'b1'): 2, ('b', 'b2'): 2 }
