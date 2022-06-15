"""

* DECISION: treat all note_ids as string
"""
import csv
import datetime
import pathlib
import re
from collections import defaultdict
from typing import List

from loguru import logger

from mml_utils.parse.parser import extract_mml_data
from mml_utils.review.build_excel import compile_to_excel


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


def _get_note_ids_from_metadata_csv(csvfile: pathlib.Path, note_id_col='note_id'):
    note_ids = set()
    with open(csvfile, newline='') as fh:
        for line in csv.DictReader(fh):
            note_ids.add(str(line[note_id_col]))
    return note_ids


def extract_data_for_review(note_directories: List[pathlib.Path], target_path: pathlib.Path = pathlib.Path('.'),
                            mml_format='json', text_extension='', text_encoding='utf8',
                            text_errors='replace', add_cr=False, sample_size=50, metadata_file=None,
                            replacements=None):
    """

    :param text_errors:
    :param add_cr:
    :param sample_size:
    :param metadata_file: add metadata in excel and/or limit the number of notes
    :param replacements:
    :param text_encoding:
    :param note_directories:
    :param target_path:
    :param mml_format:
    :param text_extension: must include `.` (e.g., `.txt`)
    :return:
    """
    if sample_size:
        try:
            import openpyxl
        except ImportError:
            logger.warning(f'Unable to import openpyxl to build review sets:'
                           f' run `pip install openpyxl` if you want Excel files rather than CSV files to review.')

    outpath = target_path / f'review_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'
    outpath.mkdir(exist_ok=False)
    note_ids = defaultdict(list)
    # limit note ids to just those in a metadata csv file
    limit_note_ids = _get_note_ids_from_metadata_csv(metadata_file) if metadata_file else None
    # run separately for each feature
    for feature_name in get_feature_names_from_directory(target_path):
        target_cuis = load_first_column(target_path / f'{feature_name}.cui.txt')
        logger.info(f'Starting "{feature_name}" with {len(target_cuis)} target CUIs.')
        # create pattern: sort by longest to ensure longest regex is matched first
        target_regex = build_regex_from_file(target_path, feature_name)
        unique_id = 0
        with open(outpath / f'{feature_name}.review.csv', 'w',
                  newline='', encoding=text_encoding) as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=['id', 'note_id', 'start', 'end', 'length', 'negation', 'type',
                            'precontext', 'keyword', 'postcontext', 'fullcontext']
            )
            writer.writeheader()
            for note_directory in note_directories:
                logger.info(f'Reading directory {note_directory}.')
                note_count = 0
                no_text_file_count = 0
                for mml_file in note_directory.glob(f'*.{mml_format}'):
                    note_id = mml_file.stem
                    if limit_note_ids and note_id not in limit_note_ids:
                        continue
                    txt_file = note_directory / f'{note_id}{text_extension}'
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
                    prev_unique_id = unique_id
                    for start, end, is_cui, negated in sorted(cui_data + text_data):
                        writer.writerow({
                            'id': unique_id,
                            'note_id': note_id,
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
                    # record all note ids by feature for sampling
                    if sample_size and prev_unique_id < unique_id:
                        note_ids[feature_name].append(note_id)
                logger.info(f'Completed processing {note_count} notes (Total Matches: {unique_id}).')
                if no_text_file_count:
                    logger.warning(f'Failed to find {no_text_file_count} text files.')
    if sample_size:
        compile_to_excel(outpath, note_ids, text_encoding, sample_size, metadata_file)


def build_regex_from_file(target_path, feature_name):
    return build_regex(
        load_first_column(target_path / f'{feature_name}.string.txt')
    )


def build_regex(term_list):
    target_pattern = re.sub(
        r'\s+', r'\\s+',
        '|'.join(re.escape(x) for x in sorted(term_list, key=lambda x: -len(x)))
    )
    target_regex = re.compile(f"({target_pattern})", re.I)
    return target_regex


def load_first_column(file: pathlib.Path):
    res = {}
    with open(file) as fh:
        for line in fh:
            if line.strip():
                res[line.strip().split('\t')[0]] = 1
    return res
