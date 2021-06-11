from datatools.util.time_util import infer_timestamp_format, parse_timestamp


def test__1():
    assert infer_timestamp_format('2020-01-01')[0] == '%Y-%m-%d'
    assert infer_timestamp_format('2021-03-16T14:01:43.376Z')[0] == '%Y-%m-%dT%H:%M:%S.%f%z'

    assert parse_timestamp('2021-03-16T14:01:43.376Z') == 1615903303.376
