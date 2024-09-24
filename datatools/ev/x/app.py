#!/usr/bin/env python3
import json
import os

from datatools.dbview.share.app_support import run_app, View
from datatools.dbview.x.types import EntityReference
from datatools.ev.x.concepts import Concepts
from datatools.ev.x.types import RestEntity
from datatools.ev.x.view_rest_entity import ViewRestEntity


def create_view(e_ref: EntityReference) -> View:
    if type(e_ref) is RestEntity:
        return ViewRestEntity(e_ref, concepts)


def main():
    global concepts
    protocol = os.environ.get('PROTOCOL', 'http')
    host = os.environ['HOST']
    path = os.environ['__REST']

    concepts = Concepts(
        json.loads(os.environ['CONCEPTS']),
        protocol,
        host,
        headers()
    )
    parse_path = concepts.parse_path(path)
    run_app(parse_path, create_view)


def headers():
    res = {}
    for k, v in os.environ.items():
        if k.startswith('HEADER__'):
            name = k.removeprefix('HEADER__').lower().replace('_', '-')
            res[name] = v
    return res


if __name__ == "__main__":
    main()
