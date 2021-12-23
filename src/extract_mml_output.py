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
import json
import pathlib
import re

import click
from loguru import logger

MML_FIELDNAMES = [
    'event_id', 'docid', 'matchedtext', 'conceptstring', 'cui', 'preferredname', 'start', 'length', 'evid', 'negated',
    'neop', 'orga', 'qnco', 'patf', 'cell', 'qlco', 'menp', 'ftcn', 'aggp', 'inpo', 'dora', 'inpr', 'famg', 'ortf',
    'npop', 'anab', 'hlca', 'podg', 'tmco', 'lbpr', 'edac', 'mbrt', 'socb', 'prog', 'medd', 'bpoc', 'mobd', 'clna',
    'topp', 'sosy', 'idcn', 'bmod', 'SRC', 'rnlw', 'virs', 'spco', 'dsyn', 'popg', 'eehu', 'acty', 'orgf', 'cgab',
    'tisu', 'hcpp', 'acab', 'lbtr', 'inbe', 'genf', 'evnt', 'comd', 'MDR', 'phsf', 'fndg', 'bdsu', 'phpr', 'diap'
]
NOTE_FIELDNAMES = [
    'filename', 'fullpath', 'num_chars', 'num_letters', 'num_words', 'processed',
]


@click.command()
@click.argument('note-directories', nargs=-1, type=click.Path(exists=True, path_type=pathlib.Path), )
@click.option('--outdir', type=click.Path(exists=True, path_type=pathlib.Path),
              help='Output directory to place result files.')
def extract_mml(note_directories: list[pathlib.Path], outdir: pathlib.Path, *, encoding='utf8'):
    """

    :param note_directories: Directories to with files processed by metamap and
                containing the output (e.g., json) files.
    :param outdir:
    :param encoding:
    :return:
    """
    now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    note_outfile = outdir / f'notes_{now}.csv'
    mml_outfile = outdir / f'mml_{now}.csv'
    missing_note_dict = set()
    missing_mml_dict = set()
    with open(note_outfile, 'w', encoding='utf8') as note_out, \
            open(mml_outfile, 'w', encoding='utf8') as mml_out:
        note_writer = csv.DictWriter(note_out, fieldnames=NOTE_FIELDNAMES)
        note_writer.writeheader()
        mml_writer = csv.DictWriter(mml_out, fieldnames=MML_FIELDNAMES)
        mml_writer.writeheader()
        for is_record, data in extract_data(note_directories, encoding=encoding):
            if is_record:
                field_names = NOTE_FIELDNAMES
            else:
                field_names = MML_FIELDNAMES
            curr_missing_data_dict = set(data.keys()) - set(field_names)
            if curr_missing_data_dict:
                logger.error('Skipping record...')
                if is_record:
                    missing_note_dict |= curr_missing_data_dict
                    logger.error(f'''Missing Note Dict: '{"','".join(missing_note_dict)}' ''')
                else:
                    missing_mml_dict |= curr_missing_data_dict
                    logger.error(f'''Missing MML Dict: '{"','".join(missing_mml_dict)}' ''')
            else:
                if is_record:
                    note_writer.writerow(data)
                else:
                    mml_writer.writerow(data)


def extract_data(note_directories: list[pathlib.Path], *, encoding='utf8', output_format='json'):
    for note_dir in note_directories:
        logger.info(f'Processing directory: {note_dir}')
        for file in note_dir.iterdir():
            if file.suffix:  # assume all notes have suffixes and all output does not
                continue
            logger.info(f'Processing file: {file}')
            record = {
                'filename': file.stem,
                'fullpath': str(file),
            }
            with open(file, encoding=encoding) as fh:
                text = fh.read()
                record['num_chars'] = len(text)
                record['num_words'] = len(text.split())
                record['num_letters'] = len(re.sub(r'[^A-Za-z0-9]', '', text, flags=re.I))
            outfile = pathlib.Path(f'{str(file)}.{output_format}')
            if outfile.exists():
                logger.info(f'Processing associated json: {outfile}.')
                yield from extract_mml_data(outfile)
                record['processed'] = True
            else:
                record['processed'] = False
            yield True, record


def extract_mml_data(file: pathlib.Path, *, target_cuis=None):
    with open(file, encoding='utf8') as fh:
        data = json.load(fh)
    i = 0
    for el in data:
        for event in el['evlist']:
            if target_cuis is None or event['conceptinfo']['cui'] in target_cuis:
                yield False, {
                    'event_id': f'{file.name}_{i}',
                    'docid': file.name,
                    'matchedtext': event['matchedtext'],
                    'conceptstring': event['conceptinfo']['conceptstring'],
                    'cui': event['conceptinfo']['cui'],
                    'preferredname': event['conceptinfo']['preferredname'],
                    'start': event['start'],
                    'length': event['length'],
                    'evid': event['id'],
                    'negated': el.get('negated', None),
                } | {
                          s: 1 for s in event['conceptinfo']['sources']
                      } | {
                          s: 1 for s in event['conceptinfo']['semantictypes']
                      }
                i += 1


if __name__ == '__main__':
    extract_mml()
