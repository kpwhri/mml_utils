"""
A script to build the initial file structure required by MetaMapLite.

This file will build 1 or more directories containing files with the name
 f'{note_id}.txt' and containing only the note's complete text.
"""
import csv
import pathlib

import click
from loguru import logger


@click.command()
@click.argument('connection-string')
@click.argument('query')
@click.option('--outdir', type=click.Path(file_okay=False, path_type=pathlib.Path), default=None,
              help='Directory to create subfolders and filelists.')
@click.option('--n-dirs', default=1, type=int,
              help='Number of directories to create.')
@click.option('--text-extension', default='.txt',
              help='Extension of text files to be created.')
@click.option('--text-encoding', default='utf8',
              help='Encoding for writing text files.')
def text_from_database(connection_string, query, outdir: pathlib.Path, n_dirs=1, text_extension='.txt',
                       text_encoding='utf8'):
    try:
        import sqlalchemy as sa
    except ImportError as ie:
        logger.exception(ie)
        logger.warning(f'Sqlalchemy is required: Install sqlalchemy with `pip install sqlalchemy`.')
        logger.warning(f'Depending on your connection string, pyodbc might also be required: `pip install pyodbc`.')
        return

    eng = sa.create_engine(connection_string)
    build_files(eng.execute(query), outdir=outdir, n_dirs=n_dirs,
                text_extension=text_extension, text_encoding=text_encoding)


@click.command()
@click.argument('csv-file', type=click.Path(dir_okay=False, path_type=pathlib.Path))
@click.option('--id-col', default='note_id', type=str,
              help='Name of column containing note ids.')
@click.option('--text-col', default='text', type=str,
              help='Name of column containing text.')
@click.option('--outdir', type=click.Path(file_okay=False, path_type=pathlib.Path), default=None,
              help='Directory to create subfolders and filelists.')
@click.option('--n-dirs', default=1, type=int,
              help='Number of directories to create.')
@click.option('--text-extension', default='.txt',
              help='Extension of text files to be created.')
@click.option('--text-encoding', default='utf8',
              help='Encoding for writing text files.')
@click.option('--csv-encoding', default='utf8',
              help='Encoding for source CSV file.')
@click.option('--csv-delimiter', default=',',
              help='Column delimiter for csv file.')
def text_from_csv(csv_file, id_col, text_col, outdir: pathlib.Path, n_dirs=1, text_extension='.txt',
                  text_encoding='utf8', csv_encoding='utf8', csv_delimiter=','):
    with open(csv_file, newline='', encoding=csv_encoding) as fh:
        reader = csv.DictReader(fh, delimiter=csv_delimiter)
        text_gen = ((row[id_col], row[text_col]) for row in reader)
        build_files(text_gen, outdir=outdir, n_dirs=n_dirs,
                    text_extension=text_extension, text_encoding=text_encoding)


def build_files(text_gen, outdir: pathlib.Path, n_dirs=1,
                text_extension='.txt', text_encoding='utf8'):
    """
    Write files to directory from generator outputting (note_id, text).
        A filelist will also be created for each outdirectory.
    :param text_gen:
    :param outdir:
    :param n_dirs:
    :param text_extension:
    :param text_encoding:
    :return:
    """
    if outdir is None:
        outdir = pathlib.Path('.')
    outdirs = [outdir / f'notes{i}' if n_dirs > 1 else outdir / f'notes' for i in range(n_dirs)]
    for d in outdirs:
        d.mkdir(exist_ok=False, parents=True)
    filelists = [open(outdir / f'filelist{i}.txt', 'w') if n_dirs > 1
                 else open(outdir / f'filelist.txt', 'w')
                 for i in range(n_dirs)]
    for i, (note_id, text) in enumerate(text_gen):
        outfile = outdirs[i % n_dirs] / f'{note_id}{text_extension}'
        with open(outfile, 'w', encoding=text_encoding, errors='replace') as out:
            out.write(text)
        filelists[i % n_dirs].write(f'{outfile.absolute()}\n')
    for fl in filelists:
        fl.close()


if __name__ == '__main__':
    text_from_database()
