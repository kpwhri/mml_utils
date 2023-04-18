from mml_utils.parse.mmi import extract_mml_from_mmi_data


def test_parse_metamap_mmi(anaphylaxis_dir):
    expected = [{'docid': 'wikipedia', 'filename': 'wikipedia.txt', 'matchedtext': 'Anaphylaxis',
                 'conceptstring': 'Anaphylactic shock', 'cui': 'C4316895', 'preferredname': '["Anaphylactic shock',
                 'start': 0, 'length': 11, 'end': 11, 'evid': None, 'negated': False, 'pos': 'noun',
                 'semantictype': 'patf', 'patf': 1, 'event_id': 'anaphylaxis_0'},
                {'docid': 'wikipedia', 'filename': 'wikipedia.txt', 'matchedtext': 'Anaphylaxis',
                 'conceptstring': 'anaphylaxis', 'cui': 'C0002792', 'preferredname': '["Anaphylaxis', 'start': 0,
                 'length': 11, 'end': 11, 'evid': None, 'negated': False, 'pos': 'noun', 'semantictype': 'patf',
                 'patf': 1, 'event_id': 'anaphylaxis_1'},
                {'docid': 'wikipedia', 'filename': 'wikipedia.txt', 'matchedtext': 'Anaphylactoid reaction',
                 'conceptstring': 'Anaphylactic shock', 'cui': 'C4316895', 'preferredname': '["Anaphylactic shock',
                 'start': 459, 'length': 22, 'end': 481, 'evid': None, 'negated': False, 'pos': 'noun',
                 'semantictype': 'patf', 'patf': 1, 'event_id': 'anaphylaxis_2'},
                {'docid': 'wikipedia', 'filename': 'wikipedia.txt', 'matchedtext': 'Anaphylaxis',
                 'conceptstring': 'Anaphylactic shock', 'cui': 'C4316895', 'preferredname': 'Anaphylactic shock',
                 'start': 769, 'length': 11, 'end': 780, 'evid': None, 'negated': False, 'pos': 'noun',
                 'semantictype': 'patf', 'patf': 1, 'event_id': 'anaphylaxis_3'},
                {'docid': 'wikipedia', 'filename': 'wikipedia.txt', 'matchedtext': 'anaphylactic shock',
                 'conceptstring': 'Anaphylactic shock', 'cui': 'C4316895', 'preferredname': 'Anaphylactic shock',
                 'start': 483, 'length': 18, 'end': 501, 'evid': None, 'negated': False, 'pos': 'noun',
                 'semantictype': 'patf', 'patf': 1, 'event_id': 'anaphylaxis_4'},
                {'docid': 'wikipedia', 'filename': 'wikipedia.txt', 'matchedtext': 'anaphylaxis',
                 'conceptstring': 'Anaphylactic shock', 'cui': 'C4316895', 'preferredname': 'Anaphylactic shock',
                 'start': 512, 'length': 11, 'end': 523, 'evid': None, 'negated': False, 'pos': 'noun',
                 'semantictype': 'patf', 'patf': 1, 'event_id': 'anaphylaxis_5'},
                {'docid': 'wikipedia', 'filename': 'wikipedia.txt', 'matchedtext': 'Anaphylaxis',
                 'conceptstring': 'Anaphylactic shock', 'cui': 'C4316895', 'preferredname': 'Anaphylactic shock',
                 'start': 131, 'length': 11, 'end': 142, 'evid': None, 'negated': False, 'pos': 'noun',
                 'semantictype': 'patf', 'patf': 1, 'event_id': 'anaphylaxis_6'},
                {'docid': 'wikipedia', 'filename': 'wikipedia.txt', 'matchedtext': 'Anaphylaxis',
                 'conceptstring': 'anaphylaxis', 'cui': 'C0002792', 'preferredname': '["Anaphylaxis', 'start': 769,
                 'length': 11, 'end': 780, 'evid': None, 'negated': False, 'pos': 'noun', 'semantictype': 'patf',
                 'patf': 1, 'event_id': 'anaphylaxis_7'},
                {'docid': 'wikipedia', 'filename': 'wikipedia.txt', 'matchedtext': 'anaphylactic shock',
                 'conceptstring': 'anaphylaxis', 'cui': 'C0002792', 'preferredname': 'Anaphylaxis', 'start': 483,
                 'length': 18, 'end': 501, 'evid': None, 'negated': False, 'pos': 'noun', 'semantictype': 'patf',
                 'patf': 1, 'event_id': 'anaphylaxis_8'},
                {'docid': 'wikipedia', 'filename': 'wikipedia.txt', 'matchedtext': 'anaphylaxis',
                 'conceptstring': 'anaphylaxis', 'cui': 'C0002792', 'preferredname': 'Anaphylaxis', 'start': 512,
                 'length': 11, 'end': 523, 'evid': None, 'negated': False, 'pos': 'noun', 'semantictype': 'patf',
                 'patf': 1, 'event_id': 'anaphylaxis_9'},
                {'docid': 'wikipedia', 'filename': 'wikipedia.txt', 'matchedtext': 'Anaphylaxis',
                 'conceptstring': 'anaphylaxis', 'cui': 'C0002792', 'preferredname': 'Anaphylaxis', 'start': 131,
                 'length': 11, 'end': 142, 'evid': None, 'negated': False, 'pos': 'noun', 'semantictype': 'patf',
                 'patf': 1, 'event_id': 'anaphylaxis_10'},
                {'docid': 'wikipedia', 'filename': 'wikipedia.txt', 'matchedtext': 'Allergic reaction',
                 'conceptstring': 'Allergic Reaction', 'cui': 'C1527304', 'preferredname': '["Allergic reaction NOS',
                 'start': 629, 'length': 17, 'end': 646, 'evid': None, 'negated': False, 'pos': 'noun',
                 'semantictype': 'patf', 'patf': 1, 'event_id': 'anaphylaxis_11'},
                {'docid': 'wikipedia', 'filename': 'wikipedia.txt', 'matchedtext': 'Allergy',
                 'conceptstring': 'Allergic Reaction', 'cui': 'C1527304', 'preferredname': 'Allergic reaction NOS',
                 'start': 285, 'length': 7, 'end': 292, 'evid': None, 'negated': False, 'pos': 'noun',
                 'semantictype': 'patf', 'patf': 1, 'event_id': 'anaphylaxis_12'},
                {'docid': 'wikipedia', 'filename': 'wikipedia.txt', 'matchedtext': 'allergic reaction',
                 'conceptstring': 'Allergic Reaction', 'cui': 'C1527304', 'preferredname': 'Allergic reaction NOS',
                 'start': 813, 'length': 17, 'end': 830, 'evid': None, 'negated': False, 'pos': 'noun',
                 'semantictype': 'patf', 'patf': 1, 'event_id': 'anaphylaxis_13'}]
    fn = 'anaphylaxis.mmi'
    with open(anaphylaxis_dir / fn) as fh:
        text = fh.read()
    data = list(extract_mml_from_mmi_data(text, fn))
    assert len(data) == len(expected)
    for d, exp in zip(data, expected):
        assert d == exp
