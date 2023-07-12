from collections import defaultdict


class TargetCuis:

    def __init__(self):
        self.data = defaultdict(set)

    def __contains__(self, item):
        if not self.data:
            return True
        return item in self.data

    def get_target_cuis(self, item):
        if self.data:
            yield from self.data[item]
        elif item is None:
            return
        else:  # no target cuis specified
            yield item

    def add(self, src, target=None):
        self.data[src].add(target or src)

    def n_keys(self):
        return len(self.data.keys())

    def n_values(self):
        return len(set().union(*self.data.values()))

    def __len__(self):
        return self.n_values()

    @classmethod
    def fromdict(cls, d: dict):
        tc = cls()
        for k, v in d.items():
            tc.add(k, v if isinstance(v, str) and v.startswith('C') else k)
        return tc
