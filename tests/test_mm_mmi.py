import pytest

from mml_utils.parse.mmi import _parse_positional_info, extract_mml_from_mmi_data


@pytest.mark.parametrize('text, exp', [
    ('59/5;[44/9],[179/9];[44/9],[179/9]',
     [(59, 64, 5), (44, 53, 9), (179, 188, 9)]),
])
def test_parse_positional_info(text, exp):
    res = list(_parse_positional_info(text))
    assert res == exp


PROBLEMATIC_LINES = lines = '''wikipedia.txt|AA|IgE|immunoglobulin E|1|3|3|16|60:3
wikipedia.txt|MMI|6.95|Immunology|C0152036|[bmod]|["Immunology"-tx-4-"immunologic"-adj-0,"Immunology"-tx-1-"Immunologic"-adj-0]|TX|512/11;0/11|'''


def test_problematic_mergedlines():
    res = list(extract_mml_from_mmi_data(PROBLEMATIC_LINES, ''))
    assert len(res) == 2
    assert res[0]['cui'] == 'C0152036'
    assert res[1]['cui'] == 'C0152036'
