"""
Extract MML format for cTAKES output data.

cTAKES output data is supplied in 'xmi' files which follow an XML format.
"""
import pathlib
from collections import defaultdict
from xml.etree import ElementTree


def build_index_references(root):
    # collect offsets
    prev_index = 1  # cTAKES is 1-based indexing
    terms = []
    postags = {}
    for child in root:
        if 'syntax.ecore}ConllDependencyNode' in child.tag and child.get('id') != '0':
            postag = child.get('postag')
            start_idx = int(child.get('begin')) - 1  # 1-based indexing
            end_idx = int(child.get('end')) - 1  # 1-based indexing
            postags[start_idx] = postag
            terms.append(' ' * (start_idx - prev_index))
            terms.append(child.get('form'))
            prev_index = end_idx
    text = ''.join(terms)
    return text, postags


def extract_mml_from_xmi_data(text, filename, *, target_cuis=None, extras=None):
    if not target_cuis:
        target_cuis = set()
    tree = ElementTree.ElementTree(ElementTree.fromstring(text))
    root = tree.getroot()
    # build text not to get 'matchedtext' equivalent
    text, postags = build_index_references(root)
    # extract info
    file = pathlib.Path(filename)
    stem = file.stem.replace('.txt', '')
    results = defaultdict(dict)
    for child in root:
        if 'textsem.ecore' in child.tag:
            if 'ontologyConceptArr' in child.keys():
                polarity = int(child.get('polarity'))
                start_idx = int(child.get('begin')) - 1
                end_idx = int(child.get('end')) - 1
                confidence = float(child.get('confidence'))
                uncertainty = float(child.get('uncertainty'))
                conditional = bool(child.get('conditional'))
                generic = bool(child.get('generic'))
                subject = child.get('subject')

                for concept in child.get("ontologyConceptArr").split():
                    concept_id = int(concept)
                    results[concept_id].update({
                        'event_id': f'{stem}_{concept_id}',
                        'docid': stem,
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
        elif 'refsem.ecore' in child.tag:
            currid = int(child.get(r'{http://www.omg.org/XMI}id'))
            results[currid].update({
                'source': child.get('codingScheme', None),
                'cui': child.get('cui', None),
                'conceptstring': child.get('preferredText', None),
                'preferredname': child.get('preferredText', None),  # not sure which this represents?
                'tui': child.get('tui', None),
                'score': float(child.get('score')),
                'code': child.get('code', None),
            })
    yield from (result for result in results.values() if result['cui'] in target_cuis)
