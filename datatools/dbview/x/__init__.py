def cleanse_dict(d: dict):
    return { k: v for k, v in d.items() if v}
