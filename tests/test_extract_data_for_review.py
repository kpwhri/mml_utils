import pathlib

import pytest

from mml_utils.review.extract_data import build_regex
from mml_utils.scripts.extract_data_for_review import extract_data_for_review


@pytest.fixture
def fever_dir():
    return pathlib.Path('fever')


def validate_csv_file(fever_dir):
    lines = []
    with open(fever_dir / 'fever.review.csv', newline='') as fh:
        for line in fh:
            lines.append(line.strip())
    assert len(lines) == 16
    assert lines[0] == ','.join(('id', 'docid', 'start', 'end', 'length', 'negation', 'type',
                                 'precontext', 'keyword', 'postcontext', 'fullcontext'))
    found_cui = False
    found_text = False
    for i, line in enumerate(lines[1:]):
        lst = line.split(',')
        assert lst[6] in {'CUI', 'TEXT'}
        found_cui = found_cui or lst[6] == 'CUI'
        found_text = found_text or lst[6] == 'TEXT'
        assert len(lst[7]) <= 102
        assert len(lst[9]) <= 102
        assert len(lst[10]) <= 550
        assert int(lst[0]) == i
        assert lst[1] == 'fever'
    assert found_cui
    assert found_text


def test_extract_data_for_review_fever_json(fever_dir):
    extract_data_for_review(
        note_directories=[fever_dir],
        target_path=fever_dir,
        mml_format='json',
        text_extension='.txt',
        text_encoding='utf8',
    )
    validate_csv_file(fever_dir)


def test_extract_data_for_review_fever_mmi(fever_dir):
    extract_data_for_review(
        note_directories=[fever_dir],
        target_path=fever_dir,
        mml_format='mmi',
        text_extension='.txt',
        text_encoding='utf8',
    )
    validate_csv_file(fever_dir)


@pytest.mark.parametrize('term_list, target, exp_found', [
    (['N&V'], 'investigate', False),
    (['N/V'], 'investigate', False),
    (['N+V'], 'investigate', False),
])
def test_build_regex(term_list, target, exp_found):
    rx = build_regex(term_list)
    found = bool(rx.search(target))
    assert found == exp_found
