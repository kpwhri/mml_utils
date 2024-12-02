"""
Remove already completed from filelist.

"""
import datetime
from pathlib import Path

import click
from loguru import logger


@click.command()
@click.argument('filelist', type=click.Path(path_type=Path, dir_okay=False))
@click.option('--output-format', type=str, default='json',
              help='Output format (e.g., json, mmi, xmi)')
@click.option('--output-directory', default=None, type=click.Path(path_type=Path, file_okay=False),
              help='Output directory if different than input.')
def clean_filelist(filelist: Path, output_directory: Path = None, output_format='json'):
    now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    bk = filelist.rename(str(filelist) + f'.{now}.bk')
    logger.info(f'Backup of original filelist at {bk}.')
    last_line = None  # keep pointer to last completed to force re-running this one
    cnt = 0
    undone = 0
    with open(filelist, 'w') as out:
        with open(bk) as fh:
            for line in fh:
                p = Path(line.strip().removesuffix('.txt') + f'.{output_format}')
                if output_directory:
                    p = output_directory / p.name
                if p.exists():
                    last_line = line
                    cnt += 1
                    continue
                if last_line is not None:
                    logger.info(f'Found {cnt} already processed.')
                    logger.info(f'Setting last completed to be repeated in case of incomplete output: {last_line}')
                    out.write(last_line)
                    last_line = None
                out.write(line)
                undone += 1
    logger.info(f'Finished writing {undone} uncompleted to filelist.')


if __name__ == '__main__':
    clean_filelist()