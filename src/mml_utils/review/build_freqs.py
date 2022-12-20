"""
Build frequency tables. [requires pandas]
"""
import csv
import datetime
import pathlib

try:
    import pandas as pd
except ImportError:
    raise ImportError(f'Pandas is required when building frequencies: run `pip install pandas`.')


def get_pivot_table(df):
    """Create pivot table from merging of mml data to metadata file."""
    curr_df = df[['studyid', 'date', 'docid', 'cui', 'count']].groupby(['studyid', 'date', 'docid', 'cui'])[
        'count'].count().reset_index()
    return pd.pivot_table(
        curr_df, values='count', index=['studyid', 'date', 'docid'], columns='cui', aggfunc='sum', fill_value=0
    ).reset_index()


def create_feature_version(df, feature_mapping, cui_definitions):
    """Create version of dataframe based on features rather than CUIs"""
    feature_df = df.copy()
    for mapping in feature_mapping:
        feature = mapping['feature']
        cuis = mapping['cuis']
        cols = {str(x) for x in feature_df.columns}
        for cui in cuis:
            if f'{cui}_count' not in cols:
                feature_df[f'{cui}_count'] = 0
            if f'{cui}_count_nonneg' not in cols:
                feature_df[f'{cui}_count_nonneg'] = 0
        # count
        feature_df[f'{feature}_count'] = feature_df[
            [f'{cui}_count' for cui in cuis]
        ].apply(lambda x: x.sum(), axis=1)  # sum isn't quite accurate, but these will be normalized to 1/0
        # nonneg count
        feature_df[f'{feature}_count_nonneg'] = feature_df[
            [f'{cui}_count_nonneg' for cui in cuis]
        ].apply(lambda x: x.sum(), axis=1)  # sum isn't quite accurate, but these will be normalized to 1/0
    for definition in cui_definitions:
        cui = definition['cui']
        del feature_df[f'{cui}_count']
        del feature_df[f'{cui}_count_nonneg']
    return feature_df


def as_int(val, default=0):
    """Convert to int; if nan, return default"""
    if pd.isna(val):
        return default
    return int(val)


def build_pt_table(input_df, columns=None):
    """Summarize data at the patient level."""
    if not columns:
        columns = {col.split('_count')[0] for col in input_df.columns if '_count' in col}
    results = []
    studyids = list(input_df['studyid'].unique())
    for studyid in studyids:
        currdf = input_df[input_df['studyid'] == studyid]
        curr_date_df = currdf.groupby('date').sum(None)
        res = {'STUDYID': studyid}
        for feature in columns:
            col = f'{feature}_count'
            col_nn = f'{feature}_count_nonneg'
            has_col = col in currdf.columns
            has_col_nn = col_nn in currdf.columns
            feature_up = feature.upper()
            res[f'N_MENTS_{feature_up}'] = as_int(currdf[col].sum(None)) if has_col else 0
            res[f'N_MENTS_NN_{feature_up}'] = as_int(currdf[col_nn].sum(None)) if has_col_nn else 0
            res[f'N_NOTES_{feature_up}'] = as_int((currdf[col] > 0).sum(None)) if has_col else 0
            res[f'N_NOTES_NN_{feature_up}'] = as_int((currdf[col_nn] > 0).sum(None)) if has_col_nn else 0
            res[f'N_CALDAYS_{feature_up}'] = as_int((curr_date_df[col] > 0).sum(None)) if has_col else 0
            res[f'N_CALDAYS_NN_{feature_up}'] = as_int((curr_date_df[col_nn] > 0).sum(None)) if has_col_nn else 0
            res[f'MAX_MENTS_{feature_up}'] = as_int(currdf[col].max()) if has_col else 0
            res[f'MAX_MENTS_NN_{feature_up}'] = as_int(currdf[col_nn].max()) if has_col_nn else 0
        results.append(res)
    return pd.DataFrame.from_records(results)


def build_table(input_df, total_pt_count, label='cui'):
    """
    Build table that creates frequencies of occurrences of cuis/features
    :param input_df:
    :param total_pt_count: total number of patients (NLP data may not include all patients
    :param label: 'cui' or 'features'
    :return:
    """
    count_df = input_df[[col for col in input_df.columns if '_count' in col]].T.applymap(lambda x: 1 if x >= 1 else 0)
    count_df['pt_count'] = count_df.sum(axis=1)
    count_df = count_df.reset_index()[['index', 'pt_count']]
    # break apart all/nonneg counts
    count_df['is_nonneg'] = count_df['index'].apply(lambda x: x.endswith('_nonneg'))
    count_df[label] = count_df['index'].apply(lambda x: x.split('_')[0])
    count_df['pt_percent'] = count_df['pt_count'] / total_pt_count  # keep as float, allow end-user to format
    # clean up columns
    cols = [label, 'pt_count', 'pt_percent']
    all_count_df = count_df[count_df['is_nonneg'] == False][cols]
    nonneg_count_df = count_df[count_df['is_nonneg'] == True][cols]
    nonneg_count_df.columns = [label, 'pt_count_nonneg', 'pt_percent_nonneg']
    table = pd.merge(all_count_df, nonneg_count_df, on=label)
    table['pt_count_negated_only'] = table['pt_count'] - table['pt_count_nonneg']
    return table


