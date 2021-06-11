from datatools.jtng.cell_renderer_stripes_sixel import WStripesSixelCellRenderer


class WTimeSeriesStripesCellRenderer(WStripesSixelCellRenderer):

    def to_hash_codes_list(self, value):
        return [0xFFFFFFFF for record in value]
