def extract_mml_from_json_data(data, filename, *, target_cuis=None, extras=None):
    """

    :param data:
    :param filename:
    :param target_cuis:
    :param extras:
    :return:
    """
    i = 0
    for el in data:
        for event in el['evlist']:
            if target_cuis is None or event['conceptinfo']['cui'] in target_cuis:
                data = {
                           'event_id': f'{filename}_{i}',
                           'docid': filename,
                           'matchedtext': event['matchedtext'],
                           'conceptstring': event['conceptinfo']['conceptstring'],
                           'cui': event['conceptinfo']['cui'],
                           'preferredname': event['conceptinfo']['preferredname'],
                           'start': event['start'],
                           'length': event['length'],
                           'evid': event['id'],
                           'negated': el.get('negated', None),
                           'semantictype': event['conceptinfo']['semantictypes'][0],
                           'source': event['conceptinfo']['sources'][0],
                           'all_sources': ','.join(event['conceptinfo']['sources']),
                           'all_semantictypes': ','.join(event['conceptinfo']['semantictypes']),
                       } | {
                           s: 1 for s in event['conceptinfo']['sources']
                       } | {
                           s: 1 for s in event['conceptinfo']['semantictypes']
                       }
                if extras:
                    data |= extras
                yield data
                i += 1
