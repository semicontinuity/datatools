from collections import defaultdict
from typing import Dict

from datatools.json.util import is_primitive
from datatools.jt.model.metadata import Metadata
from datatools.jt.model.values_info import ColumnsValuesInfo, ValuesInfo


def compute_column_values_info(data, metadata: Metadata) -> ColumnsValuesInfo:
    info_map = defaultdict(ValuesInfo)
    compute_values_info(data, info_map, metadata)
    return ColumnsValuesInfo(columns=info_map)


def compute_values_info(data, info_map: Dict[str, ValuesInfo], metadata: Metadata):
    for record in data:
        for key, value in record.items():
            column_metadata = metadata.columns[key]
            value_f = single_key_of_dict if column_metadata.has_one_dict_key else primitive_value

            info = info_map[key]
            if info.count is None:
                info.count = 0
            info.count += 1

            value = value_f(value)
            if value is ...:
                del info_map[key]

            value_as_string = str(value)

            dict_index = info.dictionary.get(value_as_string)
            if dict_index is None:
                dict_index = len(info.dictionary)
            info.dictionary[value_as_string] = dict_index

            non_unique_value_count = info.non_unique_value_counts.get(value_as_string)
            if non_unique_value_count is None:
                if value_as_string in info.unique_values:
                    info.unique_values.remove(value_as_string)
                    info.non_unique_value_counts[value_as_string] = 2
                else:
                    info.unique_values.add(value_as_string)
            else:
                info.non_unique_value_counts[value_as_string] = non_unique_value_count + 1


def primitive_value(value):
    if value is ... or value is None or not is_primitive(value):
        return ...
    else:
        return value


def single_key_of_dict(value):
    # if value is None:
    #     return None
    if is_primitive(value) or len(value) != 1:
        return ...
    return list(value)[0]
