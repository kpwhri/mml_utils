"""
TODO: In progress

Requires: pandas; xlsxwriter
"""

from pathlib import Path

import click
import pandas as pd


def format_table_to_excel(writer, df, name, how='mean'):
    df.to_excel(writer, name, index=False, startrow=1, header=False)
    ws = writer.sheets[name]
    ws.add_table(0, 0, df.shape[0], df.shape[1] - 1, {'columns': [{'header': col} for col in df.columns]})
    for i, col in enumerate(df.columns):
        if str(df[col].dtype) == 'object':
            if how == 'median':
                ws.set_column(i, i, df[col].str.len().median() + 2)
            elif how == 'mean':
                ws.set_column(i, i, df[col].str.len().mean() + 2)
            else:
                ws.set_column(i, i, df[col].str.len().max())
        else:
            ws.set_column(i, i, max(len(col), 12))


@click.command()
@click.argument('afep_path', type=click.Path(path_type=Path, file_okay=False))
@click.option('--how', type=str,
              help='How to determine length of columns (mean, median, max)')
def build_afep_excel(afep_path: Path, how='mean'):
    """Search in `afep_path` for directories containing `-selected` to find csv files with selected features"""
    cdf = None
    writer = pd.ExcelWriter(afep_path / 'afep_summary.xlsx', engine='xlsxwriter')
    names = []
    for p in afep_path.iterdir():
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
    writer.close()
    cdf.to_csv(afep_path / 'afep_summary.csv')
