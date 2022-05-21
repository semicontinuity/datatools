
from enum import Enum

from datatools.jt.model.exit_codes_mapping import *


class ColorKey(Enum):
    BOX_DRAWING = 'BOX_DRAWING'
    TITLE = 'TITLE'
    COLUMN_TITLE = 'COLUMN_TITLE'
    CURSOR = 'CURSOR'
    TEXT = 'TEXT'
    DEF_BACKGROUND = 'DEF_BACKGROUND'
    EMP_BACKGROUND = 'EMP_BACKGROUND'


THEMES = {
    "mc": {
        ColorKey.BOX_DRAWING: [C_B_CYAN, C_BLUE],
        ColorKey.TITLE: [C_BLACK, C_CYAN],
        ColorKey.COLUMN_TITLE: [C_B_YELLOW, C_BLUE],
        ColorKey.CURSOR: [C_BLACK, C_CYAN],
        ColorKey.TEXT: [C_B_CYAN, C_BLUE]
    },
    "dark": {
        ColorKey.BOX_DRAWING: (64, 96, 96, 0x29, 0x0B, 0x2E),
        ColorKey.TITLE: (255, 255, 255, 24, 16, 23),
        ColorKey.COLUMN_TITLE: (255, 255, 0, 24, 16, 23),
        ColorKey.CURSOR: [C_BLACK, C_WHITE],
        ColorKey.TEXT: (255, 255, 255, 24, 16, 23)
    },
}

DARK = (8, 9, 9)
LIGHTER = (24, 26, 26)
FOOTER_BG = (40, 40, 40)

THEMES2 = {
    "mc": {
        ColorKey.BOX_DRAWING: [C_B_CYAN, C_BLUE],
        ColorKey.TITLE: [C_BLACK, C_CYAN],
        ColorKey.COLUMN_TITLE: [C_B_YELLOW, C_BLUE],
        ColorKey.CURSOR: [C_BLACK, C_CYAN],
        ColorKey.TEXT: [C_B_CYAN, C_BLUE]
    },
    "dark": {
        ColorKey.BOX_DRAWING: ((64, 96, 96), DARK),
        ColorKey.TITLE: ((255, 255, 255), DARK),
        ColorKey.COLUMN_TITLE: ((255, 255, 0), DARK),
        ColorKey.CURSOR: [C_BLACK, C_WHITE],
        ColorKey.TEXT: ((224, 240, 224), DARK)
    },
}

COLORS = THEMES["dark"]
COLORS2 = THEMES2["dark"]

COLORS3 = {
    ColorKey.BOX_DRAWING: (64, 96, 96),
    ColorKey.TEXT: (192, 192, 192),
    ColorKey.DEF_BACKGROUND: DARK,
    ColorKey.EMP_BACKGROUND: LIGHTER,
}
