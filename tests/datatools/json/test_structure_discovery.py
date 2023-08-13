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


def test__compute_column_paths__0():
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


def test__compute_column_paths__1():
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
    assert compute_column_paths(descriptor) == [
        ('name',),
        ('type',),
    ]


def test__compute_row_paths__1():
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
    paths, _ = compute_row_paths(j, descriptor)
    assert paths == [
        ('input_parameters', 0),
        ('input_parameters', 1),
        ('output_parameters', 0)
    ]
    assert child_by_path(j, ('input_parameters', 0)) == {"name": "a", "type": "int"}
    assert child_by_path(j, ('input_parameters', 1)) == {"name": "b", "type": "int"}
    assert child_by_path(j, ('output_parameters', 0)) == {"name": "c", "type": "int"}


def test__compute_column_paths__2():
    generic_row_descriptor = MappingDescriptor(
        kind='dict',
        uniform=True,
        length=2,
        entries={
            'address': PrimitiveDescriptor('int'),
            'contents': MappingDescriptor(
                kind='list', uniform=True, length=None, entries={
                    0: MappingDescriptor(
                        kind='dict', uniform=True, length=2, entries={
                            'alias': PrimitiveDescriptor('str'),
                            'value': PrimitiveDescriptor('str')
                        },
                    )
                },
            )
        },
    )
    assert compute_column_paths(generic_row_descriptor) == [
        ('address',),
        ('contents',),
    ]


def test__compute_row_paths__2__then__compute_column_paths():
    j = {
        "discrete_inputs": [
            {
                "address": 0,
                "contents": [
                    {"alias": "alias1.1", "value": 11},
                    {"alias": "alias1.2", "value": 12}
                ]
            }
        ],
        "coils": [
            {
                "address": 0,
                "contents": [
                    {"alias": "alias2.1", "value": 21},
                    {"alias": "alias2.2", "value": 22},
                    {"alias": "alias2.3", "value": 23}
                ]
            }
        ]
    }
    descriptor = Discovery().object_descriptor(j)
    paths, generic_row_descriptor = compute_row_paths(j, descriptor)
    assert paths == [
        ('discrete_inputs', 0),
        ('coils', 0),
    ]
    assert generic_row_descriptor == MappingDescriptor(
        kind='dict',
        uniform=True,
        length=2,
        entries={
            'address': PrimitiveDescriptor('int'),
            'contents': MappingDescriptor(
                kind='list', uniform=True, length=None, entries={
                    0: MappingDescriptor(
                        kind='dict', uniform=True, length=2, entries={
                            'alias': PrimitiveDescriptor('str'),
                            'value': PrimitiveDescriptor('str')
                        },
                    )
                },
            )
        },
    )

    assert compute_column_paths(generic_row_descriptor) == [
        ('address',),
        ('contents',),
    ]

    assert descriptor_by_path(generic_row_descriptor, ('address',)) == PrimitiveDescriptor('int')

    assert child_by_path(j, ('discrete_inputs', 0)) == {
        "address": 0,
        "contents": [
            {"alias": "alias1.1", "value": 11},
            {"alias": "alias1.2", "value": 12}
        ]
    }
    assert child_by_path(j, ('coils', 0)) == {
        "address": 0,
        "contents": [
            {"alias": "alias2.1", "value": 21},
            {"alias": "alias2.2", "value": 22},
            {"alias": "alias2.3", "value": 23}
        ]
    }


def test__compute_column_paths__table_with_multi_level_headers():
    j = [
        {
            "header1": {
                "sub_header1": "1.1.1",
                "sub_header2": "1.1.2"
            }
        },
        {
            "header1": {
                "sub_header1": "2.1.1",
                "sub_header2": "2.1.2"
            }
        }
    ]
    descriptor = Discovery().object_descriptor(j)
    # OK?
    assert compute_column_paths(descriptor) == [
        (0, 'header1', 'sub_header1'),
        (0, 'header1', 'sub_header2'),
        (1, 'header1', 'sub_header1'),
        (1, 'header1', 'sub_header2'),
    ]


def test__compute_row_paths__table_with_multi_level_headers():
    j = [
        {
            "header1": {
                "sub_header1": "1.1.1",
                "sub_header2": "1.1.2"
            }
        },
        {
            "header1": {
                "sub_header1": "2.1.1",
                "sub_header2": "2.1.2"
            }
        }
    ]
    descriptor = Discovery().object_descriptor(j)
    paths, _ = compute_row_paths(j, descriptor)
    assert paths == [
        (0, "header1"),
        (1, "header1"),
    ]
    assert child_by_path(j, (0, "header1")) == {
        "sub_header1": "1.1.1",
        "sub_header2": "1.1.2"
    }
