import shutil
from pathlib import Path

import pandas as pd

from mml_utils.scripts.extract_text_to_files import text_from_csv, text_from_sas7bdat


def test_text_from_sas7bdat(source_data_path):
    """Test reading sas7bdat file"""
    outdir = source_data_path / 'sas.out'
    shutil.rmtree(outdir, ignore_errors=True)
    text_from_sas7bdat(
        source_data_path / 'corpus.sas7bdat',
        id_col='note_id',
        text_col='note_text',
        outdir=outdir,
    )
    # check
    df = pd.read_sas(source_data_path / 'corpus.sas7bdat', encoding='latin1')
    _check_text_vs_dataframe(df, outdir)


def test_text_from_csv(source_data_path):
    outdir = source_data_path / 'csv.out'
    shutil.rmtree(outdir, ignore_errors=True)
    text_from_csv(
        source_data_path / 'corpus.csv',
        id_col='note_id',
        text_col='note_text',
        outdir=outdir,
    )
    # check
    df = pd.read_csv(source_data_path / 'corpus.csv', encoding='utf8')
    _check_text_vs_dataframe(df, outdir)


def _check_text_vs_dataframe(df, outdir):
    df['note_id'] = df['note_id'].apply(int)
    assert df.shape[0] == 10  # one note has two lines
    assert df['note_id'].nunique() == 9
    df = df.groupby('note_id').agg({'note_text': lambda x: ''.join(x)}).reset_index()
    with open(outdir / 'filelist.txt') as fh:
        count = 0
        for line in fh:
            path = Path(line.strip())
            assert path.exists()
            assert df[df['note_id'] == int(path.stem)]['note_text'].values[0] == path.read_text()
            count += 1
    assert count == 9, 'Count number of files generated'
