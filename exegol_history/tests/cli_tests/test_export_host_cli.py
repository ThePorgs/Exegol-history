import io
import tempfile

import pytest
from rich.console import Console
from sqlalchemy import Engine

from exegol_history.cli.arguments import parse_arguments
from exegol_history.cli.constants import (
    EXPORT_SUBCOMMAND,
    HOSTS_SUBCOMMAND,
    IMPORT_SUBCOMMAND,
)
from exegol_history.cli.functions import cli_export_objects, cli_import_objects
from exegol_history.db_api.file_types import HostsImportFileType
from exegol_history.db_api.hosts import Host, add_hosts, get_hosts
from exegol_history.tests.common import (
    HOSTNAME_TEST_VALUE,
    IP_TEST_VALUE,
    ROLE_TEST_VALUE,
    delete_all_entries,
)


def test_export_host_csv(engine: Engine, TEST_HOST2: list[Host]):
    console = Console(file=io.StringIO())

    add_hosts(engine, [host.as_dict() for host in TEST_HOST2])

    command_line = f"{EXPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.CSV.name}".split()
    args = parse_arguments().parse_args(command_line)
    cli_export_objects(args, engine, console)

    assert (
        console.file.getvalue()
        == f"ip,hostname,role\n{IP_TEST_VALUE},,{ROLE_TEST_VALUE}\n{IP_TEST_VALUE + '2'},{HOSTNAME_TEST_VALUE.lower()},{ROLE_TEST_VALUE}\n\n"
    )


def test_export_host_csv_delimiter(engine: Engine, TEST_HOST2: list[Host]):
    console = Console(file=io.StringIO())

    add_hosts(engine, [host.as_dict() for host in TEST_HOST2])

    command_line = f"{EXPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.CSV.name} --delimiter :".split()
    args = parse_arguments().parse_args(command_line)
    cli_export_objects(args, engine, console)

    assert (
        console.file.getvalue()
        == f"ip:hostname:role\n{IP_TEST_VALUE}::{ROLE_TEST_VALUE}\n{IP_TEST_VALUE + '2'}:{HOSTNAME_TEST_VALUE.lower()}:{ROLE_TEST_VALUE}\n\n"
    )

    # Now with an invalid delimiter
    command_line = f"{EXPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.CSV.name} --delimiter BAD".split()

    with pytest.raises(SystemExit) as exit:
        args = parse_arguments().parse_args(command_line)
        assert exit.value.code == 2


def test_export_host_json(engine: Engine, TEST_HOST2: list[Host]):
    console = Console(file=io.StringIO())

    add_hosts(engine, [host.as_dict() for host in TEST_HOST2])

    command_line = f"{EXPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.JSON.name}".split()
    args = parse_arguments().parse_args(command_line)
    cli_export_objects(args, engine, console)

    assert (
        console.file.getvalue()
        == f'''[
  {{
    "ip": "{IP_TEST_VALUE}",
    "hostname": "",
    "role": "{ROLE_TEST_VALUE}"
  }},
  {{
    "ip": "{IP_TEST_VALUE + "2"}",
    "hostname": "{HOSTNAME_TEST_VALUE.lower()}",
    "role": "{ROLE_TEST_VALUE}"
  }}
]
'''
    )


# Test that the export function is compatible with the import one
def test_export_import_host_csv(engine: Engine, TEST_HOST2: list[Host]):
    console = Console(file=io.StringIO())

    add_hosts(engine, [host.as_dict() for host in TEST_HOST2])

    command_line = f"{EXPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.CSV.name}".split()
    args = parse_arguments().parse_args(command_line)
    cli_export_objects(args, engine, console)

    exported_csv = console.file.getvalue()

    # Write the exported CSV into a file
    with tempfile.NamedTemporaryFile("w", delete=False) as temp_csv:
        temp_csv.write(exported_csv)
        temp_csv.seek(0)

        delete_all_entries(engine)

        assert len(get_hosts(engine)) == 0

        command_line = f"{IMPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.CSV.name} -f {temp_csv.name}".split()
        args = parse_arguments().parse_args(command_line)

        cli_import_objects(args, engine)

    assert get_hosts(engine) == TEST_HOST2


def test_export_import_host_json(engine: Engine, TEST_HOST2: list[Host]):
    console = Console(file=io.StringIO())

    add_hosts(engine, [host.as_dict() for host in TEST_HOST2])

    command_line = f"{EXPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.JSON.name}".split()
    args = parse_arguments().parse_args(command_line)
    cli_export_objects(args, engine, console)

    exported_csv = console.file.getvalue()

    # Write the exported CSV into a file
    with tempfile.NamedTemporaryFile("w", delete=False) as temp_csv:
        temp_csv.write(exported_csv)
        temp_csv.seek(0)

        delete_all_entries(engine)

        assert len(get_hosts(engine)) == 0

        command_line = f"{IMPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.JSON.name} -f {temp_csv.name}".split()
        args = parse_arguments().parse_args(command_line)

        cli_import_objects(args, engine)

    assert get_hosts(engine) == TEST_HOST2


def test_export_host_empty(engine: Engine):
    console = Console()

    command_line = f"{EXPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.CSV.name}".split()
    args = parse_arguments().parse_args(command_line)
    cli_export_objects(args, engine, console)

    command_line = f"{EXPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.JSON.name}".split()
    args = parse_arguments().parse_args(command_line)
    cli_export_objects(args, engine, console)
