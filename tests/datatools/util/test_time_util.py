from datatools.util.time_util import infer_timestamp_format, parse_timestamp


def test__1():
    assert infer_timestamp_format('2020-01-01')[0] == '%Y-%m-%d'
    assert infer_timestamp_format('2020-01-01')[0] == '%Y-%m-%d'
    assert infer_timestamp_format('2021-03-16T14:01:43.376Z')[0] == '%Y-%m-%dT%H:%M:%S.%f%z'

    assert parse_timestamp('2021-03-16T14:01:43.376Z') == 1615903303.376


def test__2():
    timestamp_format = infer_timestamp_format('2024-09-12T13:04:38.227452876Z')
    # format_ = timestamp_format[0]
    print(timestamp_format)
    # assert format_ == '%Y-%m-%d'
    parse_timestamp('2024-09-12T13:04:38.227452876Z')


if __name__ == '__main__':
    test__2()