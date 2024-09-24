from typing import Optional

from datatools.jv.model.JElement import JElement
from datatools.jv.model.JNumber import JNumber
from datatools.jv.model.factory import JElementFactory
from datatools.tui.treeview.rich_text import Style


class MyElementFactory(JElementFactory):

    class JMyNumber(JNumber):
        def value_style(self):
            return Style(0, (240, 240, 240))

    def make_number_element(self, v, k, parent: Optional[JElement] = None):
        return JNumber(v, k)
        # return MyElementFactory.JMyNumber(v, k)

