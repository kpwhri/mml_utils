"""
Semantic Type information from: https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/Docs/SemanticTypes_2018AB.txt

This file was built by:
    * Copy-pasting text from above link and running two search/replace with PyCharm:
        1. Replacing `(\w{4})\|(T\d{3})\|.*` with `'$1': '$2',` and then cleaning
        2. Replacing `(\w{4})\|T\d{3}\|(.*)` with `'$1': '$2',` and then cleaning
"""

SEMTYPE_TO_TUI = {
    'aapp': 'T116', 'acab': 'T020', 'acty': 'T052', 'aggp': 'T100', 'amas': 'T087', 'amph': 'T011', 'anab': 'T190',
    'anim': 'T008', 'anst': 'T017', 'antb': 'T195', 'arch': 'T194', 'bacs': 'T123', 'bact': 'T007', 'bdsu': 'T031',
    'bdsy': 'T022', 'bhvr': 'T053', 'biof': 'T038', 'bird': 'T012', 'blor': 'T029', 'bmod': 'T091', 'bodm': 'T122',
    'bpoc': 'T023', 'bsoj': 'T030', 'celc': 'T026', 'celf': 'T043', 'cell': 'T025', 'cgab': 'T019', 'chem': 'T103',
    'chvf': 'T120', 'chvs': 'T104', 'clas': 'T185', 'clna': 'T201', 'clnd': 'T200', 'cnce': 'T077', 'comd': 'T049',
    'crbs': 'T088', 'diap': 'T060', 'dora': 'T056', 'drdd': 'T203', 'dsyn': 'T047', 'edac': 'T065', 'eehu': 'T069',
    'elii': 'T196', 'emod': 'T050', 'emst': 'T018', 'enty': 'T071', 'enzy': 'T126', 'euka': 'T204', 'evnt': 'T051',
    'famg': 'T099', 'ffas': 'T021', 'fish': 'T013', 'fndg': 'T033', 'fngs': 'T004', 'food': 'T168', 'ftcn': 'T169',
    'genf': 'T045', 'geoa': 'T083', 'gngm': 'T028', 'gora': 'T064', 'grpa': 'T102', 'grup': 'T096', 'hcpp': 'T068',
    'hcro': 'T093', 'hlca': 'T058', 'hops': 'T131', 'horm': 'T125', 'humn': 'T016', 'idcn': 'T078', 'imft': 'T129',
    'inbe': 'T055', 'inch': 'T197', 'inpo': 'T037', 'inpr': 'T170', 'irda': 'T130', 'lang': 'T171', 'lbpr': 'T059',
    'lbtr': 'T034', 'mamm': 'T015', 'mbrt': 'T063', 'mcha': 'T066', 'medd': 'T074', 'menp': 'T041', 'mnob': 'T073',
    'mobd': 'T048', 'moft': 'T044', 'mosq': 'T085', 'neop': 'T191', 'nnon': 'T114', 'npop': 'T070', 'nusq': 'T086',
    'ocac': 'T057', 'ocdi': 'T090', 'orch': 'T109', 'orga': 'T032', 'orgf': 'T040', 'orgm': 'T001', 'orgt': 'T092',
    'ortf': 'T042', 'patf': 'T046', 'phob': 'T072', 'phpr': 'T067', 'phsf': 'T039', 'phsu': 'T121', 'plnt': 'T002',
    'podg': 'T101', 'popg': 'T098', 'prog': 'T097', 'pros': 'T094', 'qlco': 'T080', 'qnco': 'T081', 'rcpt': 'T192',
    'rept': 'T014', 'resa': 'T062', 'resd': 'T075', 'rnlw': 'T089', 'sbst': 'T167', 'shro': 'T095', 'socb': 'T054',
    'sosy': 'T184', 'spco': 'T082', 'tisu': 'T024', 'tmco': 'T079', 'topp': 'T061', 'virs': 'T005', 'vita': 'T127',
    'vtbt': 'T010',
}
TUI_TO_SEMTYPE = {tui: stype for stype, tui in SEMTYPE_TO_TUI.items()}

