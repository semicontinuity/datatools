from datatools.jtng.cell_renderer_stripes_sixel import WStripesSixelCellRenderer


class WStripesHashesCellRenderer(WStripesSixelCellRenderer):

    def to_hash_codes_list(self, value):
        if value is None or len(value) == 0:
            return []
        elif type(value) is list:
            return [int(s, 16) for s in value]
        else:
            return [int(s, 16) for s in value.split(',')]
