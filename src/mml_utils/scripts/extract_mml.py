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


@click.command()
@click.argument('extract-directories', nargs=-1, type=click.Path(exists=True, path_type=pathlib.Path), )
@click.option('--outdir', type=click.Path(path_type=pathlib.Path),
              help='Output directory to place result files.')
@click.option('--cui-file', type=click.Path(exists=True, path_type=pathlib.Path, dir_okay=False),
              help='File containing one cui per line which should be included in the output;'
                   ' to enable mapping, place FROM_CUI,TO_CUI on the line.')
@click.option('--extract-format', type=str, default='json',
              help='Output format to look for (MML: "json" or "mmi"; cTAKES: "xmi").')
@click.option('--note-directory', 'note_directories', multiple=True,
              type=click.Path(exists=True, path_type=pathlib.Path, file_okay=False),
              help='(Optional) Note directories if different from `output-directories` (e.g., for cTAKES).')
@click.option('--add-fieldname', type=str, multiple=True,
              help='Add fieldnames to Metamaplite output.')
@click.option('--max-search', type=int, default=1000,
              help='Number of files in which to search for fieldnames.')
@click.option('--exclude-negated', is_flag=True, default=False,
              help='Exclude all results which have been determined by MML to be negated.')
@click.option('--skip-missing', is_flag=True, default=False,
              help='Skipping any missing (i.e., unprocessed) text files. Useful for generating sample data.')
@click.option('--extract-encoding', 'extract_encoding', default='cp1252',
              help='Encoding for reading output of MML or cTAKES.')
@click.option('--file-encoding', 'encoding', default='utf8',
              help='Encoding for reading text files.')
@click.option('--note-suffix', default='.txt',
              help='Specify note suffix if different than no suffix and ".txt". Include the period.')
@click.option('--extract-suffix', default=None,
              help='Specify output suffix for mmi/json files if different from default `--output-format`.'
                   ' Include the period.')
def _extract_mml(extract_directories: List[pathlib.Path], outdir: pathlib.Path, cui_file: pathlib.Path = None,
                 *, encoding='utf8', extract_format='json', max_search=1000, add_fieldname: List[str] = None,
                 exclude_negated=False, note_directories=None, extract_encoding='cp1252', note_suffix='.txt',
                 extract_suffix=None, skip_missing=False):
    extract_mml(extract_directories, outdir, cui_file,
                encoding=encoding, extract_format=extract_format, max_search=max_search, add_fieldname=add_fieldname,
                exclude_negated=exclude_negated, note_directories=note_directories, extract_encoding=extract_encoding,
                note_suffix=note_suffix, extract_suffix=extract_suffix, skip_missing=skip_missing)


def extract_mml(extract_directories: List[pathlib.Path], outdir: pathlib.Path, cui_file: pathlib.Path = None,
                *, encoding='utf8', extract_format='json', max_search=1000, add_fieldname: List[str] = None,
                exclude_negated=False, note_directories=None, extract_encoding='cp1252',
                note_suffix='.txt', extract_suffix=None, skip_missing=False):
    """

    :param note_directories:
    :param extract_encoding:
    :param note_suffix:
    :param extract_suffix:
    :param exclude_negated: exclude negated CUIs from the output
    :param add_fieldname:
    :param max_search:
    :param extract_directories:
    :param extract_format: allowed: json, mmi
    :param cui_file: File containing one cui per line which should be included in the output.
    :param note_directories: Directories to with files processed by metamap and
                containing the output (e.g., json) files.
    :param outdir:
    :param encoding:
    :return:
    """
    (note_outfile, nlp_outfile, cuis_by_doc_outfile), target_cuis = prepare_extract(outdir, add_fieldname, cui_file)

    if note_directories is None:
        note_directories = extract_directories
    get_field_names(extract_directories, extract_format=extract_format, max_search=max_search,
                    extract_encoding=extract_encoding, extract_suffix=extract_suffix)
    result_iter = extract_data(extract_directories, target_cuis=target_cuis, extract_format=extract_format,
                               encoding=encoding, exclude_negated=exclude_negated, note_directories=note_directories,
                               extract_encoding=extract_encoding, note_suffix=note_suffix,
                               extract_suffix=extract_suffix, skip_missing=skip_missing)
    build_extracted_file(result_iter, note_outfile, nlp_outfile)
    build_pivot_table(nlp_outfile, cuis_by_doc_outfile, target_cuis)
    return note_outfile, nlp_outfile, cuis_by_doc_outfile


