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
import io
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
    'tisu', 'hcpp', 'acab', 'lbtr', 'inbe', 'genf', 'evnt', 'comd', 'MDR', 'phsf', 'fndg', 'bdsu', 'phpr', 'diap',
    'USP', 'NCI_ICDC', 'GO', 'ICF', 'NCI_NCPDP', 'CHV', 'MEDLINEPLUS', 'FMA', 'NCI_CTCAE_5', 'NCI_NICHD', 'bodm',
    'OMIM', 'QMR', 'NCI_DCP', 'ICPC', 'CSP', 'aapp', 'NCI_CTCAE', 'SNOMEDCT_US', 'CCS', 'NCI_FDA', 'DRUGBANK', 'horm',
    'MED-RT', 'NCI_NCI-HL7', 'COSTAR', 'enzy', 'hops', 'NCI_CTRP', 'SNOMEDCT_VET', 'inch', 'MCM', 'ICD10PCS', 'irda',
    'DXP', 'ICD10CM', 'NCI_DTP', 'LCH_NW', 'CCSR_10', 'ICD9CM', 'UWDA', 'MTHICD9', 'NCI_ACC-AHA', 'CVX',
    'NCI_BRIDG_5_3', 'elii', 'HCPCS', 'NCI_EDQM-HC', 'NCI_NCI-GLOSS', 'phsu', 'NCI_CRCH', 'bacs', 'vita', 'HL7V3.0',
    'LNC', 'imft', 'MSH', 'NCI_CDISC-GLOSS', 'SNMI', 'NCI', 'ATC', 'chvf', 'SPN', 'AOT', 'AOD', 'HL7V2.5', 'ICF-CY',
    'USPMG', 'nnon', 'MTHMST', 'AIR', 'orch', 'NCI_CELLOSAURUS', 'LCH', 'NCI_BRIDG_3_0_3', 'MTHSPL', 'VANDF',
    'NCI_CDISC', 'MTH', 'SNM', 'CST', 'RXNORM', 'rcpt', 'NCI_CTCAE_3', 'NCI_GDC', 'CCS_10', 'PDQ', 'chvs', 'HPO'
]
NOTE_FIELDNAMES = [
    'filename', 'fullpath', 'num_chars', 'num_letters', 'num_words', 'processed',
]


@click.command()
@click.argument('note-directories', nargs=-1, type=click.Path(exists=True, path_type=pathlib.Path), )
@click.option('--outdir', type=click.Path(exists=True, path_type=pathlib.Path),
              help='Output directory to place result files.')
@click.option('--cui-file', type=click.Path(exists=True, path_type=pathlib.Path, dir_okay=False),
              help='File containing one cui per line which should be included in the output.')
def extract_mml(note_directories: list[pathlib.Path], outdir: pathlib.Path, cui_file: pathlib.Path = None,
                *, encoding='utf8'):
    """

    :param cui_file: File containing one cui per line which should be included in the output.
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

    target_cuis = None
    if cui_file is not None:
        with open(cui_file, encoding='utf8') as fh:
            target_cuis = set(x.strip() for x in fh.read().split('\n'))
        logger.info(f'Retaining only {len(target_cuis)} CUIs.')
    with open(note_outfile, 'w', newline='', encoding='utf8') as note_out, \
            open(mml_outfile, 'w', newline='', encoding='utf8') as mml_out:
        note_writer = csv.DictWriter(note_out, fieldnames=NOTE_FIELDNAMES)
        note_writer.writeheader()
        mml_writer = csv.DictWriter(mml_out, fieldnames=MML_FIELDNAMES)
        mml_writer.writeheader()
        for is_record, data in extract_data(note_directories, target_cuis=target_cuis, encoding=encoding):
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


def extract_data(note_directories: list[pathlib.Path], *, target_cuis=None, encoding='utf8', mm_encoding='cp1252',
                 output_format='json'):
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
                yield from extract_mml_data(outfile, encoding=mm_encoding,
                                            target_cuis=target_cuis, output_format=output_format)
                record['processed'] = True
            else:
                record['processed'] = False
            yield True, record


def extract_mml_data(file: pathlib.Path, *, encoding='cp1252', target_cuis=None, output_format='json'):
    with open(file, encoding=encoding) as fh:
        text = fh.read()
    if not text.strip():  # handle empty note
        return
    if output_format == 'json':  # TODO: match-case
        data = json.loads(text)
        yield from extract_mml_from_json_data(data, file.name, target_cuis=target_cuis)
    elif output_format == 'mmi':
        yield from extract_mml_from_mmi_data(text, file.name, target_cuis=target_cuis)
    else:
        raise ValueError(f'Unrecognized output format: {output_format}.')


def extract_mml_from_mmi_data(text, filename, *, target_cuis=None):
    i = 0
    for line in csv.reader(io.StringIO(text), sep='|'):
        d = extract_mmi_line(line)
        if not d:
            continue
        d['event_id'] = f'{filename}_{i}'
        yield d
        i += 1


def extract_mmi_line(line):
    if line[1] != 'MMI':
        logger.warning(f'Line contains {line[1]} rather the "MMI"; skipping line: {line}')
        return
    identifier, mmi, score, preferredname, cui, semantictype, triggerinfo, location, positional_info, treecodes = line
    return {
        'docid': identifier,
        'matchedtext': None,
        'conceptstring': None,
        'cui': cui,
        'preferredname': preferredname,
        'start': None,
        'length': None,
        'evid': None,
        'negated': None,
        'semantictype': semantictype[1:-1],
    }


def extract_mml_from_json_data(data, filename, *, target_cuis=None):
    i = 0
    for el in data:
        for event in el['evlist']:
            if target_cuis is None or event['conceptinfo']['cui'] in target_cuis:
                yield False, {
                    'event_id': f'{filename}_{i}',
                    'docid': filename,
                    'matchedtext': event['matchedtext'],
                    'conceptstring': event['conceptinfo']['conceptstring'],
                    'cui': event['conceptinfo']['cui'],
                    'preferredname': event['conceptinfo']['preferredname'],
                    'start': event['start'],
                    'length': event['length'],
                    'evid': event['id'],
                    'negated': el.get('negated', None),
                    'semantictype': event['conceptinfo']['semantictypes'][0],
                    'source': event['conceptinfo']['sources'][0],
                } | {
                          s: 1 for s in event['conceptinfo']['sources']
                      } | {
                          s: 1 for s in event['conceptinfo']['semantictypes']
                      }
                i += 1


if __name__ == '__main__':
    extract_mml()
