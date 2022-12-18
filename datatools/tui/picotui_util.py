from picotui.screen import Screen


def screen_alt():
    Screen.wr(b"\x1b[?47h")


def screen_regular():
    Screen.wr(b"\x1b[?47l")


def cursor_position_save():
    Screen.wr(b"\x1b7")


def cursor_position_restore():
    Screen.wr(b"\x1b8")


def cursor_position_set(p):
    y = p[0]
    x = p[1]
    Screen.wr(b"\x1b[%d;%dH" % (y + 1, x + 1))


def cursor_up(n):
    Screen.wr(cursor_up_cmd(n))


def cursor_up_cmd(n):
    return cursor_move_cmd(b'A', n)


def cursor_down(n):
    Screen.wr(cursor_down_cmd(n))


def cursor_down_cmd(n):
    return cursor_move_cmd(b'B', n)


def cursor_forward(n):
    Screen.wr(cursor_forward_cmd(n))


def cursor_forward_cmd(n):
    return cursor_move_cmd(b'C', n)


def cursor_backward(n):
    Screen.wr(cursor_backward_cmd(n))


def cursor_backward_cmd(n):
    return cursor_move_cmd(b'D', n)


def cursor_move_cmd(where, n):
    return b"\x1b[%d%s" % (n, where)


def scroll_region(top_row: int, bottom_row: int):
    Screen.wr(bytes(f"\x1b[{top_row + 1};{bottom_row + 1}r", 'utf-8'))


def scroll_up():
    Screen.wr(b"\x1b[1S")


def scroll_down():
    Screen.wr(b"\x1b[1T")


def with_raw_term(alt_screen: bool, f):
    try:
        cursor_position_save()
        Screen.init_tty()
        if alt_screen:
            screen_alt()
        return f()
    finally:
        if alt_screen:
            screen_regular()
        Screen.deinit_tty()
        cursor_position_restore()


def with_alt_screen(f):
    try:
        cursor_position_save()
        screen_alt()
        # Screen.init_tty()

        Screen.cls()
        Screen.attr_reset()
        Screen.cursor(False)

        f()
    finally:
        Screen.attr_reset()
        Screen.cls()
        Screen.goto(0, 0)
        Screen.cursor(True)

        # Screen.deinit_tty()
        screen_regular()
        cursor_position_restore()


def with_prepared_screen(delegate, alt_screen=True):
    try:
        screen_prepare(alt_screen)
        return delegate()
    finally:
        screen_unprepare(alt_screen)


def screen_prepare(alt_screen: bool, cls: bool = True):
    import os
    DEVEL = int(os.environ.get("DEVEL", "0"))
    # cursor_position_save()
    # if not DEVEL:
    #     Screen.init_tty()
    Screen.cursor(False)
    if cls:
        Screen.cls()
    Screen.attr_reset()


def screen_unprepare(alt_screen: bool, cls: bool = True):
    import os
    DEVEL = int(os.environ.get("DEVEL", "0"))
    Screen.attr_reset()
    if cls:
        Screen.cls()
    Screen.goto(0, 0)
    Screen.cursor(True)
    # if not DEVEL:
    #     Screen.deinit_tty()
    # cursor_position_restore()
