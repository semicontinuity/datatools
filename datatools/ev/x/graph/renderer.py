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
    for folder in root.iterdir():
        # Check if it's a directory
        if folder.is_dir():
            folder_name = folder.name
            # Iterate through all entries in the subfolder
            for subfolder in folder.iterdir():
                # Check if it's a directory
                if subfolder.is_dir():
                    subfolder_name = subfolder.name
                    if subfolder_name != '._':
                        # Create a node with name "folder:subfolder"
                        node_id = f"{folder_name}:{subfolder_name}"
                        dot.node(node_id, node_id)
    
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
