#!/usr/bin/env python3

import sys
from pathlib import Path

from datatools.fstree.fs_tree_document import FsTreeDocument
from datatools.fstree.fs_tree_model import populate_children, FsInvisibleRoot
from datatools.fstree.run_grid import run_grid
from datatools.tui.picotui_patch import patch_picotui


def make_document(root: str) -> FsTreeDocument:
    path = Path(root)
    model_root = FsInvisibleRoot(path.name)
    populate_children(model_root, path)
    return FsTreeDocument(model_root, root)


def main(root):
    patch_picotui(2, 2)
    exit_code, path = run_grid(make_document(root))
    if path is not None:
        print(path)
    sys.exit(exit_code)


if __name__ == "__main__":
    paths = [p for p in sys.argv[1:] if not p.startswith('-')]
    if len(paths) == 0:
        root = '.'
    elif len(paths) == 1:
        root = paths[0]
    else:
        sys.exit(1)

    main(root)
