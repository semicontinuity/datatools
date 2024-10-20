LOG_NODE_JS = '''

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
'''
