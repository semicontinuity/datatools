#!/usr/bin/env python3

import sys
from pathlib import Path

from datatools.fstree.applet import Applet
from datatools.fstree.fs_tree_document import FsTreeDocument
from datatools.fstree.model import FsFolder, populate_children, FsInvisibleRoot
from datatools.tui.picotui_patch import patch_picotui
from datatools.tui.picotui_util import *
from datatools.tui.terminal import screen_size_or_default
from datatools.tui.treeview.grid import GridContext, grid
from datatools.tui.tui_fd import infer_fd_tui


def make_fs_tree_applet(root: str):
    screen_width, screen_height = screen_size_or_default()
    grid_context = GridContext(0, 0, screen_width, screen_height)
    path = Path(root)
    model_root = FsInvisibleRoot(path.name)
    populate_children(model_root, path)
    document = FsTreeDocument(model_root, root)
    document.layout()
    document.optimize_layout(screen_height)
    document.layout()
    return do_make_fs_tree_applet(grid_context, document)


def do_make_fs_tree_applet(grid_context, document: FsTreeDocument):
    return Applet(
        'fs',
        grid(document, grid_context),
        document
    )


def main():
    fd_tui = infer_fd_tui()
    patch_picotui(fd_tui, fd_tui)

    try:
        cursor_position_save()
        Screen.init_tty()
        screen_alt()
        sys.exit(do_main())
    finally:
        screen_regular()
        Screen.deinit_tty()
        cursor_position_restore()


def do_main():
    return run(lambda: make_fs_tree_applet(sys.argv[1]).run())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)
    main()
