import json
import os
import sys
from json import JSONDecodeError
from typing import Sequence, List

from datatools.tui.terminal import ansi_attr_bytes
from .mono_sixel_buffer import MonoSixelBuffer


# NB:
# Sixel painting is strange: if a lane of zero sixels is to be painted, default background is not applied!
# As a workaround, inverse picture is generated: most sixels are 1, and points set sixel to 0.
# It is also possible to paint in two passes: background first, then points - but it is actually more work.
def paint_points(points: List[Sequence[int]], width: int, height: int, x_min, y_min, x_max, y_max):
    x_unit = (x_max - x_min) / width
    y_unit = (y_max - y_min) / height

    sixel_buffer = MonoSixelBuffer(width, height)
    for x, y in points:
        image_x = int((x - x_min) / x_unit)
        image_y = int((y - y_min) / y_unit)
        sixel_buffer.add_point(image_x, image_y)

    os.write(1, ansi_attr_bytes(b'107'))  # bright white BG: color for points
    os.write(1, sixel_buffer.to_bytes())
    os.write(1, ansi_attr_bytes(b'0'))    # reset attrs


def load_points():
    data = sys.stdin.read()
    try:
        return json.loads(data)
    except JSONDecodeError as e:
        print("Cannot decode input JSON", file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit(0x3F)


def main():
    if len(sys.argv) < 7:
        print("Arguments: <width> <height> <x-left> <y-left> <x-right> <y-right>", file=sys.stderr)
        sys.exit(0x3F)

    width = int(sys.argv[1])
    height = int(sys.argv[2])

    x_left = int(sys.argv[3])
    y_left = int(sys.argv[4])
    x_right = int(sys.argv[5])
    y_right = int(sys.argv[6])

    paint_points(load_points(), width, height, x_left, y_left, x_right, y_right)


if __name__ == "__main__":
    main()
