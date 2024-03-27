from typing import TypeVar, Generic, Optional, List

from datatools.misc.tree_table.jv.model.JElement import JElement

V = TypeVar('V')


class JValueElement(Generic[V], JElement):
    value: V
    packed_size: int

    def __init__(self, value: V, key: Optional[str] = None, indent=0, last_in_parent=True) -> None:
        super().__init__(value, key, indent, last_in_parent)
        self.value = value
        self.packed_size = 1

    def sub_elements(self) -> List['JValueElement']: pass

    def get_value(self) -> V:
        return self.value

    def get_value_element(self):
        return self

    def get_selector(self):
        if type(self.key) is int:
            return '[' + str(self.key) + ']'
        else:
            return '.' + self.key
