import pathlib
import shutil
import subprocess

from loguru import logger


def run_mml(filename, cwd, *, output_format='files', restrict_to_sts=None):
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


def repeat_run_mml(filename, cwd, *, output_format='files', restrict_to_sts=None, max_retry=10,
                   **kwargs):
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
            total_completed = -1
            break
        logger.info(f'Retrying metamaplite by dropping failed file.')
        logger.info(f'Looking for completed/failed files to remove from next run.')
        filelist_version += 1
        with open(f'{filename}', encoding='utf8') as fh, \
                open(error_path, 'a', encoding='utf8') as err, \
                open(f'{orig_filename}_{filelist_version}', 'w', encoding='utf8') as out:
            missing_count = 0
            still_todo = 0
            for file in fh.read().split('\n'):
                outfile = pathlib.Path(f'{file}.files')
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
        if still_todo == 0:
            break
        logger.info(f'Ready to re-run metamaplite: Remaining: {still_todo}')
        filename = f'{orig_filename}_{filelist_version}'
        logger.info(f'Completed: {total_completed}')
        if filelist_version > max_retry:
            logger.error(f'Too many retries: {max_retry}; exiting process.')
    if total_completed == -1:
        logger.info(f'Completed all.')
    else:
        logger.info(f'Completed all: {total_completed}')
    return res