def add_cui_definition(df, cui_definitions):
    """Add cui definitions as new column to existing dataframe which has a 'cui' column like C0000000"""
    definitions = {definition['cui']: definition['definition'] for definition in cui_definitions}
    if isinstance(df.columns, pd.MultiIndex):
        df['cui', 'cui_name'] = df['cui', 'cui'].apply(lambda x: definitions.get(x, ''))
        # reorder by cui - positive - negative
        df = df.reindex(
            columns=sorted(df.columns, key=lambda x: 2 if x[0][0] == 'n' else 1 if x[0][0] == 'p' else 0))
    else:
        df['cui_name'] = df['cui'].apply(lambda x: definitions.get(x, ''))
        df = df[['cui', 'cui_name'] + list(df.columns)[1:-1]]
    return df


def add_cuis_for_feature(df, feature_mapping):
    """Add list of CUIs to dataframe containing features."""
    if isinstance(df.columns, pd.MultiIndex):
        df['feature', 'cuis'] = df['feature', 'feature'].apply(
            lambda x: ','.join(
                cui for mapping in feature_mapping for cui in mapping['cuis'] if mapping['feature'] == x
            ))
        # reorder by cui - positive - negative
        df = df.reindex(
            columns=sorted(df.columns, key=lambda x: 2 if x[0][0] == 'n' else 1 if x[0][0] == 'p' else 0))
    else:
        df['cuis'] = df['feature'].apply(
            lambda x: ','.join(
                cui for mapping in feature_mapping for cui in mapping['cuis'] if mapping['feature'] == x
            ))
        df = df[['feature', 'cuis'] + list(df.columns)[1:-1]]
    return df


def build_frequency_tables(mml_csv_file, metadata_file, patient_count, cui_definitions, feature_mapping,
                           output_directory,
                           to_excel=True):
    """
    Create frequency tables
    :param mml_csv_file: CSV file built from MML output using `mml-extract-mml`
    :param metadata_file: CSV file with:
        * `studyid`: unique value per subject
        * `docid`: noteid/docid that is used to identify notes; should be equivalent to `docid` in `mml_csv_file`
        * `date`: note date, ideally as YYYY-MM-DD (this will be used for grouping based on calendar days)
    :param patient_count: [int] number of total studyids (required because metadata_file only lists those with notes)
    :param cui_definitions: json file of [{ "cui": "C0027497", "definition": "Nausea" }, ...]
    :param feature_mapping: (optional) if grouping cuis into features;
        * [{ "feature": "Diarrhea", "cuis": [ "C0011991", ... ] }, ...]
    :param output_directory: (optional) output directory; will default to current directory
    :param to_excel: output to excel file as different sheets too
    :return: subdirectory of output_directory where files are created
    """
    now = datetime.datetime.now().strftime('%Y%m%d')
    if output_directory is None:
        output_directory = pathlib.Path('.')
    output_directory = output_directory / f'freq_tables_{now}'
    output_directory.mkdir(exist_ok=True)
    # read mml summary data
    mml_data = []
    with open(mml_csv_file, encoding='utf8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            docid = int(row['docid'])
            cui = row['cui']
            negated = row['negated']
            mml_data.append((docid, cui, negated))
    # merge/format data
    mml_df = pd.DataFrame(mml_data, columns=['docid', 'cui', 'negated'])
    meta_df = pd.read_csv(metadata_file)
    df = pd.merge(mml_df, meta_df, on='docid', how='inner')[['studyid', 'docid', 'date', 'cui', 'negated']]
    df['count'] = 1
    all_counts = get_pivot_table(df)
    nonneg_counts = get_pivot_table(df[df.negated == 'False'])
    all_counts.columns = [f'{x}_count' if x.startswith('C') else x for x in all_counts.columns]
    nonneg_counts.columns = [f'{x}_count_nonneg' if x.startswith('C') else x for x in nonneg_counts.columns]
    df = pd.merge(all_counts, nonneg_counts, how='outer')
    cuis = [defn['cui'] for defn in cui_definitions]
    # build tables
    pt_df = build_pt_table(df, cuis)
    cui_count_table = add_cui_definition(build_table(df, patient_count, 'cui'), cui_definitions)

    # output directory
    pt_df.to_csv(output_directory / 'cui_cnt_by_pt.csv', index=False)
    cui_count_table.to_csv(output_directory / 'cui_freqs.csv', index=False)

    if feature_mapping:
        feature_df = create_feature_version(df, feature_mapping, cui_definitions)
        features = [mapping['feature'] for mapping in feature_mapping]
        pt_feature_df = build_pt_table(feature_df, features)
        feature_count_table = add_cuis_for_feature(build_table(feature_df, patient_count, 'feature'), feature_mapping)
        # output directory
        pt_feature_df.to_csv(output_directory / 'feat_cnt_by_pt.csv', index=False)
        feature_count_table.to_csv(output_directory / 'feat_freqs.csv', index=False)
    if to_excel:
        writer = pd.ExcelWriter(output_directory / 'feature_counts__all_cuis.xlsx')
        cui_count_table.to_excel(writer, sheet_name='cui_freqs')
        pt_df.to_excel(writer, sheet_name='cui_cnt_by_pt')
        if feature_mapping:
            feature_count_table.to_excel(writer, sheet_name='feat_freqs')
            pt_feature_df.to_excel(writer, sheet_name='feat_cnt_by_pt')
        writer.save()
    return output_directory
