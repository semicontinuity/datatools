from datatools.jt.ui.ng.cell_renderer_stripes_sixel import WStripesSixelCellRenderer
from datatools.tui.coloring import hash_to_rgb


class WStripesHashesCellRenderer(WStripesSixelCellRenderer):

    def to_color_list(self, value):
        if value is None or len(value) == 0:
            return []
        elif type(value) is list:
            hash_codes = [int(s, 16) for s in value]
            return [hash_to_rgb(hash_code, offset=64) for hash_code in hash_codes]
        else:
            hash_codes = [int(s, 16) for s in value.split(',')]
            return [hash_to_rgb(hash_code, offset=64) for hash_code in hash_codes]
