from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple, Hashable


@dataclass
class Descriptor:
    def is_array(self) -> bool:
        return type(self) is ArrayDescriptor

    def is_list(self) -> bool:
        return type(self) is ListDescriptor

    def is_dict(self) -> bool:
        return type(self) is DictDescriptor

    def is_primitive(self) -> bool:
        return type(self) is PrimitiveDescriptor


@dataclass
class PrimitiveDescriptor(Descriptor):
    primitive: str

    def __eq__(self, o) -> bool:
        if type(o) is type(self):
            return self.primitive == o.primitive
        return False

    def merge_with(self, o) -> 'PrimitiveDescriptor':
        return self


@dataclass
class DictDescriptor(Descriptor):
    dict: Dict

    def __eq__(self, o) -> bool:
        if type(o) is type(self):
            return self.dict == o.dict
        return False

    def merge_with(self, o) -> 'DictDescriptor':
        return DictDescriptor({k: v.merge_with(o.dict[k]) for k, v in self.dict.items()})


@dataclass
class ListDescriptor(Descriptor):
    list: List

    def __eq__(self, o) -> bool:
        if type(o) is type(self):
            return self.list == o.list
        return False

    def merge_with(self, o) -> 'ListDescriptor':
        return ListDescriptor([v.merge_with(o.list[k]) for k, v in enumerate(self.list)])


@dataclass
class ArrayDescriptor(Descriptor):
    array: Descriptor
    length: Optional[int] = None

    def __eq__(self, o) -> bool:
        if type(o) is type(self):
            return self.item == o.item
        return False

    def inner_item(self) -> Descriptor:
        return self.item.inner_item() if self.item.is_array() else self.item

    @property
    def item(self) -> Descriptor:
        return self.array

    def merge_with(self, o) -> 'ArrayDescriptor':
        return ArrayDescriptor(self.item, self.length if self.length == o.length else None)

    @staticmethod
    def merge(items: List) -> Descriptor:
        assert len(items) > 0

        item0 = items[0]
        for i in items:
            if i is item0:
                pass
            item0 = item0.merge_with(i)

        return item0

    @staticmethod
    def items(j):
        return j.items() if type(j) is dict else enumerate(j)


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
        item_descriptors = [(k, self.object_descriptor(v)) for k, v in j.items()]
        if len(item_descriptors) == 0:
            return DictDescriptor({})

        item0_descriptor = item_descriptors[0]
        if len(item_descriptors) > 1 and type(item0_descriptor[1]) is not PrimitiveDescriptor and all(i[1] == item0_descriptor[1] for i in item_descriptors):
            return ArrayDescriptor(ArrayDescriptor.merge([i[1] for i in item_descriptors]), len(item_descriptors))
        else:
            return DictDescriptor({i[0]: i[1] for i in item_descriptors})

    def list_descriptor(self, j):
        item_descriptors: list = [self.object_descriptor(i) for i in j]
        if len(item_descriptors) == 0:
            return ListDescriptor([])

        item0_descriptor = item_descriptors[0]
        if all(i == item0_descriptor for i in item_descriptors):
            return ArrayDescriptor(ArrayDescriptor.merge(item_descriptors), len(item_descriptors))
        else:
            return ListDescriptor(item_descriptors)

    def merge_descriptor(self, j):
        return DictDescriptor({k: self.object_descriptor(v) for k, v in j.items()})


def compute_column_paths(descriptor: DictDescriptor) -> List[Tuple[str]]:
    result = []
    compute_column_paths0(descriptor, [], result)
    return result


def compute_column_paths0(descriptor: DictDescriptor, path: List[str], result: List[Tuple[str]]):
    for name, value_descriptor in descriptor.dict.items():
        child_path = path + [name]
        if value_descriptor.is_dict() and value_descriptor.dict:
            compute_column_paths0(value_descriptor, child_path, result)
        else:
            result.append(tuple(child_path))


def compute_row_paths(j, descriptor: ArrayDescriptor) -> List[Tuple[str]]:
    result = []
    compute_row_paths0(j, descriptor, [], result)
    return result


def compute_row_paths0(j, descriptor: ArrayDescriptor, path: List[Hashable], result: List[Tuple[Hashable]]):
    for key, value in descriptor.items(j):
        child_path = path + [key]
        if descriptor.item.is_array():
            compute_row_paths0(value, descriptor.item, child_path, result)
        else:
            result.append(tuple(child_path))


def child_by_path(value, path: Tuple[Hashable, ...]) -> Tuple[bool, Optional[Hashable]]:
    for key in path:
        if value is None:
            return False, None
        if isinstance(value, dict):
            if key in value:
                value = value.get(key)
            else:
                return False, None
        elif isinstance(key, int):
            if 0 <= key < len(value):
                value = value[key]
        else:
            print(value)
            print(path)
            print(key)
            raise ValueError
    return True, value


if __name__ == "__main__":
    import sys
    import json
    from datatools.json.util import to_jsonisable
    json.dump(to_jsonisable(Discovery().object_descriptor(json.load(sys.stdin))), sys.stdout)
