import pytest

from exegol_history.db_api.creds import (
    add_credential,
    get_credentials,
    delete_credential,
)
from common_cli import (
    USERNAME_TEST_VALUE,
    PASSWORD_TEST_VALUE,
    HASH_TEST_VALUE,
    DOMAIN_TEST_VALUE,
)
from pykeepass import PyKeePass


def test_remove_credential(open_keepass: PyKeePass):
    kp = open_keepass

    add_credential(kp, USERNAME_TEST_VALUE)
    credentials = get_credentials(kp)

    assert credentials == [(USERNAME_TEST_VALUE, "", "", "")]

    delete_credential(kp, USERNAME_TEST_VALUE)
    credentials = get_credentials(kp)

    assert len(credentials) == 0


def test_remove_credential_full(open_keepass: PyKeePass):
    kp = open_keepass

    add_credential(
        kp, USERNAME_TEST_VALUE, PASSWORD_TEST_VALUE, HASH_TEST_VALUE, DOMAIN_TEST_VALUE
    )
    credentials = get_credentials(kp)

    assert credentials == [
        (USERNAME_TEST_VALUE, PASSWORD_TEST_VALUE, HASH_TEST_VALUE, DOMAIN_TEST_VALUE)
    ]

    delete_credential(kp, USERNAME_TEST_VALUE)
    credentials = get_credentials(kp)

    assert len(credentials) == 0


def test_remove_credential_not_exist(open_keepass: PyKeePass):
    kp = open_keepass

    with pytest.raises(RuntimeError):
        delete_credential(kp, "NonExistUsername")

    credentials = get_credentials(kp)

    assert len(credentials) == 0
