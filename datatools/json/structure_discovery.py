from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple, Hashable


@dataclass
class Descriptor:
    def is_any(self) -> bool:
        return type(self) is AnyDescriptor

    def is_primitive(self) -> bool:
        return type(self) is PrimitiveDescriptor

    def is_array(self) -> bool:
        return self.is_uniform()

    def is_uniform(self) -> bool:
        pass

    def is_list(self) -> bool:
        pass

    def is_dict(self) -> bool:
        pass

    def merge_with(self, o) -> 'Descriptor':
        pass

    def merge_with_descriptors(self, descriptors: List['Descriptor']) -> 'Descriptor':
        descriptor0 = self
        for d in descriptors[1:]:
            descriptor0 = descriptor0.merge_with(d)
        return descriptor0

    @staticmethod
    def merge(descriptors: List['Descriptor']) -> 'Descriptor':
        assert len(descriptors) > 0

        descriptor0 = descriptors[0]
        if len(descriptors) == 1 or type(descriptor0) == AnyDescriptor:
            return descriptor0

        for d in descriptors:
            if d is descriptor0:
                continue
            if type(d) != type(descriptor0):
                return AnyDescriptor()

        return descriptor0.merge_with_descriptors(descriptors[1:])


@dataclass
class AnyDescriptor(Descriptor):
    def merge_with(self, o) -> 'AnyDescriptor':
        return self


@dataclass
class PrimitiveDescriptor(Descriptor):
    primitive: str

    def __eq__(self, o) -> bool:
        return type(o) is type(self) and self.primitive == o.primitive

    def merge_with(self, o) -> 'Descriptor':
        if type(o) != PrimitiveDescriptor or self.primitive != o.primitive:
            return AnyDescriptor()
        return self


@dataclass
class MappingDescriptor(Descriptor):
    entries: Dict[Hashable, Descriptor]
    kind: str
    uniform: bool
    length: Optional[int] = None

    def merge_with_descriptors(self, descriptors: List['MappingDescriptor']) -> 'Descriptor':
        descriptor0 = self
        if self.kind == 'dict' and all(d.kind == 'dict' for d in descriptors):
            counter = 0
            merged_items = {}

            def put_entries(d):
                nonlocal counter
                for k, v in d.entries.items():
                    counter += 1
                    existing = merged_items.get(k)
                    if existing is None:
                        merged_items[k] = v
                    else:
                        merged_items[k] = existing.merge_with(v)

            put_entries(descriptor0)
            for d in descriptors:
                put_entries(d)

            if len(merged_items) == 0:
                return MappingDescriptor(merged_items, 'dict', False, 0)
            fill_ratio = counter / ((1 + len(descriptors)) * len(merged_items))
            if fill_ratio >= 0.75:
                return MappingDescriptor(merged_items, 'dict', True, len(merged_items))
            else:
                return AnyDescriptor()

        else:
            for d in descriptors:
                if d.kind != descriptor0.kind:
                    return AnyDescriptor()
                descriptor0 = descriptor0.merge_with(d)

        return descriptor0

    def merge_with(self, o) -> Descriptor:
        if o is self:
            return self
        if type(o) != MappingDescriptor or self.kind != o.kind:
            return AnyDescriptor()

        if self.kind == 'list':
            if self.uniform and o.uniform:
                merged = self.entries[0].merge_with(o.entries[0])
                return MappingDescriptor(
                    {0: merged}, 'list', True, self.length if self.length == o.length else None
                )
            else:
                return MappingDescriptor(
                    {0: AnyDescriptor()}, 'list', False, None
                )

        if self.kind == 'dict':
            if self.entries.keys() == o.entries.keys():
                merged_items = {k: v.merge_with(o.entries[k]) for k, v in self.entries.items()}
                array = self.entries == merged_items
                return MappingDescriptor(
                    merged_items, 'dict', array, self.length if self.length == o.length else None
                )

        return AnyDescriptor()

    def is_dict(self) -> bool:
        return self.kind == 'dict'

    def is_list(self) -> bool:
        return self.kind == 'list'

    def is_uniform(self) -> bool:
        return self.uniform

    @property
    def item(self):
        for v in self.entries.values():
            return v

    def item_is_uniform(self) -> bool:
        return self.item.is_uniform()

    def item_is_dict(self) -> bool:
        return self.item.is_dict()

    def is_not_empty(self) -> bool:
        return bool(self.entries)

    def items(self):
        return self.entries

    @staticmethod
    def enumerate_entries(j):
        return j.items() if type(j) is dict else enumerate(j)

    def entry(self, k):
        item = self.item
        if item.is_any():   # if List[Any], there is only one item descriptor for all keys
            return item

        if k not in self.entries:
            raise KeyError
        return self.entries[k]

    def inner_item(self) -> Descriptor:
        item = self.item
        if type(item) is MappingDescriptor and item.kind == 'dict': # TODO
            return item
        return item.inner_item() if item.is_uniform() else item


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
            item_descriptors = {i: self.object_descriptor(v) for i, v in enumerate(j)}
            if len(item_descriptors) == 0:
                return MappingDescriptor({}, 'list', False, None)
            merged = Descriptor.merge(list(item_descriptors.values()))
            is_uniform = not merged.is_any()
            return MappingDescriptor(
                {i: merged for i, d in item_descriptors.items()},
                'list', is_uniform, len(item_descriptors) if is_uniform else None)
            # return self.array_or_list_descriptor(j)
        elif isinstance(j, dict):
            item_descriptors = {k: self.object_descriptor(v) for k, v in j.items()}
            if len(item_descriptors) == 0:
                return MappingDescriptor({}, 'dict', False, None)
            descriptors = list(item_descriptors.values())
            merged = Descriptor.merge(descriptors)
            is_uniform = not merged.is_any()
            # is_uniform = merged.is_uniform()
            if is_uniform:
                return MappingDescriptor(
                    {i: merged for i in item_descriptors},
                    'dict', is_uniform, len(item_descriptors) if is_uniform else None
                )
            else:
                return MappingDescriptor(
                    item_descriptors, 'dict', is_uniform, len(item_descriptors) if is_uniform else None
                )
            # return self.array_or_dict_descriptor(j)
        else:
            raise AssertionError()


