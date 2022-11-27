class Drawable:
    width: int
    height: int

    def row_to_string(self, y, x_from, x_to):
        return f"Line {y}"[x_from:x_to]
