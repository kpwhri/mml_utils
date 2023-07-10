from mml_utils.parse.target_cuis import TargetCuis
from mml_utils.scripts.extract_mml_output import extract_data_from_file


def test_extract_data_from_file(short_fever_file):
    results = list(extract_data_from_file(short_fever_file))
    assert len(results) == 3
    is_record, data = results[0]  # non-negated
    assert is_record is False
    assert data['negated'] is False
    is_record, data = results[1]  # negated
    assert is_record is False
    assert data['negated'] is True
    is_record, data = results[2]  # record
    assert is_record is True
    assert data['processed'] is True
    assert data['num_chars'] == 16
    assert data['num_letters'] == 12


def test_extract_data_from_file_exclude_negated(short_fever_file):
    results = list(extract_data_from_file(short_fever_file, exclude_negated=True))
    assert len(results) == 2
    is_record, data = results[0]  # non-negated
    assert is_record is False
    assert data['negated'] is False
    is_record, data = results[1]  # record
    assert is_record is True
    assert data['processed'] is True
    assert data['num_chars'] == 16
    assert data['num_letters'] == 12


def test_extract_data_from_file_target_cuis(fever_file):
    cui = 'C4552740'
    results = list(extract_data_from_file(fever_file, target_cuis=TargetCuis.fromdict({cui: cui})))
    cnt = 0
    for is_record, data in results:
        if is_record:
            assert data['processed'] is True
            assert data['num_chars'] == 2216
            assert data['num_letters'] == 1796
        else:
            assert data['cui'] == cui
            cnt += 1
    assert cnt == 9


def test_extract_data_from_file_target_cuis_mapping(fever_file):
    cui = 'C4552740'
    results = list(extract_data_from_file(fever_file, target_cuis=TargetCuis.fromdict({cui: cui, 'C0424755': cui})))
    cnt = 0
    for is_record, data in results:
        if is_record:
            assert data['processed'] is True
            assert data['num_chars'] == 2216
            assert data['num_letters'] == 1796
        else:
            assert data['cui'] == cui
            cnt += 1
    assert cnt == 18
