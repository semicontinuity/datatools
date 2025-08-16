from datatools.util.html.elements import *

class MatrixNode:
    def __init__(self, j, parent, width, tk):
        self.data = j
        self.parent = parent
        self.width = width
        self.tk = tk

    def __str__(self):
        return div(
            span(f'Matrix {len(self.data)} x {self.width}', clazz='header'),
            table(
                thead(
                    tr(
                        self.tk.th_with_span('#'),
                        *[self.tk.th_with_span(str(i)) for i in range(self.width)]
                    )
                ),
                tbody(
                    *[
                        tr(
                            self.tk.th_with_span(str(y)),
                            *[
                                self.tk.td_value_with_color(cell, "a_v")  # all cells are primitives
                                for cell in sub_j
                            ]
                        )
                        for y, sub_j in enumerate(self.data)
                    ]
                ),
                clazz='m'
            ),
            clazz=('a', "collapsed2"), onclick='toggle2(this, "DIV")'
        ).__str__()
