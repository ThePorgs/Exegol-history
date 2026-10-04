import pathlib
import shutil
import pytest
import platform
from pathlib import Path

from sqlalchemy import Engine
from exegol_history.config.config import AppConfig
from exegol_history.connectors.netexec.netexec_sync import NetexecSyncer
from exegol_history.db_api.creds import Credential
from exegol_history.db_api.hosts import Host
from exegol_history.tests.common import (
    DOMAIN_TEST_VALUE,
    HASH_TEST_VALUE,
    HOSTNAME_TEST_VALUE,
    IP_TEST_VALUE,
    PASSWORD_TEST_VALUE,
    ROLE_TEST_VALUE,
    USERNAME_TEST_VALUE,
)

TEST_DB_NAME = "test.sqlite3"

TEST_ARTIFACTS_PATH = Path("exegol_history") / "tests" / "artifacts"
TEST_DB_PATH = TEST_ARTIFACTS_PATH / TEST_DB_NAME
TEST_NETEXEC_PATH = TEST_ARTIFACTS_PATH / "netexec_artifacts"
TEST_CONFIG_PATH = TEST_ARTIFACTS_PATH / AppConfig.CONFIG_FILENAME
TEST_PROFILE_SH = TEST_ARTIFACTS_PATH / "profile.sh"
TEST_PROFILE_PS1 = TEST_ARTIFACTS_PATH / "profile.ps1"
TEST_KERBEROS_PATH = TEST_ARTIFACTS_PATH / "kerberos_artifacts"


@pytest.fixture
def engine() -> Engine:
    # First create a test DB
    return AppConfig.setup_db(TEST_DB_PATH)


@pytest.fixture
def load_mock_config() -> AppConfig:
    mock_config = AppConfig(TEST_CONFIG_PATH)

    if platform.system() == "Windows":
        mock_config.paths.profile_sh_path = TEST_PROFILE_PS1
    else:
        mock_config.paths.profile_sh_path = TEST_PROFILE_SH

    for connector in mock_config.sync:
        connector.enabled = False

        if connector.CONNECTOR_NAME == NetexecSyncer.CONNECTOR_NAME:
            connector.workspace_path = TEST_NETEXEC_PATH

    # Point the Kerberos scanner at the test artifacts instead of the Exegol
    # default paths (/workspace, /root) which don't exist during tests.
    mock_config.kerberos.search_paths = [str(TEST_KERBEROS_PATH)]
    mock_config.kerberos.search_depth = 3

    return mock_config


@pytest.fixture(scope="function", autouse=True)
def clean():
    default_profile_path_unix = (Path(__file__).parent.parent.parent) / "profile.sh"
    default_profile_path_windows = (Path(__file__).parent.parent.parent) / "profile.ps1"
    pathlib.Path.unlink(TEST_PROFILE_SH, missing_ok=True)
    pathlib.Path.unlink(TEST_PROFILE_PS1, missing_ok=True)
    pathlib.Path.unlink(TEST_CONFIG_PATH, missing_ok=True)
    pathlib.Path.unlink(TEST_DB_PATH, missing_ok=True)
    shutil.copy(default_profile_path_unix, TEST_PROFILE_SH)
    shutil.copy(default_profile_path_windows, TEST_PROFILE_PS1)


@pytest.fixture(scope="function")
def TEST_CREDENTIAL2() -> list[Credential]:
    return [
        Credential(1, username=USERNAME_TEST_VALUE, hash=HASH_TEST_VALUE),
        Credential(
            2,
            username=USERNAME_TEST_VALUE + "2",
            password=PASSWORD_TEST_VALUE,
            hash=HASH_TEST_VALUE,
            domain=DOMAIN_TEST_VALUE,
        ),
    ]


@pytest.fixture(scope="function")
def CREDENTIALS_TEST_VALUE_GOAD_SECRETSDUMP() -> list[Credential]:
    return [
        Credential(
            1, username="Administrator", hash="2d6144ce972270349b4be753b4f7368e"
        ),
        Credential(2, username="Guest", hash="31d6cfe0d16ae931b73c59d7e0c089c0"),
        Credential(3, username="krbtgt", hash="d64dc530aa7cd2883f8c705b6e968e00"),
        Credential(4, username="localuser", hash="8846f7eaee8fb117ad06bdd830b7586c"),
        Credential(5, username="alice", hash="8d97808fb46e01433322bd704ec9e160"),
        Credential(6, username="bob", hash="d8d34b3cff03786fbe1d80b2c8c09d9e"),
        Credential(7, username="carol", hash="0deff2a0603d8c08dbc5cf5bb17965a7"),
        Credential(8, username="dave", hash="f7eb9c06fafaa23c4bcf22ba6781c1e2"),
        Credential(9, username="eve", hash="b963c57010f218edc2cc3c229b5e4d0f"),
        Credential(10, username="franck", hash="c4d15867c66cc7c09bbef86c2166e0d7"),
        Credential(
            11, username="sccm-client-push", hash="72f5cfa80f07819ccbcfb72feb9eb9b7"
        ),
        Credential(
            12, username="sccm-account-da", hash="a36708091f53bd872528841b744b4a82"
        ),
        Credential(13, username="sccm-naa", hash="c22b315c040ae6e0efee3518d830362b"),
        Credential(14, username="sccm-sql", hash="3fbc46823c86acd0b25f24e164e9397c"),
        Credential(15, username="DC$", hash="0b65cc18dde1c5548f06b8db074a76b3"),
        Credential(16, username="MECM$", hash="252633c7d64b63b0578d11fb79bedfa5"),
        Credential(17, username="MSSQL$", hash="16727c64fb06edb9ead3c06ab9a8b25b"),
        Credential(18, username="CLIENT$", hash="4f242e2b3279eeb5cdb7a19fdab2f038"),
    ]


@pytest.fixture(scope="function")
def TEST_HOST2() -> list[Host]:
    return [
        Host(1, ip=IP_TEST_VALUE, role=ROLE_TEST_VALUE),
        Host(
            2,
            ip=IP_TEST_VALUE + "2",
            hostname=HOSTNAME_TEST_VALUE,
            role=ROLE_TEST_VALUE,
        ),
    ]


@pytest.fixture(scope="function")
def HOSTS_TEST_VALUE() -> list[Host]:
    return [
        Host(1, IP_TEST_VALUE, HOSTNAME_TEST_VALUE, ROLE_TEST_VALUE),
        Host(2, IP_TEST_VALUE + "2"),
        Host(3, IP_TEST_VALUE + "2", HOSTNAME_TEST_VALUE + "2"),
        Host(4, IP_TEST_VALUE + "3"),
    ]
