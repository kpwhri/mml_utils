"""
Copy files from a completed MML directory to a new one to re-run MML.
"""
from datetime import datetime
from loguru import logger
import pathlib
import shutil

import click


@click.command()
@click.option('--source', type=click.Path(exists=True, path_type=pathlib.Path),
              help='Source directory containing text files for processing by metamap;'
                   ' notes are assumed to have no extension or ".txt"')
@click.option('--dest', type=click.Path(exists=False, path_type=pathlib.Path),
              help='Destination directory (should not exist) to write text files for processing by metamap')
@click.option('--filelist-dir', type=click.Path(exists=True, path_type=pathlib.Path),
              help='Directory to write filelist; defaults to parent of `dest`.')
@click.option('--rebuild-ok', is_flag=True)
def copy_to_new_mml_directory(source: pathlib.Path, dest: pathlib.Path,
                              filelist_dir: pathlib.Path = None, rebuild_ok=False):
    """

    :param rebuild_ok: okay to overwrite existing files
    :param source:
    :param dest: uncreated destination directory; set rebuild_ok=True to allow existing directory
    :param filelist_dir:
    :return:
    """
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    if filelist_dir is None:
        filelist_dir = dest.parent
    dest.mkdir(exist_ok=rebuild_ok)
    total_moved = 0
    with open(filelist_dir / f'filelist_{dest.name}_{now}.txt', 'w') as out:
        for file in source.iterdir():
            if file.suffix and file.suffix != '.txt':
                continue
            shutil.copy(file, dest)
            out.write(f'{str(dest / file.name)}\n')
            total_moved += 1
            if total_moved % 10000 == 0:
                logger.info(f'Moved {total_moved} to {dest}.')
    logger.info(f'Done! Moved {total_moved} to {dest}.')


if __name__ == '__main__':
    copy_to_new_mml_directory()
