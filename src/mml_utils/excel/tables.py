import datetime
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    pd = None

SESSION_WRITER = None


def format_table_to_excel(writer, df, name, how='mean'):
    if len(name) >= 32:
        name = '_'.join(str(x)[:4] for x in name.split('_'))
        if len(name) >= 32:
            name = name[:31]
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


def get_excel_writer(outpath: Path = None, name=None):
    global SESSION_WRITER
    if SESSION_WRITER is None:
        if not name:
            name = f'mml_summary_{datetime.datetime.now().strftime("%Y%m%s_%H%M%S")}'
        SESSION_WRITER = pd.ExcelWriter(outpath / f'{name}.xlsx', engine='xlsxwriter')
    return SESSION_WRITER


def _has_pandas():
    return pd is not None


def send_csv_to_excel(csvfile: Path, name=None, close=False):
    if not _has_pandas():
        return False
    writer = get_excel_writer(csvfile.parent, name or csvfile.stem)
    df = pd.read_csv(csvfile, encoding_errors='replace')
    format_table_to_excel(writer, df, csvfile.stem)
    if close:
        write_excel()
    return True


def write_excel():
    global SESSION_WRITER
    if SESSION_WRITER is not None:
        SESSION_WRITER.close()
