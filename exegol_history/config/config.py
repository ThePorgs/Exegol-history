import platform
import secrets
import shutil
import tomllib
from pathlib import Path
from typing import Any

from pykeepass import PyKeePass, create_database

from exegol_history.db_api.creds import Credential
from exegol_history.db_api.hosts import Host


class AppConfig:
    __config_data = None

    EXEGOL_HISTORY_HOME_FOLDER_NAME = Path.home() / ".exegol_history"
    CONFIG_FILENAME = "config.toml"
    PROFILE_SH_FILENAME_UNIX = "profile.sh"
    PROFILE_SH_FILENAME_WINDOWS = "profile.sh"

    @classmethod
    def setup_db(cls, db_path: str, db_key_path: str) -> None:
        cls.__setup_generate_keyfile(db_key_path)
        create_database(db_path, keyfile=db_key_path)
        kp = PyKeePass(db_path, keyfile=db_key_path)
        cls.__setup_groups(kp)

    @staticmethod
    def __setup_generate_keyfile(db_key_path: str) -> None:
        random_bytes = secrets.token_bytes(256)

        if not Path(db_key_path).is_file():
            Path(db_key_path).parent.mkdir(parents=True, exist_ok=True)
            with open(db_key_path, "wb") as key_file:
                key_file.write(random_bytes)

    @staticmethod
    def __setup_groups(kp: PyKeePass) -> None:
        kp.add_group(kp.root_group, Credential.GROUP_NAME)
        kp.add_group(kp.root_group, Host.GROUP_NAME)

        kp.save()

    @classmethod
    def setup_profile(cls, profile_path: str):
        if not Path(profile_path).exists():
            Path(profile_path).parent.mkdir(exist_ok=True, parents=True)

            default_config_path = (
                Path(__file__).parent / cls.PROFILE_SH_FILENAME_WINDOWS
                if platform.system() == "Windows"
                else Path(__file__).parent / cls.PROFILE_SH_FILENAME_UNIX
            )
            shutil.copy(default_config_path, Path(profile_path))

    @classmethod
    def load_config(cls, config_path: str = None) -> dict[str, Any]:
        if cls.__config_data is None:
            config_path = (
                config_path
                if config_path
                else cls.EXEGOL_HISTORY_HOME_FOLDER_NAME / cls.CONFIG_FILENAME
            )

            if not Path(config_path).is_file():
                Path(config_path).parent.mkdir(exist_ok=True)

                default_config_path = Path(__file__).parent / cls.CONFIG_FILENAME
                shutil.copy(default_config_path, config_path)

            with open(config_path, "rb") as config_file:
                config_data = tomllib.load(config_file)
        return config_data
