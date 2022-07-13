import json
import os
import sys
from json import JSONDecodeError
from typing import Sequence, List

from datatools.tui.terminal import ansi_attr_bytes
from .mono_sixel_buffer import MonoSixelBuffer


def paint_points(points: List[Sequence[int]], width: int, height: int):
    sixel_buffer = MonoSixelBuffer(width, height)
    for x, y in points:
        sixel_buffer.add_point(x, y)

    os.write(1, ansi_attr_bytes(b'40')) # black BG
    os.write(1, sixel_buffer.to_bytes())


def load_points():
    data = sys.stdin.read()
    try:
        return json.loads(data)
    except JSONDecodeError as e:
        print("Cannot decode input JSON", file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit(0x3F)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Arguments: <width> <height>", file=sys.stderr)
        sys.exit(0x3F)
    width = int(sys.argv[1])
    height = int(sys.argv[2])
    paint_points(load_points(), width, height)
