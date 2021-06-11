from datatools.tui.box_drawing_chars import LEFT_BORDER


class WCellRenderer:
    def toggle(self):
        pass

    def assistant(self):
        pass

    def __str__(self):
        """ Footer string """
        return LEFT_BORDER

    def __len__(self):
        pass

    def __call__(self, is_under_cursor, max_width, start, end, value, assistant_value):
        pass
