import pytest

from exegol_history.db_api.hosts import add_host, get_hosts, delete_host
from common_cli import IP_TEST_VALUE, HOSTNAME_TEST_VALUE, ROLE_TEST_VALUE
from pykeepass import PyKeePass


def test_delete_host(open_keepass: PyKeePass):
    kp = open_keepass

    add_host(kp, IP_TEST_VALUE)
    hosts = get_hosts(kp)

    assert hosts == [(IP_TEST_VALUE, "", "")]

    delete_host(kp, IP_TEST_VALUE)
    hosts = get_hosts(kp)

    assert len(hosts) == 0


def test_delete_host_full(open_keepass: PyKeePass):
    kp = open_keepass

    add_host(kp, IP_TEST_VALUE, HOSTNAME_TEST_VALUE, ROLE_TEST_VALUE)
    hosts = get_hosts(kp)

    assert hosts == [(IP_TEST_VALUE, HOSTNAME_TEST_VALUE, ROLE_TEST_VALUE)]

    delete_host(kp, IP_TEST_VALUE)
    hosts = get_hosts(kp)

    assert len(hosts) == 0


def test_delete_host_not_exist(open_keepass: PyKeePass):
    kp = open_keepass

    with pytest.raises(RuntimeError):
        delete_host(kp, IP_TEST_VALUE)

    hosts = get_hosts(kp)

    assert len(hosts) == 0
