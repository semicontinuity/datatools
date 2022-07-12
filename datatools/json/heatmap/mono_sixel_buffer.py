from typing import List
from datatools.tui.sixel import *


class MonoSixelBuffer:
    __width: int
    __height: int
    __sixels: List[bytearray]

    def __init__(self, width: int, height: int):
        self.__width = width
        self.__height = height
        self.__sixels = [bytearray(width) for _ in range((height + 5) // 6)]

    def to_bytes(self) -> bytes:
        buffer = bytearray()
        sixel_append_start_cmd(buffer)
        sixel_append_set_color_register_cmd(buffer, 0, 0, 99, 0)
        sixel_append_use_color(buffer, 0)

        for lane in self.__sixels:
            for sixel in lane:
                sixel_append_bits(buffer, sixel)
            sixel_append_lf(buffer)

        sixel_append_stop_cmd(buffer)
        return buffer

    def add_point(self, x: int, y: int):
        lane_idx = y // 6
        lane_bit = y % 6
        self.__sixels[lane_idx][x] |= (1 << lane_bit)
