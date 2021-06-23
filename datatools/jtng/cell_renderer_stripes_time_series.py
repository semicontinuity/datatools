from datetime import datetime

from datatools.jt.auto_metadata import ColumnMetadata
from datatools.jt.auto_presentation import ColumnPresentation
from datatools.jtng.cell_renderer_stripes_sixel import WStripesSixelCellRenderer
from datatools.tui.box_drawing_chars import LEFT_BORDER
from datatools.tui.coloring import hash_to_rgb, decode_rgb
from datatools.util.time_bar_util import fit_time_bar


class WTimeSeriesStripesCellRenderer(WStripesSixelCellRenderer):

    def __init__(
            self,
            column_metadata: ColumnMetadata, column_presentation: ColumnPresentation,
            max_content_width, column_state):
        super().__init__(column_metadata, column_presentation, max_content_width, column_state)

        if type(self.column_presentation.coloring) is dict:
            self.color_selector_weights = self.column_presentation.coloring['weights']
            self.color_selector_column = self.column_presentation.coloring['column']
            self.color_mapping = {
                value: decode_rgb(color[1:]) for value, color in self.column_presentation.coloring['colors'].items()
            }
        else:
            self.color_selector_weights = {}
            self.color_selector_column = None
            self.color_mapping = {}
        self.color_mapping[...] = hash_to_rgb(0xFFFFFFFF, offset=128)    # default color

        self.bar, self.n_stripes, self.x_axis_amount_per_stripe = fit_time_bar(
            self.column_metadata.time_series_timestamp_min,
            self.column_metadata.time_series_timestamp_max, 128, 4)

    def __str__(self):
        return LEFT_BORDER + self.bar

    def to_color_list(self, value):
        color_selectors = self.build_gutter(self.column_metadata.time_series_timestamp_min, value, self.n_stripes,
                                            self.x_axis_amount_per_stripe,
                                            self.column_metadata.time_series_timestamp_field)
        return [self.color_mapping.get(sel, (0, 0, 0)) for sel in color_selectors]

    def build_gutter(self, min_time, data, n_stripes, x_axis_amount_per_stripe, timestamp_field_name):
        result = [None] * n_stripes

        for i in range(len(data)):
            ts = data[i][timestamp_field_name]
            x_value = datetime.strptime(ts, self.column_metadata.time_series_timestamp_format).timestamp()
            color_selector = data[i][self.color_selector_column] if self.color_selector_column else ...
            index = int((x_value - min_time) / x_axis_amount_per_stripe)
            if index < n_stripes:
                new_weight = self.color_selector_weights.get(color_selector, -1)
                old_weight = self.color_selector_weights.get(result[index], 1000000)
                if new_weight < old_weight:
                    result[index] = color_selector

        return result
