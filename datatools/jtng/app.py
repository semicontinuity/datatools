#!/usr/bin/env python3
from typing import List

from datatools.jt.app import App, main
from datatools.jt.auto_coloring import max_column_widths
from datatools.jt.cell_renderer import column_renderers
from datatools.jtng.grid import WGrid


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def grid(state, presentation, screen_size, orig_data, column_keys) -> WGrid:
    column_widths: List[int] = [max_column_widths[c] for c in column_keys]

    g = WGrid(
        screen_size[0], screen_size[1], column_widths, column_keys,
        column_renderers(column_keys, presentation["columns"]).__getitem__,
        lambda line, column: orig_data[line].get(column_keys[column])
    )
    g.total_lines = len(orig_data)

    top_line = state["top_line"]
    if 0 <= top_line < g.total_lines:
        g.top_line = top_line

    cur_line = state["cur_line"]
    if top_line <= cur_line < g.total_lines:
        g.cur_line = cur_line

    return g


if __name__ == "__main__":
    main(grid, App)
