"""
More generic form of `run_mml` which allows running repeatedly against a single output file.
"""
from pathlib import Path

import click

from mml_utils.filelists import build_filelist
from mml_utils.run_mml import repeat_run_mml, run_mml


@click.command()
@click.option('--file', default=None, type=click.Path(path_type=Path, dir_okay=False),
              help='File to be processed.')
@click.option('--filelist', default=None, type=click.Path(path_type=Path, dir_okay=False),
              help='File with list of all files to be processed, one per line.')
@click.option('--directory', default=None, type=click.Path(path_type=Path, file_okay=False),
              help='File with list of all files to be processed, one per line.')
@click.option('--mml-home', type=click.Path(path_type=Path, file_okay=False),
              help='Path to metamaplite home.')
@click.option('--output-format', type=str, default='json',
              help='Output format (e.g., json or mmi)')
@click.option('--property-file', type=str, default=None,
              help='Path to properety file to run.')
@click.option('--properties', nargs=2, default=None, multiple=True,
              help='Specify additional properties, e.g., --properties metamaplite.index.directory $PATH.')
@click.option('--version', default=None,
              help='Specify UMLS version. If not specified, relevant version will be automatically selected'
                   ' according to dataset.')
@click.option('--dataset', default='USAbase',
              help='Specify UMLS dataset.')
@click.option('--loglevel', default='WARN',
              type=click.Choice(['ALL', 'DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL', 'OFF', 'TRACE']),
              help='Select logging level. Defaults to WARN to avoid MML\'s dense logging output.')
def run_single_mml_filelist(filelist: Path, file: Path, directory: Path, mml_home: Path, output_format='json',
                            property_file=None, properties=None, repeat=False, version=None, dataset='USAbase',
                            loglevel='WARN'):
    if file:
        filelist = build_filelist(file)
    elif directory:
        filelist = build_filelist(directory)
    if not filelist:
        raise ValueError(f'No filelist specified. Must supply `--file`, `--filelist`, or `--directory` arguments.')
    if repeat:
        repeat_run_mml(filelist, mml_home, output_format=output_format, property_file=property_file,
                       properties=properties, version=version, dataset=dataset, loglevel=loglevel)
    else:
        run_mml(filelist, mml_home, output_format=output_format, property_file=property_file, properties=properties,
                version=version, dataset=dataset, loglevel=loglevel)


if __name__ == '__main__':
    run_single_mml_filelist()
