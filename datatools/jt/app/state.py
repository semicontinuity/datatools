from datatools.jt.model.data_bundle import STATE_TOP_LINE, STATE_CUR_LINE


def default_state():
    return {STATE_TOP_LINE: 0, STATE_CUR_LINE: 0}


def init_from_state(g, state):
    top_line = state.get(STATE_TOP_LINE) or 0
    if 0 <= top_line < g.total_lines:
        g.top_line = top_line
    cur_line = state.get(STATE_CUR_LINE) or 0
    if top_line <= cur_line < g.total_lines:
        g.cur_line = cur_line