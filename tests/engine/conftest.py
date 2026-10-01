import pytest

from src.engine import Engine


@pytest.fixture
def engine():
    return Engine()
