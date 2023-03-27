from pathlib import Path

import pandas as pd


def format_table_to_excel(writer, df, name, how='mean'):
    df.to_excel(writer, name, index=False, startrow=1, header=False)
    ws = writer.sheets[name]
    ws.add_table(0, 0, df.shape[0], df.shape[1] - 1, {'columns': [{'header': col} for col in df.columns]})
    for i, col in enumerate(df.columns):
        col_len = len(col) + 1
        if str(df[col].dtype) == 'object':
            if how == 'median':
                ws.set_column(i, i, max(col_len, df[col].str.len().median() + 2))
            elif how == 'mean':
                ws.set_column(i, i, max(col_len, df[col].str.len().mean() + 2))
            else:
                ws.set_column(i, i, max(col_len, df[col].str.len().max()))
        else:
            ws.set_column(i, i, max(col_len, 12))


def add_diffs(cdf, names):
    """Add a table comparing results from different vocabularies."""
    diff_df = None
    cols = ['cui', 'preferredname']
    for i, name in enumerate(names):
        for name2 in names[i + 1:]:
            res1 = cdf[(cdf[name] == 1) & (cdf[name2] == 0)][cols].copy()
            res1[f'{name}-vs-{name2}'] = f'{name}_only'
            res2 = cdf[(cdf[name] == 0) & (cdf[name2] == 1)][cols].copy()
            res2[f'{name}-vs-{name2}'] = f'{name2}_only'
            df = pd.concat((res1, res2))
            if diff_df is None:
                diff_df = df
            else:
                diff_df = pd.merge(diff_df, df, on=cols, how='outer').fillna('NONE')
    return diff_df


def build_afep_excel(afep_path: Path, how='mean'):
    """Search in `afep_path` for directories containing `-selected` to find csv files with selected features"""
    cdf = None
    writer = pd.ExcelWriter(afep_path / 'afep_summary.xlsx', engine='xlsxwriter')
    names = []
    for p in sorted(afep_path.iterdir()):
        if p.is_dir() and 'selected' in p.stem:
            name = p.stem.replace('-selected', '')
            names.append(name)
            file = sorted(p.glob('*.csv'))[-1]  # most recent file
            df = pd.read_csv(file)
            # write to excel and format as table
            format_table_to_excel(writer, df, name, how=how)
            # merge with others to compare
            df = df[['cui', 'preferredname']]
            df[name] = 1
            if cdf is None:
                cdf = df
            else:
                cdf = pd.merge(cdf, df, on=['cui', 'preferredname'], how='outer')
    cdf.fillna(0, inplace=True)
    for name in names:
        cdf[name] = cdf[name].apply(int)
    format_table_to_excel(writer, cdf, 'afep_summary', how=how)
    diff_df = add_diffs(cdf, names)
    format_table_to_excel(writer, diff_df, 'diffs', how=how)
    writer.close()
    cdf.to_csv(afep_path / 'afep_summary.csv')
