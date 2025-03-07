import os
import pytest

from exegol_history.__main__ import setup
from pykeepass import PyKeePass

TEST_DB_NAME = "test.kdbx"
TEST_KEY_NAME = "test.key"
TEST_ARTIFACTS_PATH = os.path.join("exegol_history", "tests", "artifacts")

TEST_DB_PATH = os.path.join(TEST_ARTIFACTS_PATH, TEST_DB_NAME)
TEST_KEY_PATH = os.path.join(TEST_ARTIFACTS_PATH, TEST_KEY_NAME)


@pytest.fixture
def open_keepass() -> PyKeePass:
    # First create a test Keepass DB and key
    setup(TEST_DB_PATH, TEST_KEY_PATH)

    # Then open it and return the Pykeepass object
    return PyKeePass(TEST_DB_PATH, keyfile=TEST_KEY_PATH)
