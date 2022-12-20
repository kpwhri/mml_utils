import datetime
import json
import pathlib

import click

from mml_utils.review.build_freqs import build_frequency_tables


def read_json(file):
    """Read json file and return object if the file exists"""
    if file and file.exists():
        with open(file) as fh:
            return json.load(fh)


@click.command()
@click.argument('mml_csv_file', type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path))
@click.option('--feature-mapping', type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path),
              help='Json file with list of mappings of "feature" to a list of "cuis".')
@click.option('--cui-definitions', type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path),
              help='Json file with list of properties: "cui" and "definition"')
@click.option('--metadata-file', type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path),
              help='CSV file with columns `studyid`, `docid`, and `date`.')
@click.option('--output-directory', type=click.Path(exists=True, file_okay=False, path_type=pathlib.Path),
              help='CSV file with columns `studyid`, `docid`, and `date`.')
@click.option('--patient-count', type=int,
              help='Patient count.')
def _build_frequency_tables(mml_csv_file: pathlib.Path, *,
                            metadata_file: pathlib.Path = None,
                            patient_count: int,
                            feature_mapping: pathlib.Path = None,
                            cui_definitions: pathlib.Path = None,
                            output_directory: pathlib.Path = None):
    """

    :param mml_csv_file:
    :param feature_mapping:
    :param cui_definitions:
    :return:
    """
    cui_definitions = read_json(cui_definitions)
    feature_mapping = read_json(feature_mapping)
    build_frequency_tables(mml_csv_file, metadata_file, patient_count, cui_definitions, feature_mapping,
                           output_directory)


if __name__ == '__main__':
    _build_frequency_tables()
