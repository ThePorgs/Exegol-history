from exegol_history.db_api.creds import add_credential, get_credentials, edit_credential
from common_cli import (
    USERNAME_TEST_VALUE,
    PASSWORD_TEST_VALUE,
    HASH_TEST_VALUE,
    DOMAIN_TEST_VALUE,
)
from pykeepass import PyKeePass


def test_edit_credential_only_username(open_keepass: PyKeePass):
    kp = open_keepass

    add_credential(kp, USERNAME_TEST_VALUE)
    credentials = get_credentials(kp)

    assert credentials == [(USERNAME_TEST_VALUE, "", "", "")]

    edit_credential(kp, USERNAME_TEST_VALUE, USERNAME_TEST_VALUE + "2")
    credentials = get_credentials(kp)

    assert credentials == [(USERNAME_TEST_VALUE + "2", "", "", "")]


def test_edit_credential_full(open_keepass: PyKeePass):
    kp = open_keepass

    add_credential(kp, USERNAME_TEST_VALUE)
    credentials = get_credentials(kp)

    assert credentials == [(USERNAME_TEST_VALUE, "", "", "")]

    edit_credential(
        kp,
        USERNAME_TEST_VALUE,
        USERNAME_TEST_VALUE + "2",
        PASSWORD_TEST_VALUE,
        HASH_TEST_VALUE,
        DOMAIN_TEST_VALUE,
    )
    credentials = get_credentials(kp)

    assert credentials == [
        (
            USERNAME_TEST_VALUE + "2",
            PASSWORD_TEST_VALUE,
            HASH_TEST_VALUE,
            DOMAIN_TEST_VALUE,
        )
    ]


def test_edit_credential_not_exist(open_keepass: PyKeePass):
    kp = open_keepass

    edit_credential(kp, "NotExistingUsername", "NotExistingUsername2")
