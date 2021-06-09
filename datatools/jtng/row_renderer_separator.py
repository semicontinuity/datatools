class WRowSeparatorCellRenderer:
    def __call__(self, value):
        return b'\x1b[53m' if (value and (value == 1 or value == '1')) else b''
