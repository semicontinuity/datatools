#!/usr/bin/env python3
import json
import os
import sys
from json import JSONDecodeError

from datatools.json.coloring import *
from datatools.json.structure_analyzer import *
from datatools.json.util import is_primitive

DEBUG = os.getenv('DEBUG')


FD_METADATA_IN = 104
FD_METADATA_OUT = 105

FD_PRESENTATION_IN = 106
FD_PRESENTATION_OUT = 107

FD_STATE_IN = 108
FD_STATE_OUT = 109


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


class PageNode:
    def __init__(self, root, title):
        self.root = root
        self.title = title

    def __str__(self):
        return f'<html>\n' + \
               '<head>\n' + \
               f'<title>{self.title}</title>\n' + \
               '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n' + \
               '<link rel="icon" href="data:,">\n' + \
               '<style>\n' + \
               'body {font-family: monospace; display: inline-block;}\n' + \
               'main {display: inline-flex; border-left: solid 2px darkgrey; border-right: solid 2px darkgrey;}\n' + \
               'thead {border: solid 1px darkgray;}\n' + \
               'table {border-collapse: collapse; padding: 0;}\n' + \
               'table.ov { width:100%; }\n' + \
               '.a { width: 100%;}\n' + \
               '.ae { display: inline-block;}\n' + \
               '.index {border: solid 1px darkcyan; color: darkcyan;}\n' + \
               '.none {background: darkgray;}\n' + \
               'span {padding-left: 0.25em; padding-right: 0.25em;}\n' + \
               '//td {border: solid 1px #CCC; padding-left: 0.25em; padding-right: 0.25em;}\n' + \
               'table.aon th {border: solid 1px darkgrey; }\n' + \
               'table.aon td {border: solid 1px darkgrey; }\n' + \
               'table.aohwno th {border: solid 1px darkgrey; }\n' + \
               'table.aohwno td {border: solid 1px darkgrey; }\n' + \
               'td {border-top: solid 1px #CCC; border-bottom: solid 1px #CCC; padding: 0;}\n' + \
               'th {border-top: solid 1px darkgrey; border-bottom: solid 1px darkgrey; background: #DDD}\n' + \
               'th.ov_th {border-right: solid 2px darkgrey; }\n' + \
               '//tr:nth-child(odd)  td.index {background: #CCC;}\n' + \
               '//tr:nth-child(even) td.index {background: #BBB;}\n' + \
               'td.a_v {width:100%;}\n' + \
               'td.ov_v {width:100%;}\n' + \
               '.int {color: darkred;}\n' + \
               '.float {color: darkred;}\n' + \
               '.str {color: navy;}\n' + \
               '.bool {color: darkgreen;}\n' + \
               '.collapsed {display: none;}\n' + \
               '</style>\n' + \
               '<script>\n' + \
               '  function toggleClass(element, className) {' + \
               '    const classes = element.classList;' + \
               '    if (classes.contains(className)) {' + \
               '        classes.remove(className);' + \
               '    } else {' + \
               '        classes.add(className);' + \
               '    }' + \
               '  }' + \
               '  function toggle(e) { ' \
               '    const tb = e.parentElement.parentElement.parentElement.getElementsByTagName("tbody")[0];' \
               '    toggleClass(tb, "collapsed");' \
               '  }\n' + \
               '</script>\n' + \
               '</head>\n' + \
               f'<body><main>\n\n{str(self.root)}\n\n</main></body>\n' \
               '</html>\n'


class ArrayNode:
    def __init__(self, j, parent):
        self.parent = parent
        self.records = [node(subj, self) for subj in j]

    def __str__(self):
        return self.html_numbered_table()

    def html_numbered_table(self):
        if all((is_primitive(record) for record in self.records)) and len(str(self.records)) < 500:
            return self.html_spans_table()
        elif len(self.records) > 7 or len(str(self.records)) >= 250:
            return self.html_numbered_table_collapsed()
        else:
            return self.html_numbered_table_plain()

    def html_spans_table(self):
        s = '<div class="a">'
        for pos in range(len(self.records)):
            value = self.records[pos]
            s += array_entry(pos + 1, value)
        s += '</div>'
        return s

    def html_numbered_table_plain(self):
        s = '<table class="a">'
        for pos in range(len(self.records)):
            value = self.records[pos]
            s += '<tr>\n'
            s += th(str(pos + 1)) + '\n'
            s += td_value("a_v", value)
            s += '</tr>\n'
        s += '</table>'
        return s

    def html_numbered_table_collapsed(self):
        s = '<table class="a">'
        s += '<thead>'
        s += '<tr>'
        s += th('#', attrs=' onclick="toggle(this)"')
        s += th(f'{len(self.records)} items')
        s += '</tr>'
        s += '</thead>'

        s += '<tbody class="collapsed">'
        for pos in range(len(self.records)):
            value = self.records[pos]
            s += '<tr>\n'
            s += th(str(pos + 1)) + '\n'
            s += td_value("a_v", value)
            s += '</tr>\n'
        s += '<tbody>'

        s += '</table>'
        return s


