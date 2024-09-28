#!/usr/bin/env python3
import json
import sys
from json import JSONDecodeError

from datatools.jt2h.log_node import Log
from datatools.util.logging import stderr_print
from util.html.elements import html, head, body, style, script


def data():
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    j = json.loads(s)
    return j



def main():
    j = data()
    columns = ['time', 'level', 'method', 'requestID', 'msg']

    h = html(

        head(
            style(
                '''
                body {font-family: monospace; display: inline-block; background: #F0F0E0; margin: 0;}
                thead {border: solid 1px darkgray;}
                table {border-collapse: collapse; padding: 0;}
                table {background: white;}
                th {border-top: solid 1px darkgrey; border-bottom: solid 1px darkgrey; background: #DDD; padding-left: 0.5ex; padding-right: 0.5ex;}
                td {border-top: solid 1px #CCC; border-bottom: solid 1px #CCC; padding: 0;}
                td {border-left: solid 2px darkgrey;}
                td {padding-left: 0.25em; padding-right: 0.25em;}
                th {border-left: solid 2px darkgrey;}
                
                td:last-child { width: 100%; }
                
                td.details {background: #D0D0D0;}

                tbody.regular th.details {display: none;}
                tbody.regular td.details {display: none;}

                tbody.regular span.expanded {display: none;}
                tbody.regular span.regular  {cursor: zoom-in;}
                tbody.expanded span.regular {display: none;}
                tbody.expanded span.expanded {cursor: zoom-out;}
                
                .key {font-color: blue;}
                
                pre {font-size: 144%;} 
                ''' + "\n".join(hide_rules(n) for n in range(2, len(columns) + 2))
            ),
            script('''
function swapClass(element, tagName, class1, class2) {
  while (element.tagName !== tagName) element = element.parentElement;
  const classes = element.classList;
  if (classes.contains(class1)) {
     classes.remove(class1);
     classes.add(class2);
  } else {
     classes.remove(class2);
     classes.add(class1);
  }
}
                  ''')
        ),

        body(
            Log(j, columns)
        )
    )

    print(h)


def hide_rules(n):
    return f"""
table.hide-c-{n}>tbody>tr>td:nth-child({n})>span {{display:none;}}
table.hide-c-{n}>thead>tr>th:nth-child({n})>span {{display:none;}}
table.hide-c-{n}>thead>tr>th:nth-child({n})>span.compact {{display:inherit;}}
"""


if __name__ == "__main__":
    main()
