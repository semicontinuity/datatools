from datatools.jt.ui.ng.cell_renderer_indicator import WIndicatorCellRenderer


def collapsed_columns(column_count: int, column_cell_renderer_f):
    collapsed = {}
    for i in range(column_count):
        r = column_cell_renderer_f(i).delegate()
        collapsed[r.render_data.column_key] = type(r) == WIndicatorCellRenderer
    return collapsed


def filter_non_collapsed(r: dict, collapsed: dict[str, bool]):
    return {k: v for k, v in r.items() if not collapsed.get(k)}
