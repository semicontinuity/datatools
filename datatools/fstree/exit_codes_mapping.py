#!/usr/bin/env python3

from picotui.defs import *

from datatools.tui.exit_codes_v2 import *
from datatools.tui.picotui_keys import *

KEYS_TO_EXIT_CODES = {
    KEY_ESC: EXIT_CODE_ESCAPE,
    KEY_ENTER: EXIT_CODE_ENTER,

    KEY_F1: EXIT_CODE_F1,
    KEY_F2: EXIT_CODE_F2,
    KEY_F3: EXIT_CODE_F3,
    KEY_F4: EXIT_CODE_F4,
    KEY_F5: EXIT_CODE_F5,
    KEY_F6: EXIT_CODE_F6,
    KEY_F7: EXIT_CODE_F7,
    KEY_F8: EXIT_CODE_F8,
    KEY_F9: EXIT_CODE_F9,
    KEY_F10: EXIT_CODE_F10,
    KEY_F11: EXIT_CODE_F11,
    KEY_F12: EXIT_CODE_F12,
}
