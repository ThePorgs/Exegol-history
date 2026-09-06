import io
from rich.console import Console
from sqlalchemy import Engine
from exegol_history.cli.arguments import parse_arguments
from exegol_history.cli.functions import (
    CREDS_SUBCOMMAND,
    DELETE_SUBCOMMAND,
    delete_objects,
)
from exegol_history.db_api.creds import (
    Credential,
    add_credentials,
    delete_all_credentials,
    get_credentials,
)
from exegol_history.db_api.utils import MESSAGE_ID_NOT_EXIST, parse_ids
from exegol_history.tests.common import (
    PASSWORD_TEST_VALUE,
    USERNAME_TEST_VALUE,
)


def test_delete_credential(engine: Engine):
    credential1 = Credential(
        1, username=USERNAME_TEST_VALUE + "2", password=PASSWORD_TEST_VALUE + "2"
    )
    credential2 = Credential(2, username=USERNAME_TEST_VALUE)
    credential3 = Credential(
        3, username=USERNAME_TEST_VALUE, password=PASSWORD_TEST_VALUE
    )
    add_credentials(
        engine, [credential1.as_dict(), credential2.as_dict(), credential3.as_dict()]
    )

    command_line = f"{DELETE_SUBCOMMAND} {CREDS_SUBCOMMAND} -i 2".split()
    args = parse_arguments().parse_args(command_line)

    delete_objects(args, engine, {})

    assert get_credentials(engine) == [credential1, credential3]


def test_delete_credential_range(engine: Engine):
    credential1 = Credential(
        1, username=USERNAME_TEST_VALUE + "2", password=PASSWORD_TEST_VALUE + "2"
    )
    credential2 = Credential(2, username=USERNAME_TEST_VALUE)
    credential3 = Credential(
        3, username=USERNAME_TEST_VALUE, password=PASSWORD_TEST_VALUE
    )
    credential4 = Credential(
        4, username=USERNAME_TEST_VALUE + "4", password=PASSWORD_TEST_VALUE
    )
    credential5 = Credential(
        5, username=USERNAME_TEST_VALUE + "5", password=PASSWORD_TEST_VALUE
    )

    add_credentials(
        engine,
        [
            credential1.as_dict(),
            credential2.as_dict(),
            credential3.as_dict(),
            credential4.as_dict(),
            credential5.as_dict(),
        ],
    )

    command_line = f"{DELETE_SUBCOMMAND} {CREDS_SUBCOMMAND} -i 1-3,5".split()
    args = parse_arguments().parse_args(command_line)

    delete_objects(args, engine, {})

    assert get_credentials(engine) == [credential4]


def test_delete_credential_bad_range():
    assert len(parse_ids("BAD,BAD")) == 0


def test_delete_credential_not_exist(engine: Engine):
    console = Console(file=io.StringIO())

    command_line = f"{DELETE_SUBCOMMAND} {CREDS_SUBCOMMAND} -i 999".split()
    args = parse_arguments().parse_args(command_line)

    delete_objects(args, engine, console)

    assert MESSAGE_ID_NOT_EXIST in console.file.getvalue().replace("\n", "")
    assert len(get_credentials(engine)) == 0


def test_delete_all_credentials(engine: Engine):
    credential1 = Credential(1, username=USERNAME_TEST_VALUE + "2", password=PASSWORD_TEST_VALUE)
    credential2 = Credential(2, username=USERNAME_TEST_VALUE)
    add_credentials(engine, [credential1.as_dict(), credential2.as_dict()])

    command_line = f"{DELETE_SUBCOMMAND} {CREDS_SUBCOMMAND} --all".split()
    args = parse_arguments().parse_args(command_line)

    delete_objects(args, engine, Console(file=io.StringIO()))

    assert get_credentials(engine) == []


def test_delete_all_credentials_empty_table(engine: Engine):
    command_line = f"{DELETE_SUBCOMMAND} {CREDS_SUBCOMMAND} --all".split()
    args = parse_arguments().parse_args(command_line)

    delete_objects(args, engine, Console(file=io.StringIO()))

    assert get_credentials(engine) == []
