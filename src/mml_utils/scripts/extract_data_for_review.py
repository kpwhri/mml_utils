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
def _extract_data_for_review(note_directories: list[pathlib.Path], target_path: pathlib.Path = pathlib.Path('.'),
                             mml_format='json', text_extension='', text_encoding='utf8'):
    extract_data_for_review(note_directories, target_path, mml_format, text_extension, text_encoding)


def extract_data_for_review(note_directories: list[pathlib.Path], target_path: pathlib.Path = pathlib.Path('.'),
                            mml_format='json', text_extension='', text_encoding='utf8'):
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
        # create pattern: sort by longest to ensure longest regex is matched first
        target_pattern = re.sub(
            r'\s+', r'\\s+',
            '|'.join(sorted(load_first_column(target_path / f'{feature_name}.string.txt'), key=lambda x: -len(x)))
        )
        target_regex = re.compile(f"({target_pattern})", re.I)
        unique_id = 0
        with open(target_path / f'{feature_name}.review.csv', 'w', newline='') as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=['id', 'docid', 'start', 'end', 'length', 'negation', 'type',
                            'precontext', 'keyword', 'postcontext', 'fullcontext']
            )
            writer.writeheader()
            for note_directory in note_directories:
                for mml_file in note_directory.glob(f'*.{mml_format}'):
                    txt_file = note_directory / f'{mml_file.stem}{text_extension}'
                    if not txt_file.exists():
                        logger.warning(f'Failed to find corresponding text file:'
                                       f' {txt_file.name} (extension: {text_extension}).')
                        continue
                    with open(txt_file, encoding=text_encoding) as fh:
                        text = fh.read()
                    cui_data = []
                    for data in extract_mml_data(mml_file, target_cuis=target_cuis, output_format=mml_format):
                        start, end = find_target_text(text, data['matchedtext'], data['start'], data['end'])
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


def load_first_column(file: pathlib.Path):
    res = {}
    with open(file) as fh:
        for line in fh:
            if line.strip():
                res[line.strip().split('\t')[0]] = 1
    return res


if __name__ == '__main__':
    _extract_data_for_review()