class ArrayOfNestableObjectsNode:
    descriptor: Optional[Dict[str, Any]]
    paths_of_leaves: List[Tuple[str]]
    record_nodes: List[Dict[Hashable, Any]]

    def __init__(self, parent, j, descriptor: Optional[Dict[str, Any]]):
        self.parent = parent
        self.descriptor = descriptor
        self.paths_of_leaves = compute_paths_of_leaves(descriptor)
        debug('compute_column_attrs')
        self.column_id_to_attrs = {}

        for column_id in self.paths_of_leaves:
            self.column_id_to_attrs[column_id] = compute_column_attrs(j, column_id, child_by_path)
        debug('done')

        debug('compute_cross_column_attrs')
        compute_cross_column_attrs(j, self.column_id_to_attrs, child_by_path)
        debug('done')

    def __str__(self):
        s = '<table class="aohwno">'

        depth = depth_of(self.descriptor) - 1

        s += '<thead>'
        for level in range(depth):
            s += '<tr>'

            if level == 0:
                s += th('#', rowspan=depth, attrs=' onclick="toggle(this)"')

            items = items_at_level(self.descriptor, level + 1)
            for name, value in items:
                width = number_of_columns(value)
                rowspan = 1 if value is not None else depth - level
                # s += '<th rowspan="' + str(rowspan) + '" colspan="' + str(width) + '">' + name + '</th>'
                s += th(name, rowspan=rowspan, colspan=width)
            s += '</tr>'
        s += '</thead>'

        if len(self.record_nodes) > 1 and self.parent:
            s += '<tbody class="collapsed">'
        else:
            s += '<tbody>'

        for r in self.record_nodes:
            s += '<tr>\n'

            # i += 1
            # s += th(str(i)) + '\n'
            s += th(r['#']) + '\n'

            for leaf_path in self.paths_of_leaves:
                value = child_by_path(r, leaf_path)
                attr = self.column_id_to_attrs[leaf_path]
                string_value = str(value) if value is not None else None
                s += td_value_with_attr(attr, string_value, value)
            s += '</tr>\n'
        s += '</tbody>'

        s += '\n</table>'
        return s


class ObjectNode:
    def __init__(self, j, vertical, parent):
        self.parent = parent
        self.fields = {key: node(subj, self) for key, subj in j.items()}
        self.vertical = vertical

    def __str__(self):
        return self.vertical_html() if self.vertical else self.horizontal_html()

    def horizontal_html(self):
        s = '<table class="oh">\n'
        s += '<thead>'
        for key in self.fields:
            s += th(key)
        s += '</thead>'
        s += '<tr>\n'
        for key, value in self.fields.items():
            s += '<td>\n'
            if value is not None:
                s += str(value)
            s += '</td>\n'
        s += '</tr>\n'
        s += '\n</table>'
        return s

    def vertical_html(self):
        return '<table class="ov">\n' \
               + '\n'.join(['<tr>\n'
                            + th(key, 'ov_th') + '\n'
                            + td_value("ov_v", value) + '\n'
                            + '</tr>\n'
                            for key, value in self.fields.items()]) + '</table>\n'


def td_colored(attr, string_value, value):
    if value is None:
        return '<td></td>\n'
    elif attr.is_colored(string_value):
        bg = hash_to_rgb(attr.value_hashes.get(string_value) or hash_code(string_value))
        return td_value_with_color(bg, value) + '\n'
    else:
        return f'<td><span>\n{string_value}</span></td>\n'


