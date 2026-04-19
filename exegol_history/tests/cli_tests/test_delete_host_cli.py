import io
from rich.console import Console
from sqlalchemy import Engine
from exegol_history.cli.arguments import parse_arguments
from exegol_history.cli.functions import (
    ALL_SUBCOMMAND,
    DELETE_SUBCOMMAND,
    HOSTS_SUBCOMMAND,
    delete_objects,
)
from exegol_history.db_api.creds import Credential, add_credentials, get_credentials
from exegol_history.db_api.hosts import Host, add_hosts, get_hosts
from exegol_history.db_api.utils import MESSAGE_ID_NOT_EXIST
from exegol_history.tests.common import (
    HOSTNAME_TEST_VALUE,
    IP_TEST_VALUE,
    USERNAME_TEST_VALUE,
)


def test_delete_host(engine: Engine):
    host1 = Host(1, ip=IP_TEST_VALUE + "2", hostname=HOSTNAME_TEST_VALUE + "2")
    host2 = Host(2, ip=IP_TEST_VALUE)
    host3 = Host(3, ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE)

    add_hosts(engine, [host1.as_dict(), host2.as_dict(), host3.as_dict()])

    command_line = f"{DELETE_SUBCOMMAND} {HOSTS_SUBCOMMAND} -i 2".split()
    args = parse_arguments().parse_args(command_line)

    delete_objects(args, engine, {})

    assert get_hosts(engine) == [host1, host3]


def test_delete_host_range(engine: Engine):
    host1 = Host(1, ip=IP_TEST_VALUE + "2", hostname=HOSTNAME_TEST_VALUE + "2")
    host2 = Host(2, ip=IP_TEST_VALUE)
    host3 = Host(3, ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE)
    host4 = Host(4, ip=IP_TEST_VALUE + "4", hostname=HOSTNAME_TEST_VALUE)
    host5 = Host(5, ip=IP_TEST_VALUE + "5", hostname=HOSTNAME_TEST_VALUE)

    add_hosts(
        engine,
        [
            host1.as_dict(),
            host2.as_dict(),
            host3.as_dict(),
            host4.as_dict(),
            host5.as_dict(),
        ],
    )

    command_line = f"{DELETE_SUBCOMMAND} {HOSTS_SUBCOMMAND} -i 1-3,5".split()
    args = parse_arguments().parse_args(command_line)

    delete_objects(args, engine, {})

    assert get_hosts(engine) == [host4]


def test_delete_host_not_exist(engine: Engine):
    console = Console(file=io.StringIO())

    command_line = f"{DELETE_SUBCOMMAND} {HOSTS_SUBCOMMAND} -i 999".split()
    args = parse_arguments().parse_args(command_line)

    delete_objects(args, engine, console)

    assert MESSAGE_ID_NOT_EXIST in console.file.getvalue().replace("\n", "")
    assert len(get_hosts(engine)) == 0


def test_delete_all_hosts(engine: Engine):
    host1 = Host(1, ip=IP_TEST_VALUE + "2", hostname=HOSTNAME_TEST_VALUE + "2")
    host2 = Host(2, ip=IP_TEST_VALUE)
    add_hosts(engine, [host1.as_dict(), host2.as_dict()])

    command_line = f"{DELETE_SUBCOMMAND} {HOSTS_SUBCOMMAND} --all".split()
    args = parse_arguments().parse_args(command_line)

    delete_objects(args, engine, Console(file=io.StringIO()))

    assert get_hosts(engine) == []


def test_delete_all_hosts_empty_table(engine: Engine):
    command_line = f"{DELETE_SUBCOMMAND} {HOSTS_SUBCOMMAND} --all".split()
    args = parse_arguments().parse_args(command_line)

    delete_objects(args, engine, Console(file=io.StringIO()))

    assert get_hosts(engine) == []


def test_delete_all(engine: Engine):
    credential = Credential(1, username=USERNAME_TEST_VALUE)
    host = Host(1, ip=IP_TEST_VALUE)
    add_credentials(engine, [credential.as_dict()])
    add_hosts(engine, [host.as_dict()])

    command_line = f"{DELETE_SUBCOMMAND} {ALL_SUBCOMMAND}".split()
    args = parse_arguments().parse_args(command_line)

    delete_objects(args, engine, Console(file=io.StringIO()))

    assert get_credentials(engine) == []
    assert get_hosts(engine) == []
