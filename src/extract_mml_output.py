"""
Extract output from metamaplite, and create two tables. These are primarily in preparation
    for use by PheNorm, but alternative implementations might also be valuable.

Table 1: All CUIs (or subset, if specified) with MML and other metadata.
filename, [metamaplite metadata], [other metadata joinable on 'filename'; e.g., note metadata]

Table 2: Notes with note length and whether or not it was processed.
filename, length, processed: yes/no
"""
import json
import pathlib
import re

import click


@click.command()
@click.option('--note-directories', nargs='+', type=click.Path(exists=True), path_type=pathlib.Path,
              help='Directories to with files processed by metamap and containing the output (e.g., json) files.')
def extract_mml(note_directories: list[pathlib.Path], *, encoding='utf8'):
    notes, outfiles = read_directories(note_directories)
    note_records, mml_records = extract_data(notes, outfiles, encoding=encoding)


def extract_data(notes, outfiles, *, encoding='utf8'):
    records = []
    mml_data = []
    for filename, file in notes.items():
        record = {'filename': filename}
        with open(file, encoding=encoding) as fh:
            text = fh.read()
            record['num_chars'] = len(text)
            record['num_words'] = len(text.split())
            record['num_letters'] = len(re.sub(r'[^A-Za-z0-9]', '', text, flags=re.I))
        if filename in outfiles:
            mml_data += extract_mml_data(outfiles[filename])
            record['processed'] = True
        else:
            record['processed'] = False
        records.append(record)
    return records, mml_data


def extract_mml_data(file: pathlib.Path, *, target_cuis=None):
    records = []
    with open(file, encoding='utf8') as fh:
        data = json.load(fh)
    i = 0
    for el in data:
        for event in el['evlist']:
            if target_cuis is None or event['conceptinfo']['cui'] in target_cuis:
                records.append(
                    {
                        'event_id': f'{file.name}_{i}',
                        'docid': file.name,
                        'matchedtext': event['matchedtext'],
                        'conceptstring': event['conceptinfo']['conceptstring'],
                        'cui': event['conceptinfo']['cui'],
                        'preferredname': event['conceptinfo']['preferredname'],
                        'start': event['start'],
                        'length': event['length'],
                        'evid': event['id'],
                        'negated': el['negated'],
                    } | {
                        s: 1 for s in event['conceptinfo']['sources']
                    } | {
                        s: 1 for s in event['conceptinfo']['semantictypes']
                    }
                )
                i += 1
    return records


def read_directories(note_directories: list[pathlib.Path], output_format='json'):
    notes = {}
    outfiles = {}
    # get all data
    for note_dir in note_directories:
        for file in note_dir.iterdir():
            if file.suffix == output_format:
                outfiles[file.stem] = file
            else:
                notes[file.stem] = file
    return notes, outfiles


if __name__ == '__main__':
    extract_mml()
