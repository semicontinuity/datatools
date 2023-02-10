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


def main():
    patch_picotui(2, 2)
    exit_code, path = run_grid(make_document(sys.argv[1]))
    if path is not None:
        print(path)
    sys.exit(exit_code)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)
    main()
