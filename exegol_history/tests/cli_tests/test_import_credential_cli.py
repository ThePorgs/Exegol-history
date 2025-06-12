import tempfile
import pytest
from pykeepass import PyKeePass
from exegol_history.cli.arguments import parse_arguments
from exegol_history.cli.functions import (
    CREDS_SUBCOMMAND,
    IMPORT_SUBCOMMAND,
    cli_import_objects,
)
from exegol_history.db_api.creds import Credential, get_credentials
from exegol_history.db_api.importing import CredsImportFileType
from exegol_history.tests.common import (
    CREDENTIALS_TEST_VALUE,
    CREDENTIALS_TEST_VALUE_GOAD_PYPYKATZ,
    CREDENTIALS_TEST_VALUE_GOAD_SECRETSDUMP,
    PASSWORD_TEST_VALUE,
    TEST_CREDS_CSV_COLON,
    TEST_CREDS_CSV_COMMA,
    TEST_CREDS_JSON,
    TEST_CREDS_KDBX,
    TEST_CREDS_KDBX_KEYFILE,
    TEST_CREDS_PYPYKATZ_JSON,
    TEST_CREDS_SECRETSDUMP,
    USERNAME_TEST_VALUE,
    delete_all_entries,
)


def test_import_credential_csv(open_keepass: PyKeePass):
    kp = open_keepass

    # Comma
    command_line = f"{IMPORT_SUBCOMMAND} {CREDS_SUBCOMMAND} --format {CredsImportFileType.CSV.name} -f {TEST_CREDS_CSV_COMMA}".split()
    args = parse_arguments().parse_args(command_line)

    cli_import_objects(args, kp)

    assert get_credentials(kp) == CREDENTIALS_TEST_VALUE

    delete_all_entries(kp)

    # Colon
    command_line = f"{IMPORT_SUBCOMMAND} {CREDS_SUBCOMMAND} --format {CredsImportFileType.CSV.name} -f {TEST_CREDS_CSV_COLON}".split()
    args = parse_arguments().parse_args(command_line)

    cli_import_objects(args, kp)

    assert get_credentials(kp) == CREDENTIALS_TEST_VALUE


def test_import_credential_json(open_keepass: PyKeePass):
    kp = open_keepass

    command_line = f"{IMPORT_SUBCOMMAND} {CREDS_SUBCOMMAND} --format {CredsImportFileType.JSON.name} -f {TEST_CREDS_JSON}".split()
    args = parse_arguments().parse_args(command_line)

    cli_import_objects(args, kp)

    assert get_credentials(kp) == CREDENTIALS_TEST_VALUE


def test_import_credential_kdbx(open_keepass: PyKeePass):
    kp = open_keepass

    command_line = f"{IMPORT_SUBCOMMAND} {CREDS_SUBCOMMAND} --format {CredsImportFileType.KDBX.name} -f {TEST_CREDS_KDBX} --kdbx-password {PASSWORD_TEST_VALUE} --kdbx-keyfile {TEST_CREDS_KDBX_KEYFILE}".split()
    args = parse_arguments().parse_args(command_line)

    cli_import_objects(args, kp)

    assert get_credentials(kp) == [
        Credential("1", username=USERNAME_TEST_VALUE, password=PASSWORD_TEST_VALUE),
        Credential(
            "2", username=USERNAME_TEST_VALUE + "2", password=PASSWORD_TEST_VALUE + "2"
        ),
    ]


def test_import_credential_pypykatz_json(open_keepass: PyKeePass):
    kp = open_keepass

    # Write the exported CSV into a file
    temp_csv = tempfile.NamedTemporaryFile("w")
    temp_csv.write("test,test2,test3\ntest")
    temp_csv.seek(0)

    command_line = f"{IMPORT_SUBCOMMAND} {CREDS_SUBCOMMAND} --format {CredsImportFileType.PYPYKATZ_JSON.name} -f {TEST_CREDS_PYPYKATZ_JSON}".split()
    args = parse_arguments().parse_args(command_line)
    cli_import_objects(args, kp)

    assert get_credentials(kp) == CREDENTIALS_TEST_VALUE_GOAD_PYPYKATZ


def test_import_credential_secretsdump(open_keepass: PyKeePass):
    kp = open_keepass

    command_line = f"{IMPORT_SUBCOMMAND} {CREDS_SUBCOMMAND} --format {CredsImportFileType.SECRETSDUMP.name} -f {TEST_CREDS_SECRETSDUMP}".split()
    args = parse_arguments().parse_args(command_line)
    cli_import_objects(args, kp)

    assert get_credentials(kp) == CREDENTIALS_TEST_VALUE_GOAD_SECRETSDUMP


def test_import_credential_bad_format(open_keepass: PyKeePass):
    kp = open_keepass

    # Write the exported CSV into a file
    temp_csv = tempfile.NamedTemporaryFile("w")
    temp_csv.write("test,test2,test3\ntest")
    temp_csv.seek(0)

    command_line = f"{IMPORT_SUBCOMMAND} {CREDS_SUBCOMMAND} --format {CredsImportFileType.CSV.name} -f {temp_csv.name}".split()
    args = parse_arguments().parse_args(command_line)

    with pytest.raises(TypeError):
        cli_import_objects(args, kp)

    temp_csv.close()
