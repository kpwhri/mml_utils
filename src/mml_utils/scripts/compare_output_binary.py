"""
Console script to extract text differences between the outputs of the CSV summary files.
"""
import click

from pathlib import Path

from mml_utils.compare.compare import extract_binary_text_differences


@click.command()
@click.argument('path1', type=click.Path(exists=True, path_type=Path))
@click.argument('path2', type=click.Path(exists=True, path_type=Path))
@click.option('--outpath', type=click.Path(path_type=Path), default=Path('.'),
              help='Destination path to write csv output.')
@click.option('--text-encoding', default='latin1',
              help='Text encoding for notes.')
@click.option('--name1', default=None,
              help='Name for data in path1.')
@click.option('--name2', default=None,
              help='Name for data in path2.')
def compare_output_binary(path1: Path, path2: Path, outpath: Path = None, text_encoding='latin1',
                          name1=None, name2=None):
    """Compare output (result of `extract_mml_output`) of two different feature extraction versions"""
    extract_binary_text_differences(path1, path2, outpath, name1, name2, text_encoding=text_encoding)


if __name__ == '__main__':
    compare_output_binary()
