from typing import TypeVar, Generic, List

from datatools.jv.model.JValueElement import JValueElement

V = TypeVar('V')


class JPrimitiveElement(Generic[V], JValueElement[V]):
    def sub_elements(self) -> List[JValueElement]: return []

    def set_key(self, key: str):
        self.key = key

    def set_last_in_parent(self, last_in_parent: bool):
        self.last_in_parent = last_in_parent
