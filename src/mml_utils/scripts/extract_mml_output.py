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
    'event_id', 'docid', 'matchedtext', 'conceptstring', 'cui', 'preferredname', 'start', 'length',
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
@click.option('--output-format', type=str, default='json',
              help='Output format to look for (e.g., "json" or "mmi").')
@click.option('--add-fieldname', type=str, multiple=True,
              help='Add fieldnames to Metamaplite output.')
def extract_mml(note_directories: list[pathlib.Path], outdir: pathlib.Path, cui_file: pathlib.Path = None,
                *, encoding='utf8', output_format='json', max_search=1000, add_fieldname: list[str] = None):
    """

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
    get_field_names(note_directories, output_format=output_format, max_search=max_search)
    build_extracted_file(note_directories, target_cuis, note_outfile, mml_outfile,
                         output_format, encoding)


def get_field_names(note_directories: list[pathlib.Path], *, output_format='json', mm_encoding='cp1252',
                    max_search=1000):
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
            outfile = pathlib.Path(file.parent / f'{str(file.stem)}.{output_format}')
            if not outfile.exists():
                continue
            for _, data in extract_mml_data(outfile, encoding=mm_encoding, output_format=output_format):
                for fieldname in set(data.keys()) - fieldnames:
                    MML_FIELDNAMES.append(fieldname)
                    fieldnames.add(fieldname)
            cnt += 1
            if cnt > max_search:
                break


def build_extracted_file(note_directories, target_cuis, note_outfile, mml_outfile,
                         output_format, encoding):
    missing_note_dict = set()
    missing_mml_dict = set()
    with open(note_outfile, 'w', newline='', encoding='utf8') as note_out, \
            open(mml_outfile, 'w', newline='', encoding='utf8') as mml_out:
        note_writer = csv.DictWriter(note_out, fieldnames=NOTE_FIELDNAMES)
        note_writer.writeheader()
        mml_writer = csv.DictWriter(mml_out, fieldnames=MML_FIELDNAMES)
        mml_writer.writeheader()
        for is_record, data in extract_data(note_directories, target_cuis=target_cuis,
                                            encoding=encoding, output_format=output_format):
            if is_record:
                field_names = NOTE_FIELDNAMES
            else:
                field_names = MML_FIELDNAMES
            curr_missing_data_dict = set(data.keys()) - set(field_names)
            if curr_missing_data_dict:
                logger.error(f'Only processing known fields for record: {data["fullpath"]}')
                if is_record:
                    missing_note_dict |= curr_missing_data_dict
                    logger.error(f'''Missing Note Dict: '{"','".join(missing_note_dict)}' ''')
                    data = {k: v for k, v in data.items() if k in NOTE_FIELDNAMES}
                else:
                    missing_mml_dict |= curr_missing_data_dict
                    logger.error(f'''Missing MML Dict: '{"','".join(missing_mml_dict)}' ''')
                    data = {k: v for k, v in data.items() if k in MML_FIELDNAMES}
            if is_record:
                note_writer.writerow(data)
            else:
                mml_writer.writerow(data)


def extract_data(note_directories: list[pathlib.Path], *, target_cuis=None, encoding='utf8', mm_encoding='cp1252',
                 output_format='json'):
    for note_dir in note_directories:
        logger.info(f'Processing directory: {note_dir}')
        for file in note_dir.iterdir():
            if file.suffix not in {'.txt',
                                   ''} or file.is_dir():  # assume all notes have suffixes and all output does not
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
            outfile = pathlib.Path(file.parent / f'{str(file.stem)}.{output_format}')
            if outfile.exists():
                logger.info(f'Processing associated {output_format}: {outfile}.')
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
    if not target_cuis:
        target_cuis = set()
    i = 0
    prev_line = None
    for line in csv.reader(io.StringIO(text), delimiter='|'):
        if not line[-1] == '':
            prev_line = line
            continue
        if prev_line:
            carryover_cell = prev_line[-1] + line[0]
            line = prev_line[:-1] + [carryover_cell] + line[1:]
            prev_line = None
        for d in extract_mmi_line(line):
            if not d or d['cui'] not in target_cuis:
                continue
            d['event_id'] = f'{filename}_{i}'
            yield False, d
            i += 1


def extract_mmi_line(line):
    if line[1] != 'MMI':
        logger.warning(f'Line contains {line[1]} rather the "MMI"; skipping line: {line}')
        return
    (identifier, mmi, score, conceptstring, cui, semantictype, triggerinfo,
     location, positional_info, treecodes, *other) = line[:10]
    semantictypes = [st.strip() for st in semantictype[1:-1].split(',')]  # official doco says comma-separated
    triggerinfos = [
        list(csv.reader([element], delimiter='-'))[0]
        for row in csv.reader([triggerinfo], delimiter=',')
        for element in row
    ]
    new_triggerinfos = []
    for ti in triggerinfos:
        new_triggerinfos.append(['-'.join(ti[:len(ti) - 5])] + ti[len(ti) - 5:])
    triggerinfos = new_triggerinfos
    positional_infos = [loc.split('/') for loc in positional_info.split(';')]
    for (preferredname, loc, locpos, matchedtext, pos, negation
         ), (start, length) in zip(triggerinfos, positional_infos):
        yield {
                  'docid': identifier,
                  'matchedtext': matchedtext,
                  'conceptstring': conceptstring,
                  'cui': cui,
                  'preferredname': preferredname,
                  'start': int(start),
                  'length': int(length),
                  'evid': None,
                  'negated': int(negation),
                  'pos': pos,
                  'semantictype': semantictypes[0],  # usually (always?) just one, so show it
              } | {
                  s: 1 for s in semantictypes
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
