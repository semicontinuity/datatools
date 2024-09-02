from typing import TypeVar, Generic, List

from datatools.misc.expenses.viewer.model.JValueElement import JValueElement

V = TypeVar('V')


class JPrimitiveElement(Generic[V], JValueElement[V]):
    def sub_elements(self) -> List[JValueElement]: return []
