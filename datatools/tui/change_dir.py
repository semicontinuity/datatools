from typing import Optional, List

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


def debug_print(*s):
    screen.clear_box(0, 0, 200, 1)
    Screen.goto(0, 0)
    print(*s, file=sys.stderr)


class FolderLists:
    def __init__(self, folder, root, root_history):
        self.root = root
        self.root_history = root_history
        self.visit_history = {}
        self.lists = self.initial_lists(folder)
        self.expand_lists()

    def initial_lists(self, folder) -> List[WListBox]:
        path = folder
        lists = []
        first = True
        while True:
            a_list = self.make_list(path, 0)
            if a_list is not None:  # the deepest folder will not necessarily contain sub-folders
                a_list.folder = path

                lists.append(a_list)
                if first:
                    a_list.focus = True
                    first = False

            offset = path.rfind('/')
            name = path[offset + 1:]
            if a_list is not None:
                a_list.name = name

            if path == self.root:
                break
            path = path[:offset]

        lists = list(reversed(lists))

        for index, l in enumerate(lists):
            l.index = index
            if index == len(lists) - 1:
                chosen_name = self.recall_chosen_name(l.folder)
                l.cur_line = l.choice = self.index_of(chosen_name, l.items) or 0
            else:
                index__name = lists[index + 1].name
                l.cur_line = l.choice = self.index_of(index__name, l.items) or 0

        return lists

    def expand_lists(self):
        index = len(self.lists) - 1
        while True:
            path = self.node_path(index)
            name = self.recall_chosen_name(path)
            if name is None:
                break
            index += 1
            a_list = self.make_list(path, index)
            if a_list is None or a_list.choice is None:
                break
            self.lists.append(a_list)

    def is_empty(self):
        return len(self.lists) == 0

    def lists_in_path(self, index):
        return self.lists[: index + 1]

    def parent_path(self, index):
        return self.root if index == 0 else self.node_path(index - 1)

    def node_path(self, index):
        root = self.root + '/' if self.root != '/' else '/'
        return root + '/' + '/'.join([l.content[l.choice] for l in self.lists_in_path(index)])

    def activate_sibling(self, index):
        self.lists = self.lists[: index + 1]
        self.expand_lists()

    def try_go_in(self, index):
        if index != len(self.lists) - 1:
            return

        self.memorize_choice_in_list(self.visit_history, index)

        new_list = self.make_list(self.node_path(index), index + 1)
        if new_list is None:
            return
        if new_list.choice is None:
            new_list.choice = 0

        self.lists.append(new_list)
        return True

    def make_list(self, folder, index: int) -> Optional[WListBox]:
        contents = [name for name in sorted(os.listdir(folder)) if
                    os.path.isdir(folder + '/' + name) and not name.startswith('.')]
        if len(contents) == 0:
            return None
        box = WListBox(max(len(s) for s in contents), len(contents), contents)
        box.index = index
        box.folder = folder
        choice = self.recall_choice(folder, contents)
        box.cur_line = box.choice = 0 if choice is None else choice
        return box

    def recall_choice(self, folder, contents):
        return self.recall_choice_in(self.root_history, folder, contents) or self.recall_choice_in(self.visit_history, folder, contents)

    def recall_choice_in(self, storage, folder, contents):
        if folder in storage:
            last_name = storage[folder]
            if last_name is not None:
                return self.index_of(last_name, contents)

    def index_of(self, chosen_name, contents):
        for i, name in enumerate(contents):
            if chosen_name == name:
                return i

    def recall_chosen_name(self, folder):
        return self.root_history.get(folder) or self.visit_history.get(folder)

    def memorize_choice_in_list(self, storage, index):
        if index < 0:
            return
        node_path = self.parent_path(index)
        folder_name = self.lists[index].content[self.lists[index].choice]
        self.memorize_in(storage, node_path, folder_name)

    def memorize_in(self, storage, folder, name):
        storage[folder] = name

    def index_of_last(self):
        return len(self.lists) - 1


class ChangeFoldersDialog(Dialog):
    def __init__(self, screen_height, width, height, x, y, folder_lists: FolderLists):
        super().__init__(0, 0, width, height)
        self.screen_height = screen_height
        self.x = x
        self.y = y
        self.folder_lists = folder_lists
        self.replace_folders()

    def request_height(self, h):
        self.h = min(h, self.screen_height)
        overshoot = max(self.y + self.h - self.screen_height, 0)

        if overshoot > 0:
            Screen.goto(0, self.screen_height - 1)
            for _ in range(overshoot):
                Screen.wr('\r\n')
            self.y -= overshoot
            self.replace_folders()

    def replace_folders(self):
        self.clear()    # sometimes causes blinking; better to clear only bottom part of the view that won't be used
        self.childs = []
        child_x = 0
        max_child_h = max(len(child.items) for child in self.folder_lists.lists)
        self.request_height(max_child_h)

        for i, child in enumerate(self.folder_lists.lists):
            child.h = child.height = min(child.height, self.h)
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
        elif key == KEY_HOME:
            self.focus_idx = 0
            self.change_focus(self.folder_lists.lists[self.focus_idx])
        elif key == KEY_END:
            self.focus_idx = self.folder_lists.index_of_last()
            self.change_focus(self.folder_lists.lists[self.focus_idx])
        elif self.focus_w:
            if key == KEY_SHIFT_TAB:
                self.focus_idx = -1
                return ACTION_OK
            if key == KEY_TAB:
                self.focus_idx = self.folder_lists.index_of_last()
            if key == KEY_ENTER or key == KEY_TAB:
                for i in range(0, self.focus_idx + 1):
                    self.folder_lists.memorize_choice_in_list(self.folder_lists.root_history, i)
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
        return self.folder_lists.root if self.focus_idx < 0 else self.folder_lists.node_path(self.focus_idx)


def run(folder_lists):
    v = None
    try:
        Screen.init_tty()
        Screen.cursor(False)

        screen_width, screen_height = Screen.screen_size()
        cursor_y, cursor_x = cursor_position()

        v = ChangeFoldersDialog(screen_height, screen_width, 0, 0, cursor_y, folder_lists)
        if v.loop() == ACTION_OK:
            return v.path()
        else:
            return None
    finally:
        Screen.attr_reset()
        if v is not None:
            v.clear()
            Screen.goto(0, v.y)

        Screen.cursor(True)
        Screen.deinit_tty()


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
