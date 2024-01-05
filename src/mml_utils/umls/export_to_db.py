import csv
from pathlib import Path

from mml_utils.db_utils import Cursor


def build_mrconso(conn, path: Path, languages=None):
    fieldnames = ['cui', 'lat', 'ts', 'lui', 'stt', 'sui', 'ispref',
                  'aui', 'saui', 'scui', 'sdui', 'sab', 'tty', 'code',
                  'str', 'srl', 'suppress', 'cvf', 'empty']
    with Cursor(conn) as cur:
        cur.execute('''
            CREATE TABLE mrconso (
                cui char(8),
                --lat char(3), 
                --ts char(1),
                --lui char(10),
                --stt char(3),
                --sui char(10),
                --ispref char(1),
                --aui char(9),
                --saui char(50),
                --scui char(100),
                --sdui char(100),
                sab char(40),
                tty char(40)
                --code char(100),
                --str char(3000),
                --srl integer external,
                --suppress char(1),
                --cvf integer external
            )
        ''')
        with open(path / 'MRCONSO.RRF', encoding='utf8') as fh:
            for i, line in enumerate(csv.DictReader(fh, fieldnames=fieldnames, delimiter='|')):
                if line['sab'] != 'MDR' or (languages and line['lat'] not in languages):
                    continue
                cur.execute(f'INSERT INTO MRCONSO (cui, sab, tty) VALUES (?, ?, ?)',
                            (line['cui'], line['sab'], line['tty']))


def build_mrrel(conn, path: Path):
    fieldnames = ['cui1', 'aui1', 'stype1', 'rel', 'cui2', 'aui2', 'stype2',
                  'rela', 'rui', 'srui', 'sab', 'sl', 'rg',
                  'dir', 'suppress', 'cvf']
    with Cursor(conn) as cur:
        cur.execute('''
            CREATE TABLE mrrel (
                cui1 char(8),
                --aui1 char(9),
                --stype1 char(50),
                --rel char(4),
                cui2 char(8),
                --aui2 char(9),
                --stype2 char(50),
                rela char(100),
                --rui char(10),
                --srui char(50),
                sab char(40)
                --sl char(40),
                --rg char(10),
                --dir char(1),
                --suppress char(1),
                --cvf integer external
            )
        ''')
        with open(path / 'MRREL.RRF', encoding='utf8') as fh:
            for i, line in enumerate(csv.DictReader(fh, fieldnames=fieldnames, delimiter='|')):
                if line['sab'] != 'MDR':
                    continue
                cur.execute(f'INSERT INTO MRREL (cui1, cui2, rela, sab) VALUES (?, ?, ?, ?)',
                            (line['cui1'], line['cui2'], line['rela'], line['sab']))


