#!/usr/bin/env python3

from datatools.json.json2ansi_toolkit import *
from datatools.json.structure_discovery import *


def main():
    import json, sys

    # j = json.load(sys.stdin)
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    j = json.loads(s)

    page_node = AnsiToolkit(Discovery()).page_node(j)


    screen_size = (1000, 10000)
    if sys.stderr.isatty():
        init_tty()
        screen_size = read_screen_size()[0], 10000
        deinit_tty()

    screen_buffer = page_node.paint()
    screen_buffer.flush(*screen_size)

    # from datatools.json.util import to_jsonisable
    # print(json.dumps(to_jsonisable(page_node.root)))


FD_IN = 2
FD_OUT = 2

def read_screen_size():
    import select, os
    os.write(FD_OUT, b"\x1b[18t")
    res = select.select([FD_IN], [], [], 0.05)[0]
    resp = os.read(FD_IN, 32)
    assert resp.startswith(b"\x1b[8;") and resp[-1:] == b"t"
    vals = resp[:-1].split(b";")
    return (int(vals[2]), int(vals[1]))

def init_tty():
    import tty, termios
    global ttyattr
    ttyattr = termios.tcgetattr(FD_IN)
    tty.setraw(FD_IN)

def deinit_tty():
    import termios
    termios.tcsetattr(FD_IN, termios.TCSANOW, ttyattr)

if __name__ == "__main__":
    # try:
        main()
    # except JSONDecodeError as ex:
    #     stderr_print("Reads json. Outputs html.")
