import os


def default_folder():
    return os.environ['HOME'] + '/boards'


def set_target_folder(folder: str):
    global _folder
    _folder = folder


def get_target_folder() -> str:
    return _folder


_folder = default_folder()