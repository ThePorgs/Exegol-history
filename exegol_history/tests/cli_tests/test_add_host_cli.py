import pytest
from sqlalchemy import Engine

from exegol_history.cli.arguments import parse_arguments
from exegol_history.cli.constants import ADD_SUBCOMMAND, HOSTS_SUBCOMMAND
from exegol_history.cli.functions import add_object
from exegol_history.db_api.hosts import Host, get_hosts
from exegol_history.tests.common import (
    HOSTNAME_TEST_VALUE,
    IP_TEST_VALUE,
    ROLE_TEST_VALUE,
)


@pytest.mark.parametrize(
    "command_line,expected_result",
    [
        (
            f"{ADD_SUBCOMMAND} {HOSTS_SUBCOMMAND} --ip {IP_TEST_VALUE}",
            [Host(1, ip=IP_TEST_VALUE)],
        ),
        (
            f"{ADD_SUBCOMMAND} {HOSTS_SUBCOMMAND} --ip {IP_TEST_VALUE} --hostname {HOSTNAME_TEST_VALUE}",
            [Host(1, ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE)],
        ),
        (
            f"{ADD_SUBCOMMAND} {HOSTS_SUBCOMMAND} --ip {IP_TEST_VALUE} --hostname {HOSTNAME_TEST_VALUE} --role {ROLE_TEST_VALUE}",
            [
                Host(1, ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE, role=ROLE_TEST_VALUE)
            ],
        ),
    ],
)
def test_add_host(engine: Engine, command_line: str, expected_result: list[Host]):
    add_object(parse_arguments().parse_args(command_line.split()), engine, {})
    assert get_hosts(engine) == expected_result
