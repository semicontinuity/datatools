from datatools.util.time_series_util import time_series_list_summary


def test__1():
    assert time_series_list_summary(
        [{"ts": "2020-01-01", "value": 1}, {"ts": "2020-01-02", "value": 2}]
    ) == ('ts', '%Y-%m-%d', 1577826000.0, 1577912400.0)
