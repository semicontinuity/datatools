from dataclasses import dataclass


@dataclass
class PrimitiveDescriptor:
    primitive: str


@dataclass
class DictDescriptor:
    dict: dict


@dataclass
class ListDescriptor:
    list: list


@dataclass
class ArrayDescriptor:
    array: object


def primitive(qualifier: str):
    return PrimitiveDescriptor(qualifier)


def with_metadata(metadata, descriptor: dict):
    descriptor[''] = metadata
    return descriptor


def metadata(descriptor: dict):
    return descriptor['']


class Discovery:

    def object_descriptor(self, j):
        if j is None:
            return primitive('null')
        elif type(j) is int:
            return primitive('int')
        elif type(j) is float:
            return primitive('float')
        elif type(j) is bool:
            return primitive('bool')
        elif type(j) is str:
            return primitive('str')
        elif isinstance(j, list):
            return self.list_descriptor(j)
        elif isinstance(j, dict):
            return self.dict_descriptor(j)
        else:
            raise AssertionError()

    def list_descriptor(self, j):
        descriptors: list = [self.object_descriptor(i) for i in j]
        if len(descriptors) == 0:
            return ListDescriptor([])

        item_descriptor = descriptors[0]
        if all(i == item_descriptor for i in descriptors):
            return ArrayDescriptor(item_descriptor)
        else:
            return ListDescriptor(descriptors)

    def dict_descriptor(self, j):
        return DictDescriptor({k: self.object_descriptor(v) for k, v in j.items()})


if __name__ == "__main__":
    import sys, json
    from datatools.json.util import to_jsonisable
    json.dump(to_jsonisable(Discovery().object_descriptor(json.load(sys.stdin))), sys.stdout)
