import datetime
from collections import defaultdict
from typing import Dict

from datatools.json.util import is_primitive
from datatools.jt.model.metadata import Metadata
from datatools.jt.model.values_info import ColumnsValuesInfo, ValuesInfo
from datatools.util.logging import debug


def compute_column_values_info(data, metadata: Metadata) -> ColumnsValuesInfo:
    info_map = defaultdict(ValuesInfo)
    compute_values_info(data, info_map, metadata)
    return ColumnsValuesInfo(columns=info_map)


def compute_values_info(data, info_map: Dict[str, ValuesInfo], metadata: Metadata):
    debug('compute_values_info', info_map=info_map)
    for record in data:
        for key, value in record.items():

            column_metadata = metadata.columns[key]
            value_f = single_key_of_dict if column_metadata.has_one_dict_key else quasi_primitive_value

            info = info_map[key]
            value = value_f(value)

            # if value is ...:
            #     del info_map[key]

            value_as_string = str(value)

            if info.count is None:
                info.count = 0
            if value is not None:
                info.count += 1

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


def quasi_primitive_value(value):
    if value is None:
        return None
    if is_primitive(value) or type(value) is datetime.datetime:
        return value
    return ...


def single_key_of_dict(value):
    # if value is None:
    #     return None
    if is_primitive(value) or len(value) != 1:
        return ...
    return list(value)[0]
