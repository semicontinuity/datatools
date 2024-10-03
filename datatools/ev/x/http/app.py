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

from datatools.dbview.share.app_support import run_app, View
from datatools.dbview.x.types import EntityReference
from datatools.ev.x.http.concepts import Concepts
from datatools.ev.x.http.types import RestEntity
from datatools.ev.x.http.view_rest_entity import ViewRestEntity


def create_view(e_ref: EntityReference) -> View:
    if type(e_ref) is RestEntity:
        return ViewRestEntity(e_ref, concepts)


def main():
    global concepts
    protocol = os.environ.get('PROTOCOL', '')
    host = os.environ['HOST']
    path = os.environ['__REST']

    concepts = Concepts(
        json.loads(os.environ['CONCEPTS']),
        protocol,
        host,
        headers()
    )
    run_app(concepts.match_entity(path), create_view)


def headers():
    res = {}
    for k, v in os.environ.items():
        if k.startswith('HEADER__'):
            name = k.removeprefix('HEADER__').lower().replace('_', '-')
            res[name] = v
    return res


if __name__ == "__main__":
    main()
