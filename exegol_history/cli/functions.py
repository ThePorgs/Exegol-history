import argparse
import os
import sys
from typing import Any
from pykeepass import PyKeePass
from exegol_history.cli.utils import (
    CREDS_VARIABLES,
    HOSTS_VARIABLES,
    console_error,
    write_credential_in_profile,
    write_host_in_profile,
)
from exegol_history.db_api.creds import (
    Credential,
    add_credentials,
    delete_credentials,
    edit_credential,
    get_credentials,
)
from exegol_history.db_api.exporting import export_objects
from exegol_history.db_api.hosts import (
    Host,
    add_hosts,
    delete_hosts,
    edit_host,
    get_hosts,
)
from exegol_history.db_api.importing import (
    CredsImportFileType,
    HostsImportFileType,
    import_objects,
)
from exegol_history.db_api.utils import parse_ids
from exegol_history.tui.db_creds import DbCredsApp
from exegol_history.tui.db_hosts import DbHostsApp
from rich.console import Console
import importlib.metadata

CREDS_SUBCOMMAND = "creds"
HOSTS_SUBCOMMAND = "hosts"

ADD_SUBCOMMAND = "add"
IMPORT_SUBCOMMAND = "import"
EDIT_SUBCOMMAND = "edit"
EXPORT_SUBCOMMAND = "export"
SET_SUBCOMMAND = "set"
UNSET_SUBCOMMAND = "un" + SET_SUBCOMMAND
SHOW_SUBCOMMAND = "show"
DELETE_SUBCOMMAND = "rm"


def add_object(args: argparse.Namespace, kp: PyKeePass, config: dict[str, Any]):
    if args.subcommand == CREDS_SUBCOMMAND:
        if any([args.username, args.password, args.hash, args.domain]):
            credential_to_add = Credential(
                username=args.username,
                password=args.password,
                hash=args.hash,
                domain=args.domain,
            )
            add_credentials(kp, [credential_to_add])
        else:  # If no arguments are given, display the TUI adding screen
            app = DbCredsApp(config, kp, show_add_screen=True)
            app.run()
    elif args.subcommand == HOSTS_SUBCOMMAND:
        if any([args.ip, args.hostname, args.role]):
            host_to_add = Host(ip=args.ip, hostname=args.hostname, role=args.role)
            add_hosts(kp, [host_to_add])
        else:  # If no arguments are given, display the TUI adding screen
            app = DbHostsApp(config, kp, show_add_screen=True)
            app.run()


def delete_objects(args: argparse.Namespace, kp: PyKeePass, console: Console):
    ids = parse_ids(args.id)

    try:
        if args.subcommand == CREDS_SUBCOMMAND:
            delete_credentials(kp, ids)
        elif args.subcommand == HOSTS_SUBCOMMAND:
            delete_hosts(kp, ids)
    except RuntimeError as e:
        console.print(console_error(e))


def edit_object(args: argparse.Namespace, kp: PyKeePass, console: Console):
    try:
        if args.subcommand == CREDS_SUBCOMMAND:
            credential = Credential(
                id=args.id,
                username=args.username,
                password=args.password,
                hash=args.hash,
                domain=args.domain,
            )
            edit_credential(kp, credential)
        elif args.subcommand == HOSTS_SUBCOMMAND:
            host = Host(id=args.id, ip=args.ip, hostname=args.hostname, role=args.role)
            edit_host(kp, host)
    except RuntimeError as e:
        console.print(console_error(e))


def cli_export_objects(args: argparse.Namespace, kp: PyKeePass, console: Console):
    if args.subcommand == CREDS_SUBCOMMAND:
        objects = get_credentials(kp, redacted=args.redacted)
        format = CredsImportFileType[args.format]
    elif args.subcommand == HOSTS_SUBCOMMAND:
        objects = get_hosts(kp)
        format = HostsImportFileType[args.format]

    export_output = export_objects(
        format=format, objects=objects, delimiter=args.delimiter
    )
    if args.file:
        with open(args.file, "w") as f:
            f.write(export_output)
    else:
        if format in (CredsImportFileType.JSON, HostsImportFileType.JSON):
            console.print_json(export_output)
        else:
            console.print(export_output)


def cli_import_objects(args: argparse.Namespace, kp: PyKeePass):
    file_to_import = open(args.file, "rb")

    if args.subcommand == CREDS_SUBCOMMAND:
        import_type = CredsImportFileType[args.format]

        parsed_objects = import_objects(
            import_type,
            file_to_import.read(),
            kdbx_password=args.kdbx_password,
            keyfile_path=args.kdbx_keyfile,
        )

        add_credentials(kp, parsed_objects)
    elif args.subcommand == HOSTS_SUBCOMMAND:
        import_type = HostsImportFileType[args.format]

        parsed_objects = import_objects(
            import_type,
            file_to_import.read(),
        )

        add_hosts(kp, parsed_objects)

    file_to_import.close()


def set_objects(
    args: argparse.Namespace, kp: PyKeePass, config: dict[str, Any], console: Console
):
    if args.subcommand == CREDS_SUBCOMMAND:
        try:
            app = DbCredsApp(config, kp)
            row_data = app.run()
            write_credential_in_profile(Credential(*row_data), config)
        except TypeError:  # It means the user left the TUI without choosing anything
            sys.exit(0)
        except Exception:
            console.print_exception(show_locals=True)
            sys.exit(1)
    elif args.subcommand == HOSTS_SUBCOMMAND:
        app = DbHostsApp(config, kp)

        try:
            row_data = app.run()
            write_host_in_profile(Host(*row_data), config)
        except TypeError:  # It means the user left the TUI without choosing anything
            sys.exit(0)
        except Exception:
            console.print_exception(show_locals=True)
            sys.exit(1)


def unset_objects(config: dict[str, Any], console: Console):
    try:
        write_credential_in_profile(Credential(), config)
        write_host_in_profile(Host(), config)
        sys.exit(0)
    except Exception:
        console.print_exception(show_locals=True)
        sys.exit(1)


def show_objects(console: Console):
    env_vars = CREDS_VARIABLES + HOSTS_VARIABLES
    not_none_vars = [var for var in env_vars if os.environ.get(var) is not None]

    if not_none_vars:
        for var in not_none_vars:
            console.print(f"{var}:{os.environ.get(var)}")
    else:
        console.print("No environment variables are set.")


def show_version(console: Console):
    console.print(f"Exegol-history v{importlib.metadata.version('exegol-history')}")
    sys.exit(0)
