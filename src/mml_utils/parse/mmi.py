import csv
import io
import pathlib
import re

from loguru import logger


TRIGGER_INFO_PAT = re.compile(
    r'(?P<concept>".*?")'
    r'-'
    r'(?P<loc>\w+)'
    r'-'
    r'(?P<locpos>\d+)'
    r'-'
    r'(?P<text>".*?")'
    r'-'
    r'(?P<pos>\w*)'
    r'-'
    r'(?P<neg>[01])'  # negation flag
)


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
    for textline in text.split('\n'):
        line = textline.split('|')
        # if not line[-1] == '':
        #     prev_line = line
        #     continue
        if prev_line:
            carryover_cell = prev_line[-1] + line[0]
            line = prev_line[:-1] + [carryover_cell] + line[1:]
            prev_line = None
        for d in extract_mmi_line(line):
            if not d or (target_cuis and d['cui'] not in target_cuis):
                continue
            filename = filename.split('.')[0]  # removee extension
            d['event_id'] = f'{filename}_{i}'
            if extras:
                d |= extras
            yield d
            i += 1


def _parse_trigger_info(trigger_info_text):
    """Parse trigger information for mmi format"""
    if not trigger_info_text.startswith('"'):
        idx = trigger_info_text.index('-')
        trigger_info_text = '"' + trigger_info_text[:idx] + '"' + trigger_info_text[idx:]
    prev_end = 0
    for m in TRIGGER_INFO_PAT.finditer(trigger_info_text):
        if m.start() > prev_end:
            logger.warning(f'Possible unparsed content: {trigger_info_text[prev_end:m.end()]} in {trigger_info_text}')
        yield [
            m.group('concept'),
            m.group('loc'),
            m.group('locpos'),
            m.group('text'),
            m.group('pos'),
            m.group('neg'),
        ]
        prev_end = m.end() + 1  # the '+1' is for the comma separating valuess


def extract_mmi_line(line):
    if line[1] != 'MMI':
        logger.warning(f'Line contains {line[1]} rather the "MMI"; skipping line: {line}')
        return
    (identifier, mmi, score, conceptstring, cui, semantictype, triggerinfo,
     location, positional_info, treecodes, *other) = line[:10]
    file = pathlib.Path(identifier)
    semantictypes = [st.strip() for st in semantictype[1:-1].split(',')]  # official doco says comma-separated
    triggerinfos = list(_parse_trigger_info(triggerinfo))
    positional_infos = [loc.split('/') for loc in positional_info.split(';')]
    for (preferredname, loc, locpos, matchedtext, pos, negation
         ), (start, length) in zip(triggerinfos, positional_infos):
        yield {**{
                  'docid': file.stem,
                  'filename': identifier,
                  'matchedtext': matchedtext,
                  'conceptstring': conceptstring,
                  'cui': cui,
                  'preferredname': preferredname,
                  'start': int(start),
                  'length': int(length),
                  'end': int(start) + int(length),
                  'evid': None,
                  'negated': int(negation),
                  'pos': pos,
                  'semantictype': semantictypes[0],  # usually (always?) just one, so show it
              }, **{
                  s: 1 for s in semantictypes
              }}
