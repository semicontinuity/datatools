from collections import defaultdict
from typing import Sequence, Dict, List

from datatools.tui.coloring import hash_code, hash_to_rgb, decode_rgb
from datatools.tui.jt.themes import COLORS, ColorKey, COLORING_NONE, COLORING_HASH_FREQUENT, COLORING_HASH_ALL
from datatools.tui.terminal import ansi_foreground_escape_code, \
    set_colors_cmd_bytes
from dataclasses import dataclass
from math import sqrt


@dataclass
class ColumnAttrs:
    value_stats: Dict[str, int]
    non_uniques_count: int = 0


column_attrs = defaultdict(lambda: ColumnAttrs(defaultdict(int)))
column_is_complex = defaultdict(bool)
max_column_widths: Dict[str, int] = defaultdict(int)
unique_column_values = defaultdict(set)


# TODO: if some column is not present for some rows, it should be included with smaller priority (after other columns)
def pick_displayed_columns(screen_width) -> List[str]:
    """ Pick columns until they fit screen """
    result = []
    screen_width -= 1

    # simple columns first
    for k, v in max_column_widths.items():
        if 0 < v <= screen_width - 1 and not column_is_complex[k]:
            result.append(k)
            screen_width -= (v + 1)

    # complex columns second
    for k, v in max_column_widths.items():
        if 0 < v <= screen_width - 1 and column_is_complex[k]:
            result.append(k)
            screen_width -= (v + 1)

    return result


def analyze_data(data, params):
    for record in data:
        for key in record.keys():
            value = record[key]
            value_as_string = str(value)

            column_attr = column_attrs[key]
            if type(value) is dict or type(value) is list:
                column_is_complex[key] = True
            else:
                column_attr.value_stats[value_as_string] = column_attr.value_stats.get(value_as_string, 0) + 1

            cell_length = len(value) if key in params.columns else len(value_as_string)
            max_column_widths[key] = max(max_column_widths[key], cell_length)
            unique_column_values[key].add(value_as_string)

    for key, column_attr in column_attrs.items():
        for word, count in column_attr.value_stats.items():
            if count > 1:
                column_attr.non_uniques_count += 1


def compute_column_colorings(orig_data, column_keys: List[str]):
    return [compute_column_coloring(orig_data, c) for c in column_keys]


def compute_column_coloring(orig_data, column_key: str) -> str:
    threshold = 2 * sqrt(len(orig_data))
    nu = column_attrs[column_key].non_uniques_count
    if len(column_attrs[column_key].value_stats) < threshold:
        return COLORING_HASH_ALL
    elif nu < threshold:
        return COLORING_HASH_FREQUENT
    else:
        return COLORING_NONE


class WGridCellRenderer:
    full_block = '\u2588'

    def __init__(self, columns, column_colorings, orig_data, column_keys) -> None:
        self.columns = columns
        self.column_colorings = column_colorings
        self.orig_data = orig_data
        self.column_keys = column_keys

    def __call__(self, line, column_index, max_width, is_under_cursor):
        column_key = self.column_keys[column_index]
        value = self.orig_data[line].get(column_key)
        column_spec = self.columns.get(column_key)
        if column_spec is not None:
            value = value[:max_width]
            text = self.stripes(value, column_spec)
            attrs = COLORS[ColorKey.TEXT]
            return set_colors_cmd_bytes(*attrs) + bytes(text, 'utf-8'), len(value)
        else:
            text = str(value)
            attrs = COLORS[ColorKey.CURSOR] if is_under_cursor else self.compute_cell_attrs(column_index, text)
            return set_colors_cmd_bytes(*attrs) + bytes(text, 'utf-8'), len(text)

    def compute_cell_attrs(self, column_index, text) -> Sequence[int]:
        color = self.column_colorings[column_index] if column_index < len(self.column_colorings) else COLORING_NONE

        text_colors = COLORS[ColorKey.TEXT]
        if color == COLORING_NONE or (color == COLORING_HASH_FREQUENT and column_attrs[self.column_keys[column_index]].value_stats[text] <= 1):
            return text_colors

        fg = hash_to_rgb(hash_code(text))
        return fg[0], fg[1], fg[2], text_colors[3], text_colors[4], text_colors[5]

    @staticmethod
    def stripes(cell_contents, column_spec):
        spec_list = list(column_spec.items())
        if len(spec_list) == 1 and type(spec_list[0][1]) is dict:
            return WGridCellRenderer.stripes_for_nested_spec(cell_contents, spec_list[0][0], spec_list[0][1])
        else:
            return WGridCellRenderer.stripes_for_plain_spec(cell_contents, column_spec)

    @staticmethod
    def stripes_for_plain_spec(cell_contents, column_spec):
        s = ""
        for cell in cell_contents:
            rgb_string = column_spec.get(cell)
            attr = ansi_foreground_escape_code(*decode_rgb(rgb_string) if rgb_string is not None else (255, 255, 255))
            s = s + attr + WGridCellRenderer.full_block
        return s

    @staticmethod
    def stripes_for_nested_spec(cell_contents, field, spec):
        s = ""
        for cell in cell_contents:
            rgb_string = spec.get(cell[field])
            attr = ansi_foreground_escape_code(*decode_rgb(rgb_string) if rgb_string is not None else (255, 255, 255))
            s = s + attr + WGridCellRenderer.full_block
        return s
