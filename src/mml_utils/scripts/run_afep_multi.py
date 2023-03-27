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
import json
from pathlib import Path
import tomllib

import click
from pydantic import BaseModel

from mml_utils.phenorm.afep import run_afep_algorithm
from mml_utils.phenorm.afep_summary import build_afep_excel


class AfepRun(BaseModel):
    note_directories: list[Path]
    mml_format: str = 'json'
    outdir: Path = None  # should be assigned by parent; to alter name, use 'name'
    expand_cuis: bool = False
    apikey: str = None
    skip_greedy_algorithm: bool = False
    min_kb: int = None  # default to ceiling(n_articles/2)
    data_directory: list[Path] = None
    name: str = None  # for naming output directory

    def set_outdir(self, default: Path):
        self.outdir = self.get_outdir(default)

    def get_outdir(self, default: Path):
        name = f'{self.name if self.name else self.note_directories[0].stem}' \
               f'-selected{"-cui-exp" if self.expand_cuis else ""}'
        if default is None:
            return Path('.') / name
        elif self.name:
            return default / f'{self.name}-selected{"-cui-exp" if self.expand_cuis else ""}'
        else:
            return default / f'{self.note_directories[0].stem}-selected{"-cui-exp" if self.expand_cuis else ""}'


class MultiAfepConfig(BaseModel):
    runs: list[AfepRun]
    outdir: Path = None  # general output directory
    build_summary: bool = True
    base_directory: Path = None
    note_directories: list[Path] = None

    def __init__(self, **kw):
        super().__init__(**kw)
        # post init
        for run in self.runs:
            run.set_outdir(self.outdir)


def parse_config(config_file):
    with open(config_file, 'rb') as fh:
        if config_file.suffix == '.json':
            return json.load(fh)
        elif config_file.suffix == '.toml':
            return tomllib.load(fh)
        else:
            raise ValueError(f'Unrecognized config format: {config_file.suffix} for file: {config_file}.')


@click.command()
@click.argument('config_file', required=True, type=click.Path(exists=True, dir_okay=False, path_type=Path))
def run_afep_algorithm_multi(config_file):
    """
    Use config file to guide
    :param config_file: currently only supports toml or json
    :return:
    """
    data = parse_config(config_file)
    config = MultiAfepConfig(**data)
    for run in config.runs:
        run_afep_algorithm(**run.dict(exclude={'name'}))
    if config.build_summary:
        build_afep_excel(config.outdir)


if __name__ == '__main__':
    run_afep_algorithm_multi()
