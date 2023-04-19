import pytest

from mml_utils.parse.mmi import _parse_positional_info


@pytest.mark.parametrize('text, exp', [
    ('59/5;[44/9],[179/9];[44/9],[179/9]',
     [(59, 64, 5), (44, 53, 9), (179, 188, 9)]),
])
def test_parse_positional_info(text, exp):
    res = list(_parse_positional_info(text))
    assert res == exp
