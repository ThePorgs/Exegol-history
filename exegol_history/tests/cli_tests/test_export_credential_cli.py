import io
import tempfile

import pytest
from rich.console import Console
from sqlalchemy import Engine

from exegol_history.cli.arguments import parse_arguments
from exegol_history.cli.constants import (
    CREDS_SUBCOMMAND,
    EXPORT_SUBCOMMAND,
    IMPORT_SUBCOMMAND,
)
from exegol_history.cli.functions import cli_export_objects, cli_import_objects
from exegol_history.db_api.creds import (
    Credential,
    add_credentials,
    get_credentials,
)
from exegol_history.db_api.file_types import CredsImportFileType
from exegol_history.tests.common import (
    DOMAIN_TEST_VALUE,
    HASH_TEST_VALUE,
    PASSWORD_TEST_VALUE,
    USERNAME_TEST_VALUE,
    delete_all_entries,
)


def test_export_credential_csv(engine: Engine, TEST_CREDENTIAL2: list[Credential]):
    console = Console(file=io.StringIO())

    add_credentials(engine, [credential.as_dict() for credential in TEST_CREDENTIAL2])

    command_line = f"{EXPORT_SUBCOMMAND} {CREDS_SUBCOMMAND} --format {CredsImportFileType.CSV.name}".split()
    args = parse_arguments().parse_args(command_line)
    cli_export_objects(args, engine, console)

    assert (
        console.file.getvalue()
        == f"username,password,hash,domain\n{USERNAME_TEST_VALUE},,{HASH_TEST_VALUE},\n{USERNAME_TEST_VALUE + '2'},{PASSWORD_TEST_VALUE},{HASH_TEST_VALUE},{DOMAIN_TEST_VALUE}\n\n"
    )


def test_export_credential_csv_delimiter(
    engine: Engine, TEST_CREDENTIAL2: list[Credential]
):
    console = Console(file=io.StringIO())

    add_credentials(engine, [credential.as_dict() for credential in TEST_CREDENTIAL2])

    command_line = f"{EXPORT_SUBCOMMAND} {CREDS_SUBCOMMAND} --format {CredsImportFileType.CSV.name} --delimiter :".split()
    args = parse_arguments().parse_args(command_line)
    cli_export_objects(args, engine, console)

    assert (
        console.file.getvalue()
        == f"username:password:hash:domain\n{USERNAME_TEST_VALUE}::{HASH_TEST_VALUE}:\n{USERNAME_TEST_VALUE + '2'}:{PASSWORD_TEST_VALUE}:{HASH_TEST_VALUE}:{DOMAIN_TEST_VALUE}\n\n"
    )

    # Now with an invalid delimiter
    command_line = f"{EXPORT_SUBCOMMAND} {CREDS_SUBCOMMAND} --format {CredsImportFileType.CSV.name} --delimiter BAD".split()

    with pytest.raises(SystemExit) as exit:
        args = parse_arguments().parse_args(command_line)
        assert exit.value.code == 2


def test_export_credential_json(engine: Engine, TEST_CREDENTIAL2: list[Credential]):
    console = Console(file=io.StringIO())

    add_credentials(engine, [credential.as_dict() for credential in TEST_CREDENTIAL2])

    command_line = f"{EXPORT_SUBCOMMAND} {CREDS_SUBCOMMAND} --format {CredsImportFileType.JSON.name}".split()
    args = parse_arguments().parse_args(command_line)
    cli_export_objects(args, engine, console)

    assert (
        console.file.getvalue()
        == f'''[
  {{
    "username": "{USERNAME_TEST_VALUE}",
    "password": "",
    "hash": "{HASH_TEST_VALUE}",
    "domain": ""
  }},
  {{
    "username": "{USERNAME_TEST_VALUE + "2"}",
    "password": "{PASSWORD_TEST_VALUE}",
    "hash": "{HASH_TEST_VALUE}",
    "domain": "{DOMAIN_TEST_VALUE}"
  }}
]
'''
    )


def test_export_credential_redacted(engine: Engine, TEST_CREDENTIAL2: list[Credential]):
    console = Console(file=io.StringIO())

    add_credentials(engine, [credential.as_dict() for credential in TEST_CREDENTIAL2])

    command_line = f"{EXPORT_SUBCOMMAND} {CREDS_SUBCOMMAND} --format {CredsImportFileType.CSV.name} --redacted".split()
    args = parse_arguments().parse_args(command_line)
    cli_export_objects(args, engine, console)

    assert PASSWORD_TEST_VALUE + "3453645456" not in console.file.getvalue()


# Test that the export function is compatible with the import one
def test_export_import_credential_csv(
    engine: Engine, TEST_CREDENTIAL2: list[Credential]
):
    console = Console(file=io.StringIO())

    add_credentials(engine, [credential.as_dict() for credential in TEST_CREDENTIAL2])

    command_line = f"{EXPORT_SUBCOMMAND} {CREDS_SUBCOMMAND} --format {CredsImportFileType.CSV.name}".split()
    args = parse_arguments().parse_args(command_line)
    cli_export_objects(args, engine, console)

    exported_csv = console.file.getvalue()

    # Write the exported CSV into a file
    with tempfile.NamedTemporaryFile("w", delete=False) as temp_csv:
        temp_csv.write(exported_csv)
        temp_csv.seek(0)

        delete_all_entries(engine)

        assert len(get_credentials(engine)) == 0

        command_line = f"{IMPORT_SUBCOMMAND} {CREDS_SUBCOMMAND} --format {CredsImportFileType.CSV.name} -f {temp_csv.name}".split()
        args = parse_arguments().parse_args(command_line)

        cli_import_objects(args, engine)

    assert get_credentials(engine) == TEST_CREDENTIAL2


def test_export_import_credential_json(
    engine: Engine, TEST_CREDENTIAL2: list[Credential]
):
    console = Console(file=io.StringIO())

    add_credentials(engine, [credential.as_dict() for credential in TEST_CREDENTIAL2])

    command_line = f"{EXPORT_SUBCOMMAND} {CREDS_SUBCOMMAND} --format {CredsImportFileType.JSON.name}".split()
    args = parse_arguments().parse_args(command_line)
    cli_export_objects(args, engine, console)

    exported_csv = console.file.getvalue()

    # Write the exported CSV into a file
    with tempfile.NamedTemporaryFile("w", delete=False) as temp_csv:
        temp_csv.write(exported_csv)
        temp_csv.seek(0)

        delete_all_entries(engine)

        assert len(get_credentials(engine)) == 0

        command_line = f"{IMPORT_SUBCOMMAND} {CREDS_SUBCOMMAND} --format {CredsImportFileType.JSON.name} -f {temp_csv.name}".split()
        args = parse_arguments().parse_args(command_line)

        cli_import_objects(args, engine)

    assert get_credentials(engine) == TEST_CREDENTIAL2


def test_export_credential_empty(engine: Engine):
    console = Console()

    command_line = f"{EXPORT_SUBCOMMAND} {CREDS_SUBCOMMAND} --format {CredsImportFileType.CSV.name}".split()
    args = parse_arguments().parse_args(command_line)
    cli_export_objects(args, engine, console)

    command_line = f"{EXPORT_SUBCOMMAND} {CREDS_SUBCOMMAND} --format {CredsImportFileType.JSON.name}".split()
    args = parse_arguments().parse_args(command_line)
    cli_export_objects(args, engine, console)
