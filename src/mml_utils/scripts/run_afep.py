"""
Run AFEP greedy algorithm on results of MetaMapLite extraction of Raw Knowledge Base files.

Implementation notes:
1. Only json currently implemented (not mmi)
2. CUIs will be grouped by article type.
    * Article type is defined as all content before the first '_' (not including extension)..
"""
import datetime
import json
import math
import pathlib
import re

import click
import pandas as pd
from loguru import logger

from mml_utils.parse.mmi import extract_mml_from_mmi_data
from mml_utils.parse.json import extract_mml_from_json_data

try:
    from umls_api_tool.auth import FriendlyAuthenticator
    UMLS_API_TOOL_INSTALLED = True
except ImportError:
    logger.warning(f'UMLS API Tool not installed. CUI expansion not available.')
    UMLS_API_TOOL_INSTALLED = False


@click.command()
@click.argument('note-directories', nargs=-1, type=click.Path(exists=True, path_type=pathlib.Path), )
@click.option('--mml-format', type=str, default='json',
              help='Output format to look for (e.g., "json" or "mmi").')
@click.option('--outdir', type=click.Path(file_okay=False, path_type=pathlib.Path), default=None,
              help='Output directory')
@click.option('--expand-cuis', is_flag=True,
              help='For CUIs with and/or, look for subterms. This helps to comabat longest match in, e.g., MML.')
@click.option('--apikey', default=None, type=str,
              help='API key for use when trying to expand CUIs.')
def run_afep_algorithm(note_directories, *, mml_format='json', outdir: pathlib.Path = None,
                       expand_cuis=False, apikey=None):
    """
    Run greedy AFEP algorithm on extracted knowledge base articles

    :param outdir:
    :param note_directories:
    :param mml_format:
    :return:
    """
    now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    if outdir:
        outdir.mkdir(exist_ok=True, parents=True)
    else:
        outdir = pathlib.Path('.')

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

    logger.info(f'Article types: {article_types}')
    if expand_cuis and UMLS_API_TOOL_INSTALLED:
        logger.info(f'Trying to expand CUIs...')
        auth = FriendlyAuthenticator.from_apikey(apikey)
        known_cuis = {}  # cui -> new terms
        new_results = []
        for row in results:
            target_cui = row['cui']
            if target_cui not in known_cuis:
                target_name = row['preferredname']
                curr_results = []
                if re.search(r'\b(?:or|and)\b', target_name, re.I):
                    for term in re.split(r'\W+', target_name):
                        if term.lower() in {'and', 'or', ''}:
                            continue
                        for cui_data in auth.search(term, language='ENG', limit_pages=1):
                            if cui_data['name'].lower() == term.lower():
                                curr_results.append({
                                    'cui': cui_data['cui'],
                                    'matchedtext': cui_data['name'],
                                    'length': len(cui_data['name']),
                                    'offset': target_name.index(term)
                                })
                                break  # go to next word
                known_cuis[target_cui] = curr_results
            for res in known_cuis[target_cui]:
                # update cui, matchedtext, start, and length
                new_results.append(row | res | {'start': row['start'] + res['offset']})
        results += new_results

    logger.info(f'Building pandas dataset from {len(results)} results.')
    df = pd.DataFrame.from_records(results)
    s = df[['cui', 'article_source']].drop_duplicates().groupby('cui').count()
    half_articles = math.ceil(len(article_types) / 2)
    logger.info(f'Retaining only CUIs appearing in at least {half_articles} knowledge base sources.')
    cuis_with_three_or_more = set(s[s.article_source >= half_articles].index)
    cui_df = df[df.cui.isin(cuis_with_three_or_more)]
    logger.info(f'Retained {cui_df.shape[0]} CUIs.')

    # greedy algorithm
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

    res_dict_df = cui_df[cui_df['cui'].isin(res)].groupby(['cui', 'preferredname']).agg({
        'conceptstring': lambda x: ','.join(set(x)),
        'matchedtext': lambda x: ','.join(set(x)),
        'all_sources': lambda x: ','.join(set(x)),
        'all_semantictypes': lambda x: ','.join(set(x)),
    }).reset_index()

    with open(outdir / f'selected_cuis_{now}.txt', 'w') as out:
        out.write('\n'.join(res_dict_df['cui'].unique()))


if __name__ == '__main__':
    run_afep_algorithm()
