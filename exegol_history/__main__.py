from rich.console import Console
from rich.traceback import install
from pathlib import Path
from pykeepass import PyKeePass
from exegol_history.cli.arguments import parse_arguments
from exegol_history.cli.functions import (
    ADD_SUBCOMMAND,
    DELETE_SUBCOMMAND,
    EDIT_SUBCOMMAND,
    EXPORT_SUBCOMMAND,
    IMPORT_SUBCOMMAND,
    SET_SUBCOMMAND,
    SHOW_SUBCOMMAND,
    UNSET_SUBCOMMAND,
    add_object,
    cli_export_objects,
    cli_import_objects,
    delete_objects,
    edit_object,
    set_objects,
    show_objects,
    show_version,
    unset_objects,
)
from exegol_history.config.config import (
    EXEGOL_HISTORY_HOME_FOLDER_NAME,
    load_config,
    setup_db,
)

console = Console(soft_wrap=True)


def main():
    install()
    config = load_config()
    db_path = EXEGOL_HISTORY_HOME_FOLDER_NAME / config["paths"]["db_name"]
    db_key_path = EXEGOL_HISTORY_HOME_FOLDER_NAME / config["paths"]["db_key_name"]

    if not Path(db_path).is_file():
        Path(db_path).touch(exist_ok=True)
        setup_db(db_path, db_key_path)

    args = parse_arguments().parse_args()
    kp = PyKeePass(db_path, keyfile=db_key_path)

    # CLI
    if args.version:
        show_version(console)
    if args.command == ADD_SUBCOMMAND:
        add_object(args, kp, config)
    if args.command == IMPORT_SUBCOMMAND:
        cli_import_objects(args, kp)
    if args.command == EDIT_SUBCOMMAND:
        edit_object(args, kp, console)
    if args.command == EXPORT_SUBCOMMAND:
        cli_export_objects(args, kp, console)
    if args.command == DELETE_SUBCOMMAND:
        delete_objects(args, kp, console)

    # TUI
    if args.command == SET_SUBCOMMAND:
        set_objects(args, kp, config, console)
    if args.command == UNSET_SUBCOMMAND:
        unset_objects(console)
    if args.command == SHOW_SUBCOMMAND:
        show_objects(console)
