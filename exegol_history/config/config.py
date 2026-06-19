import platform
import shutil
import tomllib
from pathlib import Path
from exegol_history.connectors.metasploit.metasploit_sync import MetasploitSyncer
from exegol_history.connectors.netexec.netexec_sync import NetexecSyncer
from sqlalchemy import Engine, create_engine
from exegol_history.db_api.creds import Base

DEFAULT_KEYBINDS = {
    "copy_username_clipboard": "f1",
    "copy_password_clipboard": "f2",
    "copy_hash_clipboard": "f3",
    "add_credential": "f4",
    "delete_credential": "f5",
    "edit_credential": "f6",
    "export_credential": "f7",
    "copy_ip_clipboard": "f1",
    "copy_hostname_clipboard": "f2",
    "add_host": "f3",
    "delete_host": "f4",
    "edit_host": "f5",
    "export_host": "f6",
    "quit": "ctrl+c",
}


class AppConfig:
    EXEGOL_HISTORY_HOME_FOLDER_NAME = Path.home() / ".exegol_history"
    CONFIG_FILENAME = "config.toml"
    PROFILE_SH_FILENAME_UNIX = "profile.sh"
    PROFILE_SH_FILENAME_WINDOWS = "profile.ps1"

    def __init__(
        self, config_path: str = EXEGOL_HISTORY_HOME_FOLDER_NAME / CONFIG_FILENAME
    ):
        if not Path(config_path).is_file():
            Path(config_path).parent.mkdir(exist_ok=True)

            default_config_path = Path(__file__).parent / AppConfig.CONFIG_FILENAME
            shutil.copy(default_config_path, config_path)

        with open(config_path, "rb") as config_file:
            config_data = tomllib.load(config_file)

        self.paths = ConfigPaths(**config_data["paths"])
        self.keybindings = config_data["keybindings"]
        self.sync = [
            ConfigSyncNetexec(**config_data["sync"][NetexecSyncer.CONNECTOR_NAME]),
            ConfigSyncMetasploit(
                **config_data["sync"][MetasploitSyncer.CONNECTOR_NAME]
            ),
        ]
        self.theme = ConfigTheme(**config_data["theme"])

    @staticmethod
    def setup_db(db_path: str) -> Engine:
        path = Path(db_path)

        if path.is_absolute():
            engine = create_engine(f"sqlite:////{db_path}")
        else:
            engine = create_engine(f"sqlite:///{db_path}")

        Base.metadata.create_all(engine)

        return engine

    @staticmethod
    def setup_profile(profile_path: str):
        if not Path(profile_path).exists():
            Path(profile_path).parent.mkdir(exist_ok=True, parents=True)

            default_config_path = (
                Path(__file__).parent.parent
                / AppConfig.PROFILE_SH_FILENAME_WINDOWS
                if platform.system() == "Windows"
                else Path(__file__).parent.parent
                / AppConfig.PROFILE_SH_FILENAME_UNIX
            )
            shutil.copy(default_config_path, Path(profile_path))


class ConfigPaths:
    def __init__(
        self,
        db_name: str = "exh.db",
        profile_sh_path: str = "/opt/tools/Exegol-history/profile.sh",
    ):
        self.db_name = db_name
        self.profile_sh_path = profile_sh_path


class ConfigSyncNetexec:
    CONNECTOR_NAME = NetexecSyncer.CONNECTOR_NAME

    def __init__(
        self, enabled: bool = False, workspace_path: str = "~/.nxc/workspaces/"
    ):
        self.enabled = enabled
        self.workspace_path = workspace_path


class ConfigSyncMetasploit:
    CONNECTOR_NAME = MetasploitSyncer.CONNECTOR_NAME

    def __init__(
        self,
        enabled: bool = False,
        db_config_path: str = "/var/lib/postgresql/.msf4/database.yml",
    ):
        self.enabled = enabled
        self.db_config_path = db_config_path


class ConfigTheme:
    def __init__(
        self,
        primary: str = "#0178D4",
        secondary: str = "#004578",
        accent: str = "#ffa62b",
        foreground: str = "#e0e0e0",
        background: str = None,
        success: str = "#4EBF71",
        warning: str = "#ffa62b",
        error: str = "#ba3c5b",
        surface: str = None,
        panel: str = None,
        dark: bool = True,
        clipboard_icon: str = "📋",
        add_icon: str = "➕",
        delete_icon: str = "➖",
        edit_icon: str = "📝",
        export_icon: str = "📤",
        inline: bool = True,
    ):
        self.primary: str = primary
        self.secondary = secondary
        self.accent = accent
        self.foreground = foreground
        self.background = background
        self.success = success
        self.warning = warning
        self.error = error
        self.surface = surface
        self.panel = panel
        self.dark = dark
        self.clipboard_icon = clipboard_icon
        self.add_icon = add_icon
        self.delete_icon = delete_icon
        self.edit_icon = edit_icon
        self.export_icon = export_icon
        self.inline = inline
