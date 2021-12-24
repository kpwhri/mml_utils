"""
Run metamaplite from `mml_lists` and `mml` directory created by `build_filelists.py`.


Arguments:
    * --mml-home PATH
        - Path to install directory of Metamaplite. This will be placed as path to executable.

    * --filedir PATH
        - Path to mml_lists directory (output from `build_filelists.py`).
        - Must choose one of the numbered outputs.
        - Will only process current `in_progress` (reads at initialization; doesn't keep checking for new files)

Example:
    python.exe run_mml.py --mml-home ./public_mm_lite --filedir /path/to/dir/mml_lists/0

TODO:
    * Only runs `metamaplite.bat`, should be smarter about this decision
    * Customize restrictions to certain vocabulary subsets
"""
import pathlib

from mml_utils.run_mml import repeat_run_mml, run_mml


def run_mml_filelists_in_dir(filedir: pathlib.Path, mml_home: pathlib.Path, repeat=False):
    """

    :param repeat:
    :param filedir:
    :param mml_home: path to metmaplite instance
    :return:
    """
    for file in filedir.glob('*.in_progress'):
        if repeat:
            repeat_run_mml(file, mml_home)
        else:
            run_mml(file, mml_home)
        file.rename(str(file).replace('.in_progress', '.complete'))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('-m', '--mml-home', dest='mml_home',
                        help='Path to metamaplite home.')
    parser.add_argument('-f', '--filedir', type=pathlib.Path,
                        help='Path to directory containing files with lists of notes to process.')
    parser.add_argument('--repeat', action='store_true', default=False,
                        help='Repeatedly re-run if metamaplite fails on a file for any reason.')
    run_mml_filelists_in_dir(**vars(parser.parse_args()))
