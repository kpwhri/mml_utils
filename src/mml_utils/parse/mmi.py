import csv
import io

from loguru import logger


def extract_mml_from_mmi_data(text, filename, *, target_cuis=None, extras=None):
    """

    :param text:
    :param filename:
    :param target_cuis:
    :param extras:
    :return:
    """
    if not target_cuis:
        target_cuis = set()
    i = 0
    prev_line = None
    for line in csv.reader(io.StringIO(text), delimiter='|'):
        if not line[-1] == '':
            prev_line = line
            continue
        if prev_line:
            carryover_cell = prev_line[-1] + line[0]
            line = prev_line[:-1] + [carryover_cell] + line[1:]
            prev_line = None
        for d in extract_mmi_line(line):
            if not d or d['cui'] not in target_cuis:
                continue
            d['event_id'] = f'{filename}_{i}'
            if extras:
                d |= extras
            yield d
            i += 1


def extract_mmi_line(line):
    if line[1] != 'MMI':
        logger.warning(f'Line contains {line[1]} rather the "MMI"; skipping line: {line}')
        return
    (identifier, mmi, score, conceptstring, cui, semantictype, triggerinfo,
     location, positional_info, treecodes, *other) = line[:10]
    semantictypes = [st.strip() for st in semantictype[1:-1].split(',')]  # official doco says comma-separated
    triggerinfos = [
        list(csv.reader([element], delimiter='-'))[0]
        for row in csv.reader([triggerinfo], delimiter=',')
        for element in row
    ]
    new_triggerinfos = []
    for ti in triggerinfos:
        new_triggerinfos.append(['-'.join(ti[:len(ti) - 5])] + ti[len(ti) - 5:])
    triggerinfos = new_triggerinfos
    positional_infos = [loc.split('/') for loc in positional_info.split(';')]
    for (preferredname, loc, locpos, matchedtext, pos, negation
         ), (start, length) in zip(triggerinfos, positional_infos):
        yield {
                  'docid': identifier,
                  'matchedtext': matchedtext,
                  'conceptstring': conceptstring,
                  'cui': cui,
                  'preferredname': preferredname,
                  'start': int(start),
                  'length': int(length),
                  'evid': None,
                  'negated': int(negation),
                  'pos': pos,
                  'semantictype': semantictypes[0],  # usually (always?) just one, so show it
              } | {
                  s: 1 for s in semantictypes
              }
