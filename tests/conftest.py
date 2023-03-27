import files
from pathlib import Path

import pytest
from loguru import logger
from _pytest.logging import LogCaptureFixture


@pytest.fixture
def caplog(caplog: LogCaptureFixture):
    handler_id = logger.add(caplog.handler, format="{message}")
    yield caplog
    logger.remove(handler_id)


@pytest.fixture
def fever_dir():
    return Path('fever')


@pytest.fixture
def short_fever_file():
    return Path('short_fever') / 'fever.txt'


@pytest.fixture
def file0_path():
    return Path('files/file0.json')


@pytest.fixture
def file0(file0_path):
    with open(file0_path) as fh:
        return files.load(fh)
