"""
Build review set. Must be run after extracting data for reviewing (relies on those generated CSV files).

"""
import csv
import datetime
import pathlib
from collections import defaultdict

import click

from mml_utils.review.build_excel import compile_to_excel


@click.command()
@click.option('--target-path', type=click.Path(exists=True, path_type=pathlib.Path),
              help='Directory contain files like "fever.review.csv" and "fever.cui.txt",'
                   ' and text file with previous samples (to avoid resampling).')
@click.option('--text-encoding', type=str, default='utf8',
              help='Format that was used to read text files into metamaplite.')
@click.option('--sample-size', type=int, default=50,
              help='Sample size to pull for each output.')
@click.option('--metadata-file', type=click.Path(exists=True, path_type=pathlib.Path), default=None,
              help='Metadata file to add additional columns to output:'
                   ' HEADER = note_id, studyid, date, etc.; VALUES = 1, A2E, 05/06/2011, etc.')
@click.option('--build-csv', type=bool, default=False, is_flag=True,
              help='Always build CSVs (possibly in addition to Excel)')
def _compile_to_excel(target_path: pathlib.Path, text_encoding='utf8', sample_size=50, metadata_file=None,
                      build_csv=False):
    # get note_ids to sample from
    note_ids = defaultdict(set)
    for file in target_path.glob('*.review.csv'):
        feature_name = file.stem.split('.')[0]
        with open(file, newline='', encoding=text_encoding) as fh:
            for row in csv.DictReader(fh):
                note_ids[feature_name].add(row['note_id'])
    outpath = target_path / f'review_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'
    outpath.mkdir(exist_ok=False)
    compile_to_excel(outpath, note_ids, text_encoding=text_encoding,
                     sample_size=sample_size, metadata_file=metadata_file, build_csv=build_csv)


if __name__ == '__main__':
    _compile_to_excel()
