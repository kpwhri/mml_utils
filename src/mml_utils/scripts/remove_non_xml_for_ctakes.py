from pathlib import Path

import click

from mml_utils.ctakes.clean import clean_non_xml_from_directories


@click.command()
@click.argument('directories', nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option('--encoding', default='utf8',
              help='Source encoding (default=utf8)')
def remove_non_xml_for_ctakes(directories, encoding='utf8'):
    clean_non_xml_from_directories(directories, encoding=encoding)


if __name__ == '__main__':
    remove_non_xml_for_ctakes()
