import dataclasses


def is_primitive(obj):
    return obj is None or type(obj) is int or type(obj) is float or type(obj) is bool or type(obj) is str


def to_jsonisable(obj):
    if is_primitive(obj):
        return obj
    elif isinstance(obj, dict):
        if all((is_primitive(key) for key in obj)):
            return {
                key: to_jsonisable(value) for key, value in obj.items()
            }
        else:
            return [
                {"key": to_jsonisable(key), "value": to_jsonisable(value)} for key, value in obj.items()
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


def dataclass_from_dict(klass, d):
    try:
        fieldtypes = {f.name:f.type for f in dataclasses.fields(klass)}
        return klass(**{f:dataclass_from_dict(fieldtypes[f],d[f]) for f in d})
    except:
        return d
