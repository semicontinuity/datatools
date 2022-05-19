from datatools.tui.box_drawing_chars import LEFT_BORDER


class WColumnRenderer:

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
        :return: current width of the column in characters,
        it will be applied to all cells of the column currently rendered, so it must be consstent.
        """
        pass

    def __call__(self, attrs, column_width, start, end, value, row: int) -> bytes:
        """
        Has to generate and return text buffer for the contents of the cell with the value 'value'.
        :param attrs:           combination of MASK_* constants
        :param column_width:    current width of the rendered column, as returned by __len__
        """
        pass

    def __getitem__(self, row):
        """
        Has to return combination of MASK_* constants, that this renderer contributes to rendering of a row
        :param row:  index of the row being rendered
        """
        return 0
