"""
Extract output from metamaplite, and create two tables. These are primarily in preparation
    for use by PheNorm, but alternative implementations might also be valuable.

Table 1: All CUIs (or subset, if specified) with MML and other metadata.
filename, [metamaplite metadata], [other metadata joinable on 'filename'; e.g., note metadata]

Table 2: Notes with note length and whether or not it was processed.
filename, length, processed: yes/no
"""
import pathlib
from typing import List

import click
from loguru import logger

from mml_utils.extract.utils import NLP_FIELDNAMES, add_notefile_to_record
from mml_utils.extract.utils import prepare_extract, find_path, build_pivot_table, build_extracted_file
from mml_utils.parse.parser import extract_mml_data
from mml_utils.parse.target_cuis import TargetCuis

try:
    import pandas as pd
except ImportError:
    pd = None


@click.command()
@click.argument('note-directories', nargs=-1, type=click.Path(exists=True, path_type=pathlib.Path), )
@click.option('--outdir', type=click.Path(path_type=pathlib.Path),
              help='Output directory to place result files.')
@click.option('--cui-file', type=click.Path(exists=True, path_type=pathlib.Path, dir_okay=False),
              help='File containing one cui per line which should be included in the output;'
                   ' to enable mapping, place FROM_CUI,TO_CUI on the line.')
@click.option('--extract-format', type=str, default='json',
              help='Output format to look for (MML: "json" or "mmi"; cTAKES: "xmi").')
@click.option('--extract-directory', 'extract_directories', multiple=True,
              type=click.Path(exists=True, path_type=pathlib.Path, file_okay=False),
              help='(Optional) Output directories if different from `note-directories` (e.g., for cTAKES).')
@click.option('--add-fieldname', type=str, multiple=True,
              help='Add fieldnames to Metamaplite output.')
@click.option('--max-search', type=int, default=1000,
              help='Number of files in which to search for fieldnames.')
@click.option('--exclude-negated', is_flag=True, default=False,
              help='Exclude all results which have been determined by MML to be negated.')
@click.option('--skip-missing', is_flag=True, default=False,
              help='Skipping any missing (i.e., unprocessed) text files. Useful for generating sample data.')
@click.option('--extract-encoding', default='cp1252',
              help='Encoding for reading output of MML or cTAKES.')
@click.option('--file-encoding', 'encoding', default='utf8',
              help='Encoding for reading text files.')
@click.option('--note-suffix', default='.txt',
              help='Specify note suffix if different than no suffix and ".txt". Include the period.')
@click.option('--extract-suffix', default=None,
              help='Specify NLP extract suffix for mmi/json files if different from default `--extract-format`.'
                   ' Include the period.')
def _extract_mml(note_directories: List[pathlib.Path], outdir: pathlib.Path, cui_file: pathlib.Path = None,
                 *, encoding='utf8', extract_format='json', max_search=1000, add_fieldname: List[str] = None,
                 exclude_negated=False, extract_directories=None, extract_encoding='cp1252', note_suffix='.txt',
                 extract_suffix=None, skip_missing=False):
    extract_mml(note_directories, outdir, cui_file,
                encoding=encoding, extract_format=extract_format, max_search=max_search, add_fieldname=add_fieldname,
                exclude_negated=exclude_negated, extract_directories=extract_directories,
                extract_encoding=extract_encoding,
                note_suffix=note_suffix, extract_suffix=extract_suffix, skip_missing=skip_missing)


def extract_mml(note_directories: List[pathlib.Path], outdir: pathlib.Path, cui_file: pathlib.Path = None,
                *, encoding='utf8', extract_format='json', max_search=1000, add_fieldname: List[str] = None,
                exclude_negated=False, extract_directories=None, extract_encoding='cp1252',
                note_suffix='.txt', extract_suffix=None, skip_missing=False):
    """

    :param extract_directories:
    :param extract_encoding:
    :param note_suffix:
    :param extract_suffix:
    :param exclude_negated: exclude negated CUIs from the output
    :param add_fieldname:
    :param max_search:
    :param extract_format: allowed: json, mmi
    :param cui_file: File containing one cui per line which should be included in the output.
    :param note_directories: Directories to with files processed by metamap and
                containing the output (e.g., json) files.
    :param outdir:
    :param encoding:
    :return:
    """
    (note_outfile, nlp_outfile, cuis_by_doc_outfile), target_cuis = prepare_extract(outdir, add_fieldname, cui_file)

    if extract_directories is None:
        extract_directories = note_directories
    get_field_names(note_directories, extract_format=extract_format, max_search=max_search,
                    extract_directories=extract_directories, extract_encoding=extract_encoding,
                    note_suffix=note_suffix, extract_suffix=extract_suffix, skip_missing=skip_missing)
    result_iter = extract_data(note_directories, target_cuis=target_cuis,
                               extract_format=extract_format, encoding=encoding, exclude_negated=exclude_negated,
                               extract_directories=extract_directories, extract_encoding=extract_encoding,
                               note_suffix=note_suffix, extract_suffix=extract_suffix, skip_missing=skip_missing)
    build_extracted_file(result_iter, note_outfile, nlp_outfile)
    build_pivot_table(nlp_outfile, cuis_by_doc_outfile, target_cuis)
    return note_outfile, nlp_outfile, cuis_by_doc_outfile