def td_value_with_attr(attr, string_value, value):
    if value is None:
        return '<td></td>\n'
    elif attr.is_colored(string_value):
        bg = hash_to_rgb(attr.value_hashes.get(string_value) or hash_code(string_value))
        return td_value_with_color(bg, value) + '\n'
    else:
        return f'<td><span>\n{string_value}</span></td>\n'


def td_value(clazz, value):
    leaf = is_primitive(value)
    data_type = f'{type(value).__name__}' if leaf else ''
    s = f'<td class="{clazz} {data_type}">'
    s += value_str(value, leaf)
    s += '</td>'
    return s


def td_value_with_color(bg, value):
    leaf = is_primitive(value)
    clazz = f'{type(value).__name__}' if leaf else ''
    color = f'style="background: #{bg[0]:02x}{bg[1]:02x}{bg[2]:02x};"' if bg is not None else ''
    s = f'<td class="{clazz}" {color}>'
    s += value_str(value, leaf)
    s += '</td>'
    return s


def th(s, clazz=None, colspan=None, rowspan=None, attrs=None):
    if attrs is None:
        attrs = ''
    if clazz is not None:
        attrs += f' class="{clazz}"'
    if colspan is not None:
        attrs += f' colspan="{colspan}"'
    if rowspan is not None:
        attrs += f' rowspan="{rowspan}"'
    return f'<th{attrs}><span>{s}</span></th>'


def value_str(value: Optional[Any], leaf: bool):
    return span(value) if leaf else text(value)


def array_entry(i: int, contents: Optional[Any]):
    return span(index(i) + span(contents, clazz='none' if contents is None else None), clazz='ae')


def index(contents: Optional[Any]):
    return f'<span class="index">{text(contents)}</span>'


def span(contents: Optional[Any], clazz=None):
    attrs = f' class="{clazz}"' if clazz is not None else ''
    return f'<span{attrs}>{text(contents)}</span>'


def text(contents: Optional[Any]):
    return "" if contents is None else str(contents)


def node(j, parent):
    if type(j) is dict:
        descriptor, path_of_leaf_to_count = obj_descriptor_and_path_counts(j)
        if descriptor is not None:
            if len(j) == 1:
                descriptor = None
            else:
                prune_sparse_leaves(descriptor, path_of_leaf_to_count, len(j))
        if descriptor is None:
            return ObjectNode(j, True, parent)
        else:
            # dict, where all entries have the same structure, i.e., array-like dict
            dict_node = ArrayOfNestableObjectsNode(parent, j.values(), descriptor)
            dict_node.record_nodes = []
            for key, sub_j in j.items():
                record_node = {name: node(value, dict_node) for name, value in sub_j.items()}
                record_node['#'] = key
                dict_node.record_nodes.append(record_node)
            return dict_node
    elif type(j) is list:
        descriptor, path_of_leaf_to_count = array_descriptor_and_path_counts(j)
        if descriptor is not None:
            # if len(j) == 1:
            #     return ObjectNode(j[0], True, parent)
            # else:
            #     prune_sparse_leaves(descriptor, path_of_leaf_to_count, len(j))
            #     return ArrayOfNestableObjectsNode(parent, j, descriptor, compute_paths_of_leaves(descriptor))
            prune_sparse_leaves(descriptor, path_of_leaf_to_count, len(j))
            array_node = ArrayOfNestableObjectsNode(parent, j, descriptor)
            array_node.record_nodes = []
            for i, sub_j in enumerate(j):
                record_node = {name: node(value, array_node) for name, value in sub_j.items()}
                record_node['#'] = str(i)
                array_node.record_nodes.append(record_node)
            return array_node
        else:
            return ArrayNode(j, parent)
    else:
        return j


def main():
    if os.environ.get("PIPE_HEADERS_IN"):
        print("Head", file=sys.stderr)

    presentation = read_fd_or_default(fd=FD_PRESENTATION_IN, default={})

    if len(sys.argv) == 2:
        presentation["title"] = sys.argv[1]
    if len(sys.argv) == 3:
        with open(sys.argv[2]) as json_file:
            j = json.load(json_file)
    else:
        j = json.load(sys.stdin)

    print(PageNode(node(j, None), presentation.get("title", "")))


if __name__ == "__main__":
    try:
        main()
    except JSONDecodeError as ex:
        stderr_print("Reads json. Outputs html.")
