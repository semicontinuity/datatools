from datatools.json.structure_discovery import *


def test__object_descriptor__int():
    assert Discovery().object_descriptor(5) == {'': MetaData('int')}


def test__object_descriptor__dict():
    assert Discovery().object_descriptor({'a': 1, 'b': True}) == {
        '': MetaData('dict'), 'a': {'': MetaData('int')},
        'b': {'': MetaData('bool')}
    }


def test__object_descriptor__list():
    assert Discovery().object_descriptor(
        [
            {'a': 1},
            {'b': True}
        ]
    ) == [
        {'': MetaData('dict'), 'a': {'': MetaData('int')}},
        {'': MetaData('dict'), 'b': {'': MetaData('bool')}}
    ]


def test__object_descriptor__table():
    assert Discovery().object_descriptor(
        [
            {'a': 1, 'b': True},
            {'a': 2, 'b': False},
        ]
    ) == {
        '': MetaData('table'),
        'a': {'': MetaData('int')},
        'b': {'': MetaData('bool')},
    }


def test__object_descriptor__complex():
    assert Discovery().object_descriptor(
        [
            {
                'kind': 'k1',
                '_': [
                    { 'date': '2021', 'rid': 'rid1'},
                    { 'date': '2022', 'rid': 'rid2'},
                ]
            },
            {
                'kind': 'k2',
                '_': [
                    { 'date': '2023', 'rid': 'rid3'},
                    { 'date': '2024', 'rid': 'rid4'},
                ]
            },
        ]
    ) == {
        '': MetaData('table'),
        'kind': {'': MetaData('str')},
        '_': {
            '': MetaData('table'),
            'date': {'': MetaData('str')},
            'rid': {'': MetaData('str')},
        },
    }
