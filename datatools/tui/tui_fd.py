from datatools.util.fd import fd_exists

FD_TUI_DEDICATED = 103
FD_TUI_IN = 2
FD_TUI_OUT = 2


def infer_fd_tui():
    return FD_TUI_DEDICATED if fd_exists(FD_TUI_DEDICATED) else FD_TUI_OUT
