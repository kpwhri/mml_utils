from pathlib import Path

import click

from mml_utils.run_ctakes import run_ctakes


@click.command()
@click.argument('directory', type=click.Path(path_type=Path, file_okay=False))
@click.option('--ctakes-home', type=click.Path(path_type=Path, file_okay=False),
              help='Path to cTAKES home (should have "bin" dir inside).')
@click.option('--outdir', type=click.Path(path_type=Path, file_okay=False),
              help='Directory to put output XMI files.')
@click.option('--umls-key', default=None,
              help='UMLS key including hyphens for using UMLS dictionary.'
                   ' Key may also be set as environment variable.')
def run_ctakes_directory(directory: Path, ctakes_home: Path, outdir: Path, umls_key: str = None):
    run_ctakes(directory, ctakes_home, outdir, umls_key)


if __name__ == '__main__':
    run_ctakes_directory()
