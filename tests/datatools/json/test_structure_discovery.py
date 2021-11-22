from datatools.json.structure_discovery import *


def test__object_descriptor__primitive__float():
    result = Discovery().object_descriptor(5.)
    assert result == PrimitiveDescriptor('float')
    assert result.is_primitive()


def test__object_descriptor__dict():
    result = Discovery().object_descriptor({'a': 1, 'b': True})
    assert result.is_dict()


def test__object_descriptor__list():
    result = Discovery().object_descriptor([{'a': 1}, {'b': True}])
    assert result.is_list()


def test__object_descriptor__table():
    result = Discovery().object_descriptor([{'a': 1, 'b': True}, {'a': 2, 'b': False}, ])
    assert result.is_array()


def test__object_descriptor__nested_table():
    result = Discovery().object_descriptor(
        [{'a': 1, 'b': {'b1': True, 'b2': 'x'}}, {'a': 2, 'b': {'b1': False, 'b2': 'y'}}]
    )
    assert result.is_array()


def test__object_descriptor__table__deep_differences():
    result = Discovery().object_descriptor([{"a": 1, "b": [{"x": 5, "y": 6}, {"x": 7, "y": 8} ]}, {"a": 2, "b": [1,2]}])
    assert result.is_array()


def test__object_descriptor__table__qualified_rows():
    result = Discovery().object_descriptor({'key1': {'a': 1, 'b': True}, 'key2': {'a': 1, 'b': True}, })
    assert result.is_array()


def test__object_descriptor__complex():
    result = Discovery().object_descriptor(
        [{'kind': 'k1', '_': [{'date': '2021', 'rid': 'rid1'}, {'date': '2022', 'rid': 'rid2'}, ]},
         {'kind': 'k2', '_': [{'date': '2023', 'rid': 'rid3'}, {'date': '2024', 'rid': 'rid4'}, ]}, ])
    assert result.is_array()



def test__compute_column_paths__1():
    descriptor = MappingDescriptor(
        {
            'l': MappingDescriptor({0: AnyDescriptor()}, kind='list', uniform=True, length=1),
            'c': MappingDescriptor({0: AnyDescriptor()}, kind='list', uniform=True, length=1)
        },
        kind='dict',
        uniform=True,
        length=2
    )
    assert compute_column_paths(descriptor) == [
        ('l',),
        ('c',),
    ]


def test__compute_row_paths():
    j = {
        "input_parameters": [
            {"name": "a", "type": "int"},
            {"name": "b", "type": "int"}
        ],
        "output_parameters": [
            {"name": "c", "type": "int"}
        ]
    }
    descriptor = Discovery().object_descriptor(j)
    paths = compute_row_paths(j, descriptor)
    assert paths == [
        ('input_parameters', 0),
        ('input_parameters', 1),
        ('output_parameters', 0)
    ]
    assert child_by_path(j, ('input_parameters', 0)) == {"name": "a", "type": "int"}
    assert child_by_path(j, ('input_parameters', 1)) == {"name": "b", "type": "int"}
    assert child_by_path(j, ('output_parameters', 0)) == {"name": "c", "type": "int"}
