import pathlib
import shutil
import pytest
import platform
from pykeepass import PyKeePass
from typing import Any
from pathlib import Path
from exegol_history.config.config import AppConfig

TEST_DB_NAME = "test.kdbx"
TEST_KEY_NAME = "test.key"

TEST_ARTIFACTS_PATH = Path("exegol_history") / "tests" / "artifacts"
TEST_DB_PATH = TEST_ARTIFACTS_PATH / TEST_DB_NAME
TEST_KEY_PATH = TEST_ARTIFACTS_PATH / TEST_KEY_NAME
TEST_CONFIG_PATH = TEST_ARTIFACTS_PATH / AppConfig.CONFIG_FILENAME
TEST_PROFILE_SH = TEST_ARTIFACTS_PATH / "profile.sh"
TEST_PROFILE_PS1 = TEST_ARTIFACTS_PATH / "profile.ps1"


@pytest.fixture
def open_keepass() -> PyKeePass:
    # First create a test Keepass DB and key
    AppConfig.setup_db(TEST_DB_PATH, TEST_KEY_PATH)

    # Then open it and return the Pykeepass object
    return PyKeePass(TEST_DB_PATH, keyfile=TEST_KEY_PATH)


@pytest.fixture
def load_mock_config() -> dict[str, Any]:
    mock_config = AppConfig.load_config(TEST_CONFIG_PATH)

    if platform.system() == "Windows":
        mock_config["paths"]["profile_sh_path"] = TEST_PROFILE_PS1
    else:
        mock_config["paths"]["profile_sh_path"] = TEST_PROFILE_SH

    return mock_config


@pytest.fixture(scope="function", autouse=True)
def clean():
    default_profile_path_unix = (Path(__file__).parent.parent.parent) / "profile.sh"
    default_profile_path_windows = (Path(__file__).parent.parent.parent) / "profile.ps1"
    pathlib.Path.unlink(TEST_PROFILE_SH, missing_ok=True)
    pathlib.Path.unlink(TEST_PROFILE_PS1, missing_ok=True)
    pathlib.Path.unlink(TEST_CONFIG_PATH, missing_ok=True)
    pathlib.Path.unlink(TEST_DB_PATH, missing_ok=True)
    pathlib.Path.unlink(TEST_KEY_PATH, missing_ok=True)
    shutil.copy(default_profile_path_unix, TEST_PROFILE_SH)
    shutil.copy(default_profile_path_windows, TEST_PROFILE_PS1)
