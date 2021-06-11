from datatools.util.time_util import infer_timestamp_format


def test__1():
    assert infer_timestamp_format('2020-01-01')[0] == '%Y-%m-%d'
