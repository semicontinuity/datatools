from typing import TypeVar, Generic, Optional, List

E = TypeVar('E')

class TreeModel(Generic[E]):
    def get_root(self) -> E:
        pass

    def get_child(self, index: int) -> Optional[E]:
        pass

    def get_child_count(self, parent: E) -> int:
        pass

    def is_leaf(self, node: E) -> bool:
        pass
