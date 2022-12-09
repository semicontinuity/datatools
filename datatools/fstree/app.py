#!/usr/bin/env python3

import sys
from pathlib import Path

from datatools.fstree.applet import Applet
from datatools.fstree.fs_tree_document import FsTreeDocument
from datatools.fstree.model.fs_folder import FsFolder
from datatools.tui.picotui_patch import patch_picotui
from datatools.tui.picotui_util import *
from datatools.tui.terminal import screen_size_or_default
from datatools.tui.treeview.grid import GridContext, grid
from datatools.tui.tui_fd import infer_fd_tui


def make_model(path: Path, parent: FsFolder = None, indent: int = 0, last: bool = True):
    folder = FsFolder(path.name, indent, last)

    children = []
    sub_paths = [sub_path for sub_path in path.iterdir() if sub_path.is_dir()]

    for i, sub_path in enumerate(sub_paths):
        children.append(make_model(sub_path, folder, indent + 2, i == len(sub_paths) - 1))

    folder.parent = parent
    folder.set_elements(children)
    return folder


def sample_model():
    folder = FsFolder("folder")

    children = []

    c1 = FsFolder("c1", indent=2, last_in_parent=False)
    c1.set_elements([])
    c1.parent = folder
    children.append(c1)

    c2 = FsFolder("c2", indent=2)
    c2.set_elements([])
    c2.parent = folder
    children.append(c2)

    folder.parent = None
    folder.set_elements(children)
    return folder


def make_fs_tree_applet(root: str):
    screen_width, screen_height = screen_size_or_default()
    grid_context = GridContext(0, 0, screen_width, screen_height)
    folder = make_model(Path(root))
    document = FsTreeDocument(folder, root)
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
