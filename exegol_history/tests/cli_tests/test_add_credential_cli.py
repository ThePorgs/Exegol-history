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


def test_add_credential_only_username(engine: Engine):
    command_line = (
        f"{ADD_SUBCOMMAND} {CREDS_SUBCOMMAND} -u {USERNAME_TEST_VALUE}".split()
    )
    args = parse_arguments().parse_args(command_line)

    add_object(args, engine, {})

    assert get_credentials(engine) == [Credential(1, username=USERNAME_TEST_VALUE)]


def test_add_credential_half(engine: Engine):
    command_line = f"{ADD_SUBCOMMAND} {CREDS_SUBCOMMAND} -u {USERNAME_TEST_VALUE} -p {PASSWORD_TEST_VALUE}".split()
    args = parse_arguments().parse_args(command_line)

    add_object(args, engine, {})

    assert get_credentials(engine) == [
        Credential(1, username=USERNAME_TEST_VALUE, password=PASSWORD_TEST_VALUE)
    ]


def test_add_credential_full(engine: Engine):
    command_line = f"{ADD_SUBCOMMAND} {CREDS_SUBCOMMAND} -u {USERNAME_TEST_VALUE} -p {PASSWORD_TEST_VALUE} -H {HASH_TEST_VALUE} -d {DOMAIN_TEST_VALUE}".split()
    args = parse_arguments().parse_args(command_line)

    add_object(args, engine, {})

    assert get_credentials(engine) == [
        Credential(
            1,
            username=USERNAME_TEST_VALUE,
            password=PASSWORD_TEST_VALUE,
            hash=HASH_TEST_VALUE,
            domain=DOMAIN_TEST_VALUE,
        )
    ]
