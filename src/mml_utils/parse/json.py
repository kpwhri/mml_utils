import json
import pathlib

from mml_utils.parse.target_cuis import TargetCuis


def extract_mml_from_json_data(data, filename, *, target_cuis: TargetCuis = None, extras=None):
    """

    :param data:
    :param filename:
    :param target_cuis:
    :param extras:
    :return:
    """
    filename = pathlib.Path(filename)
    i = 0
    if target_cuis is None:
        target_cuis = TargetCuis()
    for el in data:
        for event in el['evlist']:
            for cui in target_cuis.get_target_cuis(event['conceptinfo']['cui']):
                semtype = event['conceptinfo']['semantictypes'][0] if event['conceptinfo']['semantictypes'] else ''
                data = {**{
                    'event_id': f'{filename.stem}_{i}',
                    'filename': filename,
                    'docid': filename.stem,
                    'matchedtext': event['matchedtext'],
                    'conceptstring': event['conceptinfo']['conceptstring'],
                    'cui': cui,
                    'preferredname': event['conceptinfo']['preferredname'],
                    'start': event['start'],
                    'length': event['length'],
                    'end': event['start'] + event['length'],
                    'evid': event['id'],
                    'negated': el.get('negated', None),
                    'semantictype': semtype,
                    'source': event['conceptinfo']['sources'][0],
                    'all_sources': ','.join(event['conceptinfo']['sources']),
                    'all_semantictypes': ','.join(event['conceptinfo']['semantictypes']),
                }, **{
                    s: 1 for s in event['conceptinfo']['sources']
                }, **{
                    s: 1 for s in event['conceptinfo']['semantictypes']
                }}
                if extras:
                    data |= extras
                yield data
                i += 1


def iter_json_matches_from_file(json_file, *fields):
    with open(json_file) as fh:
        data = json.load(fh)
    yield from iter_json_matches(data)


def iter_json_matches(data, *fields):
    fields = fields if fields else ('matchedtext', 'start', 'end', 'length')
    for match in data:
        d = {
            'matchedtext': match['matchedtext'],
            'start': match['start'],
            'length': match['length'],
            'end': match['start'] + match['length'],
        }
        yield [d[field] for field in fields]
