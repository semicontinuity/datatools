import json
import os
from os.path import relpath
from typing import Dict

from datatools.ev.app_support import run_app
from datatools.ev.app_types import Realm
from datatools.ev.x.pg.entity_resolver import initial_entity_ref
from datatools.ev.x.pg.pg_data_source import PgDataSource
from datatools.ev.x.pg.realm_pg import RealmPg


def get_realm_ctx(props):
    return relpath(
        get_realm_ctx_dir(props),
        start=props.get('CTX_DIR')
    )


def get_realm_ctx_dir(props):
    return os.path.abspath(props.get('CTX_DIR') + '/' + (props.get('CTX_BASE') or props.get('CTX')) + '/..')

