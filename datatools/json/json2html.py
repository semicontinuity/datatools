#!/usr/bin/env python3
import json
import os
import sys
from json import JSONDecodeError
from string import Template
from typing import Iterable, Union

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

    html_template = Template("""<html lang="en">
<head>
<title>$title</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<link rel="icon" href="data:,">

<style>
body {font-family: monospace; display: inline-block;}
main {display: inline-flex; border-left: solid 2px darkgrey; border-right: solid 2px darkgrey;}
thead {border: solid 1px darkgray;}
table {border-collapse: collapse; padding: 0;}
//table.ov { width:100%; }
//.a { width: 100%;}
.ae { display: inline-block;}
.index {border: solid 1px darkcyan; color: darkcyan;}
div.regular>span.header    {display: none;}
div.collapsed2>span.header {display: block; font-weight: bold; background: lightgray; border: solid 1px darkgray;}
div.collapsed2>span.ae {display: none;}
div.collapsed2>table {display: none;}
tr.collapsed2>td {display: none;}
.none {background: darkgray;}
span { white-space: pre;}
//td {border: solid 1px #CCC; padding-left: 0.25em; padding-right: 0.25em;}
th.a {background: lightgray; }
table.aon th {border: solid 1px darkgrey; }
table.aon td {border: solid 1px darkgrey; }
table.aohwno th {border: solid 1px darkgrey; }
table.aohwno td {border: solid 1px darkgrey; }
td {border-top: solid 1px #CCC; border-bottom: solid 1px #CCC; padding: 0;}
th {border-top: solid 1px darkgrey; border-bottom: solid 1px darkgrey; background: #DDD}
th.ov_th {border-right: solid 2px darkgrey; }
//tr:nth-child(odd)  td.index {background: #CCC;}
//tr:nth-child(even) td.index {background: #BBB;}
//td.a_v {width:100%;}
//td.ov_v {width:100%;}

.int {color: darkred; padding-left: 0.25em; padding-right: 0.25em;}
.float {color: darkred; padding-left: 0.25em; padding-right: 0.25em;}
.str {color: navy; padding-left: 0.25em; padding-right: 0.25em;}
.bool {color: darkgreen; padding-left: 0.25em; padding-right: 0.25em;}

.collapsed {display: none;}

.overlay {
    height: 100%;
    width: 0;
    position: fixed;
    z-index: 1; /* Sit on top */
    left: 0;
    top: 0;
    background-color: rgba(255, 255, 255, 1);
    overflow-x: hidden;
    transition: 0.2s;
}

.overlay-content {
    background: #FFFFF0;
    white-space: pre;
    position: relative;
    width: 100%;
}

</style>

<script>
function toggleClass(element, className) {
  const classes = element.classList;
  if (classes.contains(className)) {
     classes.remove(className);
  } else {
     classes.add(className);
  }
}
function toggleClass2(element, class1, class2) {
  const classes = element.classList;
  if (classes.contains(class1)) {
     classes.remove(class1);
     classes.add(class2);
  } else {
     classes.remove(class2);
     classes.add(class1);
  }
}
function toggle(e) {
  const tb = e.parentElement.parentElement.parentElement.getElementsByTagName("tbody")[0];
  toggleClass(tb, "collapsed");
}
function toggle2(e, tagName) {
  while (e.tagName !== tagName) e = e.parentElement;
  toggleClass2(e, "collapsed2", "regular");
}
function initOverlay() { overlay = document.getElementById("overlay"); }
function openOverlay() { overlay.style.width = "100%"; }
function closeOverlay() { overlay.style.width = "0%"; }
</script>

</head>

<body>

<main>
$view
</main>

<div id="overlay" class="overlay" onclick="closeOverlay()">
    <div class="overlay-content"></div>
</div>

</body>
</html>""")

    def __init__(self, root, title):
        self.root = root
        self.title = title

    def __str__(self):
        return self.html_template.substitute(title=self.title, view=str(self.root))


class MatrixNode:
    def __init__(self, j, parent, width):
        self.data = j
        self.parent = parent
        self.width = width

    def __str__(self):
        clazz = "collapsed2"
        s = f'<div class="a {clazz}" onclick="toggle2(this, \'DIV\')">'
        s += f'<span class="header">Matrix {len(self.data)} x {self.width}</span>'

        s += '<table class="m">'
        s += '<thead>'
        s += '<tr>'
        # s += th('#', attrs=' onclick="toggle(this)"')
        s += th('#')
        for i in range(self.width):
            s += th(str(i + 1))
        s += '</tr>'
        s += '</thead>'

        # s += '<tbody class="collapsed">'
        s += '<tbody>'
        for y, sub_j in enumerate(self.data):
            s += '<tr>\n'
            s += th(str(y + 1)) + '\n'
            for cell in sub_j:
                s += td_value(cell, "a_v")
            s += '</tr>\n'
        s += '<tbody>'

        s += '</table>'

        s += '</div>'
        return s


