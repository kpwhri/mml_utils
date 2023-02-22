import os


def is_windows():
    return os.name == 'nt'


def bat_or_sh():
    return 'bat' if is_windows() else 'sh'


def get_cp_sep():
    return ';' if is_windows() else ':'
