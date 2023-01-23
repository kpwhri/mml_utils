import re
from loguru import logger

try:
    from umls_api_tool.auth import FriendlyAuthenticator

    UMLS_API_TOOL_INSTALLED = True
except ImportError:
    logger.warning(f'UMLS API Tool not installed. CUI expansion not available.')
    logger.info(f'Install umls_api_tool by running `pip install git+https://github.com/dcronkite/umls_api_tool.git`')
    UMLS_API_TOOL_INSTALLED = False


def add_shorter_match_cuis(results, apikey):
    if UMLS_API_TOOL_INSTALLED:
        logger.info(f'Trying to expand CUIs...')
        auth = FriendlyAuthenticator.from_apikey(apikey)
        known_cuis = {}  # cui -> new terms
        new_results = []
        new_cui_count = 0
        for row in results:
            target_cui = row['cui']
            if target_cui not in known_cuis:
                target_name = row['preferredname']
                curr_results = []
                if re.search(r'\b(?:or|and)\b', target_name, re.I):
                    for term in re.split(r'\W+', target_name):
                        if term.lower() in {'and', 'or', ''}:
                            continue
                        for cui_data in auth.search(term, language='ENG', limit_pages=1):
                            if cui_data['name'].lower() == term.lower():
                                curr_results.append({
                                    'cui': cui_data['cui'],
                                    'matchedtext': cui_data['name'],
                                    'length': len(cui_data['name']),
                                    'offset': target_name.index(term)
                                })
                                new_cui_count += 1
                                break  # go to next word
                known_cuis[target_cui] = curr_results
            for res in known_cuis[target_cui]:
                # update cui, matchedtext, start, and length
                new_results.append(row | res | {'start': row['start'] + res['offset']})
        logger.info(f'Added {new_cui_count} new CUIs from CUI expansion.')
        logger.info(f'{len(new_results)} new results added by CUI expansion.')
        results += new_results
    return results
