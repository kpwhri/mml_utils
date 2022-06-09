"""
Extract CUIs and text strings for some feature (e.g., fever, diarrhea, etc.) from MML output.
These can then be used to review the results to determine how useful the CUIs/text strings are.

Runs on Metamaplite output directories (text file and jsonl/mmi expected in same directory).

Expects a feature directory:
* {feature_name}.string.txt
    * unique text string to look for on each line
    * Examples:
        * BM frequent
        * BM loose
* {feature_name}.cui.txt
    * unique CUI to look for on each line
    * additional data can be included in tab-separated format
    * Examples:
        * C0687681
        * C0687681\tFeeling feverish


# Generate Reviews for Output Data

--> This can be done automatically with `sample_review_set.py`

```python
import pandas as pd
from loguru import logger

SAMPLE_SIZE = 50
df = pd.GET_METADATA()  # e.g., with studyid and docid
with pd.ExcelWriter(outpath / f'features.review{SAMPLE_SIZE}.xlsx') as writer:
    logger.info(f"All notes dataset -> Unique Notes: {df['note_id'].nunique()}; Unique Patients: {df['studyid'].nunique()}")
    for file in base_path.glob('*.review.csv'):
        feature_name = file.stem.split('.')[0]
        logger.info(f'Reading feature {feature_name}: {file}')
        feature_df = pd.read_csv(file)
        logger.info(f"Source feature dataset -> Unique Notes: {feature_df['docid'].nunique()}")
        mdf = pd.merge(df, feature_df, on='docid')
        logger.info(f"Merged dataset -> Unique Notes: {mdf['docid'].nunique()}; Unique Patients: {mdf['studyid'].nunique()}")
        # output options
        mdf['Is this term referring to the feature?'] = ''
        mdf['Does the patient have this feature?'] = ''
        mdf['Optional Comments'] = ''
        unique_notes = mdf['docid'].unique()
        sampled = random.sample(sorted(unique_notes), SAMPLE_SIZE)
        rdf = mdf[mdf.docid.isin(sampled)]
        rdf = rdf[[
            'id', 'studyid', 'docid', 'precontext', 'keyword', 'postcontext', 'Is this term referring to the feature?',
            'Does the patient have this feature?', 'Optional Comments', 'fullcontext'
        ]]
        rdf.to_csv(outpath / f'{feature_name}.sample{SAMPLE_SIZE}.csv', index=False)
        rdf.to_excel(writer, sheet_name=feature_name, index=False)
```
"""
import pathlib

import click

from mml_utils.review.extract_data import extract_data_for_review


@click.command()
@click.argument('note-directories', nargs=-1, type=click.Path(exists=True, path_type=pathlib.Path))
@click.option('--target-path', type=click.Path(exists=True, path_type=pathlib.Path),
              help='Directory contain files like "fever.cui.txt" and "fever.string.txt"')
@click.option('--mml-format', type=str, default='json',
              help='MML Output format to look for (e.g., "json" or "mmi"); currently only supports "json" and "mmi".')
@click.option('--text-extension', type=str, default='',
              help='Add ".txt" if text files have an extension.')
@click.option('--text-encoding', type=str, default='utf8',
              help='Format to read text files into metamaplite.')
@click.option('--text-errors', type=str, default='replace',
              help='Passed to "errors" in "open" function to open file.')
@click.option('--add-cr', type=bool, default=False, is_flag=True,
              help='Add back carriage return; likely required if MML run on Windows.')
@click.option('--sample-size', type=int, default=50,
              help='Sample size to pull for each output.')
@click.option('--metadata-file', type=click.Path(exists=True, path_type=pathlib.Path), default=None,
              help='Metadata file to add additional columns to output:'
                   ' HEADER = note_id, studyid, date, etc.; VALUES = 1, A2E, 05/06/2011, etc.'
                   ' This file WILL LIMIT the notes to only those in this file.')
@click.option('--replacements', type=str, multiple=True,
              help='Replace text to fix offset issues. Arguments should look like "from==to" which will'
                   ' replace "from" with "to" before checking offsets.')
def _extract_data_for_review(note_directories: list[pathlib.Path], target_path: pathlib.Path = pathlib.Path('.'),
                             mml_format='json', text_extension='', text_encoding='utf8',
                             text_errors='replace', add_cr=False,
                             sample_size=50, metadata_file=None,
                             replacements=None):
    extract_data_for_review(note_directories, target_path, mml_format, text_extension, text_encoding,
                            text_errors=text_errors, add_cr=add_cr, sample_size=sample_size,
                            metadata_file=metadata_file, replacements=replacements)


if __name__ == '__main__':
    _extract_data_for_review()
