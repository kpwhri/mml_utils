import itertools
import logging
from textwrap import dedent

import pytest

from mml_utils.parse.mmi import extract_mml_from_mmi_data, extract_mmi_line, _parse_trigger_info, split_mmi_line


def fix_text(text):
    return ''.join(dedent(text).split('\n'))


@pytest.fixture()
def mmi_risk_of():
    return fix_text(
        '00000000.tx|MMI|27.63|Risk|C0035647|[idcn]|"risk of"-text-0-"risk of"--0,"risk of"-text-0-"risk of"--0,'
        '"risk of"-text-20-"risk of"--0|text|2672/7;3076/7;4271/7|G17.680.750;N06.850.520.830.600.800;N05.715.360.'
        '750.625.700;E05.318.740.600.80'
    )


def get_mmi_lines(mmi_lines, exp):
    if isinstance(exp, (str, int)):
        exp = [exp]
    for line in mmi_lines.split('\n'):
        for res, expected in zip(extract_mmi_line(line.split('|')), itertools.cycle(exp)):
            yield res, expected


@pytest.mark.parametrize(('mmi_lines', 'exp'), [
    (pytest.lazy_fixture('mmi_risk_of'), '00000000'),
])
def test_extract_mmi_filename(mmi_lines, exp):
    for res, expected in get_mmi_lines(mmi_lines, exp):
        assert expected == res['docid']


def test_mmi_skips():
    line = '23074487|AA|FY|fiscal years|1|2|3|12|9362:2'.split('|')
    assert len(list(extract_mmi_line(line))) == 0


@pytest.mark.parametrize(('mmi_lines', 'exp'), [
    (pytest.lazy_fixture('mmi_risk_of'), 'Risk'),
])
def test_extract_mmi_conceptstring(mmi_lines, exp):
    for res, expected in get_mmi_lines(mmi_lines, exp):
        assert expected == res['conceptstring']


@pytest.mark.parametrize(('mmi_lines', 'exp'), [
    (pytest.lazy_fixture('mmi_risk_of'), 'C0035647'),
])
def test_extract_mmi_cui(mmi_lines, exp):
    for res, expected in get_mmi_lines(mmi_lines, exp):
        assert expected == res['cui']


@pytest.mark.parametrize(('mmi_lines', 'exp'), [
    (pytest.lazy_fixture('mmi_risk_of'), 'idcn'),
])
def test_extract_mmi_semantictype(mmi_lines, exp):
    for res, expected in get_mmi_lines(mmi_lines, exp):
        assert expected == res['semantictype']
        assert res[expected] == 1


@pytest.mark.parametrize(('mmi_lines', 'exp'), [
    (pytest.lazy_fixture('mmi_risk_of'), [0, 0, 0]),
])
def test_extract_mmi_negated(mmi_lines, exp):
    for res, expected in get_mmi_lines(mmi_lines, exp):
        assert expected == res['negated']


@pytest.mark.parametrize(('mmi_lines', 'exp'), [
    (pytest.lazy_fixture('mmi_risk_of'), [2672, 3076, 4271]),
])
def test_extract_mmi_start(mmi_lines, exp):
    for res, expected in get_mmi_lines(mmi_lines, exp):
        assert expected == res['start']


@pytest.mark.parametrize(('mmi_lines', 'exp'), [
    (pytest.lazy_fixture('mmi_risk_of'), 7),
])
def test_extract_mmi_length(mmi_lines, exp):
    for res, expected in get_mmi_lines(mmi_lines, exp):
        assert expected == res['length']


@pytest.mark.parametrize(('posinfo', 'exp'), [
    pytest.param(
        '[4061/10,4075/11],[4166/10,4180/11]', '?',
        marks=[
            pytest.mark.skip(
                reason='This is tough...and rare: https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/Docs/MMI_Output_2016.pdf')
        ]
    ),
])
def test_positional_info(posinfo, exp):
    pass


def test_from_text(mmi_risk_of):
    res = list(extract_mml_from_mmi_data(mmi_risk_of, 'filename'))
    assert len(res) == 3
    assert {d['event_id'] for d in res} == {'filename_0', 'filename_1', 'filename_2'}


def test_comma():
    mmi_line = '0000.tx|MMI|2.30|Chest Pain|C0008031|[sosy]' \
               '|"Pain, Chest"-text-0-"Pain, chest"--0|text|0/11|C23.888.592.612.233'
    lst = mmi_line.split('|')
    result = next(extract_mmi_line(lst))
    assert result == {'docid': '0000', 'filename': '0000.tx', 'matchedtext': 'Pain, chest',
                      'conceptstring': 'Chest Pain', 'cui': 'C0008031', 'preferredname': 'Pain, Chest', 'start': 0,
                      'length': 11, 'end': 11, 'evid': None, 'negated': 0, 'pos': '', 'semantictype': 'sosy', 'sosy': 1}


