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
from mml_utils.parse.target_cuis import TargetCuis

try:
    import pandas as pd
except ImportError:
    pd = None

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
              help='File containing one cui per line which should be included in the output;'
                   ' to enable mapping, place FROM_CUI,TO_CUI on the line.')
@click.option('--output-format', type=str, default='json',
              help='Output format to look for (MML: "json" or "mmi"; cTAKES: "xmi").')
@click.option('--output-directory', 'output_directories', multiple=True,
              type=click.Path(exists=True, path_type=pathlib.Path, file_okay=False),
              help='(Optional) Output directories if different from `note-directories` (e.g., for cTAKES).')
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
@click.option('--note-suffix', default='.txt',
              help='Specify note suffix if different than no suffix and ".txt". Include the period.')
@click.option('--output-suffix', default=None,
              help='Specify output suffix for mmi/json files if different from default `--output-format`.'
                   ' Include the period.')
def _extract_mml(note_directories: List[pathlib.Path], outdir: pathlib.Path, cui_file: pathlib.Path = None,
                 *, encoding='utf8', output_format='json', max_search=1000, add_fieldname: List[str] = None,
                 exclude_negated=False, output_directories=None, mm_encoding='cp1252'):
    extract_mml(note_directories, outdir, cui_file,
                encoding=encoding, output_format=output_format, max_search=max_search, add_fieldname=add_fieldname,
                exclude_negated=exclude_negated, output_directories=output_directories, mm_encoding=mm_encoding)


def load_target_cuis(cui_file) -> TargetCuis:
    target_cuis = TargetCuis()
    if cui_file is None:
        logger.warning(f'Retaining all CUIs.')
        return target_cuis
    with open(cui_file, encoding='utf8') as fh:
        for line in fh:
            target_cuis.add(*line.strip().split(','))
    logger.info(f'Keeping {target_cuis.n_keys()} CUIs, and mapping to {target_cuis.n_values()}.')
    return target_cuis


def extract_mml(note_directories: List[pathlib.Path], outdir: pathlib.Path, cui_file: pathlib.Path = None,
                *, encoding='utf8', output_format='json', max_search=1000, add_fieldname: List[str] = None,
                exclude_negated=False, output_directories=None, mm_encoding='cp1252',
                note_suffix='.txt', output_suffix=None):
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
    cuis_by_doc_outfile = outdir / f'cuis_by_doc_{now}.csv'

    if add_fieldname:
        global MML_FIELDNAMES
        for fieldname in add_fieldname:
            MML_FIELDNAMES.append(fieldname)

    target_cuis = load_target_cuis(cui_file)
    if output_directories is None:
        output_directories = note_directories
    get_field_names(note_directories, output_format=output_format, max_search=max_search,
                    output_directories=output_directories, mm_encoding=mm_encoding,
                    note_suffix=note_suffix, output_suffix=output_suffix)
    build_extracted_file(note_directories, target_cuis, note_outfile, mml_outfile,
                         output_format, encoding, exclude_negated, output_directories=output_directories,
                         mm_encoding=mm_encoding, note_suffix=note_suffix, output_suffix=output_suffix)
    build_pivot_table(mml_outfile, cuis_by_doc_outfile)
    return note_outfile, mml_outfile, cuis_by_doc_outfile


def get_output_file(curr_directory, exp_filename, output_format, output_directories=None, skip_missing=False,
                    output_suffix=None):
    """Retrieve the extracted data from file."""
    if output_suffix is not None:
        output_format = output_suffix.lstrip('.')
    elif output_format == 'xmi':
        output_format = 'txt.xmi'  # how ctakes does renaming
    if (path := pathlib.Path(curr_directory / f'{exp_filename}.{output_format}')).exists():
        return path
    elif output_directories:
        for output_directory in output_directories:
            if (path := pathlib.Path(output_directory / f'{exp_filename}.{output_format}')).exists():
                return path
    exp_filename = exp_filename.split('.')[0]
    if (path := pathlib.Path(curr_directory / f'{exp_filename}.{output_format}')).exists():
        return path
    elif output_directories:
        for output_directory in output_directories:
            if (path := pathlib.Path(output_directory / f'{exp_filename}.{output_format}')).exists():
                return path
    msg = f'Unable to find expected output file: {exp_filename}.{output_format}.'
    if skip_missing:
        logger.warning(msg)
    else:
        raise ValueError(msg)


