import pytest
from sqlalchemy import Engine

from exegol_history.cli.arguments import parse_arguments
from exegol_history.cli.constants import ADD_SUBCOMMAND, CREDS_SUBCOMMAND
from exegol_history.cli.functions import add_object
from exegol_history.db_api.creds import Credential, get_credentials
from exegol_history.tests.common import (
    DOMAIN_TEST_VALUE,
    HASH_TEST_VALUE,
    PASSWORD_TEST_VALUE,
    USERNAME_TEST_VALUE,
)


@pytest.mark.parametrize(
    "command_line,expected_result",
    [
        (
            f"{ADD_SUBCOMMAND} {CREDS_SUBCOMMAND} -u {USERNAME_TEST_VALUE}",
            [Credential(1, username=USERNAME_TEST_VALUE)],
        ),
        (
            f"{ADD_SUBCOMMAND} {CREDS_SUBCOMMAND} -u {USERNAME_TEST_VALUE} -p {PASSWORD_TEST_VALUE}",
            [Credential(1, username=USERNAME_TEST_VALUE, password=PASSWORD_TEST_VALUE)],
        ),
        (
            f"{ADD_SUBCOMMAND} {CREDS_SUBCOMMAND} -u {USERNAME_TEST_VALUE} -p {PASSWORD_TEST_VALUE} -H {HASH_TEST_VALUE} -d {DOMAIN_TEST_VALUE}",
            [
                Credential(
                    1,
                    username=USERNAME_TEST_VALUE,
                    password=PASSWORD_TEST_VALUE,
                    hash=HASH_TEST_VALUE,
                    domain=DOMAIN_TEST_VALUE,
                )
            ],
        ),
    ],
)
def test_add_credential(
    engine: Engine, command_line: str, expected_result: list[Credential]
):
    add_object(parse_arguments().parse_args(command_line.split()), engine, {})
    assert get_credentials(engine) == expected_result
