import io
from pykeepass import PyKeePass
from exegol_history.cli.arguments import parse_arguments
from exegol_history.cli.functions import CREDS_SUBCOMMAND, EDIT_SUBCOMMAND, edit_object
from exegol_history.db_api.creds import (
    Credential,
    add_credentials,
    get_credentials,
)
from exegol_history.db_api.utils import MESSAGE_ID_NOT_EXIST
from exegol_history.tests.common import (
    DOMAIN_TEST_VALUE,
    HASH_TEST_VALUE,
    PASSWORD_TEST_VALUE,
    USERNAME_TEST_VALUE,
)
from rich.console import Console


def test_edit_credential_only_username(open_keepass: PyKeePass):
    kp = open_keepass
    credential = Credential(username=USERNAME_TEST_VALUE)

    add_credentials(kp, [credential])

    command_line = f"{EDIT_SUBCOMMAND} {CREDS_SUBCOMMAND} -i {credential.id} -u {USERNAME_TEST_VALUE + '2'}".split()
    args = parse_arguments().parse_args(command_line)

    edit_object(args, kp, {})
    credential.username = USERNAME_TEST_VALUE + "2"

    assert get_credentials(kp) == [credential]


def test_edit_credential_half(open_keepass: PyKeePass):
    kp = open_keepass
    credential = Credential(username=USERNAME_TEST_VALUE, password=PASSWORD_TEST_VALUE)

    add_credentials(kp, [credential])

    command_line = f"{EDIT_SUBCOMMAND} {CREDS_SUBCOMMAND} -i {credential.id} -u {USERNAME_TEST_VALUE + '2'} -p {PASSWORD_TEST_VALUE + '2'}".split()
    args = parse_arguments().parse_args(command_line)

    edit_object(args, kp, {})
    credential.username = USERNAME_TEST_VALUE + "2"
    credential.password = PASSWORD_TEST_VALUE + "2"

    assert get_credentials(kp) == [credential]


def test_edit_credential_full(open_keepass: PyKeePass):
    kp = open_keepass
    credential = Credential(
        username=USERNAME_TEST_VALUE,
        password=PASSWORD_TEST_VALUE,
        hash=HASH_TEST_VALUE,
        domain=DOMAIN_TEST_VALUE,
    )

    add_credentials(kp, [credential])

    command_line = f"{EDIT_SUBCOMMAND} {CREDS_SUBCOMMAND} -i {credential.id} -u {USERNAME_TEST_VALUE + '2'} -p {PASSWORD_TEST_VALUE + '2'} -H {HASH_TEST_VALUE + '2'} -d {DOMAIN_TEST_VALUE + '2'}".split()
    args = parse_arguments().parse_args(command_line)

    edit_object(args, kp, {})
    credential.username = USERNAME_TEST_VALUE + "2"
    credential.password = PASSWORD_TEST_VALUE + "2"
    credential.hash = HASH_TEST_VALUE + "2"
    credential.domain = DOMAIN_TEST_VALUE + "2"

    assert get_credentials(kp) == [credential]


def test_edit_credential_not_exist(open_keepass: PyKeePass):
    kp = open_keepass
    console = Console(file=io.StringIO())

    command_line = f"{EDIT_SUBCOMMAND} {CREDS_SUBCOMMAND} -i 999".split()
    args = parse_arguments().parse_args(command_line)

    edit_object(args, kp, console)

    assert MESSAGE_ID_NOT_EXIST in console.file.getvalue().replace('\n', '')
    assert len(get_credentials(kp)) == 0
