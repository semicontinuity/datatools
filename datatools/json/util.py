import dataclasses

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
    if is_primitive(obj):
        return obj
    elif isinstance(obj, dict):
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


def dataclass_from_dict(klass, d, klass_map = None):
    if type(klass) is str and klass_map:
        klass = klass_map[klass]

    if not dataclasses.is_dataclass(klass) and '__origin__' in klass.__dict__:
        if klass.__origin__ is dict:
            sub_data_class = klass.__args__[1]
            r = {}
            for f in d:
                r[f] = dataclass_from_dict(sub_data_class, d[f], klass_map)
            return r
        if klass.__origin__ is list:
            sub_data_class = klass.__args__[0]
            r = []
            for i in d:
                r.append(dataclass_from_dict(sub_data_class, i, klass_map))
            return r
        if klass.__origin__ is set:
            sub_data_class = klass.__args__[0]
            r = set()
            for i in d:
                r.add(dataclass_from_dict(sub_data_class, i, klass_map))
            return r

    try:
        if "type" in d:
            klass = klass_map[d["type"]]
        fieldtypes = {f.name: f.type for f in dataclasses.fields(klass)}
        res = {f: dataclass_from_dict(fieldtypes[f], d[f], klass_map) for f, v in d.items() if f != 'type'}
        return klass(**res)
    except:
        # 'regular' case when d is not dataclass (code!)
        return d
