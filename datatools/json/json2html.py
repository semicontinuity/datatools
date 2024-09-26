#!/usr/bin/env python3

# Long lists are collapsed by default, set env variable V=1 to suppress.

import json
import os
import sys
from json import JSONDecodeError

from datatools.json.html.html_toolkit_custom import *
from datatools.json.html.html_toolkit_old import OldToolkit
from datatools.json.html.page_node import PageNode
from datatools.util.logging import stderr_print
from datatools.util.meta_io import presentation_or_default


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

    ctk = CustomHtmlToolkit()
    old_tk = OldToolkit(ctk)

    print(
        PageNode(
            old_tk.node(j, None, False), presentation.get("title", ""), ctk
        )
    )


if __name__ == "__main__":
    try:
        main()
    except JSONDecodeError as ex:
        stderr_print("Reads json. Outputs html.")
