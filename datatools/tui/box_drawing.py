from picotui.screen import Screen

from datatools.tui.box_drawing_chars import *


def draw_grid(left, top, w, h, top_kind, bottom_kind, left_kind, right_kind, h_stops, v_stops):
    def draw_line(v_pos, y, current_h_kind):
        Screen.goto(left, y)
        h_stop = 0

        border_chars = CHARS[current_h_kind]
        Screen.wr(CHARS[2 * left_kind + current_h_kind][4 * v_pos + P_FIRST])
        x = left + 1
        while True:
            next_h_stop = (w - 1, right_kind) if h_stop >= len(h_stops) else h_stops[h_stop]
            next_x = left + next_h_stop[0]
            Screen.wr(border_chars[4 * v_pos + P_NONE] * (next_x - x))
            x = next_x
            if h_stop >= len(h_stops):
                break
            else:
                next_h_stop_v_kind = next_h_stop[1]
                Screen.wr(CHARS[2 * next_h_stop_v_kind + current_h_kind][4 * v_pos + P_STOP])
                x = x + 1
                h_stop = h_stop + 1
        Screen.wr(CHARS[2 * right_kind + current_h_kind][4 * v_pos + P_LAST])

    def draw_middle():
        y = top + 1
        v_stop = 0
        while True:
            next_v_stop = (h - 1, bottom_kind) if v_stop >= len(v_stops) else v_stops[v_stop]
            next_y = top + next_v_stop[0]

            while y < next_y:
                draw_line(P_NONE, y, 0)
                y = y + 1

            if v_stop >= len(v_stops):
                break
            else:
                next_v_stop_h_kind = next_v_stop[1]
                draw_line(P_STOP, y, next_v_stop_h_kind)
                y = y + 1
                v_stop = v_stop + 1

    draw_line(P_FIRST, top, top_kind)
    draw_middle()
    draw_line(P_LAST, top + h - 1, bottom_kind)
