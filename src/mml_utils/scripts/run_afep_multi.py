"""
Allow running AFEP across multiple instances and then summarizing the results in a CSV or Excel file.

## Usage

* Construct a toml file, like this:

outdir = 'path/output_dir'

[[runs]]
note_directories = ['/path/to/usabase']

[[runs]]
note_directories = ['/path/to/meddra']
name = 'mdr'  # use 'mdr' as output name rather than 'meddra'


"""
from pathlib import Path

import click
from loguru import logger

from mml_utils.config.parser import parse_config
from mml_utils.config.run_afep import MultiAfepConfig
from mml_utils.phenorm.afep import run_afep_algorithm
from mml_utils.phenorm.afep_summary import build_afep_excel


@click.command()
@click.argument('config_file', required=True, type=click.Path(exists=True, dir_okay=False, path_type=Path))
def _run_afep_algorithm_multi(config_file):
    """
    Use config file to guide
    :param config_file: currently only supports toml or json
    :return:
    """
    run_afep_algorithm_multi(config_file)


def run_afep_algorithm_multi(config_file):
    data = parse_config(config_file)
    config = MultiAfepConfig(**data)
    for run in config.runs:
        logger.info(f'Running {run.name}...')
        run_afep_algorithm(**run.dict(exclude={'name'}))
    if config.build_summary:
        build_afep_excel(config.outdir)


if __name__ == '__main__':
    _run_afep_algorithm_multi()
