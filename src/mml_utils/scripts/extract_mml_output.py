"""
Extract output from metamaplite, and create two tables. These are primarily in preparation
    for use by PheNorm, but alternative implementations might also be valuable.

Table 1: All CUIs (or subset, if specified) with MML and other metadata.
filename, [metamaplite metadata], [other metadata joinable on 'filename'; e.g., note metadata]

Table 2: Notes with note length and whether or not it was processed.
filename, length, processed: yes/no
"""
import csv
import datetime
import pathlib
import re
from typing import List

import click
from loguru import logger

from mml_utils.parse.parser import extract_mml_data

MML_FIELDNAMES = [
    'event_id', 'docid', 'filename', 'matchedtext', 'conceptstring', 'cui', 'preferredname', 'start', 'length',
]
NOTE_FIELDNAMES = [
    'filename', 'docid', 'num_chars', 'num_letters', 'num_words', 'processed',
]


@click.command()
@click.argument('note-directories', nargs=-1, type=click.Path(exists=True, path_type=pathlib.Path), )
@click.option('--outdir', type=click.Path(path_type=pathlib.Path),
              help='Output directory to place result files.')
@click.option('--cui-file', type=click.Path(exists=True, path_type=pathlib.Path, dir_okay=False),
              help='File containing one cui per line which should be included in the output.')
@click.option('--output-format', type=str, default='json',
              help='Output format to look for (MML: "json" or "mmi"; cTAKES: "xmi").')
@click.option('--output-directory', 'output_directories', multiple=True,
              type=click.Path(exists=True, path_type=pathlib.Path, file_okay=False),
              help='(Optional) Output directories if different from `note-directories`.')
@click.option('--add-fieldname', type=str, multiple=True,
              help='Add fieldnames to Metamaplite output.')
@click.option('--max-search', type=int, default=1000,
              help='Number of files in which to search for fieldnames.')
@click.option('--exclude-negated', is_flag=True, default=False,
              help='Exclude all results which have been determined by MML to be negated.')
@click.option('--output-encoding', 'mm_encoding', default='cp1252',
              help='Encoding for reading output of MML or cTAKES.')
@click.option('--file-encoding', 'encoding', default='utf8',
              help='Encoding for reading text files.')
def extract_mml(note_directories: List[pathlib.Path], outdir: pathlib.Path, cui_file: pathlib.Path = None,
                *, encoding='utf8', output_format='json', max_search=1000, add_fieldname: List[str] = None,
                exclude_negated=False, output_directories=None, mm_encoding='cp1252'):
    """

    :param exclude_negated: exclude negated CUIs from the output
    :param add_fieldname:
    :param max_search:
    :param output_format: allowed: json, mmi
    :param cui_file: File containing one cui per line which should be included in the output.
    :param note_directories: Directories to with files processed by metamap and
                containing the output (e.g., json) files.
    :param outdir:
    :param encoding:
    :return:
    """
    now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    outdir.mkdir(exist_ok=True)
    note_outfile = outdir / f'notes_{now}.csv'
    mml_outfile = outdir / f'mml_{now}.csv'

    if add_fieldname:
        global MML_FIELDNAMES
        for fieldname in add_fieldname:
            MML_FIELDNAMES.append(fieldname)

    target_cuis = None
    if cui_file is not None:
        with open(cui_file, encoding='utf8') as fh:
            target_cuis = set(x.strip() for x in fh.read().split('\n'))
        logger.info(f'Retaining only {len(target_cuis)} CUIs.')
    get_field_names(note_directories, output_format=output_format, max_search=max_search,
                    output_directories=output_directories, mm_encoding=mm_encoding)
    build_extracted_file(note_directories, target_cuis, note_outfile, mml_outfile,
                         output_format, encoding, exclude_negated, output_directories=output_directories,
                         mm_encoding=mm_encoding)


def get_output_file(curr_directory, exp_filename, output_format, output_directories=None):
    if output_format == 'xmi':
        output_format = 'txt.xmi'  # how ctakes does renaming
    if path := (pathlib.Path(curr_directory / f'{exp_filename}.{output_format}')).exists():
        return path
    elif output_directories:
        for output_directory in output_directories:
            if (path := pathlib.Path(output_directory / f'{exp_filename}.{output_format}')).exists():
                return path
    raise ValueError(f'Unable to find expected output file: {exp_filename}.{output_format}.')


def get_field_names(note_directories: List[pathlib.Path], *, output_format='json', mm_encoding='cp1252',
                    max_search=1000, output_directories=None):
    """

    :param note_directories:
    :param output_format:
    :param mm_encoding:
    :param max_search: how many files to look at in each directory
    :return:
    """
    logger.info('Retrieving fieldnames.')
    global MML_FIELDNAMES
    fieldnames = set(MML_FIELDNAMES)
    for note_dir in note_directories:
        cnt = 0
        for file in note_dir.iterdir():
            if file.suffix not in {'.txt', ''} or file.is_dir():
                continue
            outfile = get_output_file(file.parent, f'{str(file.stem)}', output_format,
                                      output_directories=output_directories)
            if not outfile.exists():
                continue
            for data in extract_mml_data(outfile, encoding=mm_encoding, output_format=output_format):
                for fieldname in set(data.keys()) - fieldnames:
                    MML_FIELDNAMES.append(fieldname)
                    fieldnames.add(fieldname)
            cnt += 1
            if cnt > max_search:
                break


