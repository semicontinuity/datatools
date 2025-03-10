import os
from pathlib import Path

from datatools.dbview.x.util.pg_query import query_from_yaml
from datatools.intent.target_folder import default_folder


class HandlerSendEntity:
    MIME_TYPE = 'multipart/form-data'
    folder: str

    def send_entity(self, realm_ctx: str, realm_ctx_dir: str, query_str: str, snapshot: bytes = None):
        print(realm_ctx)
        print(realm_ctx_dir)

        # Construct entity_realm_path from entity
        query = query_from_yaml(query_str)
        if len(query.filter) == 1 and query.filter[0].op == '=':
            entity_realm_path = f'{query.table}/:{query.filter[0].column}/{query.filter[0].value}'
        else:
            entity_realm_path = f'{query.table}/{str(hash(query_str))}'

        # Construct the target realm path
        target_realm_path = f"{self.folder}/{realm_ctx}"
        os.makedirs(target_realm_path, exist_ok=True)

        # Calculate the realm reference
        realm_ref = os.path.relpath(
            realm_ctx_dir,
            target_realm_path
        )

        # Check if the context pointer file exists, create a symlink if not
        context_pointer = Path(f"{target_realm_path}/._")
        if not context_pointer.exists():
            os.symlink(realm_ref, context_pointer)

        # Construct the entity path
        entity_path = f"{target_realm_path}/{entity_realm_path}"
        print(entity_path)
        os.makedirs(entity_path, exist_ok=True)

        # Process the query and save it to the `.query` file
        with Path(f"{entity_path}/.query").open('w') as f:
            f.write(query_str)

        if snapshot is not None:
            with Path(f"{entity_path}/content.jsonl").open('w+b') as f:
                f.write(snapshot)


handler_send_entity = HandlerSendEntity()
handler_send_entity.folder = default_folder()
