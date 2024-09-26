#!/usr/bin/env python3

# Long lists are collapsed by default, set env variable V=1 to suppress.

import json
import os
import sys
from json import JSONDecodeError

from datatools.json.coloring import *
from datatools.json.coloring import COLORING_SINGLE
from datatools.json.json_viz_helper import *
from datatools.json.structure_analyzer import *
from datatools.util.meta_io import presentation_or_default
from util.html.elements import *
from datatools.util.logging import debug, stderr_print

verbose = False


class MatrixNode:
    def __init__(self, j, parent, width):
        self.data = j
        self.parent = parent
        self.width = width

    def __str__(self):
        return div(
            span(f'Matrix {len(self.data)} x {self.width}', clazz='header'),
            table(
                thead(
                    tr(
                        tk.custom_th('#'),
                        *[tk.custom_th(str(i)) for i in range(self.width)]
                    )
                ),
                tbody(
                    *[
                        tr(
                            tk.custom_th(str(y)),
                            *[
                                tk.td_value_with_color(cell, "a_v")  # all cells are primitives
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


class ArrayOfNestableObjectsNode:
    descriptor: Optional[Dict[str, Any]]
    paths_of_leaves: List[Tuple[str]]
    record_nodes: List[Dict[Hashable, Any]]

    def __init__(self, parent, j, descriptor: Optional[Dict[str, Any]], pruned=None):
        self.parent = parent
        self.descriptor = descriptor
        self.paths_of_leaves = compute_paths_of_leaves(descriptor)
        self.pruned = pruned
        debug('compute_column_attrs')
        self.column_id_to_attrs: Dict[Hashable, ColumnAttrs] = {}

        for column_id in self.paths_of_leaves:
            self.column_id_to_attrs[column_id] = compute_column_attrs(j, column_id, child_by_path)
        debug('done')

        debug('compute_cross_column_attrs')
        compute_cross_column_attrs(j, self.column_id_to_attrs, child_by_path)
        debug('done')

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
                        tk.custom_th('#', rowspan=depth, onclick="toggle(this)") if level == 0 else None,
                        *[
                            th(
                                span(name),
                                span(name[:1] + '.', clazz='compact'),
                                rowspan=1 if value is not None else depth - level, colspan=number_of_columns(value),
                                onclick=f'toggleParentClass(this, "TABLE", "hide-c-{i + 2}")',
                            )
                            for i, (name, value) in enumerate(items_at_level(self.descriptor, level + 1))
                        ],
                        tk.custom_th('-', rowspan=depth, onclick="toggle(this)") if len(
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
                        tk.custom_th(r['#']),
                        *[
                            td_value_with_attrs(self.column_id_to_attrs[leaf_path], child_by_path(r, leaf_path))
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
            f"hide-c-{i + 2}" if self.column_id_to_attrs[(name,)].coloring == COLORING_SINGLE else None
            for i, (name, value) in enumerate(items_at_level(self.descriptor, 1))
        ]

        return table(
            *table_contents,
            clazz=["aohwno"] + table_classes
        ).__str__()

    def bg(self, name: str):
        return hash_to_rgb(hash_code(name))
    
    def combo_cell(self, record):
        return ObjectNode({key: record[key] for key in self.pruned if key in record}, True, self, True)


class ObjectNode:
    def __init__(self, j, vertical, parent, in_array_of_nestable_obj: bool):
        self.parent = parent
        self.fields = {key: node(subj, self, in_array_of_nestable_obj) for key, subj in j.items()}
        self.vertical = vertical

    def __str__(self):
        return self.vertical_html().__str__() if self.vertical else self.horizontal_html().__str__()

    def horizontal_html(self):
        return table(
            *[
                thead(
                    *[tk.custom_th(key) for key in self.fields]
                ),
                tr(
                    *[td(value) for value in self.fields.values()]
                )
            ],
            clazz="oh"
        )

    def vertical_html(self):
        return table(*[self.vertical_html_tr(key, value) for key, value in self.fields.items()], clazz="ov")

    @staticmethod
    def vertical_html_tr(key, value):
        return tr(tk.custom_th(key, clazz='ov_th'), tk.td_value_with_color(value, "ov_v"))


def td_value_with_attrs(attrs: ColumnAttrs, value):
    if value is None:
        return td()

    string_value = str(value)
    if attrs.coloring == COLORING_HASH_FREQUENT:
        if attrs.is_frequent(string_value):
            bg = hash_to_rgb(attrs.value_hashes.get(string_value) or hash_code(string_value), offset=0xC0)
        else:
            bg = None
        return tk.td_value_with_color(value, bg=bg)

    elif attrs.is_colored(string_value):
        bg = hash_to_rgb(attrs.value_hashes.get(string_value) or hash_code(string_value))
        return tk.td_value_with_color(value, bg=bg)
    else:
        return tk.td_value_with_color(value, clazz='plain')


def list_node(j, parent, in_array_of_nestable_obj: bool):
    result = ListNode(None)
    records = [node(subj, result, in_array_of_nestable_obj) for subj in j]
    result.records = records
    return result


def node(j, parent, in_array_of_nestable_obj: bool):
    pruned = []
    # replace with path_in_array_of_nestable_obj: when exhausted, allow again
    if type(j) is dict:
        descriptor, path_of_leaf_to_count = obj_descriptor_and_path_counts(j)
        if descriptor is not None:
            if len(j) == 1:
                descriptor = None
            else:
                descriptor, pruned = prune_sparse_leaves(descriptor, path_of_leaf_to_count, len(j))
        if descriptor is None or in_array_of_nestable_obj or len(j) <= 1:
            return ObjectNode(j, True, parent, in_array_of_nestable_obj)
        else:
            # dict, where all entries have the same structure, i.e., array-like dict
            dict_node = ArrayOfNestableObjectsNode(parent, j.values(), descriptor, pruned)
            dict_node.record_nodes = []
            for key, sub_j in j.items():
                record_node = {name: node(value, dict_node, True) for name, value in sub_j.items()}
                record_node['#'] = key
                dict_node.record_nodes.append(record_node)
            return dict_node
    elif type(j) is list:
        descriptor, path_of_leaf_to_count = array_descriptor_and_path_counts(j)
        if descriptor is not None and not in_array_of_nestable_obj:
            descriptor, pruned = prune_sparse_leaves(descriptor, path_of_leaf_to_count, len(j))
        if descriptor is not None and not in_array_of_nestable_obj and len(j) > 1:
            array_node = ArrayOfNestableObjectsNode(parent, j, descriptor, pruned)
            array_node.record_nodes = []
            for i, sub_j in enumerate(j):
                record_node = {name: node(value, array_node, True) for name, value in sub_j.items()}
                record_node['#'] = str(i)
                array_node.record_nodes.append(record_node)
            return array_node
        else:
            width = array_is_matrix(j)
            return MatrixNode(j, parent, width) if width is not None else list_node(j, parent, in_array_of_nestable_obj)
    else:
        return j


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


def main():
    if os.environ.get("PIPE_HEADERS_IN"):
        print("Head", file=sys.stderr)
    if os.environ.get("V") == "1":
        global verbose
        verbose = True

    presentation = presentation_or_default(default={})

    if len(sys.argv) == 2:
        presentation["title"] = sys.argv[1]
    if len(sys.argv) == 3:
        with open(sys.argv[2]) as json_file:
            j = json.load(json_file)
    else:
        j = json.load(sys.stdin)

    print(PageNode(node(j, None, False), presentation.get("title", "")))


if __name__ == "__main__":
    try:
        main()
    except JSONDecodeError as ex:
        stderr_print("Reads json. Outputs html.")
