from exegol_history.db_api.hosts import add_host, get_hosts, edit_host
from common_cli import IP_TEST_VALUE, HOSTNAME_TEST_VALUE, ROLE_TEST_VALUE
from pykeepass import PyKeePass


def test_edit_host_only_ip(open_keepass: PyKeePass):
    kp = open_keepass

    add_host(kp, IP_TEST_VALUE)
    hosts = get_hosts(kp)

    assert hosts == [(IP_TEST_VALUE, "", "")]

    edit_host(kp, IP_TEST_VALUE, IP_TEST_VALUE + "2")
    hosts = get_hosts(kp)

    assert hosts == [(IP_TEST_VALUE + "2", "", "")]


def test_edit_host_full(open_keepass: PyKeePass):
    kp = open_keepass

    add_host(kp, IP_TEST_VALUE)
    hosts = get_hosts(kp)

    assert hosts == [(IP_TEST_VALUE, "", "")]

    edit_host(
        kp,
        IP_TEST_VALUE,
        IP_TEST_VALUE + "2",
        HOSTNAME_TEST_VALUE + "2",
        ROLE_TEST_VALUE + "2",
    )
    hosts = get_hosts(kp)

    assert hosts == [
        (IP_TEST_VALUE + "2", HOSTNAME_TEST_VALUE + "2", ROLE_TEST_VALUE + "2")
    ]
