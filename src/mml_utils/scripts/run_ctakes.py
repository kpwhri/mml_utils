from pathlib import Path

import click
from loguru import logger

from mml_utils.ctakes.clean import clean_non_xml
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
@click.option('--dictionary', type=click.Path(path_type=Path, dir_okay=True),
              help='Path to XML file for custom-created dictionary.')
@click.option('--clean-files', default=False, is_flag=True,
              help='Remove non-xml characters from files in directories. Overwrites the files.')
@click.option('--clean-file-src-encoding', default='utf8',
              help='File format to read in src files for cleaning.')
def run_ctakes_directory(directory: Path, ctakes_home: Path, outdir: Path, umls_key: str = None,
                         dictionary: Path = None, clean_files: bool = False, clean_files_src_encoding='utf8'):
    if clean_files:
        logger.info(f'Overwriting files in {directory} to remove non-XML characters.')
        clean_non_xml(directory, encoding=clean_files_src_encoding)
    run_ctakes(directory, ctakes_home, outdir, umls_key, dictionary)


if __name__ == '__main__':
    run_ctakes_directory()
