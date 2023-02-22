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
@click.option('--property-file', type=str, default=None,
              help='Path to properety file to run.')
@click.option('--properties', nargs=2, default=None, multiple=True,
              help='Specify additional properties, e.g., --properties metamaplite.index.directory $PATH.')
def run_single_mml_filelist(filelist: pathlib.Path, mml_home: pathlib.Path, output_format='json',
                            property_file=None, properties=None, repeat=False):
    if repeat:
        repeat_run_mml(filelist, mml_home, output_format=output_format, property_file=property_file,
                       properties=properties)
    else:
        run_mml(filelist, mml_home, output_format=output_format, property_file=property_file, properties=properties)


if __name__ == '__main__':
    run_single_mml_filelist()
