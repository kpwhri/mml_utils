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

import click

from mml_utils.run_mml import repeat_run_mml, run_mml


@click.command()
@click.argument('filedir', type=click.Path(path_type=pathlib.Path, file_okay=False))
@click.option('--mml-home', type=click.Path(path_type=pathlib.Path, file_okay=False),
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
def run_mml_filelists_in_dir(filedir: pathlib.Path, mml_home: pathlib.Path, output_format='json',
                             property_file=None, properties=None, repeat=False, version=None, dataset='USAbase',
                             loglevel='WARN'):
    """

    :param repeat:
    :param filedir:
    :param mml_home: path to metmaplite instance
    :return:
    """
    for file in filedir.glob('*.in_progress'):
        if repeat:
            repeat_run_mml(file, mml_home, output_format=output_format, property_file=property_file,
                           properties=properties, version=version, dataset=dataset, loglevel=loglevel)
        else:
            run_mml(file, mml_home, output_format=output_format, property_file=property_file, properties=properties,
                    version=version, dataset=dataset, loglevel=loglevel)
        file.rename(str(file).replace('.in_progress', '.complete'))


if __name__ == '__main__':
    run_mml_filelists_in_dir()
