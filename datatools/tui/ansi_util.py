def ansi_foreground_escape_code(r, g, b):
    return "\x1b[38;2;" + str(r) + ';' + str(g) + ';' + str(b) + 'm'


def ansi_background_escape_code(r, g, b):
    return "\x1b[48;2;" + str(r) + ';' + str(g) + ';' + str(b) + 'm'
