import os
from pathlib import Path


def is_windows():
    return os.name == 'nt'


def bat_or_sh():
    return 'bat' if is_windows() else 'sh'


def get_cp_sep():
    return ';' if is_windows() else ':'


def escape_space(path: str | Path) ->  str:
    return str(path).replace(' ', r'\ ').replace('(', r'\(').replace(')', r'\)')
