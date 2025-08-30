#!/usr/bin/env python3

# Long lists are collapsed by default, set env variable V=1 to suppress.

import json
import os
import sys
from json import JSONDecodeError

from datatools.json.html.html_toolkit_custom import *
from datatools.json.html.html_toolkit_old import OldToolkit
from datatools.json.html.page_node import PageNode
from datatools.jt2h.app_json_page import md_node, page_node
from datatools.util.logging import stderr_print
from datatools.util.meta_io import presentation_or_default
from datatools.json.util import to_jsonisable

def to_blocks_html(j, page_title: str = None):
    if os.environ.get("PIPE_HEADERS_IN"):
        print("Head", file=sys.stderr)
    presentation = presentation_or_default(default={})
    ctk = CustomHtmlToolkit()
    old_tk = OldToolkit(ctk)

    return PageNode(
        old_tk.node(j, None, False), page_title or presentation.get("title"), ctk
    )


def main():
    argv = sys.argv[1:]

    try:
        j = json.load(sys.stdin)
    except JSONDecodeError as ex:
        stderr_print("Reads json. Outputs html.")
        sys.exit(1)

    page_title = argv[argv.index('-t') + 1] if '-t' in argv else None
    yaml = '-y' in argv
    markdown = '-m' in argv
    descriptor = '-d' in argv
    path_counts = '-c' in argv

    if yaml:
        print(page_node(j, page_title))
    elif markdown:
        print(md_node(j))
    elif descriptor:
        r = OldToolkit(CustomHtmlToolkit()).descriptor_and_path_counts(j)
        print(json.dumps(to_jsonisable(r[0])))
    elif path_counts:
        r = OldToolkit(CustomHtmlToolkit()).descriptor_and_path_counts(j)
        print(json.dumps(to_jsonisable(r[1])))
    else:
        print(to_blocks_html(j, page_title))


if __name__ == "__main__":
    main()
