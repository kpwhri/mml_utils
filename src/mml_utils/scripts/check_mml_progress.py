"""
Check Metamaplite's progress in a particular directory.
"""
import pathlib
import time
from datetime import datetime, timedelta

import click
from loguru import logger


@click.command()
@click.argument('outdir', type=click.Path(exists=True, file_okay=False, path_type=pathlib.Path))
@click.option('--textfile-ext', type=str, default='',
              help='Extension (if any) for textfiles.')
@click.option('--mmlout-ext', type=str, default='.json',
              help='Extension for metamaplite output files (e.g., ".json").')
@click.option('--repeat-hours', type=float, default=None,
              help='Re-run the progress check every this many hours '
                   '(defaults to 24h if `--repeat-end-after-*` argument supplied)')
@click.option('--repeat-end-after-hours', type=float, default=None,
              help='Stop running after this many hours (defaults to never stop).')
@click.option('--repeat-end-after-datetime', type=click.DateTime(), default=None,
              help='Do not re-run after this datetime.')
def check_mml_progress_repeat(outdir: pathlib.Path, *, textfile_ext='', mmlout_ext='.json',
                              repeat_hours=None, repeat_end_after_hours=None, repeat_end_after_datetime=None):
    """

    :param repeat_end_after_datetime:
    :param repeat_end_after_hours:
    :param repeat_hours:
    :param outdir: directory containing text files and metamaplite
    :param textfile_ext:
    :param mmlout_ext:
    :return:
    """
    if repeat_hours:
        if not isinstance(repeat_hours, (int, float)):
            repeat_hours = 24
        logger.info(f'Checking progress every {repeat_hours} hours.')
    if repeat_end_after_hours:
        repeat_end_after_datetime2 = datetime.now() + timedelta(hours=repeat_end_after_hours)
        if repeat_end_after_datetime:
            repeat_end_after_datetime = max((repeat_end_after_datetime2, repeat_end_after_datetime))
        else:
            repeat_end_after_datetime = repeat_end_after_datetime2
        logger.info(f'Stopping after {repeat_end_after_datetime}')
        if not repeat_hours:
            repeat_hours = 24

    while True:
        logger.info(f'Calculating Metamaplite Progress.')
        check_mml_progress(outdir, textfile_ext=textfile_ext, mmlout_ext=mmlout_ext)
        logger.info(f'Completed Metamaplite Progress Calculation.')
        if not repeat_hours:
            break
        if repeat_end_after_datetime:
            if datetime.now() > repeat_end_after_datetime:
                break
        logger.info(f'Sleeping for {repeat_hours} hours. Next check: {datetime.now() + timedelta(hours=repeat_hours)}')
        time.sleep(repeat_hours * 60 * 60)


def check_mml_progress(outdir: pathlib.Path, *, textfile_ext='', mmlout_ext='.json'):
    completed = 0
    total = 0
    for f in outdir.iterdir():
        if f.suffix == textfile_ext:
            if (outdir / f'{f.stem}{mmlout_ext}').exists():
                completed += 1
            total += 1
    logger.info(f'Completed {completed} / {total}: {100.0 * completed/total:.02f}%')


if __name__ == '__main__':
    check_mml_progress_repeat()
