from typing import List, Tuple

from datatools.json.structure_discovery import DictDescriptor


def compute_paths_of_table_leaves(descriptor: DictDescriptor, path: List[str] = None) -> List[Tuple[str]]:
    assert descriptor.is_dict()
    if path is None:
        path = []
    result = []
    for name, value_descriptor in descriptor.dict.items():
        if value_descriptor.is_dict():
            result += compute_paths_of_table_leaves(value_descriptor, path + [name])
        else:
            result.append(tuple(path + [name]))
    return result
