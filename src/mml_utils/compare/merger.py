import csv
from pathlib import Path
import functools

from mml_utils.review.extract_data import find_target_text


@functools.total_ordering
class DataComparator:
    """Aids in comparison of output of different feature extraction methods."""

    def __init__(self, path: Path, name=None, text_encoding='latin1'):
        notes_path = sorted(path.glob('notes_*.csv'))[-1]
        mml_path = sorted(path.glob('mml_*.csv'))[-1]
        self.text_encoding = text_encoding
        self.name = name or path.stem
        self.data = self._read_csv(mml_path)
        self.file_dict = self._read_to_filedict(notes_path)
        self.curr_idx = 0

    @property
    def current(self):
        return self.data[self.curr_idx]

    @property
    def start(self):
        return self.current[1]

    @property
    def end(self):
        return self.current[3]

    @property
    def docid(self):
        return self.current[0]

    @property
    def cui(self):
        return self.current[4]

    @property
    def concept(self):
        return self.current[5]

    @property
    def matched(self):
        return self.current[6]

    def next(self):
        self.curr_idx += 1

    def next_after(self, endpos):
        docid = self.docid
        while self.not_empty() and self.docid == docid and self.start < endpos:
            self.next()

    def _read_to_filedict(self, path: Path):
        d = {}
        with open(path, encoding=self.text_encoding) as fh:
            for row in csv.DictReader(fh):
                d[row['filename']] = row['docid']
        return d

    def _read_csv(self, path: Path):
        data = set()
        with open(path, encoding=self.text_encoding) as fh:
            for row in csv.DictReader(fh):
                data.add((row['docid'], int(row['start']), int(row['length']),
                          int(row['start']) + int(row['length']), row['cui'],
                          row['preferredname'], row['matchedtext']))
        return sorted(data)

    def get_context(self, encoding='latin1', width=20):
        with open(self.file_dict[self.docid], encoding=encoding or self.text_encoding) as fh:
            text = fh.read()
        text = text.replace('\n', '\r\n')
        try:
            start, end = find_target_text(text, self.matched, self.start, self.end)
        except:
            start, end = None, None
        if start is None:
            return self.matched
        return text[max(start - width, 0): end + width]

    def describe(self, encoding=None, width=20):
        if width <= 0:
            return self.docid, self.start, self.end, self.cui, self.concept, self.matched, self.matched
        else:
            return (self.docid, self.start, self.end, self.cui, self.concept, self.matched,
                    self.get_context(encoding=encoding, width=width))

    def overlaps(self, other):
        if self.docid != other.docid:
            return False
        elif self.start < other.end <= self.end:
            return True
        elif self.start <= other.start < self.end:
            return True
        return False

    def not_empty(self):
        return len(self.data) > self.curr_idx

    def is_empty(self):
        return not self.not_empty()

    def __bool__(self):
        return self.not_empty()

    def __eq__(self, other):
        return self.overlaps(other)

    def __gt__(self, other):
        if self.docid != other.docid:
            return self.docid > other.docid
        if self.overlaps(other):
            return False
        return self.start > other.start

    @classmethod
    def next_after_both(cls, dm1, dm2):
        """Apply `next_after` method to both elements"""
        end1 = dm1.end
        end2 = dm2.end
        dm1.next_after(end2)
        dm2.next_after(end1)
