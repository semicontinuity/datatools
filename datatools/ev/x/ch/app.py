#!/usr/bin/env python3
import json
import os

from datatools.dbview.x.util.pg import get_where_clauses
from datatools.ev.app_support import run_app
from datatools.ev.x.ch.realm_clickhouse import RealmClickhouse
from datatools.ev.x.ch.types import ClickhouseRowEntity
from datatools.ev.x.pg.types import DbTableRowsSelector, DbSelectorClause


def main():
    realm = RealmClickhouse(
        name=None,
        hostname=os.environ['YC_CH_HOST'],
        database=os.environ['YC_CH_DATABASE'],
        user=os.environ['YC_CH_USER'],
        password=os.environ['YC_CH_PASSWORD'],
        links=links(os.getenv('LINKS'))
    )
    run_app(
        {None: realm},
        ClickhouseRowEntity(
            realm_name=None,
            selector=DbTableRowsSelector(
                table=os.environ['TABLE'],
                where=[DbSelectorClause(*w) for w in get_where_clauses()]
            )
        )
    )


def links(p):
    if p is None:
        return {}
    else:
        return json.loads(p)


if __name__ == '__main__':
    main()
