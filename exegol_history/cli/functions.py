import argparse
import os
import sys
from exegol_history.cli.utils import (
    CREDS_VARIABLES,
    HOSTS_VARIABLES,
    console_error,
    write_credential_in_profile,
    write_host_in_profile,
)
from exegol_history.config.config import AppConfig
from exegol_history.db_api.creds import (
    Credential,
    add_credentials,
    delete_credentials,
    edit_credentials,
    get_credentials,
)
from exegol_history.db_api.exporting import export_objects
from exegol_history.db_api.hosts import (
    Host,
    add_hosts,
    delete_hosts,
    edit_hosts,
    get_hosts,
)
from exegol_history.db_api.importing import (
    CredsImportFileType,
    HostsImportFileType,
    import_objects,
)
from exegol_history.db_api.sync import sync_objects
from exegol_history.db_api.utils import parse_ids
from exegol_history.tui.db_creds import DbCredsApp
from exegol_history.tui.db_hosts import DbHostsApp
from typing import Any
from rich.console import Console
from sqlalchemy import Engine
import importlib.metadata

CREDS_SUBCOMMAND = "creds"
HOSTS_SUBCOMMAND = "hosts"
ALL_SUBCOMMAND = "all"
VERSION_SUBCOMMAND = "version"
ADD_SUBCOMMAND = "add"
IMPORT_SUBCOMMAND = "import"
EDIT_SUBCOMMAND = "edit"
EXPORT_SUBCOMMAND = "export"
SET_SUBCOMMAND = "set"
UNSET_SUBCOMMAND = "unset"
SHOW_SUBCOMMAND = "show"
DELETE_SUBCOMMAND = "rm"
SYNC_SUBCOMMAND = "sync"


def add_object(args: argparse.Namespace, engine: Engine, config: AppConfig):
    if args.subcommand == CREDS_SUBCOMMAND:
        if any([args.username, args.password, args.hash, args.domain]):
            add_credentials(
                engine,
                [
                    Credential.dict(
                        username=args.username,
                        password=args.password,
                        hash=args.hash,
                        domain=args.domain,
                    )
                ],
            )
            # If set flag is provided, automatically set the credential
            if args.set:
                credential_to_add = Credential(
                    username=args.username,
                    password=args.password,
                    hash=args.hash,
                    domain=args.domain,
                )
                write_credential_in_profile(credential_to_add, config)
        else:  # If no arguments are given, display the TUI adding screen
            app = DbCredsApp(config, engine, show_add_screen=True)
            app.run(inline=config.theme.inline)
    elif args.subcommand == HOSTS_SUBCOMMAND:
        if any([args.ip, args.hostname, args.role]):
            add_hosts(
                engine, [Host.dict(ip=args.ip, hostname=args.hostname, role=args.role)]
            )
            # If set flag is provided, automatically set the host
            if args.set:
                host_to_add = Host(ip=args.ip, hostname=args.hostname, role=args.role)
                write_host_in_profile(host_to_add, config)
        else:  # If no arguments are given, display the TUI adding screen
            app = DbHostsApp(config, engine, show_add_screen=True)
            app.run(inline=config.theme.inline)


def delete_objects(args: argparse.Namespace, engine: Engine, console: Console):
    ids = parse_ids(args.id)

    try:
        if args.subcommand == CREDS_SUBCOMMAND:
            delete_credentials(engine, ids)
        elif args.subcommand == HOSTS_SUBCOMMAND:
            delete_hosts(engine, ids)
    except RuntimeError as e:
        console.print(console_error(e))


def edit_object(args: argparse.Namespace, engine: Engine, console: Console):
    try:
        if args.subcommand == CREDS_SUBCOMMAND:
            credential = Credential(
                args.id,
                username=args.username,
                password=args.password,
                hash=args.hash,
                domain=args.domain,
            )
            edit_credentials(engine, [credential.as_dict()])
        elif args.subcommand == HOSTS_SUBCOMMAND:
            host = Host(args.id, ip=args.ip, hostname=args.hostname, role=args.role)
            edit_hosts(engine, [host.as_dict()])
    except RuntimeError as e:
        console.print(console_error(e))


