from typing import TypeVar, Generic, List

from datatools.jv.model.JValueElement import JValueElement

V = TypeVar('V')


class JPrimitiveElement(Generic[V], JValueElement[V]):
    def __iter__(self):
        yield self

    def sub_elements(self) -> List[JValueElement]: return []
