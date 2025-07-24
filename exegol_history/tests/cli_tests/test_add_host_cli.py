from pykeepass import PyKeePass
from exegol_history.cli.arguments import parse_arguments
from exegol_history.cli.functions import ADD_SUBCOMMAND, HOSTS_SUBCOMMAND, add_object
from exegol_history.db_api.hosts import Host, get_hosts
from exegol_history.tests.common import (
    HOSTNAME_TEST_VALUE,
    IP_TEST_VALUE,
    ROLE_TEST_VALUE,
)


def test_add_host_only_ip(open_keepass: PyKeePass):
    kp = open_keepass

    command_line = f"{ADD_SUBCOMMAND} {HOSTS_SUBCOMMAND} --ip {IP_TEST_VALUE}".split()
    args = parse_arguments().parse_args(command_line)

    add_object(args, kp, {})

    assert get_hosts(kp) == [Host(id="1", ip=IP_TEST_VALUE)]


def test_add_host_half(open_keepass: PyKeePass):
    kp = open_keepass

    command_line = f"{ADD_SUBCOMMAND} {HOSTS_SUBCOMMAND} --ip {IP_TEST_VALUE} --hostname {HOSTNAME_TEST_VALUE}".split()
    args = parse_arguments().parse_args(command_line)

    add_object(args, kp, {})

    assert get_hosts(kp) == [
        Host(id="1", ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE)
    ]


def test_add_host_full(open_keepass: PyKeePass):
    kp = open_keepass

    command_line = f"{ADD_SUBCOMMAND} {HOSTS_SUBCOMMAND} --ip {IP_TEST_VALUE} --hostname {HOSTNAME_TEST_VALUE} --role {ROLE_TEST_VALUE}".split()
    args = parse_arguments().parse_args(command_line)

    add_object(args, kp, {})

    assert get_hosts(kp) == [
        Host(
            id="1", ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE, role=ROLE_TEST_VALUE
        )
    ]
