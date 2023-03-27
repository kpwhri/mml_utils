"""
TODO: In progress

Requires: pandas; xlsxwriter
"""

from pathlib import Path

import click

from mml_utils.phenorm.afep_summary import build_afep_excel


@click.command()
@click.argument('afep_path', type=click.Path(path_type=Path, file_okay=False))
@click.option('--how', type=str,
              help='How to determine length of columns (mean, median, max)')
def _build_afep_excel(afep_path: Path, how='mean'):
    """Search in `afep_path` for directories containing `-selected` to find csv files with selected features"""
    build_afep_excel(afep_path, how=how)


if __name__ == '__main__':
    _build_afep_excel()