class ArrayNode:
    def __init__(self, j, parent, in_array_of_nestable_obj: bool):
        self.parent = parent
        self.records = [node(subj, self, in_array_of_nestable_obj) for subj in j]

    def __str__(self):
        return self.html_numbered_table()

    def html_numbered_table(self):
        if all((is_primitive(record) for record in self.records)):
            return self.html_spans_table('regular' if len(self.records) < 150 else 'collapsed2')
        elif len(self.records) > 7 or len(str(self.records)) >= 250:
            return self.html_numbered_table_collapsed()
        else:
            return self.html_numbered_table_plain()

    def html_spans_table(self, clazz):
        s = f'<div class="a {clazz}" onclick="toggle2(this, \'DIV\')">'
        s += f'<span class="header">{len(self.records)} items</span>'
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
            s += th(str(pos + 1), clazz='a') + '\n'
            s += td_value(value, "a_v")
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
            s += td_value(value, "a_v")
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

        if self.parent and (len(self.record_nodes) > 5 or len(str(self.record_nodes)) > 1000):
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
    def __init__(self, j, vertical, parent, in_array_of_nestable_obj: bool):
        self.parent = parent
        self.fields = {key: node(subj, self, in_array_of_nestable_obj) for key, subj in j.items()}
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
        for value in self.fields.values():
            s += '<td>\n'
            if value is not None:
                s += str(value)
            s += '</td>\n'
        s += '</tr>\n'
        s += '\n</table>'
        return s

    def vertical_html(self):
        return '<table class="ov">\n' \
               + '\n'.join([self.vertical_html_tr(key, value)
                            for key, value in self.fields.items()]) + '</table>\n'

    @staticmethod
    def vertical_html_tr(key, value):
        return '<tr>\n' + th(key, 'ov_th') + '\n' + td_value(value, "ov_v") + '\n' + '</tr>\n'


def td_value_with_attr(attr, string_value, value):
    if value is None:
        return '<td></td>\n'
    elif attr.is_colored(string_value):
        bg = hash_to_rgb(attr.value_hashes.get(string_value) or hash_code(string_value))
        return td_value_with_color(value, bg) + '\n'
    else:
        return f'<td><span>\n{string_value}</span></td>\n'


def td_value(value, clazz):
    leaf = is_primitive(value)
    data_type = f'{type(value).__name__}' if leaf else ''
    s = f'<td {list_attr("class", clazz, data_type)}>'
    s += value_str(value, leaf)
    s += '</td>'
    return s


def td_value_with_color(value, bg):
    # leaf = is_primitive(value)
    # data_type = f'{type(value).__name__}' if leaf else None
    # return Element(
    #     'td',
    #     value_e(value, leaf),
    #     clazz=data_type,
    #     style=f"#{bg[0]:02x}{bg[1]:02x}{bg[2]:02x};" if bg is not None else None
    # ).__str__()
    return td_value_with_style(value, f'style="background: #{bg[0]:02x}{bg[1]:02x}{bg[2]:02x};"' if bg is not None else '')


def td_value_with_style(value, style_attr):
    leaf = is_primitive(value)
    data_type = f'{type(value).__name__}' if leaf else ''
    s = f'<td class="{data_type}" {style_attr}>'
    s += value_str(value, leaf)
    s += '</td>'
    return s


def list_attr(attr, *values):
    return f" {attr}='" + " ".join(values) + "'" if len(values) > 0 else ""


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


def value_e(value: Optional[Any], leaf: bool):
    return span0(value) if leaf else text(value)


def array_entry(i: int, contents: Optional[Any]):
    # return span(index(i) + span(contents, clazz='none' if contents is None else None), clazz='ae')
    return span0(
        index(i),
        span0(contents, clazz='none' if contents is None else None), clazz='ae').__str__()


def index(contents: Optional[Any]):
    # return f'<span class="index">{text(contents)}</span>'
    return span0(contents, clazz='index')


def span(*contents, clazz=None):
    return str(Element('span', *contents, clazz=clazz))
    # return str(span0(contents, clazz=clazz))


def span0(*contents, **attrs):
    return Element('span', *contents, **attrs)


def text(contents: Optional[Any]):
    return "" if contents is None else str(contents)


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


def child_by_path(value, path):
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


class Element:
    tag: str
    contents: Iterable[Any]
    attrs: Dict[str, Union[str, Iterable[str]]]

    def __init__(self, tag, *contents, **attrs):
        self.tag = tag
        self.contents = contents
        self.attrs = attrs

    def __str__(self):
        separator = '\n' if self.contents else ''
        attrs_str = self.attrs_str()
        open_tag = f'<{self.tag}{" " + attrs_str if attrs_str else ""}>'
        close_tag = f'</{self.tag}>'
        return open_tag + separator.join(str(element) for element in self.contents if element is not None) + close_tag

    def attrs_str(self):
        return ' '.join((
            f'{k if k != "clazz" else "class"}="{Element.attr_value_str(v)}"'
            for k, v in self.attrs.items()
            if v is not None
        ))

    @staticmethod
    def attr_value_str(v: Union[str, Iterable[str]]):
        return v if type(v) is str else ' '.join((item for item in v if item is not None))


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

    print(PageNode(node(j, None, False), presentation.get("title", "")))


if __name__ == "__main__":
    try:
        main()
    except JSONDecodeError as ex:
        stderr_print("Reads json. Outputs html.")
