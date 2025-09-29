import json
import os
import sys
from pathlib import Path

from graphviz import Digraph

svg = bool(os.environ.get('SVG'))
RANKDIR = os.environ.get('RANKDIR')


def make_graph(root: Path):
    dot = Digraph('Entities', format='png')
    dot.attr(rankdir=(RANKDIR or 'LR'))
    
    # Iterate through all entries in the root directory
    for entity_type_folder in root.iterdir():
        if not entity_type_folder.is_dir():
            continue

        entity_type_folder_name = entity_type_folder.name
        if entity_type_folder_name[0].islower():
            # Now entity types start with uppercase letter; e.g. `AtsChannel`
            continue

        for entity_ids_slug_folder in entity_type_folder.iterdir():
            # Check if it's a directory
            if entity_ids_slug_folder.is_dir():
                entity_ids_slug_folder_name = entity_ids_slug_folder.name
                # Create a node with name "folder:subfolder"
                if entity_ids_slug_folder_name == '._':
                    continue

                file_path = entity_ids_slug_folder / '.entity_ids'
                # print(file_path, file=sys.stderr)

                if file_path.exists():
                    with open(file_path, 'r') as file:
                        entity_ids = json.load(file)
                        # print(entity_ids, file=sys.stderr)
                else:
                    entity_ids = [entity_ids_slug_folder_name]

                for entity_id in entity_ids:
                    node_id = f"{entity_type_folder_name}#{entity_id}"
                    # dot.node(node_id, node_id)
                    dot.node(node_id)

                for manifestation_folder in entity_ids_slug_folder.iterdir():
                    print(manifestation_folder, file=sys.stderr)
                    file_path = manifestation_folder / '.referred_entity_ids'
                    if file_path.exists():
                        with open(file_path, 'r') as file:
                            referred_entities = json.load(file)
                            for referred_entity_type, referred_entity_ids in referred_entities.items():
                                for referred_entity_id in referred_entity_ids:
                                    for entity_id in entity_ids:

                                        if '@' in entity_id or '@' in referred_entity_id:
                                            continue
                                        if '/' in entity_id or '/' in referred_entity_id:
                                            continue

                                        dot.edge(
                                            f"{entity_type_folder_name}#{entity_id}",
                                            f"{referred_entity_type}#{referred_entity_id}",
                                        )

    return dot


def main():
    folder = Path(os.environ['PWD'])
    dot = make_graph(folder)
    if os.environ.get('SVG'):
        sys.stdout.buffer.write(dot.pipe(format='svg'))
    else:
        print(dot.source)


if __name__ == '__main__':
    sys.exit(main() or 0)
