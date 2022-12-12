#!/usr/bin/env python3

import sys
from pathlib import Path

from datatools.fstree.fs_tree_document import FsTreeDocument
from datatools.fstree.fs_tree_model import populate_children, FsInvisibleRoot
from datatools.fstree.run_grid import run_grid
from datatools.tui.picotui_patch import patch_picotui
from datatools.tui.treeview.grid import GridContext, grid


def make_document(root: str, screen_height: int):
    path = Path(root)
    model_root = FsInvisibleRoot(path.name)
    populate_children(model_root, path)
    document = FsTreeDocument(model_root, root)
    document.layout()
    document.optimize_layout(screen_height)
    document.layout()
    return document


def make_grid(screen_height, screen_width, cursor_y, cursor_x):
    return grid(make_document(sys.argv[1], screen_height), GridContext(0, cursor_y, screen_width, screen_height))


def main():
    patch_picotui(2, 2)
    exit_code, path = run_grid(make_grid)
    if path is not None:
        print(path)
    sys.exit(exit_code)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)
    main()