def compute_column_paths(descriptor: Descriptor) -> List[Tuple[str]]:
    result = []
    compute_column_paths0(descriptor, [], result)
    return result


def compute_column_paths0(descriptor: Descriptor, path: List[str], result: List[Tuple[str]]):
    if type (descriptor) is AnyDescriptor:
        raise ValueError(type (descriptor))
    for name, value_descriptor in descriptor.items().items():
        child_path = path + [name]
        if value_descriptor.is_dict() and value_descriptor.items():
            compute_column_paths0(value_descriptor, child_path, result)
        else:
            result.append(tuple(child_path))


def compute_row_paths(j, descriptor: Descriptor) -> List[Tuple[str]]:
    result = []
    compute_row_paths0(j, descriptor, [], result)
    return result


def compute_row_paths0(j, descriptor: Descriptor, path: List[Hashable], result: List[Tuple[Hashable]]):
    for key, value in descriptor.enumerate_entries(j):
        child_path = path + [key]
        if descriptor.item.is_uniform() and descriptor.item.kind == 'list':
            compute_row_paths0(value, descriptor.item, child_path, result)
        else:
            result.append(tuple(child_path))


def child_by_path(value, path: Tuple[Hashable, ...]) -> Optional[Hashable]:
    """ returns ... if path is not applicable to value """
    for key in path:
        if value is None:
            return ...
        if isinstance(value, dict):
            if key in value:
                value = value.get(key)
            else:
                return ...
        elif isinstance(key, int):
            if 0 <= key < len(value):
                value = value[key]
        else:
            print('value', value)
            print('path', path)
            print(key)
            raise ValueError
    return value


if __name__ == "__main__":
    import sys
    import json
    from datatools.json.util import to_jsonisable
    json.dump(to_jsonisable(Discovery().object_descriptor(json.load(sys.stdin))), sys.stdout)
