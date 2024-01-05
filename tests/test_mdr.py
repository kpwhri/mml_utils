import sqlite3

from mml_utils.umls.export_to_db import build_mrconso, build_mrrel
from mml_utils.umls.mdr import connect


def compare_table(cur, tablename, record_count=None):
    n_records = cur.execute(f'select count(*) from {tablename}').fetchone()[0]
    if record_count:
        assert n_records == record_count, 'All relevant records read from RRF file'
    n_records_mdr = cur.execute(f'select count(*) from {tablename} where sab="MDR"').fetchone()[0]
    if record_count:
        assert n_records_mdr == record_count, 'All records are Meddra (method 1)'
    assert n_records == n_records_mdr, 'All records are Meddra (method 2)'


def test_load_mrconso(umls_path):
    record_count = 0  # dynamically count qualifying lines
    with open(umls_path / 'MRCONSO.RRF') as fh:
        for line in fh:
            if '|ENG|' in line and '|MDR|' in line:
                record_count += 1
    with sqlite3.connect(':memory:') as conn:
        build_mrconso(conn, umls_path, languages={'ENG'})
        cur = conn.cursor()
        compare_table(cur, 'MRCONSO', record_count=record_count)


def test_load_mrrel(umls_path):
    record_count = 0  # dynamically count qualifying lines
    with open(umls_path / 'MRREL.RRF') as fh:
        for line in fh:
            if '|MDR|' in line:
                record_count += 1
    with sqlite3.connect(':memory:') as conn:
        build_mrrel(conn, umls_path)
        cur = conn.cursor()
        compare_table(cur, 'MRREL', record_count=record_count)


def test_connect_and_populate(umls_path, caplog):
    db_path = umls_path / 'mml_utils.mdr.db'
    db_path.unlink(missing_ok=True)
    with connect(umls_path) as cur:
        assert 'MDR database not built' in caplog.text
        assert 'Extracting MRCONSO' in caplog.text
        assert 'Extracting MRREL' in caplog.text
        compare_table(cur, 'MRCONSO')
        compare_table(cur, 'MRREL')
    assert db_path.exists()
    # test a second connection
    caplog.clear()
    with connect(umls_path) as cur:
        assert 'Found MDR database' in caplog.text
        assert 'MDR database not built' not in caplog.text
    db_path.unlink()  # clean up
