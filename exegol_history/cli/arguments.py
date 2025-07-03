import argparse

from exegol_history.cli.functions import (
    ADD_SUBCOMMAND,
    CREDS_SUBCOMMAND,
    DELETE_SUBCOMMAND,
    EDIT_SUBCOMMAND,
    EXPORT_SUBCOMMAND,
    HOSTS_SUBCOMMAND,
    IMPORT_SUBCOMMAND,
    SET_SUBCOMMAND,
    SHOW_SUBCOMMAND,
    UNSET_SUBCOMMAND,
    VERSION_SUBCOMMAND,
)
from exegol_history.cli.utils import check_delimiter
from exegol_history.db_api.exporting import CredsExportFileType, HostsExportFileType
from exegol_history.db_api.importing import CredsImportFileType, HostsImportFileType


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="exegol_history",
        description="""
            Exegol-history: A tool to easily manage credentials and assets
            discovered during security engagements.
        """,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        VERSION_SUBCOMMAND,
        help="Display exegol history current version.",
    )
    subparsers.add_parser(
        SHOW_SUBCOMMAND,
        help="Display exegol history values currently set in the shell (i.e., environment variables).",
    )

    unset_subparser(subparsers)
    add_subparser(subparsers)
    import_subparser(subparsers)
    edit_subparser(subparsers)
    export_subparser(subparsers)
    delete_subparser(subparsers)
    tui_subparser(subparsers)

    return parser


def unset_subparser(subparsers):
    unset_parser = subparsers.add_parser(
        UNSET_SUBCOMMAND,
        help="Unset the currently selected credential or host.",
    )
    unset_subparsers = unset_parser.add_subparsers(
        dest="subcommand",
        required=True,
        help="Type of object to unset (creds, hosts).",
    )

    # Credentials
    unset_subparsers.add_parser(
        CREDS_SUBCOMMAND,
        help="Unset credentials variables.",
    )

    # Hosts
    unset_subparsers.add_parser(
        HOSTS_SUBCOMMAND,
        help="Unset hosts variables.",
    )


def add_subparser(subparsers):
    add_parser = subparsers.add_parser(
        ADD_SUBCOMMAND, help="Add new credentials or hosts to the database."
    )
    add_subparsers = add_parser.add_subparsers(
        dest="subcommand",
        required=True,
        help="Type of object to add (creds, hosts).",
    )

    # Credentials
    credential_add_parser = add_subparsers.add_parser(
        CREDS_SUBCOMMAND, help="Add or update credentials in the database."
    )
    credential_add_parser.add_argument(
        "-u", "--username", help="Username for the credential entry.", default=""
    )
    credential_add_parser.add_argument(
        "-p", "--password", help="Password for the credential entry.", default=""
    )
    credential_add_parser.add_argument(
        "-H",
        "--hash",
        help="Password hash (such as NTLM, MD5, etc.) for the credential entry.",
        default="",
    )
    credential_add_parser.add_argument(
        "-d",
        "--domain",
        help="Domain associated with the credential entry.",
        default="",
    )

    # Hosts
    hosts_add_parser = add_subparsers.add_parser(
        HOSTS_SUBCOMMAND, help="Add or update host information in the database."
    )
    hosts_add_parser.add_argument("--ip", help="IP address of the host.", default="")
    hosts_add_parser.add_argument(
        "-r",
        "--role",
        help="Role of the host in the environment (e.g., SCCM, ADCS, DC, WKS).",
        default="",
    )
    hosts_add_parser.add_argument(
        "-n", "--hostname", help="Hostname or NetBIOS name of the host.", default=""
    )


def import_subparser(subparsers):
    import_parser = subparsers.add_parser(
        IMPORT_SUBCOMMAND,
        help="Import credentials or hosts from the database in various formats.",
    )
    import_subparsers = import_parser.add_subparsers(
        dest="subcommand",
        required=True,
        help="Type of object to import (creds, hosts).",
    )

    # Credentials
    credential_import_parser = import_subparsers.add_parser(
        CREDS_SUBCOMMAND, help="Import credential information from a file."
    )
    credential_import_parser.add_argument(
        "-f",
        "--file",
        help="The file from where to import credentials.",
        required=True,
    )
    credential_import_parser.add_argument(
        "--format",
        choices=[cred_type.name for cred_type in CredsImportFileType],
        help="Type of file being imported (JSON, CSV, PYPYKATZ).",
        required=True,
    )
    credential_import_parser.add_argument(
        "--kdbx-password",
        help="Patssword of the Keepass database to import credentials from.",
    )
    credential_import_parser.add_argument(
        "--kdbx-keyfile",
        help="Keyfile of the Keepass database to import credentials from.",
    )

    # Hosts
    hosts_import_parser = import_subparsers.add_parser(
        HOSTS_SUBCOMMAND, help="Import hosts information from a file."
    )
    hosts_import_parser.add_argument(
        "-f",
        "--file",
        help="The file from where to import hosts.",
        required=True,
    )
    hosts_import_parser.add_argument(
        "--format",
        choices=[host_type.name for host_type in HostsImportFileType],
        required=True,
        help="Type of file being imported (json, csv, pypykatz).",
    )


