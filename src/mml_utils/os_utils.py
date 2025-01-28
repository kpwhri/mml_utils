import operator
import os
from pathlib import Path
from typing import Iterator


def is_windows():
    return os.name == 'nt'


def bat_or_sh():
    return 'bat' if is_windows() else 'sh'


def get_cp_sep():
    return ';' if is_windows() else ':'


def escape_space(path: str | Path) ->  str:
    return str(path).replace(' ', r'\ ').replace('(', r'\(').replace(')', r'\)')


def scandir(path: Path) -> Iterator[Path]:
    """Iterate through files in directory.
    * Prevent Path.iterdir creating an intermediate list (potentially large, memory, don't see an quick errors)
    * Code is largely taken from pathlib.Path.iterdir
    """
    root = str(path)
    remove_leading_dot = operator.itemgetter(slice(2, None))
    for entry in os.scandir(root):
        p = entry.path
        if root == '.':
            p = remove_leading_dot(p)
        path = Path(p)
        path._str = p or '.'
        yield path
