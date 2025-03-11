import os.path
import argparse
import secrets
import tomllib
import shutil

from rich.console import Console
from rich.traceback import install
from pykeepass import PyKeePass, create_database
from typing import Any

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

exegol_history_HOME_FOLDER_NAME = ".exegol_history"

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
			This program can be used to easily manage credentials 
			and assets found during an engagement.
		""",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="Operation to execute (adding, deleting, TUI).",
    )
    add_parser = subparsers.add_parser(
        "add", help="Add an object (credentials, hosts, ...)."
    )
    get_parser = subparsers.add_parser(
        "get", help="Get an object (credentials, hosts, ...)."
    )
    delete_parser = subparsers.add_parser(
        "del", help="Delete an object (credentials, hosts, ...)."
    )
    tui_parser = subparsers.add_parser(
        "export",
        help="""
			Launch the TUI to manage an object (credentials, hosts, ...).
		""",
    )
    subparsers.add_parser(
        "env",
        help="""
			Display environment variables related to Exegol-history.
		""",
    )

    add_subparsers = add_parser.add_subparsers(
        dest="subcommand",
        required=True,
        help="Choose which kind of object to add / edit (credential, host, ...).",
    )
    get_subparsers = get_parser.add_subparsers(
        dest="subcommand",
        required=True,
        help="Choose which kind of object to get (credential, host, ...).",
    )
    delete_subparsers = delete_parser.add_subparsers(
        dest="subcommand",
        required=True,
        help="Choose which kind of object to delete (credential, host, ...).",
    )
    tui_subparsers = tui_parser.add_subparsers(
        dest="subcommand",
        required=True,
        help="""
			Choose which kind of object to manage in the TUI (credential, host, ...).
		""",
    )

    # Credentials
    # Add / edit
    credential_add_parser = add_subparsers.add_parser(
        "creds", help="Add / edit an object (credentials, hosts, ...)."
    )
    credential_add_parser.add_argument("-u", "--username", help="Credential username.")
    credential_add_parser.add_argument("-p", "--password", help="Credential password.")
    credential_add_parser.add_argument("-H", "--hash", help="Credential hash.")
    credential_add_parser.add_argument("-d", "--domain", help="Credential domain.")
    credential_add_parser.add_argument(
        "-f", "--file", help="Import credentials from file."
    )
    credential_add_parser.add_argument(
        "--file-type",
        choices=[cred_type.name for cred_type in CredsFileType],
        help="Imported file type (csv, nxc, pypykatz, ...).",
    )

    # Get
    credential_get_parser = get_subparsers.add_parser(
        "creds", help="Get an object (credentials, hosts, ...)."
    )
    credential_get_parser.add_argument(
        "--json", action="store_true", help="Output in JSON format."
    )
    credential_get_parser.add_argument(
        "--csv", action="store_true", help="Output in CSV format."
    )
    credential_get_parser.add_argument(
        "--txt", action="store_true", help="Output in TXT format."
    )
    credential_get_parser.add_argument(
        "-u", "--username", help="Specific username to get credential of."
    )
    credential_get_parser.add_argument(
        "-r", "--redacted", action="store_true", help="Hide sensitive credentials"
    )

    # Delete
    credential_delete_parser = delete_subparsers.add_parser(
        "creds", help="Delete an object (credentials, hosts, ...)."
    )
    credential_delete_parser.add_argument(
        "-u", "--username", required=True, help="Credential username."
    )

    # Hosts
    # Add / edit
    hosts_add_parser = add_subparsers.add_parser("hosts", help="Add a host")
    hosts_add_parser.add_argument("--ip", help="Host IP.")
    hosts_add_parser.add_argument(
        "-r", "--role", help="Host role (SCCM, ADCS, DC, WKS, ...)."
    )
    hosts_add_parser.add_argument("-n", "--hostname", help="Hostname.")
    hosts_add_parser.add_argument("-f", "--file", help="Import hosts from file.")
    hosts_add_parser.add_argument(
        "--file-type",
        choices=[host_type.name for host_type in HostsFileType],
        help="Imported file type (csv, nxc, ...).",
    )

    # Get
    hosts_get_parser = get_subparsers.add_parser("hosts", help="Get hosts.")
    hosts_get_parser.add_argument(
        "--json", action="store_true", help="Output in JSON format."
    )
    hosts_get_parser.add_argument(
        "--csv", action="store_true", help="Output in CSV format."
    )
    hosts_get_parser.add_argument(
        "--txt", action="store_true", help="Output in TXT format."
    )
    hosts_get_parser.add_argument("--ip", help="Specific IP to search.")

    # Delete
    hosts_delete_parser = delete_subparsers.add_parser("hosts", help="Delete a host.")
    hosts_delete_parser.add_argument("--ip", required=True, help="Host IP.")

    # TUI
    tui_parser = tui_subparsers.add_parser("creds", help="Manage credentials.")
    tui_parser = tui_subparsers.add_parser("hosts", help="Manage hosts.")

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

    if args.command == "get":
        if args.subcommand == "creds":
            creds = get_credentials(kp, args.username, args.redacted)

            if args.csv:
                console.print(format_into_csv(creds))

            elif args.txt:
                console.print(format_into_txt(creds))

            elif args.json or (not args.csv and not args.txt):
                console.print_json(
                    format_into_json(
                        creds, field_names=["username", "password", "hash", "domain"]
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

    if args.command == "del":
        if args.subcommand == "creds":
            try:
                delete_credential(kp, args.username)
            except RuntimeError:
                console.print(
                    "[[bold red]*[/bold red]] The provided username does not exist !"
                )
        elif args.subcommand == "hosts":
            try:
                delete_host(kp, args.ip)
            except RuntimeError:
                console.print(
                    "[[bold red]*[/bold red]] The provided IP does not exist !"
                )

    # TUI mode
    if args.command == "export":
        if args.subcommand == "creds":
            app = DbCredsApp(config, kp)

            try:
                username, password, nt_hash, domain = app.run()

                with open("../profile.sh", "w") as profile:
                    profile.write(f"export USER='{username}'")
                    profile.write(f"export PASSWORD='{password}'")
                    profile.write(f"export NT_HASH='{nt_hash}'")
                    profile.write(f"export DOMAIN='{domain}'")

            except Exception:
                pass
        elif args.subcommand == "hosts":
            app = DbHostsApp(config, kp)

            try:
                ip, hostname, role = app.run()

                with open("../profile.sh", "w") as profile:
                    profile.write(f"export IP='{ip}'")
                    profile.write(f"export TARGET='{ip}'")
                    profile.write(f"export DB_HOSTNAME='{hostname}'")

                    if role == "DC":
                        profile.write(f"export DC_HOST='{ip}'")
                    else:
                        profile.write("export DC_HOST=''")
            except Exception:
                pass

    if args.command == "env":
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
