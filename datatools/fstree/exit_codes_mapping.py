#!/usr/bin/env python3

from picotui.defs import *

from datatools.tui.exit_codes_v2 import EXIT_CODE_ESCAPE, EXIT_CODE_ENTER

KEYS_TO_EXIT_CODES = {
    KEY_ESC: EXIT_CODE_ESCAPE,
    KEY_ENTER: EXIT_CODE_ENTER,
}
