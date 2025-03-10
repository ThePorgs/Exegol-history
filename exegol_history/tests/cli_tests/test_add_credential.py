import pytest

from exegol_history.db_api.formatter import (
    format_into_json,
    format_into_csv,
    format_into_txt,
)
from exegol_history.db_api.creds import add_credential, get_credentials
from exegol_history.db_api.parsing import parse_creds, CredsFileType
from common_cli import (
    USERNAME_TEST_VALUE,
    PASSWORD_TEST_VALUE,
    HASH_TEST_VALUE,
    DOMAIN_TEST_VALUE,
    TEST_CREDS_CSV,
)
from pykeepass import PyKeePass


def test_add_credential_only_username(open_keepass: PyKeePass):
    kp = open_keepass

    add_credential(kp, USERNAME_TEST_VALUE)
    credentials = get_credentials(kp)

    assert credentials == [(USERNAME_TEST_VALUE, "", "", "")]


def test_add_credential_half(open_keepass: PyKeePass):
    kp = open_keepass

    add_credential(kp, USERNAME_TEST_VALUE, "", HASH_TEST_VALUE, "")
    credentials = get_credentials(kp)

    assert credentials == [(USERNAME_TEST_VALUE, "", HASH_TEST_VALUE, "")]


def test_add_credential_search_username(open_keepass: PyKeePass):
    kp = open_keepass

    add_credential(kp, USERNAME_TEST_VALUE, "", HASH_TEST_VALUE, "")
    add_credential(kp, USERNAME_TEST_VALUE + "2", "", HASH_TEST_VALUE, "")
    credentials = get_credentials(kp, USERNAME_TEST_VALUE + "2")

    assert credentials == [(USERNAME_TEST_VALUE + "2", "", HASH_TEST_VALUE, "")]


def test_add_credential_full(open_keepass: PyKeePass):
    kp = open_keepass

    add_credential(
        kp, USERNAME_TEST_VALUE, PASSWORD_TEST_VALUE, HASH_TEST_VALUE, DOMAIN_TEST_VALUE
    )
    credentials = get_credentials(kp)

    assert credentials == [
        (USERNAME_TEST_VALUE, PASSWORD_TEST_VALUE, HASH_TEST_VALUE, DOMAIN_TEST_VALUE)
    ]


def test_add_credential_empty(open_keepass: PyKeePass):
    kp = open_keepass

    with pytest.raises(ValueError):
        add_credential(kp, "", "", "", "")

    credentials = get_credentials(kp)

    assert len(credentials) == 0


def test_add_credential_existing(open_keepass: PyKeePass):
    kp = open_keepass

    add_credential(kp, USERNAME_TEST_VALUE, "", HASH_TEST_VALUE, "")
    credentials = get_credentials(kp)

    assert credentials == [(USERNAME_TEST_VALUE, "", HASH_TEST_VALUE, "")]

    add_credential(
        kp, USERNAME_TEST_VALUE, PASSWORD_TEST_VALUE, HASH_TEST_VALUE, DOMAIN_TEST_VALUE
    )
    credentials = get_credentials(kp)

    assert credentials == [
        (USERNAME_TEST_VALUE, PASSWORD_TEST_VALUE, HASH_TEST_VALUE, DOMAIN_TEST_VALUE)
    ]


def test_add_credential_import_csv(open_keepass: PyKeePass):
    kp = open_keepass

    with open(TEST_CREDS_CSV, "r") as cred_file:
        parsed_creds = parsed_creds = parse_creds(CredsFileType.CSV, cred_file.read())
        if parsed_creds:
            for cred in parsed_creds:
                add_credential(kp, cred[0], cred[1], cred[2], cred[3])

    credentials = get_credentials(kp)

    assert credentials == [
        (USERNAME_TEST_VALUE, PASSWORD_TEST_VALUE, HASH_TEST_VALUE, DOMAIN_TEST_VALUE)
    ]


def test_add_credential_json_format(open_keepass: PyKeePass):
    kp = open_keepass

    add_credential(kp, USERNAME_TEST_VALUE, "", HASH_TEST_VALUE, "")
    add_credential(kp, USERNAME_TEST_VALUE + "2", "", HASH_TEST_VALUE, "")
    credentials = get_credentials(kp)

    json_text = format_into_json(
        credentials, field_names=["username", "password", "hash", "domain"]
    )

    assert (
        json_text
        == '[{"username": "'
        + USERNAME_TEST_VALUE
        + '", "password": "", "hash": "'
        + HASH_TEST_VALUE
        + '", "domain": ""}, {"username": "'
        + USERNAME_TEST_VALUE
        + "2"
        + '", "password": "", "hash": "'
        + HASH_TEST_VALUE
        + '", "domain": ""}]'
    )


def test_add_credential_csv_format(open_keepass: PyKeePass):
    kp = open_keepass

    add_credential(kp, USERNAME_TEST_VALUE, "", HASH_TEST_VALUE, "")
    add_credential(
        kp,
        USERNAME_TEST_VALUE + "2",
        USERNAME_TEST_VALUE + "2",
        USERNAME_TEST_VALUE + "2",
        USERNAME_TEST_VALUE + "2",
    )
    credentials = get_credentials(kp)

    csv_text = format_into_csv(credentials)

    assert (
        csv_text
        == f"{USERNAME_TEST_VALUE},,{HASH_TEST_VALUE},\n{USERNAME_TEST_VALUE + '2'},{USERNAME_TEST_VALUE + '2'},{USERNAME_TEST_VALUE + '2'},{USERNAME_TEST_VALUE + '2'}\n"
    )


def test_add_credential_txt_format(open_keepass: PyKeePass):
    kp = open_keepass

    add_credential(kp, USERNAME_TEST_VALUE, "", HASH_TEST_VALUE, "")
    add_credential(
        kp,
        USERNAME_TEST_VALUE + "2",
        USERNAME_TEST_VALUE + "2",
        USERNAME_TEST_VALUE + "2",
        USERNAME_TEST_VALUE + "2",
    )
    credentials = get_credentials(kp)

    txt_text = format_into_txt(credentials)

    assert (
        txt_text
        == f"{USERNAME_TEST_VALUE}\n\n{HASH_TEST_VALUE}\n\n{USERNAME_TEST_VALUE + '2'}\n{USERNAME_TEST_VALUE + '2'}\n{USERNAME_TEST_VALUE + '2'}\n{USERNAME_TEST_VALUE + '2'}\n"
    )
