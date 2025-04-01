import os.path
import argparse
import secrets
import tomllib
import shutil
import sys

from rich.console import Console
from rich.traceback import install
from pykeepass import PyKeePass, create_database
from typing import Any

import exegol_history.connectors.msf
import exegol_history.connectors.msf.extractors
import exegol_history.connectors.msf.extractors.credentials
import exegol_history.connectors.msf.extractors.hosts
import exegol_history.connectors.msf.utils
from exegol_history.db_api.creds import (
    add_credential,
    get_credentials,
    delete_credential,
    GROUP_NAME_CREDENTIALS,
)
from exegol_history.db_api.hosts import (
    add_host,
    get_hosts,
    delete_host,
    GROUP_NAME_HOSTS,
)
from exegol_history.tui.db_creds.db_creds import DbCredsApp
from exegol_history.tui.db_hosts.db_hosts import DbHostsApp
from exegol_history.db_api.formatter import (
    format_into_json,
    format_into_csv,
    format_into_txt,
)
from exegol_history.db_api.parsing import (
    parse_creds,
    parse_hosts,
    CredsFileType,
    HostsFileType,
)
from exegol_history.db_api.utils import (
    write_host_in_profile,
    write_credential_in_profile,
)

exegol_history_HOME_FOLDER_NAME = ".exegol_history"
PROFILE_SH_PATH = "/opt/tools/Exegol-history/profile.sh"

console = Console(soft_wrap=True)


def setup(db_path: str, db_key_path: str) -> None:
    setup_generate_keyfile(db_key_path)
    create_database(db_path, keyfile=db_key_path)
    kp = PyKeePass(db_path, keyfile=db_key_path)
    setup_groups(kp)


def setup_generate_keyfile(db_key_path: str) -> None:
    random_bytes = secrets.token_bytes(256)

    if not os.path.isfile(db_key_path):
        os.makedirs(os.path.dirname(db_key_path), exist_ok=True)
        with open(db_key_path, "wb") as key_file:
            key_file.write(random_bytes)


def setup_groups(kp: PyKeePass) -> None:
    kp.add_group(kp.root_group, GROUP_NAME_CREDENTIALS)
    kp.add_group(kp.root_group, GROUP_NAME_HOSTS)

    kp.save()


def load_config() -> dict[str, Any]:
    config_path = os.path.expanduser(
        os.path.join("~", exegol_history_HOME_FOLDER_NAME, "config.toml")
    )

    if not os.path.isfile(config_path):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        default_config_path = os.path.join(
            os.path.dirname(__file__), "config", "config.toml"
        )
        shutil.copy(default_config_path, config_path)

    with open(config_path, "rb") as config_file:
        return tomllib.load(config_file)


