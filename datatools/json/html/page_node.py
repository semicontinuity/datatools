from string import Template


class PageNode:
    html_template = Template("""<html lang="en">
<head>
<title>$title</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<link rel="icon" href="data:,">

<style>
body {font-family: monospace; display: inline-block; background: #F0F0E0; margin: 0;}
main {display: inline-flex; border-left: solid 2px darkgrey; border-right: solid 2px darkgrey;}
thead {border: solid 1px darkgray;}
table {border-collapse: collapse; padding: 0;}
//table.ov { width:100%; }
//.a { width: 100%;}
.ae { display: inline-block; white-space: nowrap;}
.index {border: solid 1px darkcyan; color: darkcyan;}
div.regular>span.header    {display: none;}
div.collapsed2>span.header {display: block; font-weight: bold; background: lightgray; border: solid 1px darkgray;}
div.collapsed2>span.ae {display: none;}
div.collapsed2>table {display: none;}
tr.collapsed2>td {display: none;}
.none {background: darkgray;}
span { white-space: pre;}
//td {border: solid 1px #CCC; padding-left: 0.25em; padding-right: 0.25em;}
th {border-top: solid 1px darkgrey; border-bottom: solid 1px darkgrey; background: #DDD; padding-left: 0.5ex; padding-right: 0.5ex;}
th.a {background: lightgray; }
table.aon th {border: solid 1px darkgrey; }
table.aon td {border: solid 1px darkgrey; }
table.aohwno {background: #F8F8F8; }
table.aohwno th {border: solid 1px darkgrey; border-left: solid 2px darkgrey; }
table.aohwno td {border: solid 1px darkgrey; border-left: solid 2px darkgrey; }
td {border-top: solid 1px #CCC; border-bottom: solid 1px #CCC; padding: 0;}
th.ov_th {border-right: solid 2px darkgrey; }
//tr:nth-child(odd)  td.index {background: #CCC;}
//tr:nth-child(even) td.index {background: #BBB;}
//td.a_v {width:100%;}
//td.ov_v {width:100%;}

.compact {display:none;}

$style

.plain {background: white;}
.int   {color: darkred; padding-left: 0.25em; padding-right: 0.25em;}
.float {color: darkred; padding-left: 0.25em; padding-right: 0.25em;}
.str   {color: navy; padding-left: 0.25em; padding-right: 0.25em;}
.bool  {color: darkgreen; padding-left: 0.25em; padding-right: 0.25em;}

.collapsed {display: none;}
.button {background: wheat; border: solid 1px gray;}

.overlay {
    height: 100%;
    width: 0;
    position: fixed;
    z-index: 1; /* Sit on top */
    left: 0;
    top: 0;
    background-color: rgba(255, 255, 255, 1);
    overflow-x: hidden;
    transition: 0.25s;
}

.overlay-content {
    background: #FFFFF0;
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

function _(id) { return document.getElementById(id); }

function openOverlay(text_id) {
  _('overlay-content').innerText = _(text_id).content.textContent;
  _('overlay').style.width = "100%";
  _('main').style.display="none";
}

function closeOverlay() { _('overlay').style.width = "0%"; _('main').style.display=""; }

</script>

</head>

<body>

<main id="main">
$view
</main>

<div id="overlay" class="overlay" onclick="closeOverlay()" onkeypress="closeOverlay()">
    <div id="overlay-content" class="overlay-content"></div>
</div>

$long_texts

</body>
</html>""")

    def __init__(self, root, title, tk):
        self.root = root
        self.title = title
        self.tk = tk

    def __str__(self):
        return self.html_template.substitute(
            title=self.title,
            view=str(self.root),
            style="\n".join((self.hide_rules(n) for n in range(2, 20))),
            long_texts="\n".join(f'<template id="{k}">{v}</template>' for k, v in self.tk.long_texts.items())
        )

    def hide_rules(self, n):
        return f"""
table.hide-c-{n}>tbody>tr>td:nth-child({n})>span {{display:none;}}
table.hide-c-{n}>thead>tr>th:nth-child({n})>span {{display:none;}}
table.hide-c-{n}>thead>tr>th:nth-child({n})>span.compact {{display:inherit;}}
        """
