"""
Implement AFEP, including Greedy Feature Selection.
"""
import json
import datetime
import math
from pathlib import Path

import pandas as pd

from mml_utils.datesuffix import dtstr
from mml_utils.phenorm.cui_expansion import add_shorter_match_cuis
from loguru import logger

from mml_utils.parse.json import extract_mml_from_json_data
from mml_utils.parse.mmi import extract_mml_from_mmi_data
from mml_utils.parse.xmi import extract_mml_from_xmi_data


def extract_articles(note_directories, mml_format, *, data_directories=None):
    article_types = set()
    results = []
    if data_directories is None:
        data_directories = note_directories
    for path in data_directories:
        for file in path.glob(f'*.{mml_format}'):
            article_type = file.stem.split('_')[0]
            article_types.add(article_type)
            filename = file.stem

            if mml_format == 'json':
                with open(file) as fh:
                    data = json.load(fh)
                extract_function = extract_mml_from_json_data
            elif mml_format == 'mmi':
                with open(file, encoding='utf8') as fh:
                    data = fh.read()
                extract_function = extract_mml_from_mmi_data
            elif mml_format == 'xmi':
                extract_function = extract_mml_from_xmi_data
                with open(file, encoding='utf8') as fh:
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
    if 'all_sources' not in df.columns:  # backwards compatibility: TODO: remove
        df['all_sources'] = ''
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


def run_afep_algorithm(note_directories, *, mml_format='json', outdir: Path = None,
                       expand_cuis=False, apikey=None, skip_greedy_algorithm=False, min_kb=None,
                       max_kb=None, data_directory=None):
    now = dtstr()
    if outdir:
        outdir.mkdir(exist_ok=True, parents=True)
    else:
        outdir = Path('.')

    article_types, results = extract_articles(note_directories, mml_format, data_directories=data_directory)
    logger.info(f'Article types: {article_types}')
    if len(article_types) == 0:
        logger.error(f'No articles found!')
        raise ValueError(f'No articles found! Perhaps the wrong directory was indicated for reading output?')

    if expand_cuis:
        results = add_shorter_match_cuis(results, apikey)

    logger.info(f'Building pandas dataset from {len(results)} results.')
    df = pd.DataFrame.from_records(results)
    s = df[['cui', 'article_source']].drop_duplicates().groupby('cui').count()
    if min_kb is None:
        min_kb = math.ceil(len(article_types) / 2)
    logger.info(f'Retaining only CUIs appearing in at least {min_kb} knowledge base sources.')
    cuis_with_three_or_more = set(s[s.article_source >= min_kb].index)
    cui_df = df[df.cui.isin(cuis_with_three_or_more)].copy()
    logger.info(f'Retained {cui_df.shape[0]} CUIs.')

    # max knowledge base articles
    if max_kb is not None:
        logger.info(f'Removing CUIs appearing in more than {min_kb} knowledge base sources.')
        cuis_with_max_kb = set(s[s.article_source <= max_kb].index)
        cui_df = df[df.cui.isin(cuis_with_max_kb)].copy()
        logger.info(f'Now retained {cui_df.shape[0]} CUIs.')

    # greedy algorithm to reduce number of CUIs
    if skip_greedy_algorithm:
        logger.info(f'Skipping greedy algorithm.')
        res = cui_df['cui'].unique()
    else:
        res = run_greedy_algorithm(cui_df, df)

    res_dict_df = cui_df[cui_df['cui'].isin(res)].groupby(['cui', 'preferredname']).agg({
        'conceptstring': lambda x: ','.join(set(x)),
        'matchedtext': lambda x: ','.join(set(x)),
        'all_sources': lambda x: ','.join(set(x)),
        'all_semantictypes': lambda x: ','.join(set(x)),
    }).reset_index()

    with open(outdir / f'selected_cuis_{now}.txt', 'w') as out:
        out.write('\n'.join(res_dict_df['cui'].unique()))

    cui_df['value'] = 1
    article_df = cui_df[['cui', 'article_source', 'value']].pivot_table(
        index='cui', columns='article_source', fill_value=0
    )
    article_df.columns = article_df.columns.droplevel(level=0)
    article_df.columns.name = None
    article_df['n_articles'] = article_df.apply(sum, axis=1)
    summary_df = pd.merge(res_dict_df, article_df.reset_index(), on='cui')
    summary_df.to_csv(outdir / f'selected_cui_details_{now}.csv', index=False)


def write_afep_script_for_dirs(outdir: Path, target_dirs: set[Path], **kwargs):
    with open(outdir / f'run_afep-{dtstr()}.toml', 'w') as out:
        out.write(f'# Autogenerated AFEP config: requires editing\n\n')
        out.write(f'outdir = \'{outdir}\'\n')
        out.write(f'build_summary = true\n')
        out.write(f'note_directories = [\'TODO\']\n')
        out.write(f'mml_format = \'{kwargs.get("mml_format", "json")}\'\n')
        out.write(f'expand_cuis = false\n')
        out.write(f'apikey = \'\'\n')
        for target_dir in target_dirs:
            out.write('\n[[runs]]\n')
            out.write(f'name = \'{target_dir.stem}\'\n')
            out.write(f'data_directory = [\'{target_dir}\']\n')
