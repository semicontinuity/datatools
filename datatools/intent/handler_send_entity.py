import os
from pathlib import Path

from datatools.dbview.x.util.pg_query import query_from_yaml
from datatools.ev.entity_transfer import create_ctx_reference_chain, write_entity_parts_b
from datatools.intent.target_folder import default_folder
from datatools.json.util import to_jsonisable


class HandlerSendEntity:
    folder: str

    def send_entity(self, realm_ctx: str, realm_ctx_dir: str, query: bytes, content: bytes = None, rs_metadata: bytes = None):
        q = query_from_yaml(query.decode('utf-8'))
        entity_realm_path = make_entity_realm_path(q)

        ctx_dir = realm_ctx_dir.removesuffix('/' + realm_ctx)
        created_realm_folder = f"{self.folder}/{realm_ctx}"

        entity_path = f"{created_realm_folder}/{entity_realm_path}"
        chain = Path(realm_ctx) / entity_realm_path

        # create as much as possible...
        create_ctx_reference_chain(
            ctx=chain, referring_path=Path(self.folder), referenced_path=Path(ctx_dir)
        )

        os.makedirs(entity_path, exist_ok=True)

        write_entity_parts_b(Path(entity_path), query, content, rs_metadata)


def make_entity_realm_path(query):
    if len(query.filter) == 1 and query.filter[0].op == '=':
        entity_realm_path = f'{query.table}/:{query.filter[0].column}/{query.filter[0].value}'
    else:
        entity_realm_path = f'{query.table}/{str(hash(to_jsonisable(query)))}'
    return entity_realm_path


handler_send_entity = HandlerSendEntity()
handler_send_entity.folder = default_folder()
