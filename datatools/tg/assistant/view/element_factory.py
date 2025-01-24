from typing import Optional

from datatools.jv.model import JViewOptions
from datatools.tg.assistant.view.model.VElement import VElement
from datatools.tg.assistant.view.model.VSummary import VSummary


class TgElementFactory:

    def summary(self, v):
        e = self.make_summary(v)
        e.options = JViewOptions()
        return e

    def make_summary(self, v, parent: Optional[VElement] = None):
        return VSummary(v)
