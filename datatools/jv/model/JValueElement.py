from typing import TypeVar, Generic, Optional, List

from datatools.jv.model.JElement import JElement

V = TypeVar('V')


class JValueElement(Generic[V], JElement):
    value: V
    packed_size: int

    def __init__(self, value: V, key: Optional[str] = None, indent=0, last_in_parent=True) -> None:
        super().__init__(key, indent, last_in_parent)
        self.value = value
        self.packed_size = 1

    def sub_elements(self) -> List['JValueElement']: pass
