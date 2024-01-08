import datetime
from collections import defaultdict

from datatools.jt.logic.auto_metadata import infer_metadata0, enrich_metadata
from datatools.jt.model.metadata import ColumnMetadata, Metadata, STEREOTYPE_TIME_SERIES


def test__infer_metadata0():
    data = [
        {"key": "k1", "series": [{"ts": "2020-01-01", "value": 1}, {"ts": "2020-01-02", "value": 2}]},
        {"key": "k2", "series": [{"ts": "2020-01-03", "value": 3}, {"ts": "2020-01-04", "value": 4}]}
    ]

    column_metadata_map = defaultdict(lambda: ColumnMetadata())
    infer_metadata0(data, column_metadata_map)

    series = column_metadata_map['series']
    assert series.stereotype == STEREOTYPE_TIME_SERIES
    assert series.time_series_timestamp_field == 'ts'
    assert series.time_series_timestamp_format == '%Y-%m-%d'
    assert series.min_value == datetime.datetime.strptime("2020-01-01", '%Y-%m-%d').timestamp()
    assert series.max_value == datetime.datetime.strptime("2020-01-04", '%Y-%m-%d').timestamp()


def test__infer_metadata1():
    data = [
        {"key": "k1", "series": [{"ts": "2020-01-01T00:00:00.000Z", "value": 1}, {"ts": "2020-01-02T00:00:00.000Z", "value": 2}]},
        {"key": "k2", "series": [{"ts": "2020-01-03T00:00:00.000Z", "value": 3}, {"ts": "2020-01-04T00:00:00.000Z", "value": 4}]}
    ]

    column_metadata_map = defaultdict(lambda: ColumnMetadata())
    infer_metadata0(data, column_metadata_map)

    series = column_metadata_map['series']
    assert series.stereotype == STEREOTYPE_TIME_SERIES
    assert series.time_series_timestamp_field == 'ts'
    assert series.time_series_timestamp_format == '%Y-%m-%dT%H:%M:%S.%f%z'
    assert series.min_value == datetime.datetime.strptime("2020-01-01T00:00:00.000Z", '%Y-%m-%dT%H:%M:%S.%f%z').timestamp()
    assert series.max_value == datetime.datetime.strptime("2020-01-04T00:00:00.000Z", '%Y-%m-%dT%H:%M:%S.%f%z').timestamp()


def test__enrich_metadata():
    data = [
        {"key": "k1", "series": [{"ts": "2020-01-01T00:00:00.000Z", "value": 1}, {"ts": "2020-01-02T00:00:00.000Z", "value": 2}]},
        {"key": "k2", "series": [{"ts": "2020-01-03T00:00:00.000Z", "value": 3}, {"ts": "2020-01-04T00:00:00.000Z", "value": 4}]}
    ]
    metadata = enrich_metadata(data, Metadata())
    print(metadata)
