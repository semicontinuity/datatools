from datatools.dbview.x.util.db_query import DbQuery, DbQueryFilterClause
from datatools.dbview.x.util.result_set_metadata import ResultSetMetadata
from datatools.util.dataclasses import dataclass_from_dict


def test__dataclass_from_dict__1():
    m = dataclass_from_dict(
        ResultSetMetadata,
        {
            "table": 'table',
            "primaryKeys": [
            ],
            "relations": [
            ]
        },
    )
    print(m)


if __name__ == '__main__':
    test__dataclass_from_dict__1()