def get_field_names(note_directories: List[pathlib.Path], *, output_format='json', mm_encoding='cp1252',
                    max_search=1000, output_directories=None,
                    note_suffix='.txt', output_suffix=None):
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
            if (file.suffix not in {note_suffix, ''} and ''.join(file.suffixes) != note_suffix) or file.is_dir():
                continue
            outfile = get_output_file(file.parent, file.stem, output_format,
                                      output_directories=output_directories, output_suffix=output_suffix)
            if outfile is None or not outfile.exists():
                continue
            for data in extract_mml_data(outfile, encoding=mm_encoding, output_format=output_format,
                                         target_cuis=TargetCuis()):
                for fieldname in set(data.keys()) - fieldnames:
                    MML_FIELDNAMES.append(fieldname)
                    fieldnames.add(fieldname)
            cnt += 1
            if cnt > max_search:
                break


def build_extracted_file(note_directories, target_cuis, note_outfile, mml_outfile,
                         output_format, encoding, exclude_negated, output_directories=None,
                         mm_encoding='cp1252', note_suffix='.txt', output_suffix=None):
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
                                            mm_encoding=mm_encoding, note_suffix=note_suffix,
                                            output_suffix=output_suffix):
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


def build_pivot_table(mml_file, outfile):
    if pd is None:
        logger.warning(f'Unable to build pivot table: please install pandas `pip install pandas` and try again.')
        return
    df = pd.read_csv(mml_file, usecols=['docid', 'cui'])
    n_cuis = df['cui'].nunique()
    n_docs = df['docid'].nunique()
    df['count'] = 1
    df = df.pivot_table(index='docid', columns='cui', values='count', fill_value=0, aggfunc=sum).reset_index()
    df.to_csv(outfile, index=False)
    logger.info(f'Output {n_cuis} CUIs for {n_docs} documents to: {outfile}.')


def extract_data(note_directories: List[pathlib.Path], *, target_cuis=None, encoding='utf8', mm_encoding='cp1252',
                 output_format='json', exclude_negated=False, output_directories=None, note_suffix='.txt',
                 output_suffix=None):
    for note_dir in note_directories:
        logger.info(f'Processing directory: {note_dir}')
        yield from extract_data_from_directory(
            note_dir, encoding=encoding, exclude_negated=exclude_negated, mm_encoding=mm_encoding,
            output_format=output_format, target_cuis=target_cuis, output_directories=output_directories,
            note_suffix=note_suffix, output_suffix=output_suffix
        )


def extract_data_from_directory(note_dir, *, target_cuis=None, encoding='utf8', mm_encoding='cp1252',
                                output_format='json', exclude_negated=False, output_directories=None,
                                note_suffix='.txt', output_suffix=None):
    for file in note_dir.iterdir():
        if (file.suffix not in {note_suffix, ''} and ''.join(file.suffixes) != note_suffix) or file.is_dir():
            continue
        logger.info(f'Processing file: {file}')
        yield from extract_data_from_file(
            file, encoding=encoding, exclude_negated=exclude_negated, mm_encoding=mm_encoding,
            output_format=output_format, target_cuis=target_cuis, output_directories=output_directories,
            output_suffix=output_suffix
        )


def extract_data_from_file(file, *, target_cuis=None, encoding='utf8', mm_encoding='cp1252',
                           output_format='json', exclude_negated=False, output_directories=None, output_suffix=None):
    record = {
        'filename': file.stem,
        'docid': str(file),
    }
    target_cuis = TargetCuis() if target_cuis is None else target_cuis
    with open(file, encoding=encoding) as fh:
        text = fh.read()
        record['num_chars'] = len(text)
        record['num_words'] = len(text.split())
        record['num_letters'] = len(re.sub(r'[^A-Za-z0-9]', '', text, flags=re.I))
    outfile = get_output_file(file.parent, file.stem, output_format,
                              output_directories=output_directories, output_suffix=output_suffix)
    if outfile is None:
        stem = file.stem.split('.')[0]
        outfile = get_output_file(file.parent, f'{stem}', output_format,
                                  output_directories=output_directories, output_suffix=output_suffix)
    if outfile and outfile.exists():
        logger.info(f'Processing associated {output_format}: {outfile}.')
        for data in extract_mml_data(outfile, encoding=mm_encoding,
                                     target_cuis=target_cuis, output_format=output_format):
            if exclude_negated and data['negated']:
                continue  # exclude negated terms if requested
            yield False, data
        record['processed'] = True
    else:
        exp_suffix = output_suffix if output_suffix else f'.{output_format}'
        stem = file.stem.split('.')[0]
        logger.warning(f'Expected {output_format} file like {file.stem}{exp_suffix} or {stem}{exp_suffix}'
                       f' in {output_directories}.')
        record['processed'] = False
    yield True, record


if __name__ == '__main__':
    _extract_mml()
