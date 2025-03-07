import pytest

from exegol_history.db_api.hosts import add_host, get_hosts
from common_cli import (
    IP_TEST_VALUE,
    HOSTNAME_TEST_VALUE,
    ROLE_TEST_VALUE,
    TEST_HOSTS_CSV,
)
from exegol_history.db_api.parsing import parse_hosts, HostsFileType
from pykeepass import PyKeePass


def test_add_host_only_ip(open_keepass: PyKeePass):
    kp = open_keepass

    add_host(kp, IP_TEST_VALUE)
    hosts = get_hosts(kp)

    assert hosts == [(IP_TEST_VALUE, "", "")]


def test_add_host_half(open_keepass: PyKeePass):
    kp = open_keepass

    add_host(kp, IP_TEST_VALUE, HOSTNAME_TEST_VALUE)
    hosts = get_hosts(kp)

    assert hosts == [(IP_TEST_VALUE, HOSTNAME_TEST_VALUE, "")]


def test_add_host_search_ip(open_keepass: PyKeePass):
    kp = open_keepass

    add_host(kp, IP_TEST_VALUE, HOSTNAME_TEST_VALUE)
    add_host(kp, IP_TEST_VALUE + "2", HOSTNAME_TEST_VALUE)
    hosts = get_hosts(kp, IP_TEST_VALUE + "2")

    assert hosts == [(IP_TEST_VALUE + "2", HOSTNAME_TEST_VALUE, "")]


def test_add_host_full(open_keepass: PyKeePass):
    kp = open_keepass

    add_host(kp, IP_TEST_VALUE, HOSTNAME_TEST_VALUE, ROLE_TEST_VALUE)
    hosts = get_hosts(kp)

    assert hosts == [(IP_TEST_VALUE, HOSTNAME_TEST_VALUE, ROLE_TEST_VALUE)]


def test_add_host_empty(open_keepass: PyKeePass):
    kp = open_keepass

    with pytest.raises(ValueError):
        add_host(kp, "", "", "")

    hosts = get_hosts(kp)

    assert len(hosts) == 0


def test_add_host_existing(open_keepass: PyKeePass):
    kp = open_keepass

    add_host(kp, IP_TEST_VALUE, HOSTNAME_TEST_VALUE, ROLE_TEST_VALUE)
    hosts = get_hosts(kp)

    assert hosts == [(IP_TEST_VALUE, HOSTNAME_TEST_VALUE, ROLE_TEST_VALUE)]

    add_host(kp, IP_TEST_VALUE, HOSTNAME_TEST_VALUE + "2", ROLE_TEST_VALUE + "2")
    hosts = get_hosts(kp)

    assert hosts == [(IP_TEST_VALUE, HOSTNAME_TEST_VALUE + "2", ROLE_TEST_VALUE + "2")]


def test_add_host_import_csv(open_keepass: PyKeePass):
    kp = open_keepass

    with open(TEST_HOSTS_CSV, "r") as host_file:
        parsed_hosts = parse_hosts(HostsFileType.CSV, host_file.read())
        if parsed_hosts:
            for host in parsed_hosts:
                add_host(kp, host[0], host[1], host[2])

    hosts = get_hosts(kp)

    assert hosts == [(IP_TEST_VALUE, HOSTNAME_TEST_VALUE, ROLE_TEST_VALUE)]
