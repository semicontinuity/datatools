#!/usr/bin/env python3

from util.html.elements import html, head, body, style, script


def page_node(column_count: int, contents):
    return html(

        head(
            style(
                '''
body {font-family: monospace; display: inline-block; background: #F0F0E0; margin: 0;}
thead {border: solid 1px darkgray;}
table {border-collapse: collapse; padding: 0; white-space: nowrap;}
table {background: white;}
th {border-top: solid 1px darkgrey; border-bottom: solid 1px darkgrey; background: #DDD; padding-left: 0.5ex; padding-right: 0.5ex;}
td {border-top: solid 1px #CCC; border-bottom: solid 1px #CCC; padding: 0;}
td {border-left: solid 2px darkgrey;}
td {padding-left: 0.5em; padding-right: 0.5em;}
th {border-left: solid 2px darkgrey;}

td:last-child { width: 100%; }

td.details {background: #D0D0D0;}
tbody.regular th.details {display: none;}
tbody.regular td.details {display: none;}
tbody.regular span.expanded {display: none;}
tbody.regular span.regular  {cursor: zoom-in;}

tbody.expanded span.regular {display: none;}
tbody.expanded span.expanded {cursor: zoom-out;}
thead th {cursor: zoom-out;}

.compact {display:none;}

span { white-space: nowrap;}
pre {font-size: 144%;}

.tooltip {
  position: relative;
  display: inline-block;
}

.tooltip .tooltip-text {
  visibility: hidden;
  background-color: black;
  color: #fff;
  text-align: center;
  padding: 4px;
  border-radius: 4px;
  position: absolute;
  z-index: 1;
}

.tooltip:hover .tooltip-text {
  visibility: visible;
} 
                ''' + "\n".join(hide_rules(n) for n in range(2, column_count + 2))
            ),
            script('''

function toggleClass(element, className) {
  const classes = element.classList;
  if (classes.contains(className)) {
     classes.remove(className);
  } else {
     classes.add(className);
  }
}

function toggleParentClass(e, tagName, className) {
  while (true) {
    if (e === null) return;
    if (e.tagName === tagName) {
      break;
    }
    e = e.parentElement;
  }
  toggleClass(e, className);
}
            
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
            contents
        )
    )


def hide_rules(n):
    return f"""
table.hide-c-{n}>tbody>tr>td:nth-child({n})>span {{display:none;}}
table.hide-c-{n}>thead>tr>th:nth-child({n})>span {{display:none;}}
table.hide-c-{n}>thead>tr>th:nth-child({n})>span.compact {{display:inherit;}}
table.hide-c-{n}>thead>tr>th:nth-child({n}) {{cursor: zoom-in;}}
"""
