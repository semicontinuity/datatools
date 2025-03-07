#!/usr/bin/python3
import json
import os
import subprocess
from os.path import relpath
from typing import Dict, List, Callable, Any

from datatools.ev.app_support import run_app
from datatools.ev.app_types import EntityReference
from datatools.ev.app_types import Realm
from datatools.ev.x.ch.entity_resolver import resolve_ch_entity
from datatools.ev.x.ch.realm_clickhouse import RealmClickhouse
from datatools.ev.x.pg.entity_resolver import resolve_pg_entity
from datatools.ev.x.pg.pg_data_source import PgDataSource
from datatools.ev.x.pg.realm_pg import RealmPg
from datatools.ev.x.realm_bootstrap import get_realm_ctx, get_realm_ctx_dir


def exe(cwd: str, args: List[str], env: Dict[str, str], stdin: bytes = None):
    proc = subprocess.Popen(
        args,
        cwd=cwd,
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate(stdin)
    if proc.returncode != 0:
        raise Exception((proc.returncode, err.decode()))
    return out.decode()


class Realms:
    mounts: Dict[str, Realm]
    entity_resolvers: Dict[Any, Callable[[Realm, str, str], EntityReference]]

    def __init__(self,
                 ctx_dir: str,
                 mounts: Dict[str, Callable[[str], Realm]],
                 entity_resolvers: Dict[Any, Callable[[Realm, str, str], EntityReference]]):
        self.mounts = {rel_path: f(name, ctx_dir + '/' + rel_path) for rel_path, (name, f) in
                       mounts.items()}
        self.entity_resolvers = entity_resolvers

    def resolve(self, ctx: str) -> EntityReference:
        for base_ctx, realm in self.mounts.items():
            if ctx.startswith(base_ctx + '/'):
                rest = ctx.removeprefix(base_ctx + '/')
                return self.entity_resolvers[type(realm)](realm, base_ctx, rest)

    def as_dict(self) -> Dict[str, Realm]:
        return {v.name: v for k, v in self.mounts.items()}


def realm_pg(name, path: str) -> RealmPg:
    # We need a special mode to run 'y': force-var-override
    env = {k: v for k, v in os.environ.items()}
    env.pop('HOST', None)
    env.pop('PORT', None)
    env.pop('PASSWORD', None)
    env.pop('DB_NAME', None)
    env.pop('DB_USER', None)
    env.pop('DB_CLUSTER_ID', None)
    env.pop('CTX', None)
    env.pop('CTX_DIR', None)
    env.pop('WD', None)
    env.pop('CWD', None)

    realm_env_vars_s = exe(
        path,
        ['y', 'env'],
        env
    )

    realm_env_vars = {}
    for entry in realm_env_vars_s.split('\n'):
        eq = entry.find('=')
        realm_env_vars[entry[:eq]] = entry[(eq + 1):]

    def links():
        if os.path.exists(f := path + '/.links'):
            with open(f, 'r') as file:
                return json.load(file)
        else:
            return {}

    realm = RealmPg(name, PgDataSource(realm_env_vars), links(), )
    realm.realm_ctx = relpath(path, start=realm_env_vars.get('CTX_DIR'))
    realm.realm_ctx_dir = path
    return realm


def realm_ch(name, path: str) -> RealmClickhouse:
    # We need a special mode to run 'y': force-var-override
    env = {k: v for k, v in os.environ.items()}
    env.pop('CTX', None)
    env.pop('CTX_DIR', None)
    env.pop('WD', None)
    env.pop('CWD', None)
    env.pop('YC_CH_HOST', None)
    env.pop('YC_CH_DATABASE', None)
    env.pop('YC_CH_USER', None)
    env.pop('YC_CH_PASSWORD', None)

    realm_env_vars_s = exe(
        path,
        ['y', 'env'],
        env
    )

    realm_env_vars = {}
    for entry in realm_env_vars_s.split('\n'):
        eq = entry.find('=')
        realm_env_vars[entry[:eq]] = entry[(eq + 1):]

    def links():
        if os.path.exists(f := path + '/.links'):
            with open(f, 'r') as file:
                return json.load(file)
        else:
            return {}

    realm = RealmClickhouse(name=name, hostname=realm_env_vars['YC_CH_HOST'],
                                 database=realm_env_vars['YC_CH_DATABASE'], user=realm_env_vars['YC_CH_USER'],
                                 password=realm_env_vars['YC_CH_PASSWORD'], links=links())
    realm.realm_ctx = relpath(path, start=realm_env_vars.get('CTX_DIR'))
    realm.realm_ctx_dir = path
    return realm


def infer_mounts(e):
    match e:
        case 'te-testing':
            return {
                'te-testing/deploy/infra/pg/yacalls/notification_service_test/tables': ('db_notification_service', realm_pg),
                'te-testing/deploy/infra/pg/yacalls/calls_test/tables': ('db_calls', realm_pg),
                'te-testing/deploy/infra/ch/yacalls-cdr-test/cdr/tables': ('ch_cdr', realm_ch)
            }
        case 'te-preprod':
            return {
                'te-preprod/deploy/infra/pg/yacalls/notification_service_preprod/tables': ('db_notification_service', realm_pg),
                'te-preprod/deploy/infra/pg/yacalls/calls_preprod/tables': ('db_calls', realm_pg),
                'te-preprod/deploy/infra/ch/yacalls-cdr-preprod/cdr/tables': ('ch_cdr', realm_ch)
            }
        case 'te-prod':
            return {
                'te-prod/deploy/infra/pg/yacalls/notification_service_prod/tables': ('db_notification_service', realm_pg),
                'te-prod/deploy/infra/pg/yacalls/calls_prod/tables': ('db_calls', realm_pg),
                'te-prod/deploy/infra/ch/yacalls-cdr-prod/cdr/tables': ('ch_cdr', realm_ch)
            }
        case _:
            return {}


def main():
    e = os.environ['E']
    ctx_dir = os.environ['CTX_DIR']

    realms = Realms(
        ctx_dir,
        infer_mounts(e),
        {
            RealmPg: resolve_pg_entity,
            RealmClickhouse: resolve_ch_entity,
        }
    )
    run_app(
        realms.as_dict(),
        realms.resolve(os.environ['CTX'])
    )


if __name__ == "__main__":
    main()
