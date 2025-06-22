# import os
import secrets
import shutil
import tomllib
from typing import Any
from pathlib import Path
from pykeepass import PyKeePass, create_database
from exegol_history.db_api.creds import Credential
from exegol_history.db_api.hosts import Host

EXEGOL_HISTORY_HOME_FOLDER_NAME = Path.home() / ".exegol_history"
CONFIG_FILENAME = "config.toml"


def setup_db(db_path: str, db_key_path: str) -> None:
    setup_generate_keyfile(db_key_path)
    create_database(db_path, keyfile=db_key_path)
    kp = PyKeePass(db_path, keyfile=db_key_path)
    setup_groups(kp)


def setup_generate_keyfile(db_key_path: str) -> None:
    random_bytes = secrets.token_bytes(256)
    # Path(db_key_path).touch
    if not Path(db_key_path).is_file():
        Path(db_key_path).parent.mkdir(parents=True, exist_ok=True)
        with open(db_key_path, "wb") as key_file:
            key_file.write(random_bytes)


def setup_groups(kp: PyKeePass) -> None:
    kp.add_group(kp.root_group, Credential.GROUP_NAME)
    kp.add_group(kp.root_group, Host.GROUP_NAME)

    kp.save()


def setup_profile(profile_path: str):
    if not Path(profile_path).exists():
        Path(profile_path).parent.mkdir(exist_ok=True, parents=True)
        Path(profile_path).touch()


def load_config(config_path: str = None) -> dict[str, Any]:
    config_path = (
        config_path
        if config_path
        else EXEGOL_HISTORY_HOME_FOLDER_NAME / CONFIG_FILENAME
    )

    if not Path(config_path).is_file():
        Path(config_path).parent.mkdir(exist_ok=True)

        default_config_path = Path(__file__).parent / CONFIG_FILENAME
        shutil.copy(default_config_path, config_path)

    with open(config_path, "rb") as config_file:
        return tomllib.load(config_file)
