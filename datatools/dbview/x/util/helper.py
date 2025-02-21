import os


def get_env(key):
    return get_required_prop(key, os.environ)


def get_required_prop(key, props):
    value = props.get(key)
    if value is None:
        raise Exception(f'Must set {key}')
    return value