def build_extracted_file(note_directories, target_cuis, note_outfile, mml_outfile,
                         output_format, encoding, exclude_negated, output_directories=None,
                         mm_encoding='cp1252'):
    missing_note_dict = set()
    missing_mml_dict = set()
    logger_warning_count = 5
    with open(note_outfile, 'w', newline='', encoding='utf8') as note_out, \
            open(mml_outfile, 'w', newline='', encoding='utf8') as mml_out:
        note_writer = csv.DictWriter(note_out, fieldnames=NOTE_FIELDNAMES)
        note_writer.writeheader()
        mml_writer = csv.DictWriter(mml_out, fieldnames=MML_FIELDNAMES)
        mml_writer.writeheader()
        for is_record, data in extract_data(note_directories, target_cuis=target_cuis,
                                            encoding=encoding, output_format=output_format,
                                            exclude_negated=exclude_negated, output_directories=output_directories,
                                            mm_encoding=mm_encoding):
            if is_record:
                field_names = NOTE_FIELDNAMES
            else:
                field_names = MML_FIELDNAMES
            curr_missing_data_dict = set(data.keys()) - set(field_names)
            if curr_missing_data_dict:
                if logger_warning_count > 0:
                    logger.warning(f'Only processing known fields for record: {data["docid"]}')
                    logger_warning_count -= 1
                    if logger_warning_count == 0:
                        logger.warning(f'Suppressing future warnings:'
                                       f' a final summary of added keys will be logged at the end.')
                if is_record:
                    missing_note_dict |= curr_missing_data_dict
                    if logger_warning_count >= 0:
                        logger.info(f'''Missing Note Dict: '{"','".join(missing_note_dict)}' ''')
                    data = {k: v for k, v in data.items() if k in NOTE_FIELDNAMES}
                else:
                    missing_mml_dict |= curr_missing_data_dict
                    if logger_warning_count >= 0:
                        logger.info(f'''Missing MML Dict: '{"','".join(missing_mml_dict)}' ''')
                    data = {k: v for k, v in data.items() if k in MML_FIELDNAMES}
            if is_record:
                note_writer.writerow(data)
            else:
                mml_writer.writerow(data)
    if missing_mml_dict:
        logger.warning(f'''All Missing MML Dict: '{"','".join(missing_mml_dict)}' ''')
    if missing_note_dict:
        logger.warning(f'''All Missing Note Dict: '{"','".join(missing_note_dict)}' ''')
    logger.info(f'Completed successfully.')


def extract_data(note_directories: List[pathlib.Path], *, target_cuis=None, encoding='utf8', mm_encoding='cp1252',
                 output_format='json', exclude_negated=False, output_directories=None):
    for note_dir in note_directories:
        logger.info(f'Processing directory: {note_dir}')
        yield from extract_data_from_directory(
            note_dir, encoding=encoding, exclude_negated=exclude_negated, mm_encoding=mm_encoding,
            output_format=output_format, target_cuis=target_cuis, output_directories=output_directories
        )


def extract_data_from_directory(note_dir, *, target_cuis=None, encoding='utf8', mm_encoding='cp1252',
                                output_format='json', exclude_negated=False, output_directories=None):
    for file in note_dir.iterdir():
        if file.suffix not in {'.txt', ''} or file.is_dir():  # assume all notes have suffixes and all output does not
            continue
        logger.info(f'Processing file: {file}')
        yield from extract_data_from_file(
            file, encoding=encoding, exclude_negated=exclude_negated, mm_encoding=mm_encoding,
            output_format=output_format, target_cuis=target_cuis, output_directories=output_directories,
        )


def extract_data_from_file(file, *, target_cuis=None, encoding='utf8', mm_encoding='cp1252',
                           output_format='json', exclude_negated=False, output_directories=None):
    record = {
        'filename': file.stem,
        'docid': str(file),
    }
    with open(file, encoding=encoding) as fh:
        text = fh.read()
        record['num_chars'] = len(text)
        record['num_words'] = len(text.split())
        record['num_letters'] = len(re.sub(r'[^A-Za-z0-9]', '', text, flags=re.I))
    outfile = get_output_file(file.parent, f'{str(file.stem)}', output_format,
                              output_directories=output_directories)
    if outfile.exists():
        logger.info(f'Processing associated {output_format}: {outfile}.')
        for data in extract_mml_data(outfile, encoding=mm_encoding,
                                     target_cuis=target_cuis, output_format=output_format):
            if exclude_negated and data['negated']:
                continue  # exclude negated terms if requested
            yield False, data
        record['processed'] = True
    else:
        record['processed'] = False
    yield True, record


if __name__ == '__main__':
    extract_mml()
