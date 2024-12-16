"""
Ensure that the /example/complete directory still produces the correct output.
"""
import csv
import shutil
from itertools import zip_longest

import pytest

from mml_utils.scripts.extract_mml_output import extract_mml


@pytest.fixture()
def complete_example_dir(example_directory):
    return example_directory / 'complete'


def assert_csvs_equal(path1, path2, skip_length_check=False, skip_fields=None):
    """

    :param path1: Generated file
    :param path2: Gold file
    :param skip_length_check: set to True for mml.mmi since otherwise this will a very long file
        (too long for the examples)
    :return:
    """
    lines = []
    with open(path1, newline='', encoding='utf8') as f1:
        with open(path2, newline='', encoding='utf8') as f2:
            for line1, line2 in zip_longest(csv.DictReader(f1), csv.DictReader(f2)):
                assert line1 is not None, 'Generated is missing data'
                assert line2 is not None, 'Generated has extra data'
                if not skip_length_check:
                    assert len(line1) == len(line2), f'Mismatched columns: {set(line1.keys()) ^ set(line2.keys())}'
                for key, value in line2.items():
                    if line1[key] == value:
                        continue  # matches
                    elif skip_fields and key in skip_fields:
                        continue
                    else:  # handle mismatches
                        if value and value in line1[key]:
                            # docid vs full path
                            continue
                        raise ValueError(f'{value} (from {path2}) != {line1[key]} (from {path1})')
                lines.append(line1)
    return lines


def test_complete_example_json(complete_example_dir, tmp_path):
    note_outfile, mml_outfile, cuis_by_doc_outfile = extract_mml(
        note_directories=[complete_example_dir / 'notes'],
        outdir=tmp_path / 'mmlout',
        cui_file=complete_example_dir / 'include-cuis.txt',
        extract_format='json',
    )
    assert_csvs_equal(mml_outfile, complete_example_dir / 'mmlout' / 'mml.json.csv')
    assert_csvs_equal(note_outfile, complete_example_dir / 'mmlout' / 'notes.json.csv')
    assert_csvs_equal(cuis_by_doc_outfile, complete_example_dir / 'mmlout' / 'cuis_by_doc.json.csv')


def test_complete_example_mmi(complete_example_dir, tmp_path):
    note_outfile, mml_outfile, cuis_by_doc_outfile = extract_mml(
        note_directories=[complete_example_dir / 'notes'],
        outdir=tmp_path / 'mmlout',
        cui_file=complete_example_dir / 'include-cuis.txt',
        extract_format='mmi',
    )
    assert_csvs_equal(mml_outfile, complete_example_dir / 'mmlout' / 'mml.mmi.csv', skip_length_check=True)
    assert_csvs_equal(note_outfile, complete_example_dir / 'mmlout' / 'notes.mmi.csv')
    assert_csvs_equal(cuis_by_doc_outfile, complete_example_dir / 'mmlout' / 'cuis_by_doc.mmi.csv')


def copy_files_to_path(source, extension, dest, new_extension):
    dest.mkdir(exist_ok=True)
    for file in source.glob(f'*{extension}'):
        shutil.copy(file, dest / file.name.replace(extension, new_extension))


def test_complete_arbitrary_extensions_mmi(complete_example_dir, tmp_path):
    mmi_extension = '.cleaned.out'  # convert *.mmi to *.cleaned.out
    txt_extension = '.formatted.text'  # convert *.txt to *.text
    mmi_path = tmp_path / 'mmi'
    text_path = tmp_path / 'txt'
    copy_files_to_path(complete_example_dir / 'notes', '.mmi', mmi_path, mmi_extension)
    copy_files_to_path(complete_example_dir / 'notes', '.txt', text_path, txt_extension)
    note_outfile, mml_outfile, cuis_by_doc_outfile = extract_mml(
        note_directories=[text_path],
        extract_directories=[mmi_path],
        outdir=tmp_path / 'mmlout',
        cui_file=complete_example_dir / 'include-cuis.txt',
        extract_format='mmi',
        note_suffix=txt_extension,
        extract_suffix=mmi_extension,
    )
    assert_csvs_equal(mml_outfile, complete_example_dir / 'mmlout' / 'mml.mmi.csv', skip_length_check=True)
    assert_csvs_equal(note_outfile, complete_example_dir / 'mmlout' / 'notes.mmi.csv',
                      skip_fields=['filename', 'docid'])  # these fields will not match up
    assert_csvs_equal(cuis_by_doc_outfile, complete_example_dir / 'mmlout' / 'cuis_by_doc.mmi.csv')
