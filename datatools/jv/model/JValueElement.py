from typing import TypeVar, Generic, Optional, List

from datatools.jv.model.JElement import JElement

V = TypeVar('V')


class JValueElement(Generic[V], JElement):
    value: V
    packed_size: int

    def __init__(self, name: Optional[str], value: V, indent=0, has_trailing_comma=False) -> None:
        super().__init__(name, indent, has_trailing_comma)
        self.value = value
        self.packed_size = 1

    def sub_elements(self) -> List['JValueElement']: pass
