import os
import pytest
import tomllib

from exegol_history.__main__ import setup
from pykeepass import PyKeePass
from typing import Any
from common_tui import TEST_PROFILE_SH

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


@pytest.fixture
def create_mock_profile_sh() -> None:
    with open(TEST_PROFILE_SH, "w") as profile:
        profile.write("""
#info: this file is used as buffer by the exegol-history.py utility. Exegol terminals source it to export env vars
#export INTERFACE='eth0'
#export DOMAIN='DOMAIN.LOCAL'
#export DOMAIN_SID='S-1-5-11-39129514-1145628974-103568174'
#export USER='someuser'
#export PASSWORD='somepassword'
#export NT_HASH='c1c635aa12ae60b7fe39e28456a7bac6'
#export DC_IP='192.168.56.101'
#export DC_HOST='DC01.DOMAIN.LOCAL'
#export DB_HOSTNAME='DC01.DOMAIN.LOCAL'
#export TARGET='192.168.56.69'
#export IP='192.168.56.69'
#export ATTACKER_IP='192.168.56.1'
""")
