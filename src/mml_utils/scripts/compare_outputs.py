"""
Compare output `cui_by_doc_*.csv` files.

Usage: python compare_outputs.py --compare ctakes_meddra==/path/to/folder/with/cui_by_doc_csv/
"""
import math
from pathlib import Path

import click

try:
    import pandas as pd
except ImportError:
    raise ImportError('Pandas is required to run this command: run `pip install pandas` before trying again.')
from loguru import logger
import seaborn as sns
import matplotlib.pyplot as plt


@click.command()
@click.option('--outdir', type=click.Path(path_type=Path, file_okay=False))
@click.option('--compare', type=str, multiple=True,
              help='name==/path/to/folder/with/cui_by_doc_csv/; if input is lined and comparing to'
                   ' non-lined output, add `lined` to the name and ensure that the docid is `{docid}_{line_num}`')
def _run_compare_outputs(outdir: Path = None, compare=None):
    if compare is None:
        raise ValueError('No items to compare.')
    comparisons = {}
    for c in compare:
        if '==' in c:
            name, path, *other = c.split('==')
            path = Path(path)
        else:  # assumes its a path, use folder name as name
            path = Path(c)
            name = path.name
        if name in comparisons:
            raise ValueError(f'Duplicate name in comparisons: {name}')
        comparisons[name] = path
    run_compare_outputs(comparisons=comparisons, outdir=outdir)


def run_compare_outputs(comparisons: dict[str, Path], outdir=None):
    if outdir is None:
        outdir = Path('.')
    outdir.mkdir(exist_ok=True)
    logger.add(outdir / 'compare_outputs.log')
    categories = list(comparisons.keys())
    df, cuis, docids = collect_data(comparisons)
    df = get_jaccard_coefs(df, categories, cuis, docids)
    build_violinplot(df, outdir)
    build_heatmap(df, outdir, kind='mean')
    build_heatmap(df, outdir, kind='median')
    logger.info('Finished')


def collect_data(comparisons):
    """Collect data from cui_by_doc files."""
    dfs = []
    docids = set()
    cuis = set()
    for cat, path in comparisons.items():
        logger.info(f'Loading {cat}: {path}')
        cui_by_docs = sorted(path.glob('cuis_by_doc_*.csv'))
        if not cui_by_docs:
            logger.warning(f'Missing `cuis_by_doc_*.csv` for {cat}: {path}')
            continue
        _df = pd.read_csv(cui_by_docs[-1])
        if 'lined' in cat:
            # handle comparisons of joined/lined output
            _df = _df.groupby('docid').sum().reset_index()
            _df['_docid'] = _df['docid']
            _df['docid'] = _df['_docid'].apply(lambda x: x.split('_')[0])
            del _df['_docid']
            _df = _df.groupby('docid').sum().reset_index()
            docids |= set(_df['docid'].unique())
        _df['name'] = cat
        cuis |= {c for c in _df.columns if c.startswith('C')}
        dfs.append(_df)
    # fix any issues with missing docids
    logger.info(f'Filling missing docids with 0s for all CUIs.')
    # TODO: is this necessary for Jaccard? May be necessary for other comparisons...
    _dfs = []
    for _df in dfs:
        _docids = docids - set(_df.docid)
        if _docids:
            name = list(_df['name'].unique())[0]
            _df = pd.concat((_df, pd.DataFrame({'docid': list(_docids)} | {c: 0 * len(_docids) for c in cuis})))
            _df['name'] = name
        _dfs.append(_df.fillna(0))
    return pd.concat(_dfs), cuis, docids


def get_jaccard_coefs(df, categories, cuis, docids):
    logger.info(f'Calculating Jaccard Coefficients. Notes without CUIs are skipped.')
    dfs = []
    for i, lcat in enumerate(categories[:-1]):
        ldf = df[(df.name == lcat)][['docid'] + list(cuis)].set_index('docid').sort_index()
        for rcat in categories[i + 1:]:
            name = f'{lcat}-{rcat}'
            rdf = df[df.name == rcat][['docid'] + list(cuis)].set_index(
                'docid').sort_index()
            jaccard_coefs = []
            for docid in docids:
                ls = ldf.T[docid]
                l_cuis = set(ls[ls > 0].index)
                rs = rdf.T[docid]
                r_cuis = set(rs[rs > 0].index)
                try:
                    jac_coef = len(l_cuis & r_cuis) / len(l_cuis | r_cuis)
                except ZeroDivisionError:
                    continue
                jaccard_coefs.append((docid, jac_coef, name, lcat, rcat))
            _df = pd.DataFrame(jaccard_coefs, columns=['docid', 'jaccard', 'kind', 'left', 'right'])
            dfs.append(_df)
    jac_df = pd.concat(dfs)
    return jac_df


def build_violinplot(df, outdir, n=None):
    """Group violin plots in groups of 4 to retain readability"""
    logger.info('Creating violinplots of Jaccard coefficients.')
    kinds = df.kind.unique()
    if n is None:
        plt.figure(figsize=(8, len(kinds)))
        ax = sns.violinplot(data=df, y='kind', x='jaccard', scale='width')
        plt.tight_layout()
        ax.figure.savefig(outdir / f'jaccard_violin_n{len(kinds)}.png')

    else:
        for i in range(math.ceil(len(kinds) / n)):
            plt.figure(figsize=(8, 8))
            ax = sns.violinplot(data=df[df.kind.isin(kinds[i * n:(i*n) + n])], y='kind', x='jaccard', scale='width')
            plt.tight_layout()
            ax.figure.savefig(outdir / f'jaccard_violin_{i}.png')


def build_heatmap(df, outdir, kind='mean'):
    logger.info(f'Creating heatmap of {kind} Jaccard coefficients.')
    df = df.groupby(['left', 'right'])['jaccard'].agg(kind).reset_index()
    # fill in bottom half of heat map (these are just duplicates)
    df2 = df.copy()
    df2.columns = ['right', 'left', 'jaccard']
    df = pd.concat((df, df2))
    hm_df = df.pivot(index='left', columns='right', values='jaccard').fillna(1.0)  # fill where left == right
    plt.figure(figsize=(8, 8))
    ax = sns.heatmap(hm_df, annot=True)
    plt.tight_layout()
    ax.figure.savefig(outdir / f'heatmap_{kind}_jaccard.png')


if __name__ == '__main__':
    _run_compare_outputs()
