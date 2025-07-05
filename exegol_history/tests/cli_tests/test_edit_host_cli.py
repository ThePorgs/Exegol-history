import io
from pykeepass import PyKeePass
from exegol_history.cli.arguments import parse_arguments
from exegol_history.cli.functions import EDIT_SUBCOMMAND, HOSTS_SUBCOMMAND, edit_object
from exegol_history.db_api.hosts import Host, add_hosts, get_hosts
from exegol_history.db_api.utils import MESSAGE_ID_NOT_EXIST
from exegol_history.tests.common import (
    HOSTNAME_TEST_VALUE,
    IP_TEST_VALUE,
    ROLE_TEST_VALUE,
)
from rich.console import Console


def test_edit_host_only_ip(open_keepass: PyKeePass):
    kp = open_keepass
    host = Host(ip=IP_TEST_VALUE)

    add_hosts(kp, [host])

    command_line = f"{EDIT_SUBCOMMAND} {HOSTS_SUBCOMMAND} -i {host.id} --ip {IP_TEST_VALUE + '2'}".split()
    args = parse_arguments().parse_args(command_line)

    edit_object(args, kp, {})
    host.ip = IP_TEST_VALUE + "2"

    assert get_hosts(kp) == [host]


def test_edit_host_half(open_keepass: PyKeePass):
    kp = open_keepass
    host = Host(ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE)

    add_hosts(kp, [host])

    command_line = f"{EDIT_SUBCOMMAND} {HOSTS_SUBCOMMAND} -i {host.id} --ip {IP_TEST_VALUE + '2'} --hostname {HOSTNAME_TEST_VALUE + '2'}".split()
    args = parse_arguments().parse_args(command_line)

    edit_object(args, kp, {})
    host.ip = IP_TEST_VALUE + "2"
    host.hostname = HOSTNAME_TEST_VALUE + "2"

    assert get_hosts(kp) == [host]


def test_edit_host_full(open_keepass: PyKeePass):
    kp = open_keepass
    host = Host(ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE, role=ROLE_TEST_VALUE)

    add_hosts(kp, [host])

    command_line = f"{EDIT_SUBCOMMAND} {HOSTS_SUBCOMMAND} -i {host.id} --ip {IP_TEST_VALUE + '2'} --hostname {HOSTNAME_TEST_VALUE + '2'} --role {ROLE_TEST_VALUE + '2'}".split()
    args = parse_arguments().parse_args(command_line)

    edit_object(args, kp, {})
    host.ip = IP_TEST_VALUE + "2"
    host.hostname = HOSTNAME_TEST_VALUE + "2"
    host.role = ROLE_TEST_VALUE + "2"

    assert get_hosts(kp) == [host]


def test_edit_host_not_exist(open_keepass: PyKeePass):
    kp = open_keepass
    console = Console(file=io.StringIO())

    command_line = f"{EDIT_SUBCOMMAND} {HOSTS_SUBCOMMAND} -i 999".split()
    args = parse_arguments().parse_args(command_line)

    edit_object(args, kp, console)

    assert MESSAGE_ID_NOT_EXIST in console.file.getvalue().replace("\n", "")
    assert len(get_hosts(kp)) == 0
