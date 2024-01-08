from datatools.util.frozendict import FrozenDict


def is_primitive(obj):
    return obj is None or type(obj) is int or type(obj) is float or type(obj) is bool or type(obj) is str


def to_hashable(obj):
    if is_primitive(obj):
        return obj
    elif isinstance(obj, dict):
        return FrozenDict(**{k: to_hashable(v) for k, v in obj.items()})
    elif isinstance(obj, list):
        return tuple(to_hashable(e) for e in obj)


def to_jsonisable(obj):
    if obj is ...:
        return None
    if is_primitive(obj):
        return obj
    elif isinstance(obj, dict) or isinstance(obj, FrozenDict):
        if all((is_primitive(key) for key in obj)):
            return {
                key: to_jsonisable(value) for key, value in obj.items() if value is not None
            }
        else:
            return [
                {"key": to_jsonisable(key), "value": to_jsonisable(value)} for key, value in obj.items() if value is not None
            ]
    elif isinstance(obj, set):
        return to_jsonisable(list(obj))
    elif isinstance(obj, list) or isinstance(obj, tuple):
        return [to_jsonisable(e) for e in obj]
    elif isinstance(obj, bytearray):
        return [e for e in obj]
    else:
        return to_jsonisable(obj.__dict__)


def ext_jsonisable(func):
    return lambda obj: to_jsonisable(func(obj))
