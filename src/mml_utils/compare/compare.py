import csv
from pathlib import Path

from mml_utils.compare.merger import DataComparator
from mml_utils.excel.tables import send_csv_to_excel


def binary_compare(dc1, dc2):
    dc1_missing = []
    dc2_missing = []
    while dc1 and dc2:
        if dc1 == dc2:
            DataComparator.next_after_both(dc1, dc2)
        elif dc1 > dc2:
            while dc2 and dc1 > dc2:
                dc1_missing.append(dc2.describe())
                dc2.next()
        elif dc1 and dc2 > dc1:
            while dc2 > dc1:
                dc2_missing.append(dc1.describe())
                dc1.next()
        else:
            raise ValueError(f'Comparison problem: {dc1.current} and {dc2.current}.')

    while dc1:
        dc2_missing.append(dc1.describe())
        dc1.next()

    while dc2:
        dc1_missing.append(dc2.describe())
        dc2.next()

    return dc1_missing, dc2_missing


def write_binary_comparison(miss1, miss2, outpath: Path, name1=None, name2=None, text_encoding='latin1'):
    name1 = name1 or 'self'
    name2 = name2 or 'other'
    outfn = outpath / f'compare_{name1}_{name2}.csv'
    with open(outfn, 'w', newline='', encoding=text_encoding) as fh:
        writer = csv.writer(fh)
        writer.writerow(['present_in', 'missing_from', 'cui', 'preferredname', 'docid', 'start', 'end', 'context'])
        for docid, start, end, cui, prefname, context in miss1:
            writer.writerow([name2, name1, cui, prefname, docid, start, end, context])
        for docid, start, end, cui, prefname, context in miss2:
            writer.writerow([name1, name2, cui, prefname, docid, start, end, context])
    return outfn


def extract_binary_text_differences(path1: Path, path2: Path, outpath: Path = None, name1=None, name2=None,
                                    text_encoding='latin1'):
    if outpath is None:
        outpath = Path('.')
    dc1 = DataComparator(path1, name=name1, text_encoding=text_encoding)
    dc2 = DataComparator(path2, name=name2, text_encoding=text_encoding)
    miss1, miss2 = binary_compare(dc1, dc2)
    outfile = write_binary_comparison(miss1, miss2, outpath, dc1.name, dc2.name, text_encoding=text_encoding)
    send_csv_to_excel(outfile, close=True)
