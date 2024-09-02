from typing import TypeVar, Generic, Optional, List

from datatools.jv.model.JElement import JElement

V = TypeVar('V')


class JValueElement(Generic[V], JElement):
    value: V
    packed_size: int

    def __init__(self, value: V, key: Optional[str] = None, last_in_parent=False) -> None:
        super().__init__(key, last_in_parent)
        self.value = value
        self.packed_size = 1

    def sub_elements(self) -> List['JValueElement']: pass

    def get_value(self) -> V:
        return self.value

    def get_value_element(self):
        return self

    def set_key(self, key: str):
        pass

    def set_last_in_parent(self, last_in_parent: bool):
        pass

    def handle_key(self, key: str):
        pass
