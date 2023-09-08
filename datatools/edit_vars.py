#!/usr/bin/env python3

# Arguments: list of parameters to fill
# Or, if empty - load json from STDIN (format: {"k":"v",...})
#
# Output:
#
# filled parameters in format
# PARAM="value"
#
# or json, if environment variable OF set to "json"


import json
import os
import sys

from picotui.dialogs import *

from datatools.tui.picotui_patch import patch_picotui

patch_picotui()
from datatools.tui.picotui_util import *


class MyContext:
    def __init__(self, cls=True, mouse=True):
        self.cls = cls
        self.mouse = mouse

    def __enter__(self):
        cursor_position_save()
        screen_alt()
        Screen.init_tty()
        if self.mouse:
            Screen.enable_mouse()
        if self.cls:
            Screen.cls()
        Screen.attr_reset()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.mouse:
            Screen.disable_mouse()
        Screen.cursor(True)
        Screen.attr_reset()
        Screen.cls()
        Screen.goto(0, 0)
        Screen.deinit_tty()
        screen_regular()
        cursor_position_restore()


def add_ok_cancel_buttons(d):
    if d.h == 0:
        d.autosize(0, 1)
    if d.w < 20:
        d.w = 20
    hw = d.w // 2
    off1 = (hw + 1) // 2 - 4
    off2 = (d.w - hw) + hw // 2 - 4
    b = WButton(8, "OK")
    d.add(off1, d.h - 1, b)
    b.finish_dialog = ACTION_OK

    b = WButton(8, "Cancel")
    d.add(off2, d.h - 1, b)
    b.finish_dialog = ACTION_CANCEL


def fill(vars):
    with MyContext():
        d = Dialog(10, 5, title="Please fill")
        longest = max((len(p) for p in vars))
        entries = {}
        for i, param in enumerate(vars):
            d.add(2, i + 1, param)
            value = vars.get(param)
            entry = WTextEntry(50, var_repr(value) or "")
            entry.finish_dialog = ACTION_OK
            d.add(x=longest + 3, y=i + 1, widget=entry)
            entries[param] = entry

        add_ok_cancel_buttons(d)
        res = d.loop()
        if res == ACTION_CANCEL:
            return None
        else:
            return {key: entry.get_cur_line() for key, entry in entries.items()}


def main(variables):
    filled = fill(variables)

    if not filled:
        sys.exit(1)

    output(filled, variables)


def output(filled, params):
    if os.environ.get("OF") == "json":
        json.dump(adjust_types(filled, params), sys.stdout)
    else:
        for k, v in filled.items():
            print(f'{k}="{v}"')


def adjust_types(filled, original):
    return {k: adjust_type(filled.get(k), original.get(k)) for k in filled}


def adjust_type(filled, original):
    if type(original) == int:
        return int(filled)
    elif type(original) == float:
        return float(filled)
    elif type(original) == bool:
        return bool(filled)
    else:
        return filled


def var_repr(value):
    if type(value) == str:
        return value
    else:
        return json.dumps(value)


def variables(argv):
    params = argv[1:]
    if len(params) == 0:
        return json.load(sys.stdin)
    else:
        # plain list of variables in argv
        return {k: "" if os.environ.get(k) is None else os.environ.get(k) for k in params}


if __name__ == "__main__":
    main(variables(sys.argv))
