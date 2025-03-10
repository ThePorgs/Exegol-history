import os
import pytest
import tomllib

from exegol_history.__main__ import setup
from pykeepass import PyKeePass
from typing import Any

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


@pytest.fixture
def load_mock_config() -> dict[str, Any]:
    mock_config = """
    [paths]
    db_name = "DB.kdbx"
    db_key_name = "db.key"
    
    [keybindings]
    copy_username_clipboard = "f1"
    copy_password_clipboard = "f2"
    copy_hash_clipboard = "f3"
    add_credential = "f4"
    delete_credential = "f5"
    edit_credential = "f6"
    copy_ip_clipboard = "f1"
    copy_hostname_clipboard = "f2"
    add_host = "f3"
    delete_host = "f4"
    edit_host = "f5"
    quit = "ctrl+c"
    """

    return tomllib.loads(mock_config)
