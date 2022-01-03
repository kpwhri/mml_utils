"""
More generic form of `run_mml` which allows running repeatedly against a single output file.
"""
import pathlib

import click

from mml_utils.run_mml import repeat_run_mml, run_mml


@click.command()
@click.option('--filelist', type=click.Path(path_type=pathlib.Path, dir_okay=False),
              help='File with list of all files to be processed, one per line.')
@click.option('--mml-home', type=click.Path(path_type=pathlib.Path, file_okay=False),
              help='Path to metamaplite home.')
@click.option('--output-format', type=str, default='json',
              help='Output format (e.g., json or mmi)')
def run_single_mml_filelist(filelist: pathlib.Path, mml_home: pathlib.Path, output_format='json', repeat=True):
    if repeat:
        repeat_run_mml(filelist, mml_home, output_format=output_format)
    else:
        run_mml(filelist, mml_home, output_format=output_format)


if __name__ == '__main__':
    run_single_mml_filelist()
