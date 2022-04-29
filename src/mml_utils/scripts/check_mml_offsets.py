"""
Check MetaMapLite offsets, and experiment with a variety of inputs.
"""
import json
import pathlib
from typing import Iterable

import click
from loguru import logger

from mml_utils.parse.json import iter_json_matches_from_file


@click.command()
@click.argument('mml_directories', nargs=-1, type=click.Path(exists=True, path_type=pathlib.Path), )
@click.option('--mml-format', type=str, default='json',
              help='MML Output format to look for (e.g., "json" or "mmi"); currently only supports "json".')
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
@click.option('--limit-files', default=0, type=int,
              help='Max number of files to process.')
def check_mml_offsets(mml_directories: Iterable[pathlib.Path], *, mml_format='json',
                      text_extension='', text_encoding='utf8',
                      text_errors='replace', add_cr=False, replacements=None, limit_files=0):
    """
    Check offsets in Metamaplite to ensure that the output is retrievable and locatable in the text.

    :param limit_files: Limit number of files run.
    :param text_extension: If text files, e.g., are the same as the .json files but end in '.txt', add '.txt' here.
    :param mml_directories: directories already processed by Metamaplite
    :param mml_format:
    :param text_encoding:
    :param text_errors:
    :param add_cr:
    :param replacements:
    :return:
    """
    file_count = 0
    count = 0
    errors = 0
    max_pos_error = 0
    max_neg_error = 0
    correct = 0
    first_errors = []
    if mml_format != 'json':
        raise ValueError(f'MML output format "{mml_format}" not supported.')
    if replacements:
        replacements = [replace.split('==') for replace in replacements]
        logger.info(f'Loaded {len(replacements)} replacements.')
    for mml_directory in mml_directories:
        has_error = False
        logger.info(f'Processing: {mml_directory}')
        for mml_file in mml_directory.glob(f'*.{mml_format}'):
            if limit_files and file_count > limit_files:
                break
            file_count += 1
            logger.info(f'Processing file: {mml_file.name}')
            text_file = mml_directory / f'{mml_file.stem}.{text_extension}'
            with open(text_file, encoding=text_encoding, errors=text_errors) as fh:
                text = fh.read()
            if add_cr:
                text = text.replace('\n', '\r\n')
            if replacements:
                for _from, _to in replacements:
                    text = text.replace(_from, _to)

            if mml_format == 'json':
                data = iter_json_matches_from_file(mml_file, 'matchedtext', 'start', 'end', 'length')
            else:
                raise ValueError(f'Unrecognized MML format type: {mml_format}.')

            for matched_text, start, end, length in data:
                count += 1
                target = text[start:end]
                if matched_text == target:
                    correct += 1
                else:
                    for i in range(10, 100, 10):
                        if matched_text in text[start:end + i]:
                            idx = text[start:end + i].index(matched_text)
                        elif matched_text in text[start - i:end]:
                            idx = text[start - i:end].index(matched_text) - i
                        else:
                            continue
                        if idx > max_pos_error:
                            max_pos_error = idx
                        elif idx < max_neg_error:
                            max_neg_error = idx
                        errors += abs(idx)
                        if has_error:  # print first error in file
                            error_text = (f'First error: {text_file.stem}@{start}: {matched_text} in'
                                          f' "{text[max(0, start - 10):start]} {target} {text[end:end + 10]}"')
                            print(error_text)
                            first_errors.append(error_text)
                        break

    print(f'Total files processed: {file_count}')
    print(f'Total Errors in Characters: {errors}')
    print(f'Count Correct: {correct}')
    print(f'Max Positive Error: {max_pos_error}')
    print(f'Max Negative Error: {max_neg_error}')
    print('First errors:')
    for first_error in first_errors[:20]:
        print(first_error)


def iter_json_data(json_file):
    with open(json_file) as fh:
        data = json.load(fh)
    for match in data:
        matched_text = match['matchedtext']
        start = match['start']
        length = match['length']
        end = start + length
        yield matched_text, start, end, length


if __name__ == '__main__':
    check_mml_offsets()
