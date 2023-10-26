import pathlib

import pytest


@pytest.fixture
def xml_file() -> pathlib.Path:
    return pathlib.Path(__file__).parent / 'fixtures' / 'wordpress.xml'
