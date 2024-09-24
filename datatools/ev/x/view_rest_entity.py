import os
from typing import Optional

import requests

from datatools.dbview.share.app_types import View, EntityReference
from datatools.ev.x.types import RestEntity
from datatools.jv.app import make_document, make_grid, do_loop
from datatools.jv.document import JDocument
from datatools.tui.screen_helper import with_alternate_screen

from datatools.ev.x.concepts import Concepts


class ViewRestEntity(View):
    ref: RestEntity
    doc: JDocument

    def __init__(self, ref: RestEntity, concepts: Concepts) -> None:
        self.ref = ref
        self.concepts = concepts

    def build(self):
        url = self.concepts.url(self.ref)
        response = requests.request('GET', url, headers=headers())
        if 200 <= response.status_code < 300:
            j = response.json()
        else:
            raise Exception(f"Got status {response.status_code} for {url}")

        self.doc = make_document(j, f'{self.ref.concept} {self.ref.entity_id}')
        self.g = with_alternate_screen(lambda: make_grid(self.doc))

    def run(self) -> Optional[EntityReference]:
        key_code, cur_line = with_alternate_screen(lambda: do_loop(self.g))
        return self.handle_loop_result(self.doc, key_code, cur_line)

    def handle_loop_result(self, document, key_code, cur_line: int) -> Optional[EntityReference]:
        return key_code


def headers():
    res = {}
    for k, v in os.environ.items():
        if k.startswith('HEADER__'):
            name = k.removeprefix('HEADER__').lower().replace('_', '-')
            res[name] = v
    return res
