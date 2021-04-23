from datatools.json.structure_discovery import *


def test__object_descriptor__primitive__float():
    assert Discovery().object_descriptor(5.) == PrimitiveDescriptor('float')


def test__object_descriptor__dict():
    exp = DictDescriptor({
        'a': PrimitiveDescriptor('int'),
        'b': PrimitiveDescriptor('bool')
    })
    real = Discovery().object_descriptor({'a': 1, 'b': True})
    assert real == exp


def test__object_descriptor__list():
    assert Discovery().object_descriptor(
        [
            {'a': 1},
            {'b': True}
        ]
    ) == ListDescriptor(
        [
            DictDescriptor({'a': PrimitiveDescriptor('int')}),
            DictDescriptor({'b': PrimitiveDescriptor('bool')}),
        ]
    )


def test__object_descriptor__table():
    assert Discovery().object_descriptor(
        [
            {'a': 1, 'b': True},
            {'a': 2, 'b': False},
        ]
    ) == ArrayDescriptor(DictDescriptor(
        {
            'a': PrimitiveDescriptor('int'),
            'b': PrimitiveDescriptor('bool'),
        }
    ))


def test__object_descriptor__complex():
    real = Discovery().object_descriptor(
        [{'kind': 'k1', '_': [{'date': '2021', 'rid': 'rid1'}, {'date': '2022', 'rid': 'rid2'}, ]},
         {'kind': 'k2', '_': [{'date': '2023', 'rid': 'rid3'}, {'date': '2024', 'rid': 'rid4'}, ]}, ])
    assert real == ArrayDescriptor(DictDescriptor(
        {
            'kind': PrimitiveDescriptor('str'),
            '_': ArrayDescriptor(DictDescriptor(
                {
                    'date': PrimitiveDescriptor('str'),
                    'rid': PrimitiveDescriptor('str'),
                }
            ))
        }
    ))


def test__object_descriptor__array():
    assert Discovery().object_descriptor(
        [
            [1, 2],
            [3, 4],
        ]
    ) == ArrayDescriptor(ArrayDescriptor(PrimitiveDescriptor('int')))
