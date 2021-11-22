from datatools.logs.text_classifier import with_packed_patterns, make_buckets, tokenize, annotate_lines


def test__make_buckets__1():
    res = with_packed_patterns(make_buckets(load_tokenized_strings(lines__1())), '*')
    assert list(res.keys()) == [('fill-ABC-', '*'), ('fill-XYZ-', '*')]


def load_tokenized_strings(lines):
    return [[token for token in tokenize(s)] for s in lines]


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


def test__annotate_lines__2():
    data = records__2()
    category_f = lambda p: ''.join(('*' if part is None else part) for part in p)
    annotate_lines(data, 't', '_t', category_f=category_f)
    assert data == annotated_records__2()


def records__2():
    return [
        {'t': 'fill-ABC-1'},
        {'t': 'fill-ABC-1'},
        {'t': 'fill-ABC-2'},
        {'t': 'fill-ABC-2'},
        {'t': 'fill-XYZ-3'},
        {'t': 'fill-XYZ-3'},
        {'t': 'fill-XYZ-4'},
        {'t': 'fill-XYZ-4'},
    ]


def annotated_records__2():
    return [
        {'t': 'fill-ABC-1', '_t': 'fill-ABC-*'},
        {'t': 'fill-ABC-1', '_t': 'fill-ABC-*'},
        {'t': 'fill-ABC-2', '_t': 'fill-ABC-*'},
        {'t': 'fill-ABC-2', '_t': 'fill-ABC-*'},
        {'t': 'fill-XYZ-3', '_t': 'fill-XYZ-*'},
        {'t': 'fill-XYZ-3', '_t': 'fill-XYZ-*'},
        {'t': 'fill-XYZ-4', '_t': 'fill-XYZ-*'},
        {'t': 'fill-XYZ-4', '_t': 'fill-XYZ-*'},
    ]
