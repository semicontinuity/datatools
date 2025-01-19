#!/usr/bin/env python3

####################################################################
# REST Entity browser
#
# Expects concepts spec in CONCEPTS env var in the following format:
#
# {
#   "concept-name": {
#     "path": "api/v1/entity/{variable_name}",
#     "links": [
#       {
#         "json_path": "path.elements.*.element",
#         "value": "variable-name",
#         "concept": "referenced-concept",
#         "values": [ { "value": "var_name", "key": "path" }, ... ]
#       }
#     ]
#   }
# }
#
# "values" is optional
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
    path = get_env('__REST') or ""
    path = path.split('@', 1)[0].removesuffix('/')
    print(path)

    entity = realm.match_entity(path)
    if parameters := os.getenv('PARAMETERS'):
        entity.query = json.loads(parameters)

    run_app(realms, entity)


if __name__ == "__main__":
    main()
