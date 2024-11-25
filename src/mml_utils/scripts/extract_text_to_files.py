"""
A script to build the initial file structure required by MetaMapLite.

This file will build 1 or more directories containing files with the name
 f'{note_id}.txt' and containing only the note's complete text.
"""
import csv
import json
import os
import pathlib
from collections import UserDict, OrderedDict

import click
import pandas as pd
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
def text_from_database_cmd(connection_string, query, outdir: pathlib.Path, n_dirs=1, text_extension='.txt',
                           text_encoding='utf8'):
    text_from_database(connection_string, query, outdir, n_dirs=n_dirs, text_extension=text_extension,
                       text_encoding=text_encoding)


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
@click.argument('csv-file', type=click.Path(dir_okay=False, path_type=pathlib.Path), default=None)
@click.option('--id-col', default='docid', type=str,
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
def text_from_csv_cmd(csv_file, id_col, text_col, outdir: pathlib.Path, n_dirs=1, text_extension='.txt',
                      text_encoding='utf8', csv_encoding='utf8', csv_delimiter=','):
    text_from_csv(csv_file, id_col, text_col, outdir, n_dirs=n_dirs, text_extension=text_extension,
                  text_encoding=text_encoding, csv_encoding=csv_encoding, csv_delimiter=csv_delimiter)


def text_from_csv(csv_file, id_col, text_col, outdir: pathlib.Path, n_dirs=1, text_extension='.txt',
                  text_encoding='utf8', csv_encoding='utf8', csv_delimiter=','):
    with open(csv_file, newline='', encoding=csv_encoding) as fh:
        reader = csv.DictReader(fh, delimiter=csv_delimiter)
        text_gen = ((row[id_col], row[text_col]) for row in reader)
        build_files(text_gen, outdir=outdir, n_dirs=n_dirs,
                    text_extension=text_extension, text_encoding=text_encoding)


@click.command()
@click.argument('sas-file', type=click.Path(dir_okay=False, path_type=pathlib.Path), default=None)
@click.option('--id-col', default='docid', type=str,
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
@click.option('--sas-encoding', default='latin1',
              help='Encoding for source SAS7BDAT file.')
@click.option('--force-id-to-int/--dont-force-id-to-int', default=False,
              help='By default, id column will be coerced to an int due to preference in pandas for float.')
def text_from_sas7bdat_cmd(sas_file, id_col, text_col, outdir: pathlib.Path, n_dirs=1, text_extension='.txt',
                           text_encoding='utf8', sas_encoding='latin1', force_id_to_int=True):
    text_from_sas7bdat(sas_file, id_col, text_col, outdir, n_dirs=n_dirs, text_extension=text_extension,
                       text_encoding=text_encoding, sas_encoding=sas_encoding, force_id_to_int=force_id_to_int)


def text_from_sas7bdat(sas_file, id_col, text_col, outdir: pathlib.Path, n_dirs=1, text_extension='.txt',
                       text_encoding='utf8', sas_encoding='latin1', force_id_to_int=True):
    build_files(_text_from_sas7bdat_iter(sas_file, sas_encoding, id_col, text_col, force_id_to_int=force_id_to_int),
                outdir=outdir, n_dirs=n_dirs, text_extension=text_extension, text_encoding=text_encoding)


def _text_from_sas7bdat_iter(sas_file, sas_encoding, id_col, text_col, force_id_to_int=True):
    for df in pd.read_sas(sas_file, encoding=sas_encoding, chunksize=2000):
        for row in df.itertuples():
            id_ = getattr(row, id_col)
            if force_id_to_int:
                id_ = int(id_)
            text = getattr(row, text_col)
            yield id_, text


@click.command()
@click.argument('jsonl-file', type=click.Path(dir_okay=False, path_type=pathlib.Path), default=None)
@click.option('--id-col', default='docid', type=str,
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
@click.option('--jsonl-encoding', default='utf8',
              help='Encoding for source JSONL file.')
@click.option('--resume', is_flag=True, default=False,
              help='Safely resume processing (will re-run the last recorded note_id).')
def text_from_jsonl_cmd(jsonl_file, id_col, text_col, outdir: pathlib.Path, n_dirs=1, text_extension='.txt',
                        text_encoding='utf8', jsonl_encoding='utf8', resume=False):
    text_from_jsonl(jsonl_file, id_col, text_col, outdir, n_dirs=n_dirs, text_extension=text_extension,
                    text_encoding=text_encoding, jsonl_encoding=jsonl_encoding, resume=resume)


def text_from_jsonl(jsonl_file, id_col, text_col, outdir: pathlib.Path, n_dirs=1, text_extension='.txt',
                    text_encoding='utf8', jsonl_encoding='utf8', resume=False):
    if resume:
        resume_building_files(_text_from_jsonl_iter(jsonl_file, jsonl_encoding, id_col, text_col),
                              outdir=outdir,
                              n_dirs=n_dirs,
                              text_extension=text_extension,
                              text_encoding=text_encoding)
    else:
        build_files(_text_from_jsonl_iter(jsonl_file, jsonl_encoding, id_col, text_col),
                    outdir=outdir,
                    n_dirs=n_dirs,
                    text_extension=text_extension,
                    text_encoding=text_encoding)


def _text_from_jsonl_iter(jsonl_file, jsonl_encoding, id_col, text_col):
    with open(jsonl_file, encoding=jsonl_encoding) as fh:
        for line in fh:
            data = json.loads(line)
            yield data[id_col], data[text_col]


class FIFOOrderedDict(UserDict):
    """Limit the memory footprint of dict by only retaining most recent n
    ASSUMPTION: if > max_length are present in dict (somehow) only 1 will be removed with each new insertion..
    """

    def __init__(self, max_length=10):
        super().__init__()
        self.data = OrderedDict(self.data)
        self.max_length = max_length

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if len(self.data) > self.max_length:
            self.data.popitem(last=False)


def build_files(text_gen, outdir: pathlib.Path, n_dirs=1,
                text_extension='.txt', text_encoding='utf8', require_newline=True):
    """
    Write files to directory from generator outputting (note_id, text).
        A filelist will also be created for each outdirectory.
    :param require_newline: always add a newline to avoid issues when running MetaMap
    :param text_gen:
    :param outdir:
    :param n_dirs:
    :param text_extension:
    :param text_encoding:
    :return:
    """
    if outdir is None:
        outdir = pathlib.Path('.')
    logger.info(f'Writing files to: {outdir}.')
    outdirs = [outdir / f'notes{i}' if n_dirs > 1 else outdir / f'notes' for i in range(n_dirs)]
    for d in outdirs:
        d.mkdir(exist_ok=False, parents=True)
    filelists = [open(outdir / f'filelist{i}.txt', 'w') if n_dirs > 1
                 else open(outdir / f'filelist.txt', 'w')
                 for i in range(n_dirs)]
    _build_files(text_gen, n_dirs, outdirs, filelists, text_encoding, text_extension, require_newline)


def _build_files(text_gen, n_dirs, outdirs, filelists, text_encoding, text_extension, require_newline,
                 completed: FIFOOrderedDict = None):
    if not completed:
        completed = FIFOOrderedDict(max_length=10)  # only retain last 10: multiple lines must appear together
    i = 0
    for note_id, text in text_gen:
        if not isinstance(text, str) or text.strip() == '':  # handle forms of None/nan
            continue
        if note_id in completed:  # handle notes with multiple 'note_lines'
            with open(completed[note_id], encoding=text_encoding) as fh:
                prev_text = fh.read()
            if require_newline:
                prev_text = prev_text[:-1]
            with open(completed[note_id], 'w', encoding=text_encoding, errors='replace') as out:
                out.write(prev_text)
                out.write(text)
                if require_newline:
                    out.write('\n')
            continue
        outfile = outdirs[i % n_dirs] / f'{note_id}{text_extension}'
        completed[note_id] = outfile
        with open(outfile, 'w', encoding=text_encoding, errors='replace') as out:
            out.write(text)
            if require_newline:
                out.write('\n')
        filelists[i % n_dirs].write(f'{outfile.absolute()}\n')
        i += 1
        if i % 100_000 == 0:
            logger.info(f'Finished reading {i:,} lines.')
    for fl in filelists:
        fl.close()
    logger.info(f'Done! Finished reading {i:,} lines (i.e., notes/note parts) from source dataset.')


def _get_last_path(file: pathlib.Path):
    num_newlines = 0
    with open(file, 'rb') as f:
        try:
            f.seek(-2, os.SEEK_END)
            while num_newlines < 2:  # each path is written with a newline at the end
                f.seek(-2, os.SEEK_CUR)
                if f.read(1) == b'\n':
                    break
        except OSError:
            f.seek(0)
        last_line = f.readline().decode().strip()
    return pathlib.Path(last_line)


def resume_building_files(text_gen, outdir: pathlib.Path, n_dirs=1,
                          text_extension='.txt', text_encoding='utf8', require_newline=True):
    """
    Figure otu where the process was interrupted by getting last note ids written to filelist. Re-run the last one
      and then keep going.
    :param text_gen:
    :param outdir:
    :param n_dirs:
    :param text_extension:
    :param text_encoding:
    :param require_newline:
    :return:
    """
    logger.info(f'Attempting to resume building files.')
    outdirs = [p for p in sorted(outdir.glob('notes*'))]
    filelist_paths = [p for p in sorted(outdir.glob('filelist*.txt'))]
    assert len(outdirs) == len(
        filelist_paths) == n_dirs, 'Ensure no disagreement between number of output directories/sets.'
    # get last value in each filelist
    last_paths = [_get_last_path(f) for f in filelist_paths]
    last_noteids = {p.name.removesuffix(text_extension): p for p in last_paths}
    logger.info(f'Possible last note_ids: {last_noteids}.'
                f' Will skip all files until all three of these are found.'
                f' The last found will be re-processed.')
    filelists = [open(f, 'a') for f in filelist_paths]
    completed = FIFOOrderedDict(max_length=10)  # only retain last 10: multiple lines must appear together
    for note_id, text in text_gen:
        if not isinstance(text, str) or text.strip() == '':  # handle forms of None/nan
            continue
        note_id_str = str(note_id)
        if note_id_str in last_noteids:
            if len(last_noteids) == 1:
                last_file = last_noteids[note_id_str]
                logger.info(f'Last completed note_id: {note_id_str}.')
                logger.info(f'Preparing to re-run and re-build: {last_file}.')
                last_file.unlink(missing_ok=True)  # might not have been written, possible cause of error
                completed[note_id] = last_file
                with open(last_file, 'w', encoding=text_encoding, errors='replace') as out:
                    out.write(text)
                    if require_newline:
                        out.write('\n')
                logger.info(f'Successfully re-wrote {note_id} to {last_file}. Running notes going forward.')
                break
            else:
                del last_noteids[note_id]
    _build_files(text_gen, n_dirs, outdirs, filelists, text_encoding, text_extension, require_newline, completed)


if __name__ == '__main__':
    # text_from_database_cmd()
    text_from_jsonl_cmd()
