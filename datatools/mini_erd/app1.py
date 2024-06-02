#!/usr/bin/env python3

from datatools.mini_erd.ui_toolkit import UiToolkit
from datatools.tui.buffer.json2ansi_buffer import Buffer
from datatools.tui.terminal import screen_size_or_default


def main():
    root = ui(UiToolkit())
    root.compute_width()
    root.compute_height()
    root.compute_position(0, 0)

    buffer = Buffer(root.width, root.height)
    root.paint(buffer)

    screen_size = screen_size_or_default()
    buffer.flush(*screen_size)


def ui(tk):
    return tk.hbox(
        [
            tk.vbox(
                [
                    tk.header_node("left"),
                    tk.spacer(),
                    tk.header_node("left2"),
                ]
            ),

            tk.spacer(),
            tk.header_node("center"),
            tk.spacer(),

            tk.vbox(
                [
                    tk.header_node("right"),
                    tk.spacer(),
                    tk.header_node("right2"),
                    tk.spacer(),
                    tk.header_node("right3"),
                ]
            )
        ]
    )


if __name__ == "__main__":
    main()
