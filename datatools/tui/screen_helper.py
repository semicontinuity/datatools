from picotui.screen import Screen

from datatools.tui.picotui_patch import patch_picotui
from datatools.tui.picotui_util import cursor_position_save, screen_alt, with_prepared_screen, screen_regular, \
    cursor_position_restore
from datatools.tui.tui_fd import infer_fd_tui


def with_alternate_screen(delegate):
    fd_tui = infer_fd_tui()
    patch_picotui(fd_tui, fd_tui)

    try:
        cursor_position_save()
        Screen.init_tty()
        screen_alt()
        return with_prepared_screen(delegate)
    finally:
        screen_regular()
        Screen.deinit_tty()
        cursor_position_restore()
