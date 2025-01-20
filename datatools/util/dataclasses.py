import dataclasses

from datatools.util.logging import debug


def dataclass_from_dict(klass, d, klass_map = None):
    if type(klass) is str and klass_map:
        klass = klass_map[klass]

    is_dataclass = dataclasses.is_dataclass(klass)
    debug('dataclass_from_dict', klass=klass, is_dataclass=is_dataclass, d=d)
    if not is_dataclass:

        if not hasattr(klass, '__dict__'):
            return d

        if '__origin__' in klass.__dict__:
            debug('dataclass_from_dict', klass=klass, is_dataclass=is_dataclass, has_origin=True)
            if klass.__origin__ is dict:
                sub_data_class = klass.__args__[1]
                r = {}
                for f in d:
                    r[f] = dataclass_from_dict(sub_data_class, d[f], klass_map)
                return r
            elif klass.__origin__ is list:
                sub_data_class = klass.__args__[0]
                r = []
                for i in d:
                    r.append(dataclass_from_dict(sub_data_class, i, klass_map))
                return r
            elif klass.__origin__ is set:
                sub_data_class = klass.__args__[0]
                r = set()
                for i in d:
                    r.add(dataclass_from_dict(sub_data_class, i, klass_map))
                return r
            else:
                debug('dataclass_from_dict', klass=klass, d=d)
                raise ValueError(d)
        else:
            debug('dataclass_from_dict', klass=klass, is_dataclass=is_dataclass, has_origin=False)

    try:
        if "type" in d:
            the_type = d["type"]
            klass = klass_map[the_type]
            if the_type == 'stripes-time-series':
                debug('dataclass_from_dict', _='#####################################################')
            debug('dataclass_from_dict', the_type=the_type, klass=klass)
        field_types = {f.name: f.type for f in dataclasses.fields(klass)}
        debug('dataclass_from_dict', klass=klass, field_types=field_types)

        res = {f: dataclass_from_dict(field_types[f], d[f], klass_map) for f, v in d.items() if f != 'type' and f in field_types}

        # res = {}
        # for f, v in d.items():
        #     if f != 'type':
        #         field_type = field_types[f]
        #         debug('dataclass_from_dict', f=f, field_type=field_type, raw=d[f])
        #         value = dataclass_from_dict(field_type, d[f], klass_map)
        #         debug('dataclass_from_dict', f=f, field_type=field_type, value=value)
        #         res[f] = value

        return klass(**res)
    except:
        # 'regular' case when d is not dataclass (code!)
        debug('dataclass_from_dict', regular=True, d=d)
        return d
