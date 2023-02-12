#!/usr/bin/env python3

import sys
from threading import Thread, Event
from time import sleep

from datatools.fstree.fs_tree_document import FsTreeDocument
from datatools.fstree.run_grid import run_grid
from datatools.tui.picotui_patch import patch_picotui


class PeriodicDocumentRefresher(Thread):

    def __init__(self, document: FsTreeDocument):
        Thread.__init__(self)
        self._stop = Event()
        self.document = document

    def run(self):
        while True:
            self.document.refresh()
            if self._stop.wait(2):
                break

    def stop(self):
        self._stop.set()


def do_main(root: str):
    patch_picotui(2, 2)
    document = FsTreeDocument(root)
    refresher = PeriodicDocumentRefresher(document)

    refresher.start()
    exit_code, path = run_grid(document)
    if path is not None:
        print(path)
    refresher.stop()

    sys.exit(exit_code)


def main():
    paths = [p for p in sys.argv[1:] if not p.startswith('-')]
    if len(paths) == 0:
        root = '.'
    elif len(paths) == 1:
        root = paths[0]
    else:
        sys.exit(1)
    do_main(root)


if __name__ == "__main__":
    main()
