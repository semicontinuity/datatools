from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Any

from datatools.jt.model.presentation import ColumnRenderer
from datatools.jt.ui.ng.cell_renderer_stripes_sixel import WStripesSixelCellRenderer
from datatools.jt.ui.ng.render_data import RenderData
from datatools.tui.box_drawing_chars import LEFT_BORDER
from datatools.tui.coloring import hash_to_rgb, decode_rgb
from datatools.util.time_bar_util import fit_time_bar


@dataclass
class ColumnRendererStripesTimeSeries(ColumnRenderer):
    type = 'stripes-time-series'
    coloring: Any = None

    def make_delegate(self, render_data: RenderData):
        return WTimeSeriesStripesCellRenderer(self, render_data)


class WTimeSeriesStripesCellRenderer(WStripesSixelCellRenderer):
    color_selector_weights: Dict
    color_selector_column: Optional[str]

    def __init__(self,
                 column_renderer: ColumnRendererStripesTimeSeries,
                 render_data: RenderData):
        super().__init__(column_renderer, render_data)

        if type(column_renderer.coloring) is dict:
            self.color_selector_weights = column_renderer.coloring['weights']
            self.color_selector_column = column_renderer.coloring['column']
            self.color_mapping = {
                value: decode_rgb(color[1:]) for value, color in column_renderer.coloring['colorMap'].items()
            }
        else:
            self.color_selector_weights = {}
            self.color_selector_column = None
            self.color_mapping = {}
        self.color_mapping[...] = hash_to_rgb(0xFFFFFFFF, offset=128)    # default color

        max_bar_chars = self.max_content_width - 2
        if max_bar_chars == 0:
            max_bar_chars = 1   # hack
        self.bar, self.n_stripes, self.x_axis_amount_per_stripe = fit_time_bar(
            self.render_data.column_metadata.min_value,
            self.render_data.column_metadata.max_value, max_bar_chars, WStripesSixelCellRenderer.STRIPES_PER_CHAR)

    def __str__(self):
        return LEFT_BORDER + self.bar

    def to_color_list(self, value):
        color_selectors = self.build_gutter(self.render_data.column_metadata.min_value, value, self.n_stripes,
                                            self.x_axis_amount_per_stripe,
                                            self.render_data.column_metadata.time_series_timestamp_field)
        return [self.color_mapping.get(sel, (0, 0, 0)) for sel in color_selectors]

    def build_gutter(self, min_time, data, n_stripes, x_axis_amount_per_stripe, timestamp_field_name):
        result = [None] * n_stripes

        for i in range(len(data)):
            ts = data[i][timestamp_field_name]
            x_value = datetime.strptime(ts, self.render_data.column_metadata.time_series_timestamp_format).timestamp()
            color_selector = data[i][self.color_selector_column] if self.color_selector_column else ...
            index = int((x_value - min_time) / x_axis_amount_per_stripe)
            if index < n_stripes and 0 < index < len(result):   # something weird with min/max time
                new_weight = self.color_selector_weights.get(color_selector, -1)
                old_weight = self.color_selector_weights.get(result[index], 1000000)
                if new_weight < old_weight:
                    result[index] = color_selector

        return result
