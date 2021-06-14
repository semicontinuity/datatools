from datetime import datetime

from datatools.json.coloring import hash_to_rgb
from datatools.jt.auto_metadata import ColumnMetadata
from datatools.jt.auto_presentation import ColumnPresentation
from datatools.jtng.cell_renderer_stripes_sixel import WStripesSixelCellRenderer
from datatools.tui.box_drawing_chars import LEFT_BORDER
from datatools.tui.terminal import ansi_foreground_escape_code, ansi_background_escape_code
from datatools.util.time_bar_util import fit_time_bar


left_half_block = '\u258C'


class WTimeSeriesStripesCellRenderer(WStripesSixelCellRenderer):

    def __init__(
            self,
            column_metadata: ColumnMetadata, column_presentation: ColumnPresentation,
            max_content_width, column_state):
        super().__init__(column_metadata, column_presentation, max_content_width, column_state)

        self.bar, self.n_stripes, self.x_axis_amount_per_stripe = fit_time_bar(
            self.column_metadata.time_series_timestamp_min,
            self.column_metadata.time_series_timestamp_max, 128, 4)

    def __str__(self):
        return LEFT_BORDER + self.bar

    def to_hash_codes_list(self, value):
        return self.build_gutter(
            self.column_metadata.time_series_timestamp_min,
            value, self.n_stripes,
            self.x_axis_amount_per_stripe,
            self.column_metadata.time_series_timestamp_field
        )

    def build_gutter(self, min_time, data, n_stripes, x_axis_amount_per_stripe, timestamp_field_name):
        result = [None] * n_stripes
        for i in range(len(data)):
            ts = data[i][timestamp_field_name]
            x_value = datetime.strptime(ts, self.column_metadata.time_series_timestamp_format).timestamp()
            h = 0xFFFFFFFF
            index = int((x_value - min_time) / x_axis_amount_per_stripe)
            if index < n_stripes:
                result[index] = h

        return result

    def gutter_bar_string(self, gutter):
        result = ''

        i = 0
        while True:
            left = gutter[i]
            i += 1
            right = gutter[i]
            i += 1
            left_attr = ansi_foreground_escape_code(*hash_to_rgb(left) if left is not None else (0, 0, 0))
            right_attr = ansi_background_escape_code(*hash_to_rgb(right) if right is not None else (0, 0, 0))
            result += \
                left_attr + \
                right_attr + \
                left_half_block
            if i >= len(gutter):
                break

        return result
