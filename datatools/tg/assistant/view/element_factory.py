from typing import Optional

from datatools.jv.model import JViewOptions
from datatools.tg.assistant.view.model.VElement import VElement
from datatools.tg.assistant.view.model.VString import VString


class TgElementFactory:

    def string(self, v, k, parent: Optional[VElement] = None):
        e = self.make_string_element(v, parent)
        e.parent = parent
        e.options = JViewOptions()
        return e

    def make_string_element(self, v, parent: Optional[VElement] = None):
        return VString(v)
