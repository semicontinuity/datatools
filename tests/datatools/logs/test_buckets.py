from datatools.logs.buckets import *


def test__compute_clusters__1():
    # load_lines.has_run = True
    # load_lines.cached_result = lines__1()
    clusters = Classifier(lines__1()).compute_clusters()
    assert clusters[0].pattern == ['fill', '-', 'ABC', '-', None]
    assert clusters[1].pattern == ['fill', '-', 'XYZ', '-', None]


def lines__1():
    return [
        'fill-ABC-1',
        'fill-ABC-1',
        'fill-ABC-2',
        'fill-ABC-2',
        'fill-XYZ-3',
        'fill-XYZ-3',
        'fill-XYZ-4',
        'fill-XYZ-4',
    ]
