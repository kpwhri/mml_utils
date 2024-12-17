import csv
import datetime
import re
from pathlib import Path

from loguru import logger

from mml_utils.parse.target_cuis import TargetCuis

try:
    import pandas as pd
except ImportError:
    pd = None

NLP_FIELDNAMES = [
    'event_id', 'docid', 'filename', 'matchedtext', 'conceptstring', 'cui', 'preferredname', 'start', 'length',
]
NOTE_FIELDNAMES = [
    'filename', 'docid', 'num_chars', 'num_letters', 'num_words', 'processed',
]


def load_target_cuis(cui_file) -> TargetCuis:
    target_cuis = TargetCuis()
    if cui_file is None:
        logger.warning(f'Retaining all CUIs.')
        return target_cuis
    with open(cui_file, encoding='utf8') as fh:
        for line in fh:
            target_cuis.add(*line.strip().split(','))
    logger.info(f'Keeping {target_cuis.n_keys()} CUIs, and mapping to {target_cuis.n_values()}.')
    return target_cuis


def prepare_extract(outdir, fieldnames, cui_file):
    now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    outdir.mkdir(exist_ok=True)
    note_outfile = outdir / f'notes_{now}.csv'
    nlp_outfile = outdir / f'nlp_{now}.csv'
    cuis_by_doc_outfile = outdir / f'cuis_by_doc_{now}.csv'
    add_fieldnames(fieldnames)
    target_cuis = load_target_cuis(cui_file)
    return (note_outfile, nlp_outfile, cuis_by_doc_outfile), target_cuis


def add_fieldnames(fieldnames):
    global NLP_FIELDNAMES
    for fieldname in fieldnames:
        NLP_FIELDNAMES.append(fieldname)


def find_path(exp_filename, curr_directory, target_directories=None, dir_index=None):
    """Look for the expected filename + output format at a particular path."""
    if target_directories:
        # prefer output directory corresponding to ordered list of note directories
        if dir_index < len(target_directories) and (
                path := Path(target_directories[dir_index] / exp_filename)).exists():
            return path
        for i, target_dir in enumerate(target_directories):
            if i == dir_index:  # already looked here
                continue
            if (path := Path(target_dir / exp_filename)).exists():
                return path
    elif (path := Path(curr_directory / exp_filename)).exists():
        return path


def build_extracted_file(result_iter, note_outfile, nlp_outfile):
    missing_note_dict = set()
    missing_mml_dict = set()
    logger_warning_count = 5
    with open(note_outfile, 'w', newline='', encoding='utf8') as note_out, \
            open(nlp_outfile, 'w', newline='', encoding='utf8') as nlp_out:
        note_writer = csv.DictWriter(note_out, fieldnames=NOTE_FIELDNAMES)
        note_writer.writeheader()
        mml_writer = csv.DictWriter(nlp_out, fieldnames=NLP_FIELDNAMES)
        mml_writer.writeheader()
        for is_record, data in result_iter:
            if is_record:
                field_names = NOTE_FIELDNAMES
            else:
                field_names = NLP_FIELDNAMES
            curr_missing_data_dict = set(data.keys()) - set(field_names)
            if curr_missing_data_dict:
                if logger_warning_count > 0:
                    logger.warning(f'Only processing known fields for record: {data["docid"]}')
                    logger_warning_count -= 1
                    if logger_warning_count == 0:
                        logger.warning(f'Suppressing future warnings:'
                                       f' a final summary of added keys will be logged at the end.')
                if is_record:
                    missing_note_dict |= curr_missing_data_dict
                    if logger_warning_count >= 0:
                        logger.info(f'''Missing Note Dict: '{"','".join(missing_note_dict)}' ''')
                    data = {k: v for k, v in data.items() if k in NOTE_FIELDNAMES}
                else:
                    missing_mml_dict |= curr_missing_data_dict
                    if logger_warning_count >= 0:
                        logger.info(f'''Missing NLP Dict: '{"','".join(missing_mml_dict)}' ''')
                    data = {k: v for k, v in data.items() if k in NLP_FIELDNAMES}
            if is_record:
                note_writer.writerow(data)
            else:
                mml_writer.writerow(data)
    if missing_mml_dict:
        logger.warning(f'''All Missing NLP Dict: '{"','".join(missing_mml_dict)}' ''')
    if missing_note_dict:
        logger.warning(f'''All Missing Note Dict: '{"','".join(missing_note_dict)}' ''')
    logger.info(f'Completed successfully.')


def build_pivot_table(nlpfile, outfile, target_cuis: TargetCuis = None):
    if pd is None:
        logger.warning(f'Unable to build pivot table: please install pandas `pip install pandas` and try again.')
        return
    df = pd.read_csv(nlpfile, usecols=['docid', 'cui'])
    n_cuis = df['cui'].nunique()
    n_docs = df['docid'].nunique()
    df['count'] = 1
    df = df.pivot_table(index='docid', columns='cui', values='count', fill_value=0, aggfunc='sum').reset_index()
    if target_cuis:  # ensure that all output cuis have been included in the output
        missing_cuis = set(target_cuis.values) - set(df.columns)
        logger.info(f'Adding back {len(missing_cuis)} CUIs that were not found in the notes.')
        n_cuis += len(missing_cuis)
        for missing_cui in missing_cuis:
            df[missing_cui] = 0
    # sort output columns
    df = df[['docid'] + sorted(col for col in df.columns if col.startswith('C'))]
    df.to_csv(outfile, index=False)
    logger.info(f'Output {n_cuis} CUIs (requested {len(target_cuis)}) found in {n_docs} documents to: {outfile}.')


def add_notefile_to_record(record: dict, file: Path, encoding='utf8'):
    with open(file, encoding=encoding) as fh:
        text = fh.read()
        record['num_chars'] = len(text)
        record['num_words'] = len(text.split())
        record['num_letters'] = len(re.sub(r'[^A-Za-z0-9]', '', text, flags=re.I))
