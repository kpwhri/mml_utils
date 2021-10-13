"""
Prepare files for running metamaplite.

Take a directory with text documents (input files for metamaplite), organize them into groups of 100.000
    for subsequent processing. The subsequent processing will be done by related `run_mml.py` file.

Arguments:
    * --outpath OUTPATH
        - This is more of a workspace. Input documents are expected under `outpath`/clarity.
        - Target files (text documents) will be moved from `clarity` to `mml`
        - Files with groups of 100.000 text documents will be plaaced in `mml_lists` subdirectory.


Example:
    python build_filelists.py --outpath /path/to/dir
        - /path/to/dir
            - clarity [assumes exists with text documents]
                - 001.txt
                - 002.txt
                - etc.
            - mml [starts empty; text documents will be moved here]
                - 001.txt
                - 002.txt
                - etc.
            - mml_lists [starts empty; lists of files in `mml` directory will be placed here
                - files_[date].in_progress  [100.000 references to `mml` directory; ready for processing]
                - files_[date].in_progress  [100.000 references to `mml` directory; ready for processing]
                - files_[date].building  [currently being built; don't process]

    After, run `run_mml.py` to process all these files. Their extension will be changed to `.complete`.
"""
import pathlib
import shutil
import time
from datetime import datetime

from loguru import logger


def run(outpath: pathlib.Path, *, n_dirs=3, file_limit=100_000):
    # parameters
    clarity_path = outpath / 'clarity'
    mml_path = outpath / 'mml'
    curr_dir = 0

    # mml runs
    mml_run_path = outpath / 'mml_lists'
    mml_run_path.mkdir(exist_ok=True)
    mml_run_paths = []
    for i in range(n_dirs):
        mrpath = mml_run_path / str(i)
        mrpath.mkdir(exist_ok=True)
        mml_run_paths.append(mrpath)

    # logging
    logger.add(outpath / 'collect_for_mml_{time}.log')

    # find up to 100 files
    files = []
    logger.info(f'Collecting new files from {clarity_path}.')
    for f in clarity_path.rglob("*"):
        if f.is_dir():
            continue
        files.append(f)
        if len(files) >= file_limit:
            prepare_mml_list(files, mml_path, mml_run_paths[curr_dir])
            curr_dir = (curr_dir + 1) % n_dirs
            files = []
            logger.info('Continuing building file list.')
    prepare_mml_list(files, mml_path, mml_run_paths[curr_dir])


def prepare_mml_list(files, mml_path, mml_run_path):
    logger.info(f'Processing {len(files)} files.')
    if not files:
        return
    time.sleep(10)  # make sure these are finished writing

    logger.info(f'Moving files from {mml_path} to {mml_run_path}.')
    fp = mml_run_path / f'files_{datetime.now().strftime("%Y%m%d_%H%M%S")}.building'
    with open(fp, 'w') as out:
        for file in files:
            target = mml_path / file.name
            out.write(f'{target}\n')
            shutil.move(file, target)
    fp.rename(str(fp).replace('.building', '.in_progress'))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('-o', '--outpath', type=pathlib.Path,
                        help='Directory for output to be placed.'
                             ' Three sub-directories will be created for processing.')
    parser.add_argument('--n-dirs', dest='n_dirs', default=3,
                        help='Number of directories to place output files. (Allows MML parallel-processing.')
    parser.add_argument('--file-limit', dest='file_limit', default=100_000,
                        help='Maximum number of files to include in input files for MML.')
    run(**vars(parser.parse_args()))
