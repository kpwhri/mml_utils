import pathlib
import re

from loguru import logger

from mml_utils.parse.target_cuis import TargetCuis

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
                if len(segments) == 6 and textline[i + 1] == '-':  # in the middle of trigger info, ensure not in string
                    quoted = False
                elif len(segments) != 6 and textline[i + 1] in '|':
                    quoted = False
            elif not quoted:
                quoted = True
        elif letter == '|':
            if not quoted:
                segments.append(textline[segment_start:i])
                segment_start = i + 1  # starts next character
            elif i + 1 >= len(textline):  # character was just a quote
                raise ValueError(f'Unsure how to handle quotation mark in: {textline[:i]} [source:{textline}]')
            elif quoted and len(segments) == 3 and textline[i + 1] == 'C':  # handle single quote in matchedtext
                segments.append(textline[segment_start:i])
                segment_start = i + 1  # starts next character
                quoted = False
    segments.append(textline[segment_start:])
    return segments


def extract_mml_from_mmi_data(text, filename, *, target_cuis: TargetCuis=None, extras=None):
    """

    :param text:
    :param filename:
    :param target_cuis:
    :param extras:
    :return:
    """
    if not target_cuis:
        target_cuis = TargetCuis()
    i = 0
    prev_line = None
    for textline in text.split('\n'):
        if textline and not prev_line and (line := textline.split('|')[1]) not in {'MMI'}:
            if line not in {'CONJ', 'AA'}:  # known abbreviations, not problems
                logger.warning(f'Line contains {line} rather the "MMI"; skipping line: {textline}')
            continue
        line = split_mmi_line(textline)
        # if not line[-1] == '':
        #     prev_line = line
        #     continue
        if prev_line:
            carryover_cell = prev_line[-1] + line[0]
            line = prev_line[:-1] + [carryover_cell] + line[1:]
            prev_line = None
        if len(line) == 9 and line[1] == 'AA':
            continue  # AA=Acronyms and Abbreviations with only length 9 (Metamap only)
        if len(line) < 10:
            prev_line = line
            continue
        for d in extract_mmi_line(line):
            if not d:
                continue
            for cui in target_cuis.get_target_cuis(d['cui']):
                d['cui'] = cui
                filename = filename.split('.')[0]  # removee extension
                d['event_id'] = f'{filename}_{i}'
                if extras:
                    d |= extras
                yield d
                i += 1


def _parse_trigger_info(trigger_info_text):
    """Parse trigger information for mmi format"""
    trigger_info_text = trigger_info_text.strip('[]')
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
        logger.error(
            f'Unknown format of length {len(info)} for {label} ({info_string}, section {info}) in file `{file}`: {line}')
        return True
    return False


def get_start_end_length_from_pos_info_loc(loc):
    start, length = loc.strip('[]').split('/')
    start = int(start)
    length = int(length)
    end = start + length
    return start, end, length


def _parse_positional_info(positional_info_text):
    """

    :param positional_info_text:
    :return:  tuple[int, int, int] : tuple[start, end, length]
    """
    if positional_info_text.startswith('['):  # weird MM mmi output which duplicates after semicolon
        positional_info_text = positional_info_text.replace('[', '').replace(']', '').split(';')[0].replace(',', ';')
    multi_indices = {}  # comma-separated values with same reference (metamap-specific); e.g., loc of [44/9],[179/9]
    for loc in positional_info_text.split(';'):
        if ',' in loc:  # split phrase
            if loc not in multi_indices:
                multi_indices[loc] = [get_start_end_length_from_pos_info_loc(value) for value in loc.split(',')]
            yield multi_indices[loc].pop(0)
        else:
            yield get_start_end_length_from_pos_info_loc(loc)


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
    positional_infos = list(_parse_positional_info(positional_info))
    for ti, pi in zip(triggerinfos, positional_infos):
        if _has_invalid_length(ti, 6, 'trigger info', triggerinfo, file, line):
            continue
        preferredname, loc, locpos, matchedtext, pos, negation = ti
        start, end, length = pi
        yield {**{
            'docid': file.stem,
            'filename': identifier,
            'matchedtext': matchedtext,
            'conceptstring': conceptstring,
            'cui': cui,
            'preferredname': preferredname,
            'start': start,
            'length': length,
            'end': end,
            'evid': None,
            'negated': bool(int(negation)),
            'pos': pos,
            'semantictype': semantictypes[0],  # usually (always?) just one, so show it
            'all_semantictypes': ','.join(semantictypes),
            'all_sources': '',
        }, **{
            s: 1 for s in semantictypes
        }}