def parse_arguments() -> None:
    parser = argparse.ArgumentParser(
        prog="exegol_history",
        description="""
            Exegol-history: A tool to easily manage credentials and assets
            discovered during security engagements.
        """,
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="Command to execute (add, export, rm, set, show).",
    )
    add_parser = subparsers.add_parser(
        "add", help="Add new credentials or hosts to the database."
    )
    sync_parser = subparsers.add_parser(
        "sync", help="Synchronize credentials and hosts to the database."
    )
    get_parser = subparsers.add_parser(
        "export",
        help="Export credentials or hosts from the database in various formats.",
    )
    delete_parser = subparsers.add_parser(
        "rm", help="Remove existing credentials or hosts from the database."
    )
    tui_parser = subparsers.add_parser(
        "set",
        help="Select credentials or assets and set them in the current shell to use with the preset history commands.",
    )
    subparsers.add_parser(
        "show",
        help="Display exegol history values currently set in the shell (i.e., environment variables).",
    )
    subparsers.add_parser(
        "unset",
        help="Unset the currently selected credential.",
    )

    add_subparsers = add_parser.add_subparsers(
        dest="subcommand",
        required=True,
        help="Type of object to add (creds, hosts).",
    )
    sync_subparsers = sync_parser.add_subparsers(
        dest="subcommand",
        required=True,
        help="Type of synchronization to do (nxc, msf).",
    )
    get_subparsers = get_parser.add_subparsers(
        dest="subcommand",
        required=True,
        help="Type of object to export (creds, hosts).",
    )
    delete_subparsers = delete_parser.add_subparsers(
        dest="subcommand",
        required=True,
        help="Type of object to remove (creds, hosts).",
    )
    tui_subparsers = tui_parser.add_subparsers(
        dest="subcommand",
        required=True,
        help="Type of object to manage in the TUI (creds, hosts).",
    )

    # Credentials
    # Add / edit
    credential_add_parser = add_subparsers.add_parser(
        "creds", help="Add or update credentials in the database."
    )
    credential_add_parser.add_argument(
        "-u", "--username", help="Username for the credential entry."
    )
    credential_add_parser.add_argument(
        "-p", "--password", help="Password for the credential entry."
    )
    credential_add_parser.add_argument(
        "-H",
        "--hash",
        help="Password hash (such as NTLM, MD5, etc.) for the credential entry.",
    )
    credential_add_parser.add_argument(
        "-d", "--domain", help="Domain associated with the credential entry."
    )
    credential_add_parser.add_argument(
        "-f", "--file", help="Import multiple credentials from a file."
    )
    credential_add_parser.add_argument(
        "--file-type",
        choices=[cred_type.name for cred_type in CredsFileType],
        help="Type of file being imported (csv, nxc, pypykatz, etc.) - required when using --file.",
    )

    # Get
    credential_get_parser = get_subparsers.add_parser(
        "creds", help="Export credential information from the database."
    )
    credential_get_parser.add_argument(
        "--json",
        action="store_true",
        help="Export data in JSON format (default if no format specified).",
    )
    credential_get_parser.add_argument(
        "--csv", action="store_true", help="Export data in CSV format."
    )
    credential_get_parser.add_argument(
        "--txt", action="store_true", help="Export data in plain text format."
    )
    credential_get_parser.add_argument(
        "-u",
        "--username",
        help="Filter export to only show credentials with this specific username.",
    )
    credential_get_parser.add_argument(
        "-d",
        "--domain",
        help="Filter export to only show credentials with this specific domain.",
    )
    credential_get_parser.add_argument(
        "-p",
        "--password",
        help="Filter export to only show credentials with this specific password.",
    )
    credential_get_parser.add_argument(
        "-H",
        "--hash",
        help="Filter export to only show credentials with this specific hash.",
    )
    credential_get_parser.add_argument(
        "-i",
        "--id",
        help="Filter export to only show credentials with this specific id.",
    )
    credential_get_parser.add_argument(
        "-r",
        "--redacted",
        action="store_true",
        help="Mask sensitive information like passwords and hashes in the output.",
    )

    # Delete
    credential_delete_parser = delete_subparsers.add_parser(
        "creds", help="Delete credentials from the database."
    )
    credential_delete_parser.add_argument(
        "-u",
        "--username",
        required=True,
        help="Username of the credential entry to delete.",
    )

    # Hosts
    # Add / edit
    hosts_add_parser = add_subparsers.add_parser(
        "hosts", help="Add or update host information in the database."
    )
    hosts_add_parser.add_argument("--ip", help="IP address of the host.")
    hosts_add_parser.add_argument(
        "-r",
        "--role",
        help="Role of the host in the environment (e.g., SCCM, ADCS, DC, WKS).",
    )
    hosts_add_parser.add_argument(
        "-n", "--hostname", help="Hostname or NetBIOS name of the host."
    )
    hosts_add_parser.add_argument(
        "-f", "--file", help="Import multiple hosts from a file."
    )
    hosts_add_parser.add_argument(
        "--file-type",
        choices=[host_type.name for host_type in HostsFileType],
        help="Type of file being imported (csv, nxc, etc.) - required when using --file.",
    )

    # Get
    hosts_get_parser = get_subparsers.add_parser(
        "hosts", help="Export host information from the database."
    )
    hosts_get_parser.add_argument(
        "--json",
        action="store_true",
        help="Export data in JSON format (default if no format specified).",
    )
    hosts_get_parser.add_argument(
        "--csv", action="store_true", help="Export data in CSV format."
    )
    hosts_get_parser.add_argument(
        "--txt", action="store_true", help="Export data in plain text format."
    )
    hosts_get_parser.add_argument(
        "--ip", help="Filter export to only show hosts with this specific IP address."
    )

    # Delete
    hosts_delete_parser = delete_subparsers.add_parser(
        "hosts", help="Delete host information from the database."
    )
    hosts_delete_parser.add_argument(
        "--ip", required=True, help="IP address of the host to delete."
    )

    # TUI
    tui_parser = tui_subparsers.add_parser(
        "creds",
        help="Manage credentials using the TUI and set related environment variables.",
    )
    tui_parser = tui_subparsers.add_parser(
        "hosts",
        help="Manage hosts using the TUI and set related environment variables.",
    )

    # Sync
    sync_subparsers.add_parser(
        "msf",
        help="Synchronize MSF (Metasploit Framework) credentials and hosts database.",
    )

    return parser.parse_args()


