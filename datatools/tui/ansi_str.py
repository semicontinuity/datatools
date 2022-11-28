ANSI_CMD_ATTR_RESET = '\x1b[0m'


def ansi_cmd_set_fg(fg: int):
    return '\x1b[%dm' % (fg + 30)
