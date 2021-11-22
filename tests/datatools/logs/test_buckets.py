from datatools.logs.buckets_classifier import Classifier


def test__compute_clusters__1():
    clusters = Classifier.tokenize(lines__1()).compute_clusters()
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
