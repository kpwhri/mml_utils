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
import shutil
import subprocess

from loguru import logger


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


def run_mml(filename, cwd, *, output_format='json', restrict_to_sts=None):
    restrict_to_sts = f"--restrict_to_sts={','.join(restrict_to_sts)}" if restrict_to_sts else ''
    # metamaplite
    logger.info(f'Running Metamaplite on current set (install location: {cwd})')
    cmd = (f'metamaplite.bat --filelistfn={filename} --outputformat={output_format}'
           f' --overwrite --usecontext {restrict_to_sts}'
           # f' --restrict_to_sts=topp,fndg,dsyn,sosy,lbpr'
           f''.split()
           )
    res = subprocess.run(cmd, shell=True, universal_newlines=True, cwd=cwd)
    if res.returncode != 0:
        logger.warning(f'Metamaplite returned with status code {res.returncode}.')
        logger.info(f'MML STDERR: {res.stderr}')
    return res


def repeat_run_mml(filename, cwd, *, output_format='json', restrict_to_sts=None, **kwargs):
    filelist_version = 0
    return_code = 1
    total_completed = 0
    error_path = pathlib.Path(filename).parent / 'errors.txt'

    orig_filename = filename
    filename = f'{orig_filename}_{filelist_version}'
    shutil.copy(orig_filename, filename)

    res = None
    while return_code != 0:
        res = run_mml(
            filename,
            cwd,
            output_format=output_format,
            restrict_to_sts=restrict_to_sts
        )
        return_code = res.returncode
        if return_code == 0:
            break
        logger.info(f'Retrying metamaplite by dropping failed file.')
        logger.info(f'Looking for completed/failed files to remove from next run.')
        filelist_version += 1
        with open(f'{filename}', encoding='utf8') as fh, \
                open(error_path, 'a', encoding='utf8') as err, \
                open(f'{orig_filename}_{filelist_version + 1}', 'w', encoding='utf8') as out:
            missing_count = 0
            still_todo = 0
            for file in fh.read().split('\n'):
                outfile = pathlib.Path(f'{file}.json')
                if outfile.exists():
                    total_completed += 1
                    continue
                elif missing_count == 0:  # first record assumed to be faulty
                    logger.info(f'Failed file is likely: {file}. '
                                f'Metamaplite has difficulty with control (and other) characters. '
                                f'You can retry MML on just that file.')
                    err.write(f'{file}\n')
                else:
                    still_todo += 1
                    out.write(f'{file}\n')
                missing_count += 1
        filelist_version += 1
        if still_todo == 0:
            break
        logger.info(f'Ready to re-run metamaplite: Remaining: {still_todo}')
        logger.info(f'Completed: {total_completed}')
    logger.info(f'Completed all: {total_completed}')
    return res


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
