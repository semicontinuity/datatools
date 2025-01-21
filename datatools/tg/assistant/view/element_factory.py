from typing import Optional

from datatools.jv.model import JViewOptions
from datatools.jv.model.JElement import JElement
from datatools.jv.model.JString import JString


class TgElementFactory:

    def string(self, v, k, parent: Optional[JElement] = None):
        e = self.make_string_element(k, v, parent)
        e.parent = parent
        e.options = JViewOptions()
        return e

    def make_string_element(self, k, v, parent: Optional[JElement] = None):
        return JString(v, k)
