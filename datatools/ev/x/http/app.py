#!/usr/bin/env python3

####################################################################
# REST Entity browser
#
# Expects concepts spec in CONCEPTS env var in the following format:
#
# {
#   "concept-name": {
#     "path": "base path like api/v1/entity",
#     "links": [
#       {
#         "path_pattern": ["path", "elements", null, "element"],
#         "concept": "referenced-concept"
#       }
#     ]
#   }
# }
#
# null in path pattern means "any array element"
####################################################################

import json
import os
from typing import Dict

from datatools.ev.app_support import run_app
from datatools.ev.app_types import Realm
from datatools.ev.x.http.realm_rest import RealmRest


def headers():
    res = {}
    for k, v in os.environ.items():
        if k.startswith('HEADER__'):
            name = k.removeprefix('HEADER__').lower().replace('_', '-')
            res[name] = v
    return res


def get_env(key):
    value = os.getenv(key)
    if value is None:
        raise Exception(f'Must set {key}')
    return value


realm = RealmRest(
    None,
    json.loads(get_env('CONCEPTS')),
    get_env('PROTOCOL'),
    get_env('HOST'),
    headers()
)
realms: Dict[str, Realm] = {None: realm}


def main():
    entity = realm.match_entity(get_env('__REST'))
    if parameters := os.getenv('PARAMETERS'):
        entity.query = json.loads(parameters)

    run_app(realms, entity)


if __name__ == "__main__":
    main()
