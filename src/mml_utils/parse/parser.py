import json
import pathlib

from mml_utils.parse.json import extract_mml_from_json_data
from mml_utils.parse.mmi import extract_mml_from_mmi_data


def extract_mml_data(file: pathlib.Path, *, encoding='cp1252', target_cuis=None, output_format='json'):
    with open(file, encoding=encoding) as fh:
        text = fh.read()
    if not text.strip():  # handle empty note
        return
    if output_format == 'json':  # TODO: match-case
        data = json.loads(text)
        yield from extract_mml_from_json_data(data, file.name, target_cuis=target_cuis)
    elif output_format == 'mmi':
        yield from extract_mml_from_mmi_data(text, file.name, target_cuis=target_cuis)
    else:
        raise ValueError(f'Unrecognized output format: {output_format}.')
