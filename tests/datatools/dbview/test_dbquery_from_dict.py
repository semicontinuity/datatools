from datatools.dbview.x.util.db_query import DbQuery, DbQueryFilterClause
from datatools.util.dataclasses import dataclass_from_dict


def test__dataclass_from_dict__presentation__0():
    params = {
        'table': 'table',
        'filter': [
            DbQueryFilterClause(
                column='c',
                op='=',
                value=0
            )
        ]
    }

    m = DbQuery(**params)
    print(m)


def test__dataclass_from_dict__presentation__1():
    m = dataclass_from_dict(
        DbQuery,
        {
            "table": 'table',
            "filter": [
                {
                    'column': 'c',
                    'op': '=',
                    'value': 1
                }
            ]
        },
    )
    print(m)


def test__dataclass_from_dict__presentation__2():
    m = dataclass_from_dict(
        DbQuery,
        {
            "table": 'table',
            "selectors": [
                {
                    "column": 'C',
                    "resolve": {
                        "table": 'TABLE'
                    }
                }
            ],
            "filter": [
                {
                    'column': 'c',
                    'op': '=',
                    'value': 1
                }
            ]
        },
    )
    print(m)


if __name__ == '__main__':
    test__dataclass_from_dict__presentation__2()
