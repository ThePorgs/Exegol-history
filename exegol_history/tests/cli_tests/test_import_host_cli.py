import tempfile

import pytest
from sqlalchemy import Engine

from exegol_history.cli.arguments import parse_arguments
from exegol_history.cli.constants import HOSTS_SUBCOMMAND, IMPORT_SUBCOMMAND
from exegol_history.cli.functions import cli_import_objects
from exegol_history.db_api.hosts import Host, get_hosts
from exegol_history.db_api.importing import HostsImportFileType
from exegol_history.tests.common import (
    TEST_HOSTS_CSV_COLON,
    TEST_HOSTS_CSV_COMMA,
    TEST_HOSTS_JSON,
    delete_all_entries,
)


def test_import_host_csv(engine: Engine, HOSTS_TEST_VALUE: list[Host]):
    # Comma
    command_line = f"{IMPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.CSV.name} -f {TEST_HOSTS_CSV_COMMA}".split()
    args = parse_arguments().parse_args(command_line)

    cli_import_objects(args, engine)

    assert get_hosts(engine) == HOSTS_TEST_VALUE

    delete_all_entries(engine)

    # Colon
    command_line = f"{IMPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.CSV.name} -f {TEST_HOSTS_CSV_COLON}".split()
    args = parse_arguments().parse_args(command_line)

    cli_import_objects(args, engine)

    assert get_hosts(engine) == HOSTS_TEST_VALUE


def test_import_host_json(engine: Engine, HOSTS_TEST_VALUE: list[Host]):
    command_line = f"{IMPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.JSON.name} -f {TEST_HOSTS_JSON}".split()
    args = parse_arguments().parse_args(command_line)

    cli_import_objects(args, engine)

    assert get_hosts(engine) == HOSTS_TEST_VALUE


def test_import_host_bad_format(engine: Engine):
    # Write the exported CSV into a file
    with tempfile.NamedTemporaryFile("w", delete=False) as temp_csv:
        temp_csv.write("test,test2,test3\ntest")
        temp_csv.seek(0)

        command_line = f"{IMPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.CSV.name} -f {temp_csv.name}".split()
        args = parse_arguments().parse_args(command_line)

        with pytest.raises(Exception):
            cli_import_objects(args, engine)