def get_extract_file(curr_directory, exp_filename, extract_format, extract_directories=None, skip_missing=False,
                     extract_suffix=None, dir_index=None):
    """Retrieve the extracted data from file."""
    if extract_suffix is not None:
        extract_format = extract_suffix.lstrip('.')
    elif extract_format == 'xmi':
        extract_format = 'txt.xmi'  # how ctakes does renaming

    if path := find_path(f'{exp_filename}.{extract_format}',
                         curr_directory, extract_directories, dir_index):
        return path

    exp_filename_2 = exp_filename.split('.')[0]
    if exp_filename != exp_filename_2:
        logger.warning(f'Failed to find expected output file: {exp_filename}.{extract_format};'
                       f' trying: {exp_filename_2}.{extract_format}.')
        if path := find_path(f'{exp_filename_2}.{extract_format}',
                             curr_directory, extract_directories, dir_index):
            return path

    msg = f'Failed to find expected output file: {exp_filename}.{extract_format}.'
    if skip_missing:
        logger.warning(msg)
    else:
        raise ValueError(msg)


def get_field_names(note_directories: List[pathlib.Path], *, extract_format='json', extract_encoding='cp1252',
                    max_search=1000, extract_directories=None, skip_missing=False,
                    note_suffix='.txt', extract_suffix=None):
    """

    :param extract_directories:
    :param skip_missing: don't raise error if missing output file is found
    :param note_suffix:
    :param extract_suffix:
    :param note_directories:
    :param extract_format:
    :param extract_encoding:
    :param max_search: how many files to look at in each directory
    :return:
    """
    logger.info('Retrieving fieldnames.')
    fieldnames = set(NLP_FIELDNAMES)
    target_search = max_search // len(note_directories)
    logger.info(f'Exploring first {target_search} of {len(note_directories)} directories.')
    for i, note_dir in enumerate(note_directories):
        cnt = 0
        for file in note_dir.iterdir():
            if (file.suffix not in {note_suffix, ''} and ''.join(file.suffixes) != note_suffix) or file.is_dir():
                continue
            extract_file = get_extract_file(file.parent, file.stem, extract_format, skip_missing=skip_missing,
                                            extract_directories=extract_directories, extract_suffix=extract_suffix,
                                            dir_index=i)
            if extract_file is None or not extract_file.exists():
                continue
            for data in extract_mml_data(extract_file, encoding=extract_encoding, extract_format=extract_format,
                                         target_cuis=TargetCuis()):
                for fieldname in set(data.keys()) - fieldnames:
                    NLP_FIELDNAMES.append(fieldname)
                    fieldnames.add(fieldname)
            cnt += 1
            if cnt > target_search:
                break


def extract_data(note_directories: List[pathlib.Path], *, target_cuis=None, encoding='utf8', extract_encoding='cp1252',
                 extract_format='json', exclude_negated=False, extract_directories=None, note_suffix='.txt',
                 extract_suffix=None, skip_missing=False):
    for i, note_dir in enumerate(note_directories):
        logger.info(f'Processing directory: {note_dir}')
        yield from extract_data_from_directory(
            note_dir, encoding=encoding, exclude_negated=exclude_negated, extract_encoding=extract_encoding,
            extract_format=extract_format, target_cuis=target_cuis, extract_directories=extract_directories,
            note_suffix=note_suffix, extract_suffix=extract_suffix, skip_missing=skip_missing, dir_index=i,
        )


def extract_data_from_directory(note_dir, *, target_cuis=None, encoding='utf8', extract_encoding='cp1252',
                                extract_format='json', exclude_negated=False, extract_directories=None,
                                note_suffix='.txt', extract_suffix=None, skip_missing=False, dir_index=None):
    for file in note_dir.iterdir():
        if (file.suffix not in {note_suffix, ''} and ''.join(file.suffixes) != note_suffix) or file.is_dir():
            continue
        logger.info(f'Processing file: {file}')
        yield from extract_data_from_file(
            file, encoding=encoding, exclude_negated=exclude_negated, extract_encoding=extract_encoding,
            extract_format=extract_format, target_cuis=target_cuis, extract_directories=extract_directories,
            extract_suffix=extract_suffix, skip_missing=skip_missing, dir_index=dir_index,
        )


def extract_data_from_file(file, *, target_cuis=None, encoding='utf8', extract_encoding='cp1252',
                           extract_format='json', exclude_negated=False, skip_missing=False,
                           extract_directories=None, extract_suffix=None, dir_index=None):
    record = {
        'docid': file.stem,
        'filename': str(file),
    }
    target_cuis = TargetCuis() if target_cuis is None else target_cuis
    add_notefile_to_record(record, file, encoding)
    extract_file = get_extract_file(file.parent, file.stem, extract_format, skip_missing=skip_missing,
                                    extract_directories=extract_directories, extract_suffix=extract_suffix,
                                    dir_index=dir_index)
    if extract_file is None:
        stem = file.stem.split('.')[0]
        extract_file = get_extract_file(file.parent, f'{stem}', extract_format, skip_missing=skip_missing,
                                        extract_directories=extract_directories, extract_suffix=extract_suffix,
                                        dir_index=dir_index)
    if extract_file and extract_file.exists():
        logger.info(f'Processing associated {extract_format}: {extract_file}.')
        for data in extract_mml_data(extract_file, encoding=extract_encoding,
                                     target_cuis=target_cuis, extract_format=extract_format):
            if exclude_negated and data['negated']:
                continue  # exclude negated terms if requested
            yield False, data
        record['processed'] = True
    else:
        exp_suffix = extract_suffix if extract_suffix else f'.{extract_format}'
        stem = file.stem.split('.')[0]
        logger.warning(f'Expected {extract_format} file like {file.stem}{exp_suffix} or {stem}{exp_suffix}'
                       f' in {extract_directories or file.parent}.')
        record['processed'] = False
    yield True, record


if __name__ == '__main__':
    _extract_mml()
