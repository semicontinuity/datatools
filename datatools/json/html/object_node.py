class ObjectNode:
    def __init__(self, j, descriptor, vertical, tk):
        self.tk = tk
        self.fields = {key: tk.node(subj, descriptor.dict[key]) for key, subj in j.items()}
        self.vertical = vertical

    def __str__(self):
        return self.vertical_html().__str__() if self.vertical else self.horizontal_html().__str__()

    def horizontal_html(self):
        return table(
            *[
                thead(
                    *[self.tk.th_with_span(key) for key in self.fields]
                ),
                tr(
                    *[td(value) for value in self.fields.values()]
                )
            ],
            clazz="oh"
        )

    def vertical_html(self):
        return table(*[self.vertical_html_tr(key, value) for key, value in self.fields.items()], clazz="ov")

    def vertical_html_tr(self, key, value):
        return tr(self.tk.th_with_span(key, clazz='ov_th'), self.tk.td_value_with_color(value, "ov_v"))
