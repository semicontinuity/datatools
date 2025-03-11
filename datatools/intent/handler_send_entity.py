import os

from datatools.dbview.x.util.pg_query import query_from_yaml
from datatools.ev.entity_transfer import write_entity_parts, create_context_pointers_chain
from datatools.intent.target_folder import default_folder
from datatools.json.util import to_jsonisable


class HandlerSendEntity:
    folder: str

    def send_entity(self, realm_ctx: str, realm_ctx_dir: str, query_str: str, content: bytes = None):
        query = query_from_yaml(query_str)

        created_realm_folder = f"{self.folder}/{realm_ctx}"
        create_context_pointers_chain(created_realm_folder, realm_ctx_dir)
        entity_path = f"{created_realm_folder}/{make_entity_realm_path(query)}"
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
