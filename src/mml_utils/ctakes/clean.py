import re
import sys

from pathlib import Path


def build_non_xml_regex():
    illegal_chars = [(0x00, 0x08), (0x0B, 0x0C), (0x0E, 0x1F),
                       (0x7F, 0x84), (0x86, 0x9F),
                       (0xFDD0, 0xFDDF), (0xFFFE, 0xFFFF)]
    if sys.maxunicode >= 0x10000:  # not narrow build
        illegal_chars.extend([(0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF),
                                (0x3FFFE, 0x3FFFF), (0x4FFFE, 0x4FFFF),
                                (0x5FFFE, 0x5FFFF), (0x6FFFE, 0x6FFFF),
                                (0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF),
                                (0x9FFFE, 0x9FFFF), (0xAFFFE, 0xAFFFF),
                                (0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF),
                                (0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF),
                                (0xFFFFE, 0xFFFFF), (0x10FFFE, 0x10FFFF)])

    illegal_ranges = [fr'{chr(low)}-{chr(high)}' for (low, high) in illegal_chars]
    return re.compile('[' + ''.join(illegal_ranges) + ']')


def clean_non_xml(directory: Path, encoding='utf8'):
    pat = build_non_xml_regex()
    for file in directory.iterdir():
        with open(file, encoding=encoding) as fh:
            text = fh.read()
        new_text = pat.sub(' ', text)
        if new_text != text:
            with open(file, 'w', encoding='utf8') as out:
                out.write(new_text)
