import io
from pykeepass import PyKeePass
from rich.console import Console
from exegol_history.cli.arguments import parse_arguments
from exegol_history.cli.functions import (
    DELETE_SUBCOMMAND,
    HOSTS_SUBCOMMAND,
    delete_objects,
)
from exegol_history.db_api.hosts import Host, add_hosts, get_hosts
from exegol_history.db_api.utils import MESSAGE_ID_NOT_EXIST
from exegol_history.tests.common import (
    HOSTNAME_TEST_VALUE,
    IP_TEST_VALUE,
)


def test_delete_host(open_keepass: PyKeePass):
    kp = open_keepass

    host1 = Host(ip=IP_TEST_VALUE + "2", hostname=HOSTNAME_TEST_VALUE + "2")
    host2 = Host(ip=IP_TEST_VALUE)
    host3 = Host(ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE)

    add_hosts(kp, [host1, host2, host3])

    command_line = f"{DELETE_SUBCOMMAND} {HOSTS_SUBCOMMAND} -i 2".split()
    args = parse_arguments().parse_args(command_line)

    delete_objects(args, kp, {})

    assert get_hosts(kp) == [host1, host3]


def test_delete_host_range(open_keepass: PyKeePass):
    kp = open_keepass

    host1 = Host(ip=IP_TEST_VALUE + "2", hostname=HOSTNAME_TEST_VALUE + "2")
    host2 = Host(ip=IP_TEST_VALUE)
    host3 = Host(ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE)
    host4 = Host(ip=IP_TEST_VALUE + "4", hostname=HOSTNAME_TEST_VALUE)
    host5 = Host(ip=IP_TEST_VALUE + "5", hostname=HOSTNAME_TEST_VALUE)

    add_hosts(kp, [host1, host2, host3, host4, host5])

    command_line = f"{DELETE_SUBCOMMAND} {HOSTS_SUBCOMMAND} -i 1-3,5".split()
    args = parse_arguments().parse_args(command_line)

    delete_objects(args, kp, {})

    assert get_hosts(kp) == [host4]


def test_delete_host_not_exist(open_keepass: PyKeePass):
    kp = open_keepass
    console = Console(file=io.StringIO())

    command_line = f"{DELETE_SUBCOMMAND} {HOSTS_SUBCOMMAND} -i 999".split()
    args = parse_arguments().parse_args(command_line)

    delete_objects(args, kp, console)

    assert MESSAGE_ID_NOT_EXIST in console.file.getvalue().replace("\n", "")
    assert len(get_hosts(kp)) == 0
