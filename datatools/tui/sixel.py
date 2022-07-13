# SIXEL primitives
# https://vt100.net/docs/vt3xx-gp/chapter14.html

# ======================================================
# Few terminals support SIXEL,
# and not all terminals support SIXEL well.
# E.g. dev version of Gnome Terminal
# does not ensure, that every character is 10x20 sixels,
# and actual appearance depends on the font used.
# Known "good" font: Noto Mono 12
# ======================================================

from datatools.tui.terminal import TCAP_SIXEL, read_tcaps


def sixel_supported() -> bool:
    return TCAP_SIXEL in read_tcaps()[1]


def sixel_append_start_cmd(buffer: bytearray, p1=0, p2=0, p3=0):
    # DCS P1 ; P2; P3; q: P2=0 or 2 (default): 0 will be painted with the currently set BG color; 1: transparency
    buffer.append(0x1b)
    buffer.append(0x50)  # 'P'
    sixel_append_number(buffer, p1)
    buffer.append(0x3B)  # ';'
    sixel_append_number(buffer, p2)
    buffer.append(0x3B)  # ';'
    sixel_append_number(buffer, p3)
    buffer.append(0x3B)  # ';'
    buffer.append(0x71)  # 'q'


def sixel_append_stop_cmd(buffer: bytearray):
    buffer.append(0x1b)
    buffer.append(0x5c)  # '\'


def sixel_append_number(buffer: bytearray, n: int):
    buffer += bytes(str(n), 'ascii')


def sixel_append_set_color_register_cmd(buffer: bytearray, register: int, r: int, g: int, b: int):
    """ r,g,b values must be in the range 0-99 (%) """
    buffer.append(0x23)  # '#'
    sixel_append_number(buffer, register)
    buffer.append(0x3B)  # ';'
    buffer.append(0x32)  # '2'
    buffer.append(0x3B)  # ';'
    sixel_append_number(buffer, r)
    buffer.append(0x3B)  # ';'
    sixel_append_number(buffer, g)
    buffer.append(0x3B)  # ';'
    sixel_append_number(buffer, b)


def sixel_append_use_color(buffer: bytearray, color_reg: int):
    buffer.append(0x23)   # '#'
    sixel_append_number(buffer, color_reg)


def sixel_append_bits(buffer: bytearray, bits: int):
    buffer.append(63 + bits)


def sixel_append_encoded(buffer: bytearray, data: bytes):
    buffer += data


def sixel_append_repeated(buffer: bytearray, count: int, bits: int):
    if count == 1:
        buffer.append(63 + bits)
    elif count == 2:
        buffer.append(63 + bits)
        buffer.append(63 + bits)
    else:
        buffer.append(0x21)   # '#'
        sixel_append_number(buffer, count)
        buffer.append(63 + bits)


def sixel_append_cr(buffer: bytearray):
    buffer.append(0x24)   # '$'


def sixel_append_lf(buffer: bytearray):
    buffer.append(0x2D)   # '-'


# example usage:
#
# import os
# cmd = bytearray()
# sixel_append_start_cmd(cmd)
# sixel_append_set_color_register_cmd(cmd, 1, 99, 0, 0)
# sixel_append_set_color_register_cmd(cmd, 7000000, 0, 99, 0)
# sixel_append_set_color_register_cmd(cmd, 1255, 0, 0, 99)
#
# sixel_append_use_color(cmd, 1)
# sixel_append_repeated(cmd, 100, 60)
# sixel_append_lf(cmd)
#
# sixel_append_use_color(cmd, 7000000)
# sixel_append_repeated(cmd, 100, 63)
# sixel_append_lf(cmd)
#
# sixel_append_use_color(cmd, 1255)
# sixel_append_repeated(cmd, 100, 63)
# sixel_append_stop_cmd(cmd)
# sixel_append_start_cmd(cmd)
#
# os.write(2, cmd)
# os.write(2, b'$$$')