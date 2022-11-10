import os


def is_windows():
    return os.name == 'nt'


def bat_or_sh():
    return 'bat' if is_windows() else 'sh'
