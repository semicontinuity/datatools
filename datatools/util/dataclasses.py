import dataclasses

from datatools.util.logging import debug


def dataclass_from_dict(klass, d, klass_map = None):
    if type(klass) is str and klass_map:
        klass = klass_map[klass]

    is_dataclass = dataclasses.is_dataclass(klass)
    debug('dataclass_from_dict', klass=klass, is_dataclass=is_dataclass)
    if not is_dataclass and '__origin__' in klass.__dict__:
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
