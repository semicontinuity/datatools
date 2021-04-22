from dataclasses import dataclass


@dataclass
class MetaData:
    type: str


class Discovery:

    def object_descriptor(self, j):
        if j is None:
            return {'': MetaData('null')}
        elif type(j) is int:
            return {'': MetaData('int')}
        elif type(j) is float:
            return {'': MetaData('float')}
        elif type(j) is bool:
            return {'': MetaData('bool')}
        elif type(j) is str:
            return {'': MetaData('str')}
        elif isinstance(j, list):
            return self.list_descriptor(j)
        elif isinstance(j, dict):
            return self.dict_descriptor(j)
        else:
            raise AssertionError()

    def list_descriptor(self, j):
        array_descriptor = [self.object_descriptor(i) for i in j]
        if len(array_descriptor) <= 1:
            return array_descriptor

        item_descriptor = array_descriptor[0]
        if all(i == item_descriptor for i in array_descriptor):
            item_descriptor[''] = MetaData('table')
            return item_descriptor
        else:
            return array_descriptor

    def dict_descriptor(self, j):
        result = {k: self.object_descriptor(v) for k, v in j.items()}
        result[''] = MetaData('dict')
        return result
