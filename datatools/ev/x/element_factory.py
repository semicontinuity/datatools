from typing import Optional

from datatools.jv.model.JElement import JElement
from datatools.jv.model.JString import JString
from datatools.jv.model.factory import JElementFactory
from datatools.tui.treeview.rich_text import Style



class MyElementFactory(JElementFactory):

    class JDateTime(JString):
        def value_style(self):
            return Style(0, (0, 120, 240))

    def make_string_element(self, k, v, parent: Optional[JElement] = None):
        print(parent)
        return super().make_string_element(k, v, parent)

