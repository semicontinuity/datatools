#!/usr/bin/env python3
import json
import os
import sys

from datatools.dbview.x.util.pg import get_where_clauses
from datatools.ev.app_support import run_app
from datatools.ev.x.ch.clickhouse_connection_settings import ClickhouseConnectionSettings
from datatools.ev.x.ch.realm_clickhouse import RealmClickhouse
from datatools.ev.x.ch.types import ClickhouseRowEntity
from datatools.ev.x.pg.types import DbTableRowsSelector, DbSelectorClause


def main():
    connection_settings = ClickhouseConnectionSettings(
        hostname='localhost' if os.environ.get('LOCAL_PORT') else os.environ['YC_CH_HOST'],
        port=os.environ.get('LOCAL_PORT') if os.environ.get('LOCAL_PORT') else 8443,
        secure=False if os.environ.get('LOCAL_PORT') else True, database=os.environ['YC_CH_DATABASE'],
        user=os.environ['YC_CH_USER'], password=os.environ['YC_CH_PASSWORD'])
    realm = RealmClickhouse(
        name=None,
        connection_settings=connection_settings,
        links=links(os.getenv('LINKS')),
    )
    print('connection_settings', str(connection_settings), file=sys.stderr)

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
