import sys
from typing import Hashable, Callable

from datatools.json.coloring import *
from datatools.json.coloring import COLORING_SINGLE
from datatools.json.coloring_cross_column import compute_cross_column_attrs
from datatools.json.coloring_hash import hash_to_rgb, hash_code
from datatools.json.html.object_node_old import ObjectNode
from datatools.json.structure_analyzer import *
from datatools.util.html.elements import *
from datatools.util.logging import debug

verbose = False


class ArrayOfNestableObjectsNode:
    descriptor: Optional[Dict[str, Any]]
    paths_of_leaves: List[Tuple[str]]
    record_nodes: List[Dict[Hashable, Any]]

    def __init__(self, parent, j, descriptor: Optional[Dict[str, Any]], tk, old_tk, pruned=None):
        self.tk = tk
        self.old_tk = old_tk
        self.parent = parent
        self.descriptor = descriptor
        self.paths_of_leaves = compute_paths_of_leaves(descriptor)
        self.pruned = pruned
        debug('compute_column_attrs')
        self.column_id_to_attrs: Dict[Hashable, ColumnAttrs] = {}

        for column_id in self.paths_of_leaves:
            self.column_id_to_attrs[column_id] = self.compute_column_attrs(j, column_id, child_by_path)
        debug('done')

        debug('compute_cross_column_attrs')
        compute_cross_column_attrs(j, self.column_id_to_attrs, child_by_path)
        debug('done')

    def compute_column_attrs(self, j, column_id: Hashable, cell_value_function: Callable[[Any, Any], Any]) -> ColumnAttrs:
        attr = ColumnAttrs()
        for record in j:
            cell = cell_value_function(record, column_id)
            attr.add_value(cell)
        attr.compute_coloring()
        return attr

    def __str__(self):
        depth = depth_of(self.descriptor) - 1

        table_contents = []

        # experimental.
        # background, if defined, should depend on the single value of the column.
        # if depth == 1:
        #     table_contents.append(
        #         colgroup(
        #             *[
        #                 col(
        #                     span=number_of_columns(value),
        #                     style=f"background: #{self.bg(name)[0]:02x}{self.bg(name)[1]:02x}{self.bg(name)[2]:02x};",
        #                 )
        #                 for name, value in items_at_level(self.descriptor, 1)
        #             ]
        #         )
        #     )

        table_contents.append(
            thead(
                *[
                    tr(
                        self.tk.th_with_span('#', rowspan=depth, onclick="toggle(this)") if level == 0 else None,
                        *[
                            th(
                                span(name),
                                span(name[:1] + '.', clazz='compact'),
                                rowspan=1 if value is not None else depth - level, colspan=number_of_columns(value),
                                onclick=f'toggleParentClass(this, "TABLE", "hide-c-{i + 2}")',
                            )
                            for i, (name, value) in enumerate(items_at_level(self.descriptor, level + 1))
                        ],
                        self.tk.th_with_span('-', rowspan=depth, onclick="toggle(this)") if len(
                            self.pruned) > 0 and level == 0 else None,
                    )
                    for level in range(depth)
                ]
            )
        )

        table_contents.append(
            tbody(
                *[
                    tr(
                        self.tk.th_with_span(r['#']),
                        *[
                            self.td_value_with_attrs(self.column_id_to_attrs[leaf_path], child_by_path(r, leaf_path))
                            for leaf_path in self.paths_of_leaves
                        ],
                        td(self.combo_cell(r)) if len(self.pruned) > 0 else None
                    )
                    for r in self.record_nodes
                ],
                clazz="collapsed" if not verbose and self.parent and (
                        len(self.record_nodes) > 7 or len(str(self.record_nodes)) > 1024) else None
            )
        )

        table_classes = [
            f"hide-c-{i + 2}" if self.coloring(name) == COLORING_SINGLE else None
            for i, (name, value) in enumerate(items_at_level(self.descriptor, 1))
        ]

        return table(
            *table_contents,
            clazz=["aohwno"] + table_classes
        ).__str__()

    def coloring(self, name):
        o = self.column_id_to_attrs.get((name,))
        if o is None:
            return None
        return o.coloring

    def bg(self, name: str):
        return hash_to_rgb(hash_code(name))

    def combo_cell(self, record):
        return ObjectNode({key: record[key] for key in self.pruned if key in record}, True, self, True, self.old_tk, self.tk)

    def td_value_with_attrs(self, attrs: ColumnAttrs, value):
        if value is None:
            return td()

        string_value = str(value)
        if attrs.coloring == COLORING_HASH_FREQUENT:
            if attrs.is_frequent(string_value):
                bg = hash_to_rgb(attrs.value_hashes.get(string_value) or hash_code(string_value), offset=0xC0)
            else:
                bg = None
            return self.tk.td_value_with_color(value, bg=bg)

        elif attrs.is_colored(string_value):
            bg = hash_to_rgb(attrs.value_hashes.get(string_value) or hash_code(string_value))
            return self.tk.td_value_with_color(value, bg=bg)
        else:
            return self.tk.td_value_with_color(value, clazz='plain')


def child_by_path(value: Any, path: Tuple[str]) -> Any:
    for name in path:
        if value is None:
            return None
        if isinstance(value, dict):
            value = value.get(name)
        elif isinstance(value, ObjectNode):
            value = value.fields.get(name)  # hack (ObjectNode)
        else:
            print(f"path: {path}, value: ${type(value)}", file=sys.stderr)
            raise ValueError
    return value
