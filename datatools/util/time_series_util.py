import datetime
from typing import Optional, Tuple

from datatools.util.time_util import infer_timestamp_format

# TODO: return dataclass


def time_series_list_summary(data) -> Optional[Tuple]:
    """ Returns timestamp column name, format, min ts, max ts """
    summaries = {}
    for record in data:
        if type(record) is not dict:
            return None
        for key, value in record.items():
            if type(value) is not str:
                summaries[key] = ...
                continue

            current_summary = summaries.get(key)
            if current_summary is ...:
                continue

            pattern = infer_timestamp_format(value)
            if type(pattern) is tuple:
                pattern, _ = pattern
            if pattern is None:
                summaries[key] = ...
                continue

            if pattern == 'ISO':
                ts = datetime.datetime.fromisoformat(value).timestamp()
            else:
                ts = datetime.datetime.strptime(value, pattern).timestamp()

            if current_summary is None:
                summaries[key] = pattern, ts, ts
                continue

            if current_summary[0] != pattern:
                summaries[key] = ...
                continue

            summaries[key] = pattern, min(current_summary[1], ts), max(current_summary[1], ts)

    good = [(k, v) for k, v in summaries.items() if v is not ...]

    if len(good) == 0:
        return None

    # In real-world data there were 2 different time formats in the dataset...

    # if len(good) != 1:
    #     raise ValueError(good)
    #     return None

    only = good[0]
    return only[0], only[1][0], only[1][1], only[1][2]
