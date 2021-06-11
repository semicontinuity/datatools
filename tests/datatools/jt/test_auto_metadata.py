from collections import defaultdict

from datatools.jt.auto_metadata import infer_metadata0, ColumnMetadata


def test__infer_metadata0():
    data = [
        {"key": "k1", "series": [{"ts": "2020-01-01", "value": 1}, {"ts": "2020-01-02", "value": 2}]},
        {"key": "k2", "series": [{"ts": "2020-01-03", "value": 3}, {"ts": "2020-01-04", "value": 4}]}
    ]

    column_metadata_map = defaultdict(lambda: ColumnMetadata(set(), {}))
    infer_metadata0(data, column_metadata_map)

    series = column_metadata_map['series']
    assert series.stereotype == 'time_series'
    assert series.time_series_timestamp_field == 'ts'
    assert series.time_series_timestamp_format == '%Y-%m-%d'
    assert series.time_series_timestamp_min == 1577826000.0
    assert series.time_series_timestamp_max == 1578085200.0