def edit_subparser(subparsers):
    edit_parser = subparsers.add_parser(
        EDIT_SUBCOMMAND, help="Add new credentials or hosts to the database."
    )
    edit_subparsers = edit_parser.add_subparsers(
        dest="subcommand",
        required=True,
        help="Type of object to add (creds, hosts).",
    )

    # Credentials
    credential_edit_parser = edit_subparsers.add_parser(
        CREDS_SUBCOMMAND, help="Edit credential in the database."
    )
    credential_edit_parser.add_argument(
        "-i",
        "--id",
        required=True,
        help="ID used to know which credentials to edit.",
    )
    credential_edit_parser.add_argument(
        "-u", "--username", help="Username for the credential entry.", default=""
    )
    credential_edit_parser.add_argument(
        "-p", "--password", help="Password for the credential entry.", default=""
    )
    credential_edit_parser.add_argument(
        "-H",
        "--hash",
        help="Password hash (such as NTLM, MD5, etc.) for the credential entry.",
        default="",
    )
    credential_edit_parser.add_argument(
        "-d",
        "--domain",
        help="Domain associated with the credential entry.",
        default="",
    )

    # Hosts
    hosts_edit_parser = edit_subparsers.add_parser(
        HOSTS_SUBCOMMAND, help="Edit host information in the database."
    )
    hosts_edit_parser.add_argument(
        "-i",
        "--id",
        required=True,
        help="ID used to know which hosts to edit.",
    )
    hosts_edit_parser.add_argument(
        "--ip",
        help="IP address of the host.",
        default="",
    )
    hosts_edit_parser.add_argument(
        "-r",
        "--role",
        help="Role of the host in the environment (e.g., SCCM, ADCS, DC, WKS).",
        default="",
    )
    hosts_edit_parser.add_argument(
        "-n",
        "--hostname",
        help="Hostname or NetBIOS name of the host.",
        default="",
    )


def export_subparser(subparsers):
    export_parser = subparsers.add_parser(
        EXPORT_SUBCOMMAND,
        help="Export credentials or hosts from the database in various formats.",
    )
    export_subparsers = export_parser.add_subparsers(
        dest="subcommand",
        required=True,
        help="Type of object to export (creds, hosts).",
    )

    # Credentials
    credential_export_parser = export_subparsers.add_parser(
        CREDS_SUBCOMMAND, help="Export credential information from the database."
    )
    credential_export_parser.add_argument(
        "--format",
        choices=[cred_type.name for cred_type in CredsExportFileType],
        default=CredsExportFileType.CSV.name,
        help="Format of exporting.",
        required=True,
    )
    credential_export_parser.add_argument(
        "--delimiter",
        type=check_delimiter,
        help="Delimiter used to separate columns.",
    )
    credential_export_parser.add_argument(
        "-r",
        "--redacted",
        action="store_true",
        help="Mask sensitive information like passwords and hashes in the output.",
    )
    credential_export_parser.add_argument(
        "-f", "--file", help="The file from where to export creds."
    )

    # Hosts
    hosts_export_parser = export_subparsers.add_parser(
        HOSTS_SUBCOMMAND, help="Export host information from the database."
    )
    hosts_export_parser.add_argument(
        "--format",
        choices=[host_type.name for host_type in HostsExportFileType],
        default=HostsExportFileType.CSV,
        help="Format of exporting.",
        required=True,
    )
    hosts_export_parser.add_argument(
        "--delimiter",
        type=check_delimiter,
        help="Delimiter used to separate columns.",
    )
    hosts_export_parser.add_argument(
        "-f", "--file", help="The file from where to export hosts."
    )


def delete_subparser(subparsers):
    delete_parser = subparsers.add_parser(
        DELETE_SUBCOMMAND,
        help="Remove existing credentials or hosts from the database.",
    )
    delete_subparsers = delete_parser.add_subparsers(
        dest="subcommand",
        required=True,
        help="Type of object to remove (creds, hosts).",
    )

    # Credentials
    credential_delete_parser = delete_subparsers.add_parser(
        CREDS_SUBCOMMAND, help="Delete credentials from the database."
    )
    credential_delete_parser.add_argument(
        "-i",
        "--id",
        help="IDs of the credentials to be deleted, value are separated by a ',', and ranges by a '-', e.g: '5,7,8-18'.",
    )

    # Hosts
    hosts_delete_parser = delete_subparsers.add_parser(
        HOSTS_SUBCOMMAND, help="Delete hosts from the database."
    )
    hosts_delete_parser.add_argument(
        "-i",
        "--id",
        required=True,
        help="IDs of the hosts to be deleted, value are separated by a ',', and ranges by a '-', e.g: '5,7,8-18'.",
    )


def tui_subparser(subparsers):
    tui_parser = subparsers.add_parser(
        SET_SUBCOMMAND,
        help="Select credentials or assets and set them in the current shell to use with the preset history commands.",
    )
    tui_subparsers = tui_parser.add_subparsers(
        dest="subcommand",
        required=True,
        help="Type of object to manage in the TUI (creds, hosts).",
    )

    # Credentials
    tui_subparsers.add_parser(
        CREDS_SUBCOMMAND,
        help="Manage credentials using the TUI and set related environment variables.",
    )

    # Hosts
    tui_subparsers.add_parser(
        HOSTS_SUBCOMMAND,
        help="Manage hosts using the TUI and set related environment variables.",
    )
