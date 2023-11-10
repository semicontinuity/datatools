from typing import List

FULL_BLOCK = "█"
FULL_BLOCK_BYTES = b'\xE2\x96\x88'
LEFT_BORDER = '▏'
LEFT_BORDER_BYTES = b'\xE2\x96\x8F'
LEFT_THICK_BORDER = '▎'
LEFT_THICK_BORDER_BYTES = b'\xE2\x96\x8E'

KIND_SINGLE = 0
KIND_DOUBLE = 1

H_SINGLE = b'\xe2\x94\x80'
H_DOUBLE = b'\xe2\x95\x90'
V_SINGLE = b'\xe2\x94\x82'
V_DOUBLE = b'\xe2\x95\x91'

V_DOUBLE_H_DOUBLE = [
    b'\xe2\x95\x94', H_DOUBLE, b'\xe2\x95\xa6', b'\xe2\x95\x97',
    V_DOUBLE, b' ', V_DOUBLE, V_DOUBLE,
    b'\xe2\x95\xa0', H_DOUBLE, b'\xe2\x95\xac', b'\xe2\x95\xa3',
    b'\xe2\x95\x9a', H_DOUBLE, b'\xe2\x95\xa9', b'\xe2\x95\x9d'
]
V_DOUBLE_H_SINGLE = [
    b'\xe2\x95\x93', H_SINGLE, b'\xe2\x95\xa5', b'\xe2\x95\xa6',
    V_DOUBLE, b' ', V_DOUBLE, V_DOUBLE,
    b'\xe2\x95\x9f', H_SINGLE, b'\xe2\x95\xab', b'\xe2\x95\xa2',
    b'\xe2\x95\x99', H_SINGLE, b'\xe2\x95\xa8', b'\xe2\x95\x9c'
]
V_SINGLE_H_DOUBLE = [
    b'\xe2\x95\x92', H_DOUBLE, b'\xe2\x95\xa4', b'\xe2\x95\x95',
    V_SINGLE, b' ', V_SINGLE, V_SINGLE,
    b'\xe2\x95\x9e', H_DOUBLE, b'\xe2\x95\xaa', b'\xe2\x95\xa1',
    b'\xe2\x95\x98', H_DOUBLE, b'\xe2\x95\xa7', b'\xe2\x95\x9b'
]
V_SINGLE_H_SINGLE = [
    b'\xe2\x94\x8c', H_SINGLE, b'\xe2\x94\xac', b'\xe2\x94\x90',
    V_SINGLE, b' ', V_SINGLE, V_SINGLE,
    b'\xe2\x94\x9c', H_SINGLE, b'\xe2\x94\xbc', b'\xe2\x94\xa4',
    b'\xe2\x94\x94', H_SINGLE, b'\xe2\x94\xb4', b'\xe2\x94\x98'
]

# for every sub-array: [vertical position * 4 + horizontal position]
# contains duplicates, but easily addressable
CHARS = [
    V_SINGLE_H_SINGLE,
    V_SINGLE_H_DOUBLE,
    V_DOUBLE_H_SINGLE,
    V_DOUBLE_H_DOUBLE
]


def box_drawing_chars(vertical_double: bool, horizontal_double: bool) -> List[bytes]:
    return CHARS[2 * int(vertical_double) + int(horizontal_double)]


P_FIRST = 0
P_NONE = 1
P_STOP = 2
P_LAST = 3


def box_drawing_bytes(chars: List[bytes], vertical_stop: int, horizontal_stop: int) -> bytes:
    return chars[4 * vertical_stop + horizontal_stop]
