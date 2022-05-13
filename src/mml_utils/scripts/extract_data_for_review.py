"""
Extract CUIs and text strings for some feature (e.g., fever, diarrhea, etc.) from MML output.
These can then be used to review the results to determine how useful the CUIs/text strings are.

Runs on Metamaplite output directories (text file and jsonl/mmi expected in same directory).

Expects a feature directory:
* {feature_name}.string.txt
    * unique text string to look for on each line
    * Examples:
        * BM frequent
        * BM loose
* {feature_name}.cui.txt
    * unique CUI to look for on each line
    * additional data can be included in tab-separated format
    * Examples:
        * C0687681
        * C0687681\tFeeling feverish


# Generate Reviews for Output Data

```python
import pandas as pd
from loguru import logger

SAMPLE_SIZE = 50
df = pd.GET_METADATA()  # e.g., with studyid and docid
with pd.ExcelWriter(outpath / f'features.review{SAMPLE_SIZE}.xlsx') as writer:
    logger.info(f"All notes dataset -> Unique Notes: {df['note_id'].nunique()}; Unique Patients: {df['studyid'].nunique()}")
    for file in base_path.glob('*.review.csv'):
        feature_name = file.stem.split('.')[0]
        logger.info(f'Reading feature {feature_name}: {file}')
        feature_df = pd.read_csv(file)
        logger.info(f"Source feature dataset -> Unique Notes: {feature_df['docid'].nunique()}")
        mdf = pd.merge(df, feature_df, on='docid')
        logger.info(f"Merged dataset -> Unique Notes: {mdf['docid'].nunique()}; Unique Patients: {mdf['studyid'].nunique()}")
        # output options
        mdf['Is this term referring to the feature?'] = ''
        mdf['Does the patient have this feature?'] = ''
        mdf['Optional Comments'] = ''
        unique_notes = mdf['docid'].unique()
        sampled = random.sample(sorted(unique_notes), SAMPLE_SIZE)
        rdf = mdf[mdf.docid.isin(sampled)]
        rdf = rdf[[
            'id', 'studyid', 'docid', 'precontext', 'keyword', 'postcontext', 'Is this term referring to the feature?',
            'Does the patient have this feature?', 'Optional Comments', 'fullcontext'
        ]]
        rdf.to_csv(outpath / f'{feature_name}.sample{SAMPLE_SIZE}.csv', index=False)
        rdf.to_excel(writer, sheet_name=feature_name, index=False)
```
"""
import csv
import pathlib
import re

import click
from loguru import logger

from mml_utils.parse.parser import extract_mml_data


def get_feature_names_from_directory(target_path: pathlib.Path):
    done = set()
    for f in target_path.iterdir():
        if not f.name.endswith('cui.txt'):
            continue
        feature_name, label, ext = f.name.split('.')
        if feature_name in done:
            continue
        yield feature_name
        done.add(feature_name)


def finditer(target, text: str, offset=0):
    """

    :param target:
    :param text:
    :param offset:
    :return: start, end
    """
    sub_offset = 0
    while True:
        try:
            index = text.index(target, sub_offset)
        except ValueError:
            return
        end = index + len(target)
        yield index + offset, end + offset
        sub_offset = end


def find_target_text(text, target, start, end):
    if target == text[start:end]:
        return start, end
    for width in [50, 100]:
        curr_text = text[max(start - width, 0):end + width]
        if target in curr_text:
            best_distance = width  # default to max
            best_start = None
            best_end = None
            for _start, _end in finditer(target, curr_text, offset=start - width):
                new_distance = min(abs(_start - start), abs(_end - start), abs(_start - end), abs(_end - end))
                if new_distance < best_distance:
                    best_distance = new_distance
                    best_start = _start
                    best_end = _end
            return best_start, best_end
    else:
        raise ValueError(f'Unable to find target `{target}` in text at {start}:{end}.')


def clean_text(text: str):
    return text.replace('\n', '\\n').replace('\t', ' ')


@click.command()
@click.argument('note-directories', nargs=-1, type=click.Path(exists=True, path_type=pathlib.Path))
@click.option('--target-path', type=click.Path(exists=True, path_type=pathlib.Path),
              help='Directory contain files like "fever.cui.txt" and "fever.string.txt"')
@click.option('--mml-format', type=str, default='json',
              help='MML Output format to look for (e.g., "json" or "mmi"); currently only supports "json" and "mmi".')
@click.option('--text-extension', type=str, default='',
              help='Add ".txt" if text files have an extension.')
@click.option('--text-encoding', type=str, default='utf8',
              help='Format to read text files into metamaplite.')
@click.option('--text-errors', type=str, default='replace',
              help='Passed to "errors" in "open" function to open file.')
@click.option('--add-cr', type=bool, default=False, is_flag=True,
              help='Add back carriage return; likely required if MML run on Windows.')
