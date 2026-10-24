# PYTHON_ARGCOMPLETE_OK
import sys
import argcomplete

# Only lightweight (stdlib-only) modules are imported at the top level:
# argcomplete re-executes this file on every <TAB>, and every command pays
# for whatever is imported here before doing anything.
from exegol_history.cli.arguments import parse_arguments
from exegol_history.cli.constants import (
    ADD_SUBCOMMAND,
    DELETE_SUBCOMMAND,
    EDIT_SUBCOMMAND,
    EXPORT_SUBCOMMAND,
    HOSTS_SUBCOMMAND,
    CREDS_SUBCOMMAND,
    IMPORT_SUBCOMMAND,
    KRB_SUBCOMMAND,
    SET_SUBCOMMAND,
    SHOW_SUBCOMMAND,
    SYNC_SUBCOMMAND,
    UNSET_SUBCOMMAND,
    VERSION_SUBCOMMAND,
)


def _launches_tui(args) -> bool:
    if args.command == SET_SUBCOMMAND:
        return True
    if args.command == ADD_SUBCOMMAND:
        if args.subcommand == CREDS_SUBCOMMAND:
            return not any([args.username, args.password, args.hash, args.domain])
        if args.subcommand == HOSTS_SUBCOMMAND:
            return not any([args.ip, args.hostname, args.role])
    return False


def main():
    parser = parse_arguments()
    # Must run before any heavy import so that shell completion stays instant
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    # Fast paths that need nothing but the standard library
    if args.command == VERSION_SUBCOMMAND:
        import importlib.metadata

        print(f"Exegol-history v{importlib.metadata.version('exegol-history')}")
        sys.exit(0)

    from rich.console import Console
    from rich.traceback import install

    console = Console(soft_wrap=True)
    install(show_locals=False)

    if args.command == SHOW_SUBCOMMAND:
        from exegol_history.cli.functions import show_objects

        show_objects(console)
        return

    from sqlalchemy import exc
    from exegol_history.config.config import AppConfig
    from exegol_history.cli.functions import (
        add_object,
        cli_export_objects,
        cli_import_objects,
        cli_sync_objects,
        delete_objects,
        edit_object,
        set_objects,
        sync_objects,
        unset_objects,
    )

    need_config = False
    need_db = False
    config = None
    engine = None
    background_sync = False

    # Functions that needs the database (also need config)
    if args.command in [
        ADD_SUBCOMMAND,
        IMPORT_SUBCOMMAND,
        EDIT_SUBCOMMAND,
        EXPORT_SUBCOMMAND,
        DELETE_SUBCOMMAND,
        SET_SUBCOMMAND,
        SYNC_SUBCOMMAND,
    ]:
        need_db = True
        need_config = True
    # Functions that only need config
    elif args.command in [UNSET_SUBCOMMAND]:
        need_config = True

    if need_config:
        config = AppConfig()
        AppConfig.setup_profile(config.paths.profile_sh_path)

        db_path = AppConfig.EXEGOL_HISTORY_HOME_FOLDER_NAME / config.paths.db_name

        if need_db:
            engine = AppConfig.setup_db(db_path)

            is_krb = getattr(args, "subcommand", None) == KRB_SUBCOMMAND

            if args.command == SYNC_SUBCOMMAND or is_krb:
                # Explicit sync is handled below; Kerberos doesn't use the DB
                pass
            elif _launches_tui(args):
                # Show the TUI immediately with the current DB content and
                # let it synchronise the connectors in a background worker.
                background_sync = True
            else:
                # Synchronise enabled connectors automatically
                try:
                    sync_objects(engine, config, True, True)
                except Exception:
                    pass

    try:
        # CLI
        if args.command == ADD_SUBCOMMAND:
            try:
                add_object(args, engine, config, background_sync)
            except exc.IntegrityError:
                console.print("[-] The credential already exist !")
        elif args.command == IMPORT_SUBCOMMAND:
            cli_import_objects(args, engine)
        elif args.command == EDIT_SUBCOMMAND:
            edit_object(args, engine, console)
        elif args.command == EXPORT_SUBCOMMAND:
            cli_export_objects(args, engine, console)
        elif args.command == DELETE_SUBCOMMAND:
            delete_objects(args, engine, console)
        elif args.command == SYNC_SUBCOMMAND:
            cli_sync_objects(engine, config, console, True, True)

        # TUI
        elif args.command == SET_SUBCOMMAND:
            set_objects(args, engine, config, console, background_sync)
        elif args.command == UNSET_SUBCOMMAND:
            unset_objects(args, config)
        else:
            raise NotImplementedError("This function is not available")
    except Exception:
        console.print_exception(show_locals=True)
        sys.exit(1)
