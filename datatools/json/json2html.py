#!/usr/bin/env python3

# Long lists are collapsed by default, set env variable V=1 to suppress.

import json
import os
import sys
from json import JSONDecodeError

from datatools.json.coloring import *
from datatools.json.json_viz_helper import *
from datatools.json.structure_analyzer import *
from datatools.util.html_util import *

DEBUG = os.getenv('DEBUG')

FD_METADATA_IN = 104
FD_METADATA_OUT = 105

FD_PRESENTATION_IN = 106
FD_PRESENTATION_OUT = 107

FD_STATE_IN = 108
FD_STATE_OUT = 109

verbose = False


def read_fd_or_default(fd, default):
    try:
        with os.fdopen(fd, 'r') as f:
            return json.load(f)
    except Exception:
        return default


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, file=sys.stderr, **kwargs)


def stderr_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


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
                        *[tk.custom_th(str(i + 1)) for i in range(self.width)]
                    )
                ),
                tbody(
                    *[
                        tr(
                            tk.custom_th(str(y + 1)),
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


class ArrayNode:
    def __init__(self, j, parent, in_array_of_nestable_obj: bool):
        self.parent = parent
        self.records = [node(subj, self, in_array_of_nestable_obj) for subj in j]

    def __str__(self):
        return self.html_numbered_table().__str__()

    def html_numbered_table(self):
        if all((is_primitive(record) for record in self.records)):
            return self.html_spans_table('regular' if len(self.records) < 150 else 'collapsed2')
        elif len(self.records) > 7 or len(str(self.records)) >= 250:
            return self.html_numbered_table_collapsed()
        else:
            return self.html_numbered_table_plain()

    def html_spans_table(self, clazz):
        return div(
            tk.custom_span(f'{len(self.records)} items', clazz="header", onclick='toggle2(this, "DIV")'),
            *[
                self.array_entry(pos + 1, self.records[pos]) for pos in range(len(self.records))
            ],
            clazz=("a", clazz), onclick="toggle2(this, 'DIV')"
        )

    @staticmethod
    def array_entry(i: int, contents: Optional[Any]):
        return tk.custom_span(
            tk.custom_span(i, clazz='index'),
            tk.custom_span(contents, clazz='none' if contents is None else None),
            clazz='ae'
        )

    def html_numbered_table_plain(self):
        return table(
            *[
                tr(Element('th', pos + 1, clazz='a'), tk.td_value_with_color(self.records[pos], "a_v"))
                for pos in range(len(self.records))
            ],
            clazz="a"
        )

    def html_numbered_table_collapsed(self):
        return table(
            thead(
                tk.custom_th('#', onclick="toggle(this)"),
                tk.custom_th(f'{len(self.records)} items')
            ),
            tbody(
                *[
                    tr(tk.custom_th(str(pos + 1)), tk.td_value_with_color(self.records[pos], "a_v"))
                    for pos in range(len(self.records))
                ],
                clazz="collapsed"
            ),
            clazz="a"
        )


class ArrayOfNestableObjectsNode:
    descriptor: Optional[Dict[str, Any]]
    paths_of_leaves: List[Tuple[str]]
    record_nodes: List[Dict[Hashable, Any]]

    def __init__(self, parent, j, descriptor: Optional[Dict[str, Any]]):
        self.parent = parent
        self.descriptor = descriptor
        self.paths_of_leaves = compute_paths_of_leaves(descriptor)
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
        return table(
            thead(
                *[
                    tr(
                        tk.custom_th('#', rowspan=depth, onclick="toggle(this)") if level == 0 else None,
                        *[
                            tk.custom_th(
                                name,
                                rowspan=1 if value is not None else depth - level, colspan=number_of_columns(value)
                            )
                            for name, value in items_at_level(self.descriptor, level + 1)
                        ]
                    )
                    for level in range(depth)
                ]
            ),
            tbody(
                *[
                    tr(
                        tk.custom_th(r['#']),
                        *[
                            td_value_with_attrs(self.column_id_to_attrs[leaf_path], child_by_path(r, leaf_path))
                            for leaf_path in self.paths_of_leaves
                        ]
                    )
                    for r in self.record_nodes
                ],
                clazz="collapsed" if not verbose and self.parent and (
                        len(self.record_nodes) > 7 or len(str(self.record_nodes)) > 1024) else None
            ),
            clazz="aohwno"
        ).__str__()


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


def td_value_with_attrs(attrs, value):
    if value is None:
        return td()

    string_value = str(value)
    if attrs.is_colored(string_value):
        bg = hash_to_rgb(attrs.value_hashes.get(string_value) or hash_code(string_value))
        return tk.td_value_with_color(value, bg=bg)
    else:
        return tk.td_value_with_color(value)


def node(j, parent, in_array_of_nestable_obj: bool):
    # replace with path_in_array_of_nestable_obj: when exhausted, allow again
    if type(j) is dict:
        descriptor, path_of_leaf_to_count = obj_descriptor_and_path_counts(j)
        if descriptor is not None:
            if len(j) == 1:
                descriptor = None
            else:
                descriptor = prune_sparse_leaves(descriptor, path_of_leaf_to_count, len(j))
        if descriptor is None or in_array_of_nestable_obj or len(j) <= 1:
            return ObjectNode(j, True, parent, in_array_of_nestable_obj)
        else:
            # dict, where all entries have the same structure, i.e., array-like dict
            dict_node = ArrayOfNestableObjectsNode(parent, j.values(), descriptor)
            dict_node.record_nodes = []
            for key, sub_j in j.items():
                record_node = {name: node(value, dict_node, True) for name, value in sub_j.items()}
                record_node['#'] = key
                dict_node.record_nodes.append(record_node)
            return dict_node
    elif type(j) is list:
        descriptor, path_of_leaf_to_count = array_descriptor_and_path_counts(j)
        if descriptor is not None and not in_array_of_nestable_obj:
            descriptor = prune_sparse_leaves(descriptor, path_of_leaf_to_count, len(j))
        if descriptor is not None and not in_array_of_nestable_obj and len(j) > 1:
            array_node = ArrayOfNestableObjectsNode(parent, j, descriptor)
            array_node.record_nodes = []
            for i, sub_j in enumerate(j):
                record_node = {name: node(value, array_node, True) for name, value in sub_j.items()}
                record_node['#'] = str(i)
                array_node.record_nodes.append(record_node)
            return array_node
        else:
            width = array_is_matrix(j)
            return MatrixNode(j, parent, width) if width is not None else ArrayNode(j, parent, in_array_of_nestable_obj)
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

    presentation = read_fd_or_default(fd=FD_PRESENTATION_IN, default={})

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
