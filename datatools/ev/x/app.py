#!/usr/bin/env python3
import os

from datatools.dbview.share.app_support import run_app, View
from datatools.dbview.x.types import EntityReference
from datatools.ev.x.types import RestEntity
from datatools.ev.x.view_rest_entity import ViewRestEntity


def main():
    run_app(RestEntity(initial_url()), create_view)


def create_view(e_ref: EntityReference) -> View:
    if type(e_ref) is RestEntity:
        return ViewRestEntity(e_ref)


def initial_url():
    protocol = os.environ.get('PROTOCOL', 'http')
    host = os.environ['HOST']
    path = os.environ['__REST']
    url = f'{protocol}://{host}/{path}'
    return url


if __name__ == "__main__":
    main()