def cli_export_objects(args: argparse.Namespace, engine: Engine, console: Console):
    if args.subcommand == CREDS_SUBCOMMAND:
        objects = get_credentials(engine, redacted=args.redacted)
        file_format = CredsImportFileType[args.format]
    elif args.subcommand == HOSTS_SUBCOMMAND:
        objects = get_hosts(engine)
        file_format = HostsImportFileType[args.format]
    else:
        raise NotImplementedError

    export_output = export_objects(
        format=file_format, objects=objects, delimiter=args.delimiter
    )
    if args.file:
        with open(args.file, "w") as f:
            f.write(export_output)
    else:
        if file_format in (CredsImportFileType.JSON, HostsImportFileType.JSON):
            console.print_json(export_output)
        else:
            console.print(export_output)


def cli_import_objects(args: argparse.Namespace, engine: Engine):
    file_to_import = open(args.file, "rb")

    if args.subcommand == CREDS_SUBCOMMAND:
        import_type = CredsImportFileType[args.format]

        parsed_objects = import_objects(
            import_type,
            file_to_import.read(),
            kdbx_password=args.kdbx_password,
            keyfile_path=args.kdbx_keyfile,
        )

        add_credentials(engine, parsed_objects)
    elif args.subcommand == HOSTS_SUBCOMMAND:
        import_type = HostsImportFileType[args.format]

        parsed_objects = import_objects(
            import_type,
            file_to_import.read(),
        )

        add_hosts(engine, parsed_objects)

    file_to_import.close()


def set_objects(
    args: argparse.Namespace, engine: Engine, config: AppConfig, console: Console
):
    if args.subcommand == CREDS_SUBCOMMAND:
        try:
            app = DbCredsApp(config, engine)
            row_data = app.run(inline=config.theme.inline)
            if row_data is not None:
                write_credential_in_profile(Credential(*row_data), config)
        except TypeError:  # It means the user left the TUI without choosing anything
            sys.exit(0)
    elif args.subcommand == HOSTS_SUBCOMMAND:
        app = DbHostsApp(config, engine)

        try:
            row_data = app.run(inline=config.theme.inline)
            if row_data is not None:
                write_host_in_profile(Host(*row_data), config)
        except TypeError:  # It means the user left the TUI without choosing anything
            sys.exit(0)


def unset_objects(args: argparse.Namespace, config: dict[str, Any]): 
    if args.subcommand == CREDS_SUBCOMMAND: 
        write_credential_in_profile(Credential(), config) 
    elif args.subcommand == HOSTS_SUBCOMMAND: 
        write_host_in_profile(Host(), config) 
    elif args.subcommand == ALL_SUBCOMMAND: 
        write_credential_in_profile(Credential(), config) 
        write_host_in_profile(Host(), config) 
    else: 
        raise NotImplementedError 
    sys.exit(0)


def show_objects(console: Console):
    env_vars = CREDS_VARIABLES + HOSTS_VARIABLES
    not_none_vars = [var for var in env_vars if os.environ.get(var) is not None]

    if not_none_vars:
        for var in not_none_vars:
            console.print(f"{var}:{os.environ.get(var)}")
    else:
        console.print("No environment variables are set.")


def cli_sync_objects(
    engine: Engine,
    config: AppConfig,
    console: Console,
    sync_credentials: bool = False,
    sync_hosts: bool = False,
):
    try:
        sync_objects(engine, config, sync_credentials, sync_hosts)
    except Exception as e:
        console.print(e)


def show_version(console: Console):
    console.print(f"Exegol-history v{importlib.metadata.version('exegol-history')}")
    sys.exit(0)
