from pathlib import Path

from pydantic import BaseModel


class AfepRun(BaseModel):
    note_directories: list[Path]
    mml_format: str = 'json'
    outdir: Path = None  # should be assigned by parent; to alter name, use 'name'
    expand_cuis: bool = False
    apikey: str = None
    skip_greedy_algorithm: bool = False
    min_kb: int = None  # default to ceiling(n_articles/2)
    max_kb: int = None
    data_directory: list[Path] = None
    name: str = None  # for naming output directory

    def set_outdir(self, default: Path):
        self.outdir = self.get_outdir(default)

    def get_outdir(self, default: Path):
        name = f'{self.name if self.name else self.note_directories[0].stem}' \
               f'-selected{"-cui-exp" if self.expand_cuis else ""}'
        if default is None:
            return Path('.') / name
        elif self.name:
            return default / f'{self.name}-selected{"-cui-exp" if self.expand_cuis else ""}'
        else:
            return default / f'{self.note_directories[0].stem}-selected{"-cui-exp" if self.expand_cuis else ""}'


class MultiAfepConfig(BaseModel):
    runs: list[AfepRun]
    outdir: Path = None  # general output directory
    build_summary: bool = True
    base_directory: Path = None
    note_directories: list[Path] = None
    apikey: str = None
    expand_cuis: bool = False
    min_kb: int = None
    max_kb: int = None

    def __init__(self, **kw):
        super().__init__(**kw)
        # post init
        for run in self.runs:
            run.set_outdir(self.outdir)
            if self.expand_cuis or run.expand_cuis:
                run.apikey = self.apikey
                run.expand_cuis = True
            if self.min_kb and run.min_kb is None:
                run.min_kb = self.min_kb
            if self.max_kb and run.max_kb is None:
                run.max_kb = self.max_kb
