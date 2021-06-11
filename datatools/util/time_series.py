from typing import Optional, Tuple

from datatools.util.time_util import infer_timestamp_format


def time_series_list_descriptor(data) -> Optional[Tuple[str, str]]:
    """ Returns timestamp column name """
    timestamp_formats = {}
    for record in data:
        if type(record) is dict:
            for key, value in record.items():
                if type(value) is str:
                    current_ts_format = timestamp_formats.get(key)
                    if current_ts_format != '':
                        format, _ = infer_timestamp_format(value)
                        if format != current_ts_format:
                            timestamp_formats[key] = format if current_ts_format is None else ''
                timestamp_formats[key] = ''

    good_timestamp_formats = [(k, v) for k, v in timestamp_formats.items() if v != '']
    if len(good_timestamp_formats) == 1:
        return good_timestamp_formats[0]    # timestamp field, timestamp format
    return None
