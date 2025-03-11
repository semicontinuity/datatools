import os
from pathlib import Path

from datatools.dbview.x.util.pg_query import query_from_yaml
from datatools.ev.entity_transfer import write_entity_parts, create_ctx_reference_chain
from datatools.intent.target_folder import default_folder
from datatools.json.util import to_jsonisable


class HandlerSendEntity:
    folder: str

    def send_entity(self, realm_ctx: str, realm_ctx_dir: str, query_str: str, content: bytes = None):
        query = query_from_yaml(query_str)
        entity_realm_path = make_entity_realm_path(query)

        ctx_dir = realm_ctx_dir.removesuffix('/' + realm_ctx)
        created_realm_folder = f"{self.folder}/{realm_ctx}"

        entity_path = f"{created_realm_folder}/{entity_realm_path}"
        chain = Path(realm_ctx) / entity_realm_path

        # create as much as possible...
        create_ctx_reference_chain(
            ctx=chain, referring_path=Path(self.folder), referenced_path=Path(ctx_dir)
        )

        os.makedirs(entity_path, exist_ok=True)

        write_entity_parts(entity_path, query_str, content)


def make_entity_realm_path(query):
    if len(query.filter) == 1 and query.filter[0].op == '=':
        entity_realm_path = f'{query.table}/:{query.filter[0].column}/{query.filter[0].value}'
    else:
        entity_realm_path = f'{query.table}/{str(hash(to_jsonisable(query)))}'
    return entity_realm_path


handler_send_entity = HandlerSendEntity()
handler_send_entity.folder = default_folder()
