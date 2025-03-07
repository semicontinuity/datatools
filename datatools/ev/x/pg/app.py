#!/usr/bin/env python3
import json
import os
from typing import Dict

from datatools.ev.app_support import run_app
from datatools.ev.app_types import Realm
from datatools.ev.x.pg.entity_resolver import initial_entity_ref
from datatools.ev.x.pg.pg_data_source import PgDataSource
from datatools.ev.x.pg.realm_pg import RealmPg
from datatools.ev.x.realm_bootstrap import get_realm_ctx, get_realm_ctx_dir

data_source = PgDataSource(os.environ)


def load_links(p):
    if p is None:
        return {}
    else:
        return json.loads(p)


def realms() -> Dict[str, Realm]:
    links = load_links(os.getenv('LINKS'))
    realm_pg = RealmPg(None, data_source, links)
    realm_pg.realm_ctx = get_realm_ctx(os.environ)
    realm_pg.realm_ctx_dir = get_realm_ctx_dir(os.environ)

    return {
        None: realm_pg
    }


def main():
    run_app(
        realms(),
        initial_entity_ref(data_source)
    )


if __name__ == "__main__":
    main()
