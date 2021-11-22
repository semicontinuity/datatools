from collections import defaultdict
from typing import Dict, Optional, List, Any, Tuple
from datatools.json.util import is_primitive


def array_is_matrix(array: List[Any]) -> Optional[int]:
    width = None
    for row in array:
        if not isinstance(row, list) or not all((is_primitive(cell) for cell in row)):
            return None
        row_width = len(row)
        if width is None:
            width = row_width
        else:
            if width != row_width:
                return None
    return width


def array_descriptor_and_path_counts(obj: List[Any]) -> Tuple[Optional[Dict[str, Any]], Dict[Tuple[str, ...], int]]:
    return values_descriptor_and_path_counts(obj)


def obj_descriptor_and_path_counts(obj: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Dict[Tuple[str, ...], int]]:
    return values_descriptor_and_path_counts(obj.values())


def values_descriptor_and_path_counts(values):
    """ Returns None if some child value is not dict """
    path_of_leaf_to_count = defaultdict(int)

    def update_descriptor(d, obj, p):
        if type(obj) is not dict:
            path_of_leaf_to_count[tuple(p)] += 1
            return None
        for name, value in obj.items():
            field_descriptor = d.get(name)
            if name in d and field_descriptor is None:
                # field is banned (seen as not containing an object before)
                path_of_leaf_to_count[tuple(p + [name])] += 1
                continue

            if field_descriptor is None:
                field_descriptor = {}  # first time seen

            d[name] = update_descriptor(field_descriptor, value, p + [name])
        return d

    descriptor: Dict = {}
    path = []
    for item in values:
        descriptor = update_descriptor(descriptor, item, path)
        if descriptor is None:
            return None, path_of_leaf_to_count
    return descriptor, path_of_leaf_to_count


def prune_sparse_leaves(descriptor: Dict[str, Any], path_of_leaf_to_count: Dict[Tuple[str, ...], int], length: int):
    d = {}
    pruned = []
    for root, value_descriptor in descriptor.items():
        occupancies = [occupancy for column_id, occupancy in path_of_leaf_to_count.items() if column_id[0] == root]
        if len(occupancies) == 0:
            continue
        min_column_occupancy = min(occupancies)
        if min_column_occupancy <= 0.5 * length:    # or better, compute total occupancy
            # pruned[root] = value_descriptor
            pruned.append(root)
        else:
            d[root] = value_descriptor

    for root in pruned:
        del descriptor[root]

    d = None if len(descriptor) == 0 else descriptor
    return d, pruned


def compute_paths_of_leaves(descriptor, path: List[str] = None) -> List[Tuple[str]]:
    if path is None:
        path = []
    result = []
    for name, value_descriptor in descriptor.items():
        if value_descriptor is None:
            result.append(tuple(path + [name]))
        else:
            result += compute_paths_of_leaves(value_descriptor, path + [name])
    return result


def number_of_columns(descriptor: Optional[Dict[str, Any]]):
    if descriptor is None:
        return 1
    return sum([number_of_columns(sub_d) for name, sub_d in descriptor.items()])


def items_at_level(descriptor: Optional[Dict[str, Any]], level, result=None, current_level=0):
    if result is None:
        result = []
    # stderr_print("items_at_level", d, "current_level", current_level, "level", level)
    if current_level == level - 1:
        for name, value in descriptor.items():
            result.append((name, value))
    else:
        for name, value in descriptor.items():
            if value is not None:
                items_at_level(value, level, result, current_level + 1)
    return result


def depth_of(descriptor):
    """ If descriptor has sub-fields, than returns the number of items in the path to the deepest child """
    if descriptor is None:
        return 1
    else:
        return 1 + max([depth_of(value) for name, value in descriptor.items()], default=0)
