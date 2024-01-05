"""
Functions for working with MedDRa.

Particularly, in manipulating and expanding CUIs using preferred terms and lower-level terms.
"""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from loguru import logger

from mml_utils.umls.export_to_db import build_mrconso, build_mrrel


@contextmanager
def connect(meta_path: Path, *, languages: set = None):
    db_path = meta_path / 'mml_utils.mdr.db'
    exists = db_path.exists()
    conn = sqlite3.connect(db_path)
    if not exists:
        if not languages:
            languages = {'ENG'}
        logger.info(f'MDR database not built: extracting subset of MDR for {languages} at {db_path}.')
        logger.info(f'Extracting MRCONSO (<5min)...')
        build_mrconso(conn, meta_path, languages)
        logger.info(f'Extracting MRREL (<5min)...')
        build_mrrel(conn, meta_path)
        logger.info(f'Extracted MRCONSO and MRREL subset to {db_path}.')
    else:
        logger.info(f'Found MDR database at: {db_path}')
    yield conn.cursor()
    conn.close()


def get_llts_for_pts(cuis, meta_path, *, languages: set = None):
    """
    Determine which supplied CUIs are PTs (preferred terms), and get all LLTs for them (Lower-level terms).

    :param cuis: all CUIs
    :param meta_path: path to location of MRCONSO and MRREL
    :param languages: set; defaults to english (`{ENG}`)
    :return: list[ tuple[PT, LLT] ]
    """
    # get all LLTs for a PT
    with connect(meta_path, languages=languages) as cur:
        subquery = f'''
            select distinct CUI
            from MRCONSO
            where SAB='MDR' and TTY='PT'
            and CUI in (?{', ?' * (len(cuis) - 1)})
        '''
        cur.execute(f'''
            select b.cui1, b.cui2 
            from mrconso a
            inner join mrrel b on a.cui = b.cui1
            inner join mrconso c on b.cui2 = c.cui
            where a.SAB='MDR' 
            and b.SAB='MDR' 
            and c.SAB='MDR'
            and b.rela='classified_as'
            and (c.TTY='LLT' or c.TTY='OL')
            and a.cui !=c.cui
            and a.cui in ({subquery})
            group by b.cui1, b.cui2
        ''', cuis)
        return cur.fetchall()


def get_pts_for_llts(cuis, meta_path, *, languages: set = None):
    """
    Determine which supplied CUIs are LLTs (Lower-level terms), and get all PTs for them (preferred terms).

    :param cuis: all CUIs (all PTs with be ignored)
    :param meta_path: path to location of MRCONSO and MRREL
    :param languages: set; defaults to english (`{ENG}`)
    :return: list[ tuple[PT, LLT] ]
    """
    # get all LLTs for a PT
    with connect(meta_path, languages=languages) as cur:
        subquery = f'''
            select distinct CUI
            from MRCONSO
            where SAB='MDR' and TTY in ('OT', 'LLT')
            and CUI in (?{', ?' * (len(cuis) - 1)})
        '''
        cur.execute(f'''
            select b.cui1, b.cui2 
            from mrconso a
            inner join mrrel b on a.cui = b.cui1
            inner join mrconso c on b.cui2 = c.cui
            where a.SAB='MDR' 
            and b.SAB='MDR' 
            and c.SAB='MDR'
            and b.rela='classified_as'
            and a.TTY='PT'
            and a.cui != c.cui
            and c.cui in ({subquery})
            group by b.cui1, b.cui2;
        ''', cuis)
        return cur.fetchall()
