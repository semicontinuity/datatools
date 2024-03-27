from typing import TypeVar, Generic, List

from datatools.misc.tree_table.jv.model.JValueElement import JValueElement

V = TypeVar('V')


class JPrimitiveElement(Generic[V], JValueElement[V]):
    def sub_elements(self) -> List[JValueElement]: return []
