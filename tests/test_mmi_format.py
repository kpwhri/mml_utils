from textwrap import dedent

import pytest

from mml_utils.scripts.extract_mml_output import extract_mml_from_mmi_data, extract_mmi_line


def fix_text(text):
    return ''.join(dedent(text).split('\n'))


def mmi_risk_of():
    return fix_text(
        '''00000000.tx|MMI|27.63|Risk|C0035647|[idcn]|"risk of"-text-0-"risk of"--0,"risk of"-text-0-"risk of"--0,
        "risk of"-text-20-"risk of"--0|text|2672/7;3076/7;4271/7|G17.680.750;N06.850.520.830.600.800;N05.715.360.
        750.625.700;E05.318.740.600.80'''
    )


@pytest.mark.parametrize(('mmi_lines', 'exp'), [
    (mmi_risk_of(), '00000000.tx'),
])
def test_extract_mmi_filename(mmi_lines, exp):
    for line in mmi_lines.split('\n'):
        res = extract_mmi_line(line.split('|'))
        assert exp == res['docid']
