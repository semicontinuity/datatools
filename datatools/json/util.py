from dataclasses import is_dataclass, dataclass


def is_primitive(obj):
    return obj is None or type(obj) is int or type(obj) is float or type(obj) is bool or type(obj) is str


def to_jsonisable(obj):
    if is_dataclass(obj):
        return obj.__dict__
    elif isinstance(obj, dict):
        if all((is_primitive(key) for key in obj)):
            return obj
        else:
            return [
                {"key": to_jsonisable(key), "value": to_jsonisable(value)} for key, value in obj.items()
            ]
    elif isinstance(obj, set):
        return to_jsonisable(list(obj))
    elif isinstance(obj, list):
        return [to_jsonisable(e) for e in obj]
    else:
        return obj


def ext_jsonisable(func):
    return lambda obj: to_jsonisable(func(obj))