"""
Implement AFEP, including Greedy Feature Selection.
"""
import json

from loguru import logger

from mml_utils.parse.json import extract_mml_from_json_data
from mml_utils.parse.mmi import extract_mml_from_mmi_data


def extract_articles(note_directories, mml_format):
    article_types = set()
    results = []
    for path in note_directories:
        for file in path.glob(f'*.{mml_format}'):
            article_type = file.stem.split('_')[0]
            article_types.add(article_type)
            filename = file.stem

            with open(file) as fh:
                if mml_format == 'json':
                    data = json.load(fh)
                    extract_function = extract_mml_from_json_data
                elif mml_format == 'mmi':
                    extract_function = extract_mml_from_mmi_data
                    data = fh.read()
                else:
                    raise ValueError(f'Unrecognized file format for MetaMapLite data: {mml_format}.')
            extras = {
                'article_source': article_type,
            }
            for result in extract_function(data, filename, extras=extras):
                results.append(result)
    return article_types, results


def run_greedy_algorithm(cui_df, df):
    retain_semtypes = {
        'aapp', 'aapp',
        # 'anab',  # not sure why was removed?
        'antb', 'biof', 'bacs', 'bodm', 'chem', 'chvf', 'chvs', 'clnd', 'cgab',
        'diap', 'dsyn', 'elii', 'enzy', 'fndg', 'hops', 'horm', 'imft', 'irda', 'inbe', 'inpo', 'inch',
        'lbtr', 'lbpr', 'medd', 'mobd', 'neop', 'nnon', 'orch', 'patf', 'phsu', 'phpr', 'rcpt', 'sosy',
        'topp', 'vita'
    }
    cui_to_source_count = {r.cui: len(r.all_sources.split(',')) for r in
                           df[['cui', 'all_sources']].drop_duplicates().itertuples()}
    # use length or not?
    master_cui = cui_df.query('>0 or '.join(x for x in retain_semtypes if x in cui_df.columns) + '>0')[
        ['cui', 'matchedtext', 'docid', 'start', 'length']].groupby(
        ['docid', 'start', 'matchedtext', 'cui']).count().reset_index()
    # get unique values of docid, matchedtext, start
    master_cui_as_col = master_cui.pivot(
        index=['docid', 'matchedtext', 'start'],
        columns='cui',
        values='length'
    ).fillna(0).reset_index()
    logger.info(f'Unique CUIs: {master_cui["cui"].nunique()}')
    # run greedy algorithm
    res = []
    temp_df = master_cui_as_col.copy()
    while temp_df.shape[0] > 0:
        _temp_df = temp_df[[col for col in temp_df.columns if str(col).startswith('C')]].sum()  # only CUI columns
        max_val = _temp_df.max()  # get most frequent
        cuis = list(_temp_df[_temp_df == max_val].index)  # all CUIs with most frequent value
        d = {c: cui_to_source_count[c] for c in cuis}
        cui = max(d, key=d.get)
        assert cui in cuis
        res.append(cui)
        temp_df = temp_df[temp_df[cui] == 0.0]
    logger.info(f'Result of greedy algorithm: retained {len(res)} CUIs.')
    return res
