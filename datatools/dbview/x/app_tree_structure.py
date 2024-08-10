from typing import Hashable, List


class JsonTreeStructure:
    @staticmethod
    def path_is_pk_element(path: List[Hashable]):
        return len(path) == 8 and path[6] == 'key'

    @staticmethod
    def get_pk_value(path: List[Hashable]):
        return path[7]

    @staticmethod
    def get_referring_table(path: List[Hashable]) -> str:
        return path[3]

    @staticmethod
    def is_self_field_name(path):
        return len(path) == 4 and path[0:3] == ['ENTITY', 'data', 'self']

    @staticmethod
    def self_field_name(path):
        return path[3]
