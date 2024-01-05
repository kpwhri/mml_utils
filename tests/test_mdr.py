import sqlite3

from mml_utils.umls.export_to_db import build_mrconso


def test_load_mrconso(umls_path):
    record_count = 0  # dynamically count qualifying lines
    with open(umls_path / 'MRCONSO.RRF') as fh:
        for line in fh:
            if '|ENG|' in line and '|MDR|' in line:
                record_count += 1
    with sqlite3.connect(':memory:') as conn:
        build_mrconso(conn, umls_path, languages={'ENG'})
        cur = conn.cursor()
        n_records = cur.execute('select count(*) from MRCONSO').fetchone()
        assert n_records[0] == record_count
