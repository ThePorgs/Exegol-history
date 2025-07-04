import io
from pykeepass import PyKeePass
from rich.console import Console
from exegol_history.cli.arguments import parse_arguments
from exegol_history.cli.functions import (
    CREDS_SUBCOMMAND,
    DELETE_SUBCOMMAND,
    delete_objects,
)
from exegol_history.db_api.creds import (
    Credential,
    add_credentials,
    get_credentials,
)
from exegol_history.db_api.utils import MESSAGE_ID_NOT_EXIST, parse_ids
from exegol_history.tests.common import (
    PASSWORD_TEST_VALUE,
    USERNAME_TEST_VALUE,
)


def test_delete_credential(open_keepass: PyKeePass):
    kp = open_keepass

    credential1 = Credential(
        username=USERNAME_TEST_VALUE + "2", password=PASSWORD_TEST_VALUE + "2"
    )
    credential2 = Credential(username=USERNAME_TEST_VALUE)
    credential3 = Credential(username=USERNAME_TEST_VALUE, password=PASSWORD_TEST_VALUE)
    add_credentials(kp, [credential1, credential2, credential3])

    command_line = f"{DELETE_SUBCOMMAND} {CREDS_SUBCOMMAND} -i 2".split()
    args = parse_arguments().parse_args(command_line)

    delete_objects(args, kp, {})

    assert get_credentials(kp) == [credential1, credential3]


def test_delete_credential_range(open_keepass: PyKeePass):
    kp = open_keepass

    credential1 = Credential(
        username=USERNAME_TEST_VALUE + "2", password=PASSWORD_TEST_VALUE + "2"
    )
    credential2 = Credential(username=USERNAME_TEST_VALUE)
    credential3 = Credential(username=USERNAME_TEST_VALUE, password=PASSWORD_TEST_VALUE)
    credential4 = Credential(
        username=USERNAME_TEST_VALUE + "4", password=PASSWORD_TEST_VALUE
    )
    credential5 = Credential(
        username=USERNAME_TEST_VALUE + "5", password=PASSWORD_TEST_VALUE
    )

    add_credentials(
        kp, [credential1, credential2, credential3, credential4, credential5]
    )

    command_line = f"{DELETE_SUBCOMMAND} {CREDS_SUBCOMMAND} -i 1-3,5".split()
    args = parse_arguments().parse_args(command_line)

    delete_objects(args, kp, {})

    assert get_credentials(kp) == [credential4]


def test_delete_credential_bad_range():
    assert len(parse_ids("BAD,BAD")) == 0


def test_delete_credential_not_exist(open_keepass: PyKeePass):
    kp = open_keepass
    console = Console(file=io.StringIO())

    command_line = f"{DELETE_SUBCOMMAND} {CREDS_SUBCOMMAND} -i 999".split()
    args = parse_arguments().parse_args(command_line)

    delete_objects(args, kp, console)

    assert MESSAGE_ID_NOT_EXIST in console.file.getvalue().replace("\n", "")
    assert len(get_credentials(kp)) == 0
