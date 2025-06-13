import tempfile
import pytest
from pykeepass import PyKeePass
from exegol_history.cli.arguments import parse_arguments
from exegol_history.cli.functions import (
    HOSTS_SUBCOMMAND,
    IMPORT_SUBCOMMAND,
    cli_import_objects,
)
from exegol_history.db_api.hosts import get_hosts
from exegol_history.db_api.importing import HostsImportFileType
from exegol_history.tests.common import (
    HOSTS_TEST_VALUE,
    TEST_HOSTS_CSV_COLON,
    TEST_HOSTS_CSV_COMMA,
    TEST_HOSTS_JSON,
    delete_all_entries,
)


def test_import_host_csv(open_keepass: PyKeePass):
    kp = open_keepass

    # Comma
    command_line = f"{IMPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.CSV.name} -f {TEST_HOSTS_CSV_COMMA}".split()
    args = parse_arguments().parse_args(command_line)

    cli_import_objects(args, kp)

    assert get_hosts(kp) == HOSTS_TEST_VALUE

    delete_all_entries(kp)

    # Colon
    command_line = f"{IMPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.CSV.name} -f {TEST_HOSTS_CSV_COLON}".split()
    args = parse_arguments().parse_args(command_line)

    cli_import_objects(args, kp)

    assert get_hosts(kp) == HOSTS_TEST_VALUE


def test_import_host_json(open_keepass: PyKeePass):
    kp = open_keepass

    command_line = f"{IMPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.JSON.name} -f {TEST_HOSTS_JSON}".split()
    args = parse_arguments().parse_args(command_line)

    cli_import_objects(args, kp)

    assert get_hosts(kp) == HOSTS_TEST_VALUE


def test_import_host_bad_format(open_keepass: PyKeePass):
    kp = open_keepass

    # Write the exported CSV into a file
    temp_csv = tempfile.NamedTemporaryFile("w", delete=False)
    temp_csv.write("test,test2,test3\ntest")
    temp_csv.seek(0)

    command_line = f"{IMPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.CSV.name} -f {temp_csv.name}".split()
    args = parse_arguments().parse_args(command_line)

    with pytest.raises(TypeError):
        cli_import_objects(args, kp)

    temp_csv.close()
