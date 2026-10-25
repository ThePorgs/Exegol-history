import io

from rich.console import Console
from sqlalchemy import Engine

from exegol_history.cli.arguments import parse_arguments
from exegol_history.cli.constants import EDIT_SUBCOMMAND, HOSTS_SUBCOMMAND
from exegol_history.cli.functions import edit_object
from exegol_history.db_api.hosts import Host, add_hosts, get_hosts
from exegol_history.db_api.utils import MESSAGE_ID_NOT_EXIST
from exegol_history.tests.common import (
    HOSTNAME_TEST_VALUE,
    IP_TEST_VALUE,
    ROLE_TEST_VALUE,
)


def test_edit_host_only_ip(engine: Engine):
    host = Host(1, ip=IP_TEST_VALUE)

    add_hosts(engine, [host.as_dict()])

    command_line = f"{EDIT_SUBCOMMAND} {HOSTS_SUBCOMMAND} -i {host.host_id} --ip {IP_TEST_VALUE + '2'}".split()
    args = parse_arguments().parse_args(command_line)

    edit_object(args, engine, {})
    host.ip = IP_TEST_VALUE + "2"

    assert get_hosts(engine) == [host]


def test_edit_host_half(engine: Engine):
    host = Host(1, ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE)

    add_hosts(engine, [host.as_dict()])

    command_line = f"{EDIT_SUBCOMMAND} {HOSTS_SUBCOMMAND} -i {host.host_id} --ip {IP_TEST_VALUE + '2'} --hostname {HOSTNAME_TEST_VALUE + '2'}".split()
    args = parse_arguments().parse_args(command_line)

    edit_object(args, engine, {})
    host.ip = IP_TEST_VALUE + "2"
    host.hostname = HOSTNAME_TEST_VALUE + "2"

    assert get_hosts(engine) == [host]


def test_edit_host_full(engine: Engine):
    host = Host(1, ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE, role=ROLE_TEST_VALUE)

    add_hosts(engine, [host.as_dict()])

    command_line = f"{EDIT_SUBCOMMAND} {HOSTS_SUBCOMMAND} -i {host.host_id} --ip {IP_TEST_VALUE + '2'} --hostname {HOSTNAME_TEST_VALUE + '2'} --role {ROLE_TEST_VALUE + '2'}".split()
    args = parse_arguments().parse_args(command_line)

    edit_object(args, engine, {})
    host.ip = IP_TEST_VALUE + "2"
    host.hostname = HOSTNAME_TEST_VALUE + "2"
    host.role = ROLE_TEST_VALUE + "2"

    assert get_hosts(engine) == [host]


def test_edit_host_not_exist(engine: Engine):
    console = Console(file=io.StringIO())

    command_line = f"{EDIT_SUBCOMMAND} {HOSTS_SUBCOMMAND} -i 999".split()
    args = parse_arguments().parse_args(command_line)

    edit_object(args, engine, console)

    assert MESSAGE_ID_NOT_EXIST in console.file.getvalue().replace("\n", "")
    assert len(get_hosts(engine)) == 0
