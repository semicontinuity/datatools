#!/usr/bin/env python3
# ──────────────────────────────────────────────────────────────────────────────
# A tool for interactive selection of a row from TextUI-style table.
#
# arguments:
# [-s]: streaming model
# [-t title]: title
# [json]: json with stripe colors specification
# like '{"column name":{"0":"ff0000", "1":"00ff00", "2":"8080ff"}}'
# corresponding data must look like "stripes": ["2","1","0","2"]
#
#
# STDIN: data as sequence of one-line jsons like {"field1":"value1", ... }
# result (json, corresponding to selected line) is printed to to STDOUT,
# if user has selected a row, or nothing, if user has cancelled selection.
#
# To paint UI and read keyboard, uses STDERR.
#
# Exit code corresponds to key code + sum of modifiers codes.
# ──────────────────────────────────────────────────────────────────────────────
import json

from datatools.jt.app.app_kit import Applet, app_kit_main
from datatools.jt.app.classic.jt_classic_grid_factory import grid
from datatools.jt.model.data_bundle import STATE_CUR_LINE
from datatools.jt.model.exit_codes import EXIT_CODE_MAX_REGULAR, exit_code_key_has_modifier, EXIT_CODE_SHIFT, \
    EXIT_CODE_ESCAPE


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def app_router(app, exit_code):
    if exit_code <= EXIT_CODE_MAX_REGULAR:
        if exit_code_key_has_modifier(exit_code, EXIT_CODE_SHIFT):
            print(json.dumps(app.data_bundle.orig_data))
            return None

    if exit_code != EXIT_CODE_ESCAPE:
        print(json.dumps(app.data_bundle.orig_data[app.data_bundle.state[STATE_CUR_LINE]]))

    return None


if __name__ == "__main__":
    app_kit_main('jt', Applet, grid, app_router)
