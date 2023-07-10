"""
Extract MML format for cTAKES output data.

cTAKES output data is supplied in 'xmi' files which follow an XML format.
"""
import pathlib
from collections import defaultdict
from xml.etree import ElementTree

from mml_utils.umls.semantictype import TUI_TO_SEMTYPE


def build_index_references(root):
    # collect offsets
    prev_index = 1  # cTAKES is 1-based indexing
    terms = []
    postags = {}
    for child in root:
        if 'syntax.ecore}ConllDependencyNode' in child.tag and child.get('id') != '0':
            postag = child.get('postag')
            start_idx = int(child.get('begin'))
            end_idx = int(child.get('end'))
            postags[start_idx] = postag
            terms.append(' ' * (start_idx - prev_index))
            terms.append(child.get('form'))
            prev_index = end_idx
    text = ''.join(terms)
    return text, postags


def extract_mml_from_xmi_data(text, filename, *, target_cuis=None, extras=None):
    if not target_cuis:
        target_cuis = {}
    tree = ElementTree.ElementTree(ElementTree.fromstring(text))
    root = tree.getroot()
    # build text not to get 'matchedtext' equivalent
    text, postags = build_index_references(root)
    # extract info
    file = pathlib.Path(filename)
    stem = file.stem.replace('.txt', '')
    # results are stored, prefixed by any extras
    if extras is None:
        extras = {}
    results = defaultdict(lambda: extras.copy())
    i = 0
    for child in root:
        if 'textsem.ecore' in child.tag:
            if 'ontologyConceptArr' in child.keys():
                polarity = int(child.get('polarity'))
                start_idx = int(child.get('begin'))
                end_idx = int(child.get('end'))
                confidence = float(child.get('confidence'))
                uncertainty = float(child.get('uncertainty'))
                conditional = bool(child.get('conditional'))
                generic = bool(child.get('generic'))
                subject = child.get('subject')

                for concept in child.get('ontologyConceptArr').split():
                    concept_id = int(concept)
                    results[concept_id].update({
                        'event_id': f'{stem}_{concept_id}_{i}',
                        'docid': stem,
                        'filename': file.name,
                        'start': start_idx,
                        'end': end_idx,
                        'length': end_idx - start_idx,
                        'negated': polarity <= 0,
                        'confidence': confidence,
                        'uncertainty': uncertainty,
                        'conditional': conditional,
                        'generic': generic,
                        'subject': subject,
                        'matchedtext': text[start_idx: end_idx],
                        'evid': None,
                        'pos': postags[start_idx],
                    })
                    i += 1
        elif 'refsem.ecore' in child.tag:
            currid = int(child.get(r'{http://www.omg.org/XMI}id'))
            tui = child.get('tui', None)
            semtype = TUI_TO_SEMTYPE.get(tui, None)
            source = child.get('codingScheme', None)
            # check if already present (i.e., multiple sources) -> not sure if this ever happens
            if currid in results and 'source' in results[currid]:
                results[currid]['all_sources'].append(source)
                results[currid]['all_semantictypes'].append(semtype)
                results[currid][semtype] = 1
                results[currid][source] = 1
            else:
                cui = child.get('cui', None)
                results[currid].update({
                    'source': source,
                    'cui': target_cuis[cui] if target_cuis else cui,
                    'conceptstring': child.get('preferredText', None),
                    'preferredname': child.get('preferredText', None),  # not sure which this represents?
                    'tui': tui,
                    'semantictype': semtype,
                    'score': float(child.get('score')),
                    'code': child.get('code', None),
                    'all_sources': [source],
                    'all_semantictypes': [semtype],
                    semtype: 1,
                })
    for currid in results:
        results[currid]['all_sources'] = ','.join(results[currid]['all_sources'])
        results[currid]['all_semantictypes'] = ','.join(results[currid]['all_semantictypes'])
    yield from (result for result in results.values() if not target_cuis or result['cui'] in target_cuis)
