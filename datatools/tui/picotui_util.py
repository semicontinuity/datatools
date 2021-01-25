from picotui.screen import Screen


def screen_alt():
    Screen.wr(b"\x1b[?47h")


def screen_regular():
    Screen.wr(b"\x1b[?47l")


def cursor_position_save():
    Screen.wr(b"\x1b7")


def cursor_position_restore():
    Screen.wr(b"\x1b8")


def cursor_up(n):
    cursor_move(b'A', n)


def cursor_down(n):
    cursor_move(b'B', n)


def cursor_forward(n):
    cursor_move(b'C', n)


def cursor_backward(n):
    cursor_move(b'D', n)


def cursor_move(where, n):
    Screen.wr(b"\x1b[" + bytes(n) + where)


def scroll_region(top_row: int, bottom_row: int):
    Screen.wr(bytes(f"\x1b[{top_row + 1};{bottom_row + 1}r", 'utf-8'))


def scroll_up():
    Screen.wr(b"\x1b[1S")


def scroll_down():
    Screen.wr(b"\x1b[1T")


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
