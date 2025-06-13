import io
import tempfile
from pykeepass import PyKeePass
from rich.console import Console
from exegol_history.cli.arguments import parse_arguments
from exegol_history.cli.functions import (
    EXPORT_SUBCOMMAND,
    HOSTS_SUBCOMMAND,
    IMPORT_SUBCOMMAND,
    cli_export_objects,
    cli_import_objects,
)
from exegol_history.db_api.hosts import Host, add_hosts, get_hosts
from exegol_history.db_api.importing import HostsImportFileType
from exegol_history.tests.common import (
    HOSTNAME_TEST_VALUE,
    IP_TEST_VALUE,
    ROLE_TEST_VALUE,
    delete_all_entries,
)
import pytest

HOST1 = Host(ip=IP_TEST_VALUE, role=ROLE_TEST_VALUE)
HOST2 = Host(ip=IP_TEST_VALUE + "2", hostname=HOSTNAME_TEST_VALUE, role=ROLE_TEST_VALUE)


def test_export_host_csv(open_keepass: PyKeePass):
    kp = open_keepass
    console = Console(file=io.StringIO())

    add_hosts(kp, [HOST1, HOST2])

    command_line = f"{EXPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.CSV.name}".split()
    args = parse_arguments().parse_args(command_line)
    cli_export_objects(args, kp, console)

    assert (
        console.file.getvalue()
        == f"ip,hostname,role\n{IP_TEST_VALUE},,{ROLE_TEST_VALUE}\n{IP_TEST_VALUE + '2'},{HOSTNAME_TEST_VALUE},{ROLE_TEST_VALUE}\n\n"
    )


def test_export_host_csv_delimiter(open_keepass: PyKeePass):
    kp = open_keepass
    console = Console(file=io.StringIO())

    add_hosts(kp, [HOST1, HOST2])

    command_line = f"{EXPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.CSV.name} --delimiter :".split()
    args = parse_arguments().parse_args(command_line)
    cli_export_objects(args, kp, console)

    assert (
        console.file.getvalue()
        == f"ip:hostname:role\n{IP_TEST_VALUE}::{ROLE_TEST_VALUE}\n{IP_TEST_VALUE + '2'}:{HOSTNAME_TEST_VALUE}:{ROLE_TEST_VALUE}\n\n"
    )

    # Now with an invalid delimiter
    command_line = f"{EXPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.CSV.name} --delimiter BAD".split()

    with pytest.raises(SystemExit) as exit:
        args = parse_arguments().parse_args(command_line)
        assert exit.value.code == 2


def test_export_host_json(open_keepass: PyKeePass):
    kp = open_keepass
    console = Console(file=io.StringIO())

    add_hosts(kp, [HOST1, HOST2])

    command_line = f"{EXPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.JSON.name}".split()
    args = parse_arguments().parse_args(command_line)
    cli_export_objects(args, kp, console)

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
    "hostname": "{HOSTNAME_TEST_VALUE}",
    "role": "{ROLE_TEST_VALUE}"
  }}
]
'''
    )


# Test that the export function is compatible with the import one
def test_export_import_host_csv(open_keepass: PyKeePass):
    kp = open_keepass
    console = Console(file=io.StringIO())

    add_hosts(kp, [HOST1, HOST2])

    command_line = f"{EXPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.CSV.name}".split()
    args = parse_arguments().parse_args(command_line)
    cli_export_objects(args, kp, console)

    exported_csv = console.file.getvalue()

    # Write the exported CSV into a file
    temp_csv = tempfile.NamedTemporaryFile("w", delete=False)
    temp_csv.write(exported_csv)
    temp_csv.seek(0)

    delete_all_entries(kp)

    assert len(get_hosts(kp)) == 0

    command_line = f"{IMPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.CSV.name} -f {temp_csv.name}".split()
    args = parse_arguments().parse_args(command_line)

    cli_import_objects(args, kp)

    temp_csv.close()

    assert get_hosts(kp) == [HOST1, HOST2]


def test_export_import_host_json(open_keepass: PyKeePass):
    kp = open_keepass
    console = Console(file=io.StringIO())

    add_hosts(kp, [HOST1, HOST2])

    command_line = f"{EXPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.JSON.name}".split()
    args = parse_arguments().parse_args(command_line)
    cli_export_objects(args, kp, console)

    exported_csv = console.file.getvalue()

    # Write the exported CSV into a file
    temp_csv = tempfile.NamedTemporaryFile("w", delete=False)
    temp_csv.write(exported_csv)
    temp_csv.seek(0)

    delete_all_entries(kp)

    assert len(get_hosts(kp)) == 0

    command_line = f"{IMPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.JSON.name} -f {temp_csv.name}".split()
    args = parse_arguments().parse_args(command_line)

    cli_import_objects(args, kp)

    temp_csv.close()

    assert get_hosts(kp) == [HOST1, HOST2]


def test_export_host_empty(open_keepass: PyKeePass):
    kp = open_keepass
    console = Console()

    command_line = f"{EXPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.CSV.name}".split()
    args = parse_arguments().parse_args(command_line)
    cli_export_objects(args, kp, console)

    command_line = f"{EXPORT_SUBCOMMAND} {HOSTS_SUBCOMMAND} --format {HostsImportFileType.JSON.name}".split()
    args = parse_arguments().parse_args(command_line)
    cli_export_objects(args, kp, console)