def main():
    install()
    config = load_config()
    exegol_history_home_folder = os.path.join("~", exegol_history_HOME_FOLDER_NAME)

    db_path = os.path.expanduser(
        os.path.join(exegol_history_home_folder, config["paths"]["db_name"])
    )
    db_key_path = os.path.expanduser(
        os.path.join(exegol_history_home_folder, config["paths"]["db_key_name"])
    )

    if not os.path.isfile(db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        setup(db_path, db_key_path)

    args = parse_arguments()
    kp = PyKeePass(db_path, keyfile=db_key_path)

    if args.command == "add":
        if args.subcommand == "creds":
            if args.username:
                add_credential(
                    kp,
                    args.username,
                    args.password if args.password else "",
                    args.hash if args.hash else "",
                    args.domain if args.domain else "",
                )

            if args.file:
                with open(args.file, "r") as cred_file:
                    parsed_creds = parse_creds(
                        CredsFileType[args.file_type].value, cred_file.read()
                    )

                    if parsed_creds:
                        for cred in parsed_creds:
                            add_credential(kp, cred[0], cred[1], cred[2], cred[3])

            # If no arguments are given, display the TUI adding screen
            if len(sys.argv) <= 3:
                app = DbCredsApp(config, kp, show_add_screen=True)
                app.run()

        elif args.subcommand == "hosts":
            if args.ip:
                add_host(
                    kp,
                    args.ip,
                    args.hostname if args.hostname else "",
                    args.role if args.role else "",
                )

            if args.file:
                with open(args.file, "r") as host_file:
                    parsed_hosts = parse_hosts(
                        HostsFileType[args.file_type].value, host_file.read()
                    )

                    if parsed_hosts:
                        for host in parsed_hosts:
                            add_host(kp, host[0], host[1], host[2])

            # If no arguments are given, display the TUI adding screen
            if len(sys.argv) <= 3:
                app = DbHostsApp(config, kp, show_add_screen=True)
                app.run()

    if args.command == "sync":
        if args.subcommand == "msf":
            (database, port, username, password) = (
                exegol_history.connectors.msf.utils.get_msf_postgres_db_infos(
                    exegol_history.connectors.msf.utils.MSF_DB_CONFIG_PATH
                )
            )
            exegol_history.connectors.msf.extractors.credentials.sync_credentials(
                kp,
                msf_db_name=database,
                msf_db_port=port,
                msf_db_username=username,
                msf_db_password=password,
            )
            exegol_history.connectors.msf.extractors.hosts.sync_hosts(
                kp,
                msf_db_name=database,
                msf_db_port=port,
                msf_db_username=username,
                msf_db_password=password,
            )

    if args.command == "export":
        if args.subcommand == "creds":
            creds = get_credentials(
                kp,
                args.id,
                args.username,
                args.password,
                args.hash,
                args.domain,
                args.redacted,
            )

            if args.csv:
                console.print(format_into_csv(creds))

            elif args.txt:
                console.print(format_into_txt(creds))

            elif args.json or (not args.csv and not args.txt):
                console.print_json(
                    format_into_json(
                        creds,
                        field_names=["id", "username", "password", "hash", "domain"],
                    )
                )

        elif args.subcommand == "hosts":
            hosts = get_hosts(kp, args.ip)

            if args.csv:
                console.print(format_into_csv(hosts))

            elif args.txt:
                console.print(format_into_txt(hosts))

            elif args.json or (not args.csv and not args.txt):
                console.print_json(
                    format_into_json(hosts, field_names=["ip", "hostname", "role"])
                )

    if args.command == "rm":
        if args.subcommand == "creds":
            try:
                delete_credential(kp, args.username)
            except RuntimeError:
                console.print(
                    "[[bold red]![/bold red]] The provided username does not exist !"
                )
        elif args.subcommand == "hosts":
            try:
                delete_host(kp, args.ip)
            except RuntimeError:
                console.print(
                    "[[bold red]![/bold red]] The provided IP does not exist !"
                )

    # TUI mode
    if args.command == "set":
        if args.subcommand == "creds":
            app = DbCredsApp(config, kp)

            try:
                _id, username, password, hash, domain = app.run()
                write_credential_in_profile(
                    PROFILE_SH_PATH, username, password, hash, domain
                )
            except (
                TypeError
            ):  # It means the user left the TUI without choosing anything
                sys.exit(0)
            except Exception:
                console.print_exception(show_locals=True)
                sys.exit(1)
        elif args.subcommand == "hosts":
            app = DbHostsApp(config, kp)

            try:
                ip, hostname, role = app.run()
                write_host_in_profile(PROFILE_SH_PATH, ip, hostname, role)
            except (
                TypeError
            ):  # It means the user left the TUI without choosing anything
                sys.exit(0)
            except Exception:
                console.print_exception(show_locals=True)
                sys.exit(1)

    if args.command == "unset":
        try:
            write_credential_in_profile(PROFILE_SH_PATH, "", "", "", "")
            sys.exit(0)
        except Exception:
            console.print_exception(show_locals=True)
            sys.exit(1)

    if args.command == "show":
        env_vars = [
            "USER",
            "PASSWORD",
            "NT_HASH",
            "DOMAIN",
            "IP",
            "TARGET",
            "DB_HOSTNAME",
            "DC_HOST",
        ]
        not_none_vars = [var for var in env_vars if os.environ.get(var) is not None]

        if not_none_vars:
            for var in not_none_vars:
                console.print(f"{var}:{os.environ.get(var)}")
        else:
            console.print("No environment variables are set.")