def get_note_file(curr_directory, filename: str, extract_format, note_directories=None, skip_missing=False,
                  note_suffix='.txt', dir_index=None, extract_suffix=None):
    """Retrieve the extracted data from file."""
    if extract_suffix:
        exp_filename = filename.removesuffix(extract_suffix) + note_suffix
    elif extract_format == 'xmi':
        exp_filename = filename.removesuffix('.xmi')
    else:
        exp_filename = f"{filename.removesuffix(f'.{extract_format}')}{note_suffix}"
    if path := find_path(exp_filename, curr_directory, note_directories, dir_index):
        return path

    # maybe NLP program stripped all suffixes?
    exp_filename_2 = f"{exp_filename.split('.')[0]}{note_suffix}"
    if exp_filename != exp_filename_2:
        logger.warning(f'Failed to find expected output file: {exp_filename}{note_suffix};'
                       f' trying: {exp_filename_2}{note_suffix}.')
        if path := find_path(exp_filename_2, curr_directory, note_directories, dir_index):
            return path

    msg = f'Failed to find expected output file: {exp_filename}, {exp_filename_2}.'
    if skip_missing:
        logger.warning(msg)
    else:
        raise ValueError(msg)


def get_field_names(extract_directories: List[pathlib.Path], *, extract_format='json', extract_encoding='cp1252',
                    max_search=1000, extract_suffix=None):
    """

    :param extract_directories:
    :param extract_suffix:
    :param extract_format:
    :param extract_encoding:
    :param max_search: how many files to look at in each directory
    :return:
    """
    logger.info('Retrieving fieldnames.')
    fieldnames = set(NLP_FIELDNAMES)
    target_search = max_search // len(extract_directories)
    logger.info(f'Exploring first {target_search} of {len(extract_directories)} directories.')
    for i, extract_dir in enumerate(extract_directories):
        cnt = 0
        for extract_file in extract_dir.glob(f'*{extract_suffix or "." + extract_format}'):
            for data in extract_mml_data(extract_file, encoding=extract_encoding, extract_format=extract_format,
                                         target_cuis=TargetCuis()):
                for fieldname in set(data.keys()) - fieldnames:
                    NLP_FIELDNAMES.append(fieldname)
                    fieldnames.add(fieldname)
            cnt += 1
            if cnt > target_search:
                break


def extract_data(extract_directories: List[pathlib.Path], *, target_cuis=None, encoding='utf8',
                 extract_encoding='cp1252',
                 extract_format='json', exclude_negated=False, note_directories=None, note_suffix='.txt',
                 extract_suffix=None, skip_missing=False):
    for i, extract_dir in enumerate(extract_directories):
        logger.info(f'Processing directory: {extract_dir}')
        yield from extract_data_from_directory(
            extract_dir, encoding=encoding, exclude_negated=exclude_negated, extract_encoding=extract_encoding,
            extract_format=extract_format, target_cuis=target_cuis, note_directories=note_directories,
            note_suffix=note_suffix, extract_suffix=extract_suffix, skip_missing=skip_missing, dir_index=i,
        )


def extract_data_from_directory(extract_dir, *, target_cuis=None, encoding='utf8', extract_encoding='cp1252',
                                extract_format='json', exclude_negated=False, note_directories=None,
                                note_suffix='.txt', extract_suffix=None, skip_missing=False, dir_index=None):
    for file in extract_dir.glob(f'*{extract_suffix or "." + extract_format}'):
        logger.info(f'Processing file: {file}')
        yield from extract_data_from_file(
            file, encoding=encoding, exclude_negated=exclude_negated, extract_encoding=extract_encoding,
            extract_format=extract_format, target_cuis=target_cuis, note_directories=note_directories,
            extract_suffix=extract_suffix, skip_missing=skip_missing, dir_index=dir_index, note_suffix=note_suffix,
        )


def extract_data_from_file(file, *, target_cuis=None, encoding='utf8', extract_encoding='cp1252',
                           extract_format='json', exclude_negated=False, skip_missing=False,
                           note_directories=None, extract_suffix=None, dir_index=None, note_suffix='.txt'):
    """

    :yield: tuple[ is_record = True (i.e., note data) vs False (i.e., nlp data),
                   data
                   ]
    """
    record = {
        'docid': file.stem,
        'filename': str(file),
    }
    target_cuis = TargetCuis() if target_cuis is None else target_cuis
    for data in extract_mml_data(file, encoding=extract_encoding,
                                 target_cuis=target_cuis, extract_format=extract_format):
        if exclude_negated and data['negated']:
            continue  # exclude negated terms if requested
        yield False, data

    # find note data
    note = get_note_file(file.parent, file.name, extract_format, skip_missing=skip_missing,
                         note_directories=note_directories, note_suffix=note_suffix,
                         dir_index=dir_index, extract_suffix=extract_suffix)
    if note and note.exists():
        logger.info(f'Processing associated note text: {note}.')
        add_notefile_to_record(record, note, encoding)
        yield True, record
    else:
        logger.warning(f'Expected text file for {extract_format} file like {file.with_suffix(note_suffix)}'
                       f' in {note_directories or file.parent}.')


if __name__ == '__main__':
    _extract_mml()
