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
    :return: list[ tuple[LLT, PT] ]
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
            select b.cui2, b.cui1 
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
    :return: list[ tuple[LLT, PT] ]
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
            select b.cui2, b.cui1 
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


def get_pts(cuis, meta_path, *, languages: set = None):
    """
    Get preferred terms for give CUI list.
    :param cuis:
    :param meta_path:
    :param languages:
    :return:
    """
    with connect(meta_path, languages=languages) as cur:
        cur.execute(f'''
                select distinct cui
                from mrconso
                where sab='MDR' and tty = 'PT'
                and cui in (?{', ?' * (len(cuis) - 1)})
            ''', cuis)
        return [x[0] for x in cur.fetchall()]


def build_cui_normalisation_table(
        cuis, meta_path, *, languages: set = None,
        map_to_pts_only=False,
        self_map_all_llts=False,

):
    """
    Build a table of all possible CUI relationships for MDR
    1. Retrieve all PTs for the LLTs
    2. Retrieve all LLTs for the PTs
    3. Merge the results together (ensuring that no mappings are lost)

    :param map_to_pts_only: all outputs should be PTs (though LLTs will be mapped to PTs)
    :param cuis:
    :param meta_path:
    :param languages:
    :return:
    """
    # create default mapping of all CUIs to self: these were all found
    cuis_table = [(cui, cui) for cui in cuis]
    # retrieve all PTs for the LLTs
    all_pts_table = get_pts_for_llts(cuis, meta_path, languages=languages)
    possible_new_pts = [pt for llt, pt in all_pts_table]
    self_map_pts_table = [(cui, cui) for cui in possible_new_pts]
    all_possible_pts = cuis + possible_new_pts
    # retrieve all LLTs for the PTs
    all_llts_table = get_llts_for_pts(all_possible_pts, meta_path, languages=languages)
    self_map_llts_table = [(llt, llt) for llt, pt in all_llts_table]
    # combine and dedupe result
    merged_lists = cuis_table + self_map_pts_table + all_pts_table + all_llts_table
    if self_map_all_llts:
        merged_lists += self_map_llts_table
    final_list = list(sorted(set(merged_lists)))
    if map_to_pts_only:
        target_cuis = [target for src, target in final_list]
        all_pts = set(get_pts(target_cuis, meta_path, languages=languages))
        final_list = [(src, target) for src, target in final_list if target in all_pts]
    return final_list
