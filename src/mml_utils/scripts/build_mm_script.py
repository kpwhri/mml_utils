"""
Script to build metamap shell scripts.

This is useful since metamap runs on individual files (rather than, e.g., a filelist).
"""
from pathlib import Path

import click

from mml_utils.build.mm_scripts import build_mm_script


@click.command()
@click.option('--outpath', default=None, type=click.Path(file_okay=False, path_type=Path),
              help='Directory to place output shell scripts.')
@click.option('--script-stem', default='script',
              help='Name for shell script (different scripts will receive a number appended).')
@click.option('--mm-path', default=None, type=click.Path(path_type=Path),
              help='If `metamap` not in PATH, use this to specify the full path.')
@click.option('--filelist', type=click.Path(dir_okay=False, path_type=Path),
              help='Filelist containing fullpaths to files to process.')
@click.option('--directory', type=click.Path(file_okay=False, path_type=Path),
              help='Path to directory to process.')
@click.option('--mm-outpath', default=None, type=click.Path(file_okay=False, path_type=Path),
              help='Directory to output metamap-processed files. Defaults to the same location as the file itself.')
@click.option('--num-scripts', default=-1, type=int,
              help='Number of shell scripts to create. Defaults to 1, unless `max-per-script` option specified.')
@click.option('--max-per-script', default=-1, type=int,
              help='Specify a maximum number of commands in each output shell script.')
@click.option('--parameters', default='',
              help='Parameters that should be passed to metamap.')
def _build_mm_script(parameters, outpath: Path, mm_path: Path, filelist: Path, directory: Path,
                     mm_outpath: Path, script_stem: str, num_scripts=-1, max_per_script=-1):
    build_mm_script(parameters, outpath, mm_path, filelist, directory, mm_outpath,
                    script_stem, num_scripts, max_per_script)


if __name__ == '__main__':
    _build_mm_script()