@click.option('--replacements', type=str, multiple=True,
              help='Replace text to fix offset issues. Arguments should look like "from==to" which will'
                   ' replace "from" with "to" before checking offsets.')
def _extract_data_for_review(note_directories: list[pathlib.Path], target_path: pathlib.Path = pathlib.Path('.'),
                             mml_format='json', text_extension='', text_encoding='utf8',
                             text_errors='replace', add_cr=False, replacements=None):
    extract_data_for_review(note_directories, target_path, mml_format, text_extension, text_encoding,
                            text_errors=text_errors, add_cr=add_cr, replacements=replacements)


def extract_data_for_review(note_directories: list[pathlib.Path], target_path: pathlib.Path = pathlib.Path('.'),
                            mml_format='json', text_extension='', text_encoding='utf8',
                            text_errors='replace', add_cr=False, replacements=None):
    """

    :param text_encoding:
    :param note_directories:
    :param target_path:
    :param mml_format:
    :param text_extension: must include `.` (e.g., `.txt`)
    :return:
    """
    for feature_name in get_feature_names_from_directory(target_path):
        target_cuis = load_first_column(target_path / f'{feature_name}.cui.txt')
        logger.info(f'Starting "{feature_name}" with {len(target_cuis)} target CUIs.')
        # create pattern: sort by longest to ensure longest regex is matched first
        target_pattern = re.sub(
            r'\s+', r'\\s+',
            '|'.join(sorted(load_first_column(target_path / f'{feature_name}.string.txt'), key=lambda x: -len(x)))
        )
        target_regex = re.compile(f"({target_pattern})", re.I)
        unique_id = 0
        with open(target_path / f'{feature_name}.review.csv', 'w',
                  newline='', encoding=text_encoding) as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=['id', 'docid', 'start', 'end', 'length', 'negation', 'type',
                            'precontext', 'keyword', 'postcontext', 'fullcontext']
            )
            writer.writeheader()
            for note_directory in note_directories:
                logger.info(f'Reading directory {note_directory}.')
                note_count = 0
                no_text_file_count = 0
                for mml_file in note_directory.glob(f'*.{mml_format}'):
                    txt_file = note_directory / f'{mml_file.stem}{text_extension}'
                    if not txt_file.exists():
                        logger.warning(f'Failed to find corresponding text file:'
                                       f' {txt_file.name} (extension: {text_extension}).')
                        no_text_file_count += 1
                        continue
                    note_count += 1
                    with open(txt_file, encoding=text_encoding, errors=text_errors) as fh:
                        text = fh.read()
                    if add_cr:
                        text = text.replace('\n', '\r\n')
                    if replacements:
                        for _from, _to in replacements:
                            text = text.replace(_from, _to)
                    cui_data = []
                    for data in extract_mml_data(mml_file, target_cuis=target_cuis, output_format=mml_format):
                        try:
                            start, end = find_target_text(text, data['matchedtext'], data['start'], data['end'])
                        except ValueError as ve:
                            logger.error(f'Lookup failed for {mml_file}.')
                            logger.exception(ve)
                            raise
                        if cui_data and (cui_data[-1][0] <= start <= cui_data[-1][1]):  # overlaps?
                            # keep longer if overlaps with previous cui
                            if end - start > cui_data[-1][1] - cui_data[-1][0]:
                                cui_data[-1] = start, end, True, data['negated']
                        else:  # no overlap
                            cui_data.append((start, end, True, data['negated']))
                    # find mentions from string
                    text_data = []
                    for m in target_regex.finditer(text):
                        start, end = m.start(), m.end()
                        overlap = False
                        for cui_start, cui_end, is_cui, negated in cui_data:
                            if not is_cui or cui_start > start:
                                break
                            # is there overlap from cuis?
                            if is_cui and start <= cui_start <= end or start <= cui_end <= end:
                                overlap = True
                                break  # skip if cui already contained
                        if not overlap:
                            text_data.append((start, end, False, -1))
                    # output remaining matches
                    for start, end, is_cui, negated in sorted(cui_data + text_data):
                        writer.writerow({
                            'id': unique_id,
                            'docid': mml_file.stem,
                            'start': start,
                            'end': end,
                            'length': end - start,
                            'negation': negated,
                            'type': 'CUI' if is_cui else 'TEXT',
                            'precontext': clean_text(text[max(0, start - 100):start]),
                            'keyword': clean_text(text[start:end]),
                            'postcontext': clean_text(text[end:end + 100]),
                            'fullcontext': clean_text(text[max(0, start - 250): end + 250]),
                        })
                        unique_id += 1
                logger.info(f'Completed processing {note_count} notes (Total Matches: {unique_id}).')
                if no_text_file_count:
                    logger.warning(f'Failed to find {no_text_file_count} text files.')


def load_first_column(file: pathlib.Path):
    res = {}
    with open(file) as fh:
        for line in fh:
            if line.strip():
                res[line.strip().split('\t')[0]] = 1
    return res


if __name__ == '__main__':
    _extract_data_for_review()
