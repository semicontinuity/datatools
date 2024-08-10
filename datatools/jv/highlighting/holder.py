from typing import Optional

CURRENT_HIGHLIGHTING: Optional['Highlighting'] = None


def get_current_highlighting() -> 'Highlighting':
    return CURRENT_HIGHLIGHTING


def set_current_highlighting(h: 'Highlighting'):
    global CURRENT_HIGHLIGHTING
    CURRENT_HIGHLIGHTING = h
