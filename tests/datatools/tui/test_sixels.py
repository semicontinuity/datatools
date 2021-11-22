import os

from datatools.tui.sixel import *

SIZE = 40
os.write(2, b'_' * SIZE)
os.write(2, b'\n')

os.write(2, b'\x1b[s')          # save cursor
os.write(2, b'  \xE2\x96\x8F ') # mark
os.write(2, b'\x1b[u')          # restore cursor

# No transparency...
cmd = bytearray()
sixel_append_start_cmd(cmd)
sixel_append_set_color_register_cmd(cmd, 7000000, 0, 99, 0)
sixel_append_use_color(cmd, 7000000)
sixel_append_repeated(cmd, 10 * SIZE, 0b111100)
sixel_append_stop_cmd(cmd)
os.write(2, cmd)

os.write(2, b'\n####\n')
