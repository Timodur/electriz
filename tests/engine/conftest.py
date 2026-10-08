import pytest

from electriz.engine import Engine


@pytest.fixture
def engine():
    return Engine()
