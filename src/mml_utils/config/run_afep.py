"""
Pydantic models for configuring AFEP.
"""
from pathlib import Path

from pydantic import BaseModel


class AfepRun(BaseModel):
    note_directories: list[Path] = None
    mml_format: str = None  # default to json if not specified by MultiAfepConfig
    outdir: Path = None  # should be assigned by parent; to alter name, use 'name'
    expand_cuis: bool = False
    apikey: str = None
    skip_greedy_algorithm: bool = False
    min_kb: int = None  # default to ceiling(n_articles/2)
    max_kb: int = None
    data_directory: list[Path] = None
    name: str = None  # for naming output directory
    cui_normalisation: bool = None
    meta_path: Path = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # post init
        if not self.name:
            if self.data_directory:
                self.name = self.data_directory[0].stem
            else:
                self.name = 'afep_run'

    def set_outdir(self, default: Path):
        self.outdir = self.get_outdir(default)

    def set_meta_path(self, default: Path):
        self.meta_path = self.meta_path or default

    def set_note_directories(self, default: list[Path]):
        if not self.note_directories:
            self.note_directories = default

    def set_mml_format(self, default: str):
        if not self.mml_format:
            if default:
                self.mml_format = default
            else:  # default to json if not otherwise specified
                self.mml_format = 'json'

    def get_outdir(self, default: Path):
        name = f'{self.name if self.name else self.note_directories[0].stem}' \
               f'-selected{"-cui-exp" if self.expand_cuis else ""}'
        if default is None:
            return Path('.') / name
        elif self.name:
            return default / f'{self.name}-selected{"-cui-exp" if self.expand_cuis else ""}'
        else:
            return default / f'{self.note_directories[0].stem}-selected{"-cui-exp" if self.expand_cuis else ""}'

    def is_valid(self):
        assert self.note_directories is not None


class MultiAfepConfig(BaseModel):
    runs: list[AfepRun]
    outdir: Path = None  # general output directory
    build_summary: bool = True
    base_directory: Path = None
    note_directories: list[Path] = None
    mml_format: str = None
    apikey: str = None
    expand_cuis: bool = False
    min_kb: int = None
    max_kb: int = None
    cui_normalisation: bool = False
    meta_path: Path = None

    def __init__(self, **kw):
        super().__init__(**kw)
        # post init
        for run in self.runs:
            run.set_outdir(self.outdir)
            run.set_note_directories(self.note_directories)
            run.set_mml_format(self.mml_format)
            run.set_meta_path(self.meta_path)
            if self.expand_cuis or run.expand_cuis:
                run.apikey = self.apikey
                run.expand_cuis = True
            if self.min_kb and run.min_kb is None:
                run.min_kb = self.min_kb
            if self.max_kb and run.max_kb is None:
                run.max_kb = self.max_kb
            if self.cui_normalisation and run.cui_normalisation is None:
                run.cui_normalisation = True
            run.is_valid()