SEMTYPE_TO_NAME = {
    'aapp': 'Amino Acid, Peptide, or Protein', 'acab': 'Acquired Abnormality', 'acty': 'Activity', 'aggp': 'Age Group',
    'amas': 'Amino Acid Sequence', 'amph': 'Amphibian', 'anab': 'Anatomical Abnormality', 'anim': 'Animal',
    'anst': 'Anatomical Structure', 'antb': 'Antibiotic', 'arch': 'Archaeon', 'bacs': 'Biologically Active Substance',
    'bact': 'Bacterium', 'bdsu': 'Body Substance', 'bdsy': 'Body System', 'bhvr': 'Behavior',
    'biof': 'Biologic Function', 'bird': 'Bird', 'blor': 'Body Location or Region',
    'bmod': 'Biomedical Occupation or Discipline', 'bodm': 'Biomedical or Dental Material',
    'bpoc': 'Body Part, Organ, or Organ Component', 'bsoj': 'Body Space or Junction', 'celc': 'Cell Component',
    'celf': 'Cell Function', 'cell': 'Cell', 'cgab': 'Congenital Abnormality', 'chem': 'Chemical',
    'chvf': 'Chemical Viewed Functionally', 'chvs': 'Chemical Viewed Structurally', 'clas': 'Classification',
    'clna': 'Clinical Attribute', 'clnd': 'Clinical Drug', 'cnce': 'Conceptual Entity',
    'comd': 'Cell or Molecular Dysfunction', 'crbs': 'Carbohydrate Sequence', 'diap': 'Diagnostic Procedure',
    'dora': 'Daily or Recreational Activity', 'drdd': 'Drug Delivery Device', 'dsyn': 'Disease or Syndrome',
    'edac': 'Educational Activity', 'eehu': 'Environmental Effect of Humans', 'elii': 'Element, Ion, or Isotope',
    'emod': 'Experimental Model of Disease', 'emst': 'Embryonic Structure', 'enty': 'Entity', 'enzy': 'Enzyme',
    'euka': 'Eukaryote', 'evnt': 'Event', 'famg': 'Family Group', 'ffas': 'Fully Formed Anatomical Structure',
    'fish': 'Fish', 'fndg': 'Finding', 'fngs': 'Fungus', 'food': 'Food', 'ftcn': 'Functional Concept',
    'genf': 'Genetic Function', 'geoa': 'Geographic Area', 'gngm': 'Gene or Genome',
    'gora': 'Governmental or Regulatory Activity', 'grpa': 'Group Attribute', 'grup': 'Group',
    'hcpp': 'Human-caused Phenomenon or Process', 'hcro': 'Health Care Related Organization',
    'hlca': 'Health Care Activity', 'hops': 'Hazardous or Poisonous Substance', 'horm': 'Hormone', 'humn': 'Human',
    'idcn': 'Idea or Concept', 'imft': 'Immunologic Factor', 'inbe': 'Individual Behavior',
    'inch': 'Inorganic Chemical', 'inpo': 'Injury or Poisoning', 'inpr': 'Intellectual Product',
    'irda': 'Indicator, Reagent, or Diagnostic Aid', 'lang': 'Language', 'lbpr': 'Laboratory Procedure',
    'lbtr': 'Laboratory or Test Result', 'mamm': 'Mammal', 'mbrt': 'Molecular Biology Research Technique',
    'mcha': 'Machine Activity', 'medd': 'Medical Device', 'menp': 'Mental Process', 'mnob': 'Manufactured Object',
    'mobd': 'Mental or Behavioral Dysfunction', 'moft': 'Molecular Function', 'mosq': 'Molecular Sequence',
    'neop': 'Neoplastic Process', 'nnon': 'Nucleic Acid, Nucleoside, or Nucleotide',
    'npop': 'Natural Phenomenon or Process', 'nusq': 'Nucleotide Sequence', 'ocac': 'Occupational Activity',
    'ocdi': 'Occupation or Discipline', 'orch': 'Organic Chemical', 'orga': 'Organism Attribute',
    'orgf': 'Organism Function', 'orgm': 'Organism', 'orgt': 'Organization', 'ortf': 'Organ or Tissue Function',
    'patf': 'Pathologic Function', 'phob': 'Physical Object', 'phpr': 'Phenomenon or Process',
    'phsf': 'Physiologic Function', 'phsu': 'Pharmacologic Substance', 'plnt': 'Plant',
    'podg': 'Patient or Disabled Group', 'popg': 'Population Group', 'prog': 'Professional or Occupational Group',
    'pros': 'Professional Society', 'qlco': 'Qualitative Concept', 'qnco': 'Quantitative Concept', 'rcpt': 'Receptor',
    'rept': 'Reptile', 'resa': 'Research Activity', 'resd': 'Research Device', 'rnlw': 'Regulation or Law',
    'sbst': 'Substance', 'shro': 'Self-help or Relief Organization', 'socb': 'Social Behavior',
    'sosy': 'Sign or Symptom', 'spco': 'Spatial Concept', 'tisu': 'Tissue', 'tmco': 'Temporal Concept',
    'topp': 'Therapeutic or Preventive Procedure', 'virs': 'Virus', 'vita': 'Vitamin', 'vtbt': 'Vertebrate', }

TUI_TO_NAME = {SEMTYPE_TO_TUI[stype]: name for stype, name in SEMTYPE_TO_NAME.items()}
