"""
Run AFEP greedy algorithm on results of MetaMapLite extraction of Raw Knowledge Base files.

Implementation notes:
1. Only json currently implemented (not mmi)
2. CUIs will be grouped by article type.
    * Article type is defined as all content before the first '_' (not including extension)..
"""
import datetime
import math
import pathlib

import click
import pandas as pd
from loguru import logger

from mml_utils.phenorm.afep import extract_articles, run_greedy_algorithm
from mml_utils.phenorm.cui_expansion import add_shorter_match_cuis


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
@click.option('--skip-greedy-algorithm', is_flag=True, default=False,
              help='Skip greedy selection algorithm.')
def run_afep_algorithm(note_directories, *, mml_format='json', outdir: pathlib.Path = None,
                       expand_cuis=False, apikey=None, skip_greedy_algorithm=False):
    """
    Run greedy AFEP algorithm on extracted knowledge base articles

    :param expand_cuis:
    :param apikey:
    :param skip_greedy_algorithm:
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

    article_types, results = extract_articles(note_directories, mml_format)
    logger.info(f'Article types: {article_types}')

    if expand_cuis:
        results = add_shorter_match_cuis(results, apikey)

    logger.info(f'Building pandas dataset from {len(results)} results.')
    df = pd.DataFrame.from_records(results)
    s = df[['cui', 'article_source']].drop_duplicates().groupby('cui').count()
    half_articles = math.ceil(len(article_types) / 2)
    logger.info(f'Retaining only CUIs appearing in at least {half_articles} knowledge base sources.')
    cuis_with_three_or_more = set(s[s.article_source >= half_articles].index)
    cui_df = df[df.cui.isin(cuis_with_three_or_more)]
    logger.info(f'Retained {cui_df.shape[0]} CUIs.')

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


if __name__ == '__main__':
    run_afep_algorithm()