@pytest.mark.parametrize('triggerinfo_text, concept, loc, locpos, text, pos, neg', [
    ('"Pain" Chest"-text-0-"Pain" chest"--0', 'Pain" Chest', 'text', '0', 'Pain" chest', '', '0'),
    ('"Pain, Chest"-text-0-"Pain, chest"--0', 'Pain, Chest', 'text', '0', 'Pain, chest', '', '0'),
    ('"Pain Chest"-text-0-"Pain chest"--0', 'Pain Chest', 'text', '0', 'Pain chest', '', '0'),
    ('"Pain, Chest"-text-92-"pain, chest"-NN-0', 'Pain, Chest', 'text', '92', 'pain, chest', 'NN', '0'),
    ('Pain, Chest-text-92-"pain, chest"-NN-0', 'Pain, Chest', 'text', '92', 'pain, chest', 'NN', '0'),
    ('"C-reactive protein"-text-57-"C-REACTIVE PROTEIN"-NNP-0',
     'C-reactive protein', 'text', '57', 'C-REACTIVE PROTEIN', 'NNP', '0'),
    ('C-reactive protein-text-57-"C-REACTIVE PROTEIN"-NNP-0',
     'C-reactive protein', 'text', '57', 'C-REACTIVE PROTEIN', 'NNP', '0'),
])
def test_triggerinfo(triggerinfo_text, concept, loc, locpos, text, pos, neg):
    """Test for only a single result"""
    result = next(_parse_trigger_info(triggerinfo_text))
    assert result[0] == concept
    assert result[1] == loc
    assert result[2] == locpos
    assert result[3] == text
    assert result[4] == pos
    assert result[5] == neg


@pytest.mark.parametrize('mmi_line', [
    [], [''],
])
def test_empty_mmi_line(mmi_line):
    with pytest.raises(StopIteration):
        next(extract_mmi_line(mmi_line))


@pytest.mark.parametrize('line, exp_logtext', [
    ('0000.tx|MMI|2.30|Chest Pain|C0008031|[sosy]'
     '|"Pain, Chest"-text-0-"Pain, chest"--0|text|11|C23.888.592.612.233',
     'Unknown format of length 1 for positional info'),
])
def test_has_invalid_length(caplog, line, exp_logtext):
    with caplog.at_level(logging.ERROR):
        _ = list(extract_mmi_line(line.split('|')))
    assert exp_logtext in caplog.text


@pytest.mark.parametrize('text, exp_length, exp_triggerinfo', [
    ('181695.txt|MMI|0.92|3/4|C0442757|[fndg]|"3 4"-text-77-"3 / 4"-CD-0,"3 4"-text-83-"3/4"-CD-0|text|616/4;621/5||',
     11,
     '"3 4"-text-77-"3 / 4"-CD-0,"3 4"-text-83-"3/4"-CD-0',
     ),
    ('181695.txt|MMI|0.92|3/4|C0442757|[fndg]|"3 4"-text-77-"3  4"-CD-0,"3 4"-text-83-"3 / 4"-CD-0|text|616/4;621/5||',
     11,
     '"3 4"-text-77-"3  4"-CD-0,"3 4"-text-83-"3 / 4"-CD-0',
     ),
    ('181695.txt|MMI|0.92|3/4|C0442757|[fndg]|"3 4"-text-77-"3  4"-CD-0,"3 4"-text-83-"3  4"-CD-0|text|616/4;621/5||',
     11,
     '"3 4"-text-77-"3  4"-CD-0,"3 4"-text-83-"3  4"-CD-0',
     ),
    ('181695.txt|MMI|0.92|3/4|C0442757|[fndg]|"3 4"-text-77-"3  4"-CD-0,"3 4"-text-83-"3   4"-CD-0|text|616/4;621/5||',
     11,
     '"3 4"-text-77-"3  4"-CD-0,"3 4"-text-83-"3   4"-CD-0',
     ),
    ('181695.txt|MMI|0.92|3/4|C0442757|[fndg]|"3 4"-text-77-"3  4"-CD-0,"3 4"-text-83-"3 | 4"-CD-0|text|616/4;621/5||',
     11,
     '"3 4"-text-77-"3  4"-CD-0,"3 4"-text-83-"3 | 4"-CD-0',
     ),
    ('181690.txt|MMI|0.92|3/4|C0442757|[fndg]|"3 4"-text-77-"3  4"-CD-0,"3 4"-text-83-"3 | 4"-CD-0|text|705/4;710/5||',
     11,
     '"3 4"-text-77-"3  4"-CD-0,"3 4"-text-83-"3 | 4"-CD-0',
     ),
    ('181690.txt|MMI|0.92|3/4|C0442757|[fndg]|"3 4"-text-77-"3  4"-CD-0,"3 4"-text-83-"3 "| 4"-CD-0|text|705/4;710/5||',
     11,
     '"3 4"-text-77-"3  4"-CD-0,"3 4"-text-83-"3 "| 4"-CD-0',
     ),  # handle quote mark inside
    (pytest.lazy_fixture('mmi_risk_of'),
     10,
     '"risk of"-text-0-"risk of"--0,"risk of"-text-0-"risk of"--0,"risk of"-text-20-"risk of"--0',
     ),
])
def test_pipes_in_capture_mmi(text, exp_length, exp_triggerinfo):
    line = split_mmi_line(text)
    assert len(line) == exp_length
    assert line[6] == exp_triggerinfo
