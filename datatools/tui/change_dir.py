from typing import Optional

from picotui.widgets import WListBox, Dialog, ACTION_CANCEL, ACTION_PREV, ACTION_NEXT, ACTION_OK

from datatools.tui.picotui_patch import patch_picotui

patch_picotui()
from datatools.tui.picotui_patch import *

from datatools.tui.picotui_util import *
from picotui.defs import *
import os
import sys
import json

screen = Screen()
HEIGHT = 25


def debug_print(*s):
    screen.clear_box(0, 0, 200, 1)
    Screen.goto(0, 0)
    print(*s, file=sys.stderr)


class FolderLists:
    def __init__(self, folder, root, root_history):
        self.root = root
        self.root_history = root_history
        self.lists = self.initial_lists(folder)

    def initial_lists(self, folder):
        path = folder
        lists = []
        first = True
        while True:
            a_list = self.make_list(path, 0)
            if a_list is not None:  # the deepest folder will not necessarily contain sub-folders
                lists.append(a_list)
                if first:
                    a_list.focus = True
                    first = False
            if path == self.root:
                break
            path = path[:path.rfind('/')]

        lists = list(reversed(lists))
        for index, l in enumerate(lists):
            l.index = index

        return lists

    def is_empty(self):
        return len(self.lists) == 0

    def lists_in_path(self, index):
        return self.lists[: index + 1]

    def node_path(self, index):
        return self.root if index == 0 else self.child_path(index - 1)

    def child_path(self, index):
        return self.root + '/' + '/'.join([l.content[l.choice] for l in self.lists_in_path(index)])

    def activate_sibling(self, index):
        self.lists = self.lists[: index + 1]

    def try_go_in(self, index):
        if index != len(self.lists) - 1:
            return

        self.memorize_choice_in_list(index)

        new_list = self.make_list(self.child_path(index), index + 1)
        if new_list is None:
            return

        self.lists.append(new_list)
        return True

    def memorize_choice_in_list(self, index):
        if index < 0:
            return
        node_path = self.node_path(index)
        folder_name = self.lists[index].content[self.lists[index].choice]
        self.memorize(node_path, folder_name)

    def make_list(self, folder, index: int) -> Optional[WListBox]:
        contents = [name for name in sorted(os.listdir(folder)) if
                    os.path.isdir(folder + '/' + name) and not name.startswith('.')]
        if len(contents) == 0:
            return None
        box = WListBox(max(len(s) for s in contents), HEIGHT, contents)
        box.index = index
        box.folder = folder
        choice = self.recall(folder, contents)
        box.choice = 0 if choice is None else choice
        box.cur_line = box.choice
        return box

    def recall(self, folder, contents):
        if folder in self.root_history:
            last_name = self.root_history[folder]
            if last_name is not None:
                for i, name in enumerate(contents):
                    if last_name == name:
                        return i

    def memorize(self, folder, name):
        self.root_history[folder] = name


class ChangeFoldersDialog(Dialog):
    def __init__(self, width, height, x, y, folder_lists: FolderLists):
        super().__init__(0, 0, width, height)
        self.x = x
        self.y = y
        self.folder_lists = folder_lists
        self.replace_folders()

    def replace_folders(self):
        self.childs = []
        child_x = 0
        for i, child in enumerate(self.folder_lists.lists):
            self.add(child_x, 0, child)
            child_x += child.width + 1
            if child.focus:
                self.focus_w = child
                self.focus_idx = i

    def handle_mouse(self, x, y):
        pass

    def handle_key(self, key):
        if key == KEY_QUIT:
            return key
        if key == KEY_ESC and self.finish_on_esc:
            return ACTION_CANCEL
        if key == KEY_RIGHT:
            if self.focus_idx == len(self.folder_lists.lists) - 1:
                if self.folder_lists.try_go_in(self.focus_idx):
                    self.replace_folders()
                    self.redraw()
                    self.move_focus(1)
            else:
                self.move_focus(1)
        elif key == KEY_LEFT:
            if self.focus_w.index != 0:
                self.move_focus(-1)
        elif self.focus_w:
            if key == KEY_ENTER:
                self.folder_lists.memorize_choice_in_list(self.focus_idx)
                return ACTION_OK

            choice_before = self.focus_w.choice
            res = self.focus_w.handle_key(key)
            choice_after = self.focus_w.choice

            if choice_before != choice_after:
                self.folder_lists.activate_sibling(self.focus_idx)
                self.replace_folders()
                self.redraw()

            if res == ACTION_PREV:
                self.move_focus(-1)
            elif res == ACTION_NEXT:
                self.move_focus(1)
            else:
                return res

    def clear(self):
        screen.clear_box(self.x, self.y, self.w, self.h)

    def redraw(self):
        # Init some state on first redraw
        if self.focus_idx == -1:
            self.autosize()
            self.focus_idx, self.focus_w = self.find_focusable_by_idx(0, 1)
            if self.focus_w:
                self.focus_w.focus = True

        self.clear()
        for w in self.childs:
            w.redraw()

    def path(self):
        return self.folder_lists.child_path(self.focus_idx)


def run(folder_lists):
    v = None
    try:
        cursor_position_save()
        Screen.init_tty()
        Screen.cursor(False)

        screen_width, screen_height = Screen.screen_size()
        cursor_y, cursor_x = cursor_position()

        v = ChangeFoldersDialog(screen_width, HEIGHT, 0, cursor_y, folder_lists)
        if v.loop() == ACTION_OK:
            return v.path()
        else:
            return None
    finally:
        Screen.attr_reset()
        if v is not None:
            v.clear()

        Screen.cursor(True)
        Screen.deinit_tty()
        cursor_position_restore()


def load_history():
    try:
        with open(history_file()) as json_file:
            return json.load(json_file)
    except:
        return {}


def save_history(history):
    try:
        with open(history_file(), 'w') as f:
            json.dump(history, f, indent=2, sort_keys=True)
    except Exception as e:
        pass


def history_file():
    return os.getenv("HOME") + "/.fndr_history"


def find_root_for(folder, roots):
    path = folder
    while True:
        if path in roots:
            return str(path)
        if path == '/' or path == '' or path.startswith('.'):
            return folder
        i = path.rfind('/')
        path = path[:i]


if __name__ == "__main__":
    history = load_history()
    folder = os.getenv('PWD')
    root = find_root_for(folder, history)
    root_history = history[root] if root in history else {}

    folder_lists = FolderLists(folder, root, root_history)
    if folder_lists.is_empty():
        sys.exit(2)

    r = run(folder_lists)

    save_history(history)
    if r is None:
        sys.exit(1)
    print(r)
