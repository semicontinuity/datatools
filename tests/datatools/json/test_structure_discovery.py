from datatools.json.structure_discovery import *


def test__object_descriptor__primitive__float():
    result = Discovery().object_descriptor(5.)
    assert result == PrimitiveDescriptor('float')
    assert result.is_primitive()


def test__object_descriptor__dict():
    result = Discovery().object_descriptor({'a': 1, 'b': True})
    assert result == DictDescriptor({
        'a': PrimitiveDescriptor('int'),
        'b': PrimitiveDescriptor('bool')
    })
    assert result.is_dict()


def test__object_descriptor__list():
    result = Discovery().object_descriptor([{'a': 1}, {'b': True}])
    assert result == ListDescriptor(
        [
            DictDescriptor({'a': PrimitiveDescriptor('int')}),
            DictDescriptor({'b': PrimitiveDescriptor('bool')}),
        ]
    )
    assert result.is_list()


def test__object_descriptor__table():
    result = Discovery().object_descriptor([{'a': 1, 'b': True}, {'a': 2, 'b': False}, ])
    assert result == ArrayDescriptor(DictDescriptor(
        {
            'a': PrimitiveDescriptor('int'),
            'b': PrimitiveDescriptor('bool'),
        }
    ))
    assert result.is_array()


def test__object_descriptor__nested_table():
    result = Discovery().object_descriptor(
        [{'a': 1, 'b': {'b1': True, 'b2': 'x'}}, {'a': 2, 'b': {'b1': False, 'b2': 'y'}}]
    )
    assert result == ArrayDescriptor(DictDescriptor(
        {
            'a': PrimitiveDescriptor('int'),
            'b': DictDescriptor({
                'b1': PrimitiveDescriptor('bool'),
                'b2': PrimitiveDescriptor('str'),
            }),
        }
    ), length=2)
    assert result.is_array()


def test__object_descriptor__table__deep_differences():
    result = Discovery().object_descriptor([{"a": 1, "b": [{"x": 5, "y": 6}, {"x": 7, "y": 8} ]}, {"a": 2, "b": [1,2]}])
    assert result == ArrayDescriptor(DictDescriptor(
        {
            'a': PrimitiveDescriptor('int'),
            'b': ArrayDescriptor(AnyDescriptor()),
        }
    ))
    assert result.is_array()


def test__object_descriptor__table__qualified_rows():
    result = Discovery().object_descriptor({'key1': {'a': 1, 'b': True}, 'key2': {'a': 1, 'b': True}, })
    assert result == ArrayDescriptor(DictDescriptor(
        {
            'a': PrimitiveDescriptor('int'),
            'b': PrimitiveDescriptor('bool'),
        }
    ))
    assert result.is_array()


def test__object_descriptor__complex():
    result = Discovery().object_descriptor(
        [{'kind': 'k1', '_': [{'date': '2021', 'rid': 'rid1'}, {'date': '2022', 'rid': 'rid2'}, ]},
         {'kind': 'k2', '_': [{'date': '2023', 'rid': 'rid3'}, {'date': '2024', 'rid': 'rid4'}, ]}, ])
    assert result == ArrayDescriptor(
        DictDescriptor(
            {
                'kind': PrimitiveDescriptor('str'),
                '_': ArrayDescriptor(
                    DictDescriptor(
                        {
                            'date': PrimitiveDescriptor('str'),
                            'rid': PrimitiveDescriptor('str'),
                        }
                    ), length=2
                )
            }
        ), length=2
    )
    assert result.is_array()


def test__object_descriptor__matrix():
    descriptor = Discovery().object_descriptor([[1, 2, 3], [5, 6, 7], ])
    assert descriptor == ArrayDescriptor(ArrayDescriptor(PrimitiveDescriptor('int')))
    assert descriptor.length == 2
    assert descriptor.array.length == 3


def test__compute_column_paths():
    descriptor = DictDescriptor(
        {
            'a': PrimitiveDescriptor('int'),
            'b': DictDescriptor({
                'b1': PrimitiveDescriptor('bool'),
                'b2': PrimitiveDescriptor('str'),
            }),
        }
    )
    assert compute_column_paths(descriptor) == [
        ('a',),
        ('b', 'b1'),
        ('b', 'b2'),
    ]


def test__compute_column_paths__with_empty_dict():
    descriptor = DictDescriptor(
            {
                'parent': DictDescriptor({
                    'empty': DictDescriptor({}),
                    'full': PrimitiveDescriptor('str')
                })
            }
        )
    assert compute_column_paths(descriptor) == [
        ('parent', 'empty'),
        ('parent', 'full'),
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
    assert child_by_path(j, ('input_parameters', 0)) == (True, {"name": "a", "type": "int"})
    assert child_by_path(j, ('input_parameters', 1)) == (True, {"name": "b", "type": "int"})
    assert child_by_path(j, ('output_parameters', 0)) == (True, {"name": "c", "type": "int"})
