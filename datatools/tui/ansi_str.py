SINGLE_UNDERLINE = '\x1b[4m'
DOUBLE_UNDERLINE = '\x1b[21m'

ANSI_CMD_DEFAULT_FG = '\x1b[39m'
ANSI_CMD_DEFAULT_BG = '\x1b[49m'

ANSI_CMD_ATTR_BOLD = '\x1b[1m'
ANSI_CMD_ATTR_NOT_BOLD = '\x1b[22m'

ANSI_CMD_ATTR_RESET = '\x1b[0;22m'

ANSI_CMD_ATTR_INVERTED = '\x1b[7m'
ANSI_CMD_ATTR_NOT_INVERTED = '\x1b[27m'


def ansi_cmd_set_fg(fg: int) -> str:
    if fg > 8:
        return '\x1b[1;%dm' % (fg + 30 - 8)
    else:
        return '\x1b[%dm' % (fg + 30)


def ansi_cmd_set_bg(bg: int) -> str:
    return '\x1b[%dm' % (bg + 40)
