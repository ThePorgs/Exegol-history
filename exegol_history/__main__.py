import sys
from pathlib import Path

from pykeepass import PyKeePass
from rich.console import Console
from rich.traceback import install

from exegol_history.cli.arguments import parse_arguments
from exegol_history.cli.functions import (
    ADD_SUBCOMMAND,
    DELETE_SUBCOMMAND,
    EDIT_SUBCOMMAND,
    EXPORT_SUBCOMMAND,
    IMPORT_SUBCOMMAND,
    SET_SUBCOMMAND,
    SHOW_SUBCOMMAND,
    SYNC_SUBCOMMAND,
    UNSET_SUBCOMMAND,
    add_object,
    cli_export_objects,
    cli_import_objects,
    delete_objects,
    edit_object,
    set_objects,
    show_objects,
    show_version,
    sync_objects,
    unset_objects,
    VERSION_SUBCOMMAND,
)
from exegol_history.config.config import AppConfig
from exegol_history.connectors.nxc.nxc_workspace_syncer import NXCWorkspaceSyncer

console = Console(soft_wrap=True)


def main():
    install()

    need_config = False
    need_kp = False
    config = None
    kp = None

    args = parse_arguments().parse_args()

    # Functions that needs KP database (also need config)
    if args.command in [
        ADD_SUBCOMMAND,
        IMPORT_SUBCOMMAND,
        EDIT_SUBCOMMAND,
        EXPORT_SUBCOMMAND,
        DELETE_SUBCOMMAND,
        SET_SUBCOMMAND,
        SYNC_SUBCOMMAND,
    ]:
        need_kp = True
        need_config = True
    # Functions that only need config
    elif args.command in [UNSET_SUBCOMMAND]:
        need_config = True

    if need_config:
        config = AppConfig.load_config()
        db_path = AppConfig.EXEGOL_HISTORY_HOME_FOLDER_NAME / config["paths"]["db_name"]
        db_key_path = (
            AppConfig.EXEGOL_HISTORY_HOME_FOLDER_NAME / config["paths"]["db_key_name"]
        )

        AppConfig.setup_profile(config["paths"]["profile_sh_path"])

        if need_kp:
            if not Path(db_path).is_file():
                Path(db_path).touch(exist_ok=True)
                AppConfig.setup_db(db_path, db_key_path)
            kp = PyKeePass(db_path, keyfile=db_key_path)

            # Synchronise all connectors
            if args.command != SYNC_SUBCOMMAND:
                sync_objects(kp, config)

    try:
        # CLI
        if args.command == VERSION_SUBCOMMAND:
            show_version(console)
        elif args.command == ADD_SUBCOMMAND:
            add_object(args, kp, config)
        elif args.command == IMPORT_SUBCOMMAND:
            cli_import_objects(args, kp)
        elif args.command == EDIT_SUBCOMMAND:
            edit_object(args, kp, console)
        elif args.command == EXPORT_SUBCOMMAND:
            cli_export_objects(args, kp, console)
        elif args.command == DELETE_SUBCOMMAND:
            delete_objects(args, kp, console)
        elif args.command == SYNC_SUBCOMMAND:
            sync_objects(kp, config)

        # TUI
        elif args.command == SET_SUBCOMMAND:
            set_objects(args, kp, config, console)
        elif args.command == UNSET_SUBCOMMAND:
            unset_objects(args, config)
        elif args.command == SHOW_SUBCOMMAND:
            show_objects(console)
        else:
            raise NotImplementedError("This function is not available")
    except Exception:
        console.print_exception(show_locals=True)
        sys.exit(1)
