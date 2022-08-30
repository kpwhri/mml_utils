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
    r'(?P<neg>[01])',  # negation flag
    re.DOTALL  # handle newline inside term
)


def split_mmi_line(textline):
    segment_start = 0
    segments = []
    quoted = False
    for i, letter in enumerate(textline):
        if letter == '"':
            if quoted and i + 1 < len(textline):
                if len(segments) == 6 and textline[i+1] == '-':  # in the middle of trigger info, ensure not in string
                    quoted = False
                elif len(segments) != 6 and textline[i+1] in '|':
                    quoted = False
            elif not quoted:
                quoted = True
        elif letter == '|':
            if not quoted:
                segments.append(textline[segment_start:i])
                segment_start = i + 1  # starts next character
    segments.append(textline[segment_start:])
    return segments


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
        line = split_mmi_line(textline)
        # if not line[-1] == '':
        #     prev_line = line
        #     continue
        if prev_line:
            carryover_cell = prev_line[-1] + line[0]
            line = prev_line[:-1] + [carryover_cell] + line[1:]
            prev_line = None
        if len(line) < 10:
            prev_line = line
            continue
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
    if not trigger_info_text.startswith('"'):  # backwards compatibility with CSV parser which stripped quotes
        idx = trigger_info_text.index('-')
        i = 0
        while trigger_info_text[idx + 1:idx + 4] not in {'tex', 'ti-', 'ab-', 'tx-'} and i < 4:
            idx = trigger_info_text.index('-', idx + 1)
            i += 1
        trigger_info_text = '"' + trigger_info_text[:idx] + '"' + trigger_info_text[idx:]
    prev_end = 0
    for m in TRIGGER_INFO_PAT.finditer(trigger_info_text):
        if m.start() > prev_end:
            logger.warning(f'Possible unparsed content: {trigger_info_text[prev_end:m.end()]} in {trigger_info_text}')
        yield [
            m.group('concept').strip('"'),
            m.group('loc'),
            m.group('locpos'),
            m.group('text').strip('"'),
            m.group('pos'),
            m.group('neg'),
        ]
        prev_end = m.end() + 1  # the '+1' is for the comma separating valuess


def _has_invalid_length(info, exp_length, label, info_string, file, line):
    if len(info) != exp_length:
        logger.error(f'Unknown format of length {len(info)} for {label} ({info_string}, section {info}) in file `{file}`: {line}')
        return True
    return False


def extract_mmi_line(line):
    if not line or len(line) == 1:
        return
    if line[1] != 'MMI':
        logger.warning(f'Line contains {line[1]} rather the "MMI"; skipping line: {line}')
        return
    (identifier, mmi, score, conceptstring, cui, semantictype, triggerinfo,
     location, positional_info, treecodes, *other) = line[:10]
    file = pathlib.Path(identifier)
    semantictypes = [st.strip() for st in semantictype[1:-1].split(',')]  # official doco says comma-separated
    triggerinfos = list(_parse_trigger_info(triggerinfo))
    positional_infos = [loc.split('/') for loc in positional_info.split(';')]
    for ti, pi in zip(triggerinfos, positional_infos):
        if _has_invalid_length(ti, 6, 'trigger info', triggerinfo, file, line):
            continue
        if _has_invalid_length(pi, 2, 'positional info', positional_info, file, line):
            continue
        preferredname, loc, locpos, matchedtext, pos, negation = ti
        start, length = pi
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
            'negated': bool(int(negation)),
            'pos': pos,
            'semantictype': semantictypes[0],  # usually (always?) just one, so show it
        }, **{
            s: 1 for s in semantictypes
        }}
