from datatools.jt.model.attributes import MASK_OVERLINE, MASK_BG_EMPHASIZED


class WRowSeparatorCellRenderer:
    def __call__(self, value):
        """ returns a combination of MASK_* constants from attributes.py """
        return MASK_OVERLINE | MASK_BG_EMPHASIZED if (value and (value == 1 or value == '1')) else 0
