from typing import List


class MonoSixelBuffer:
    __width: int
    __height: int
    __stripes: List[bytearray]

    def __init__(self, width: int, height: int):
        self.__width = width
        self.__height = height
        self.__stripes = [bytearray(width) for _ in range((height + 5) // 6)]

    def to_bytes(self) -> bytes:
        s = bytearray()

        for stripe in self.__stripes:
            s.append(10)

        return s
