ANSI_CMD_ATTR_RESET = '\x1b[0;22m'


def ansi_cmd_set_fg(fg: int):
    if fg > 8:
        return '\x1b[1;%dm' % (fg + 30 - 8)
    else:
        return '\x1b[%dm' % (fg + 30)
