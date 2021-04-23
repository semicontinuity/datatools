from dataclasses import dataclass
from typing import Optional, List, Any, Dict


@dataclass
class PrimitiveDescriptor:
    primitive: str

    def __eq__(self, o) -> bool:
        if type(o) is type(self):
            return self.primitive == o.primitive
        return False

    def merge_with(self, o) -> 'PrimitiveDescriptor':
        return self


@dataclass
class DictDescriptor:
    dict: Dict

    def __eq__(self, o) -> bool:
        if type(o) is type(self):
            return self.dict == o.dict
        return False

    def merge_with(self, o) -> 'DictDescriptor':
        return DictDescriptor({k: v.merge_with(o.dict[k]) for k, v in self.dict.items()})


@dataclass
class ListDescriptor:
    list: List

    def __eq__(self, o) -> bool:
        if type(o) is type(self):
            return self.list == o.list
        return False

    def merge_with(self, o) -> 'ListDescriptor':
        return ListDescriptor([v.merge_with(o.list[k]) for k, v in enumerate(self.list)])


@dataclass
class ArrayDescriptor:
    array: Any
    length: Optional[int] = None

    def __eq__(self, o) -> bool:
        if type(o) is type(self):
            return self.array == o.array
        return False

    def merge_with(self, o) -> 'ArrayDescriptor':
        return ArrayDescriptor(self.array, self.length if self.length == o.length else None)

    @staticmethod
    def merge(items: List) -> Optional[object]:
        if len(items) == 0:
            return None

        item0 = items[0]
        for i in items:
            if i is item0:
                pass
            item0 = item0.merge_with(i)

        return item0


class Discovery:

    def object_descriptor(self, j):
        if j is None:
            return PrimitiveDescriptor('null')
        elif type(j) is int:
            return PrimitiveDescriptor('int')
        elif type(j) is float:
            return PrimitiveDescriptor('float')
        elif type(j) is bool:
            return PrimitiveDescriptor('bool')
        elif type(j) is str:
            return PrimitiveDescriptor('str')
        elif isinstance(j, list):
            return self.list_descriptor(j)
        elif isinstance(j, dict):
            return self.dict_descriptor(j)
        else:
            raise AssertionError()

    def dict_descriptor(self, j):
        return DictDescriptor({k: self.object_descriptor(v) for k, v in j.items()})

    def list_descriptor(self, j):
        item_descriptors: list = [self.object_descriptor(i) for i in j]
        if len(item_descriptors) == 0:
            return ListDescriptor([])

        item_descriptor = item_descriptors[0]
        if all(i == item_descriptor for i in item_descriptors):
            return ArrayDescriptor(ArrayDescriptor.merge(item_descriptors), len(item_descriptors))
        else:
            return ListDescriptor(item_descriptors)

    def merge_descriptor(self, j):
        return DictDescriptor({k: self.object_descriptor(v) for k, v in j.items()})


if __name__ == "__main__":
    import sys
    import json
    from datatools.json.util import to_jsonisable
    json.dump(to_jsonisable(Discovery().object_descriptor(json.load(sys.stdin))), sys.stdout)
