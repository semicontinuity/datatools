from typing import Callable, Any

from datatools.tui.box_drawing_chars import LEFT_BORDER


class WColumnRenderer:
    named_cell_value_f: Callable[[int, str], Any]

    def assistant(self):
        pass

    def __str__(self):
        """
        Has to return complete footer string, including border, (if border is painted).
        If shorter than column width, will be padded with spaces.
        """
        return LEFT_BORDER

    def __len__(self) -> int:
        """
        Has to return the width of the column (or cell?) in characters.
        """
        pass

    def __call__(self, attrs, max_width, start, end, value, assistant_value, row: int) -> bytes:
        """
        Has to generate and return text buffer for the contents of the cell with the value 'value'.
        attrs: combination of MASK_* constants.
        """
        pass
