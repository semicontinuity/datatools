from typing import TypeVar, Generic, List

from datatools.jv.model.JValueElement import JValueElement

V = TypeVar('V')


class JPrimitiveElement(Generic[V], JValueElement[V]):
    def sub_elements(self) -> List[JValueElement]: return []

    def set_key(self, key: str):
        self.key = key
