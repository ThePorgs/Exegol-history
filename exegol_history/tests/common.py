from pykeepass import PyKeePass
from textual.keys import Keys
from exegol_history.db_api.creds import Credential
from exegol_history.db_api.hosts import Host
from pathlib import Path


IP_TEST_VALUE = "127.0.0.1"
HOSTNAME_TEST_VALUE = "DC01"
ROLE_TEST_VALUE = "DC"

USERNAME_TEST_VALUE = "username"
PASSWORD_TEST_VALUE = "password"
HASH_TEST_VALUE = "hash"
DOMAIN_TEST_VALUE = "test.local"
CREDENTIALS_TEST_VALUE = [
    Credential(
        "1",
        USERNAME_TEST_VALUE + "7",
    ),
    Credential(
        "2",
        USERNAME_TEST_VALUE,
        PASSWORD_TEST_VALUE,
        HASH_TEST_VALUE,
        DOMAIN_TEST_VALUE,
    ),
    Credential("3", USERNAME_TEST_VALUE + "2", PASSWORD_TEST_VALUE + "2"),
    Credential("4", USERNAME_TEST_VALUE + "3", PASSWORD_TEST_VALUE, HASH_TEST_VALUE),
    Credential("5", USERNAME_TEST_VALUE + "4"),
    Credential("6", USERNAME_TEST_VALUE),
    Credential(
        "7",
        USERNAME_TEST_VALUE + "6",
        PASSWORD_TEST_VALUE + "6",
        HASH_TEST_VALUE + "6",
        DOMAIN_TEST_VALUE + "6",
    ),
]
CREDENTIALS_TEST_VALUE_GOAD_PYPYKATZ = [
    Credential("1", "DC$", hash="0b65cc18dde1c5548f06b8db074a76b3", domain="SCCMLAB"),
    Credential(
        "2",
        "localuser",
        password="password",
        hash="8846f7eaee8fb117ad06bdd830b7586c",
        domain="SCCMLAB",
    ),
]
CREDENTIALS_TEST_VALUE_GOAD_SECRETSDUMP = [
    Credential("1", "Administrator", hash="2d6144ce972270349b4be753b4f7368e"),
    Credential("2", "Guest", hash="31d6cfe0d16ae931b73c59d7e0c089c0"),
    Credential("3", "krbtgt", hash="d64dc530aa7cd2883f8c705b6e968e00"),
    Credential("4", "localuser", hash="8846f7eaee8fb117ad06bdd830b7586c"),
    Credential("5", "alice", hash="8d97808fb46e01433322bd704ec9e160"),
    Credential("6", "bob", hash="d8d34b3cff03786fbe1d80b2c8c09d9e"),
    Credential("7", "carol", hash="0deff2a0603d8c08dbc5cf5bb17965a7"),
    Credential("8", "dave", hash="f7eb9c06fafaa23c4bcf22ba6781c1e2"),
    Credential("9", "eve", hash="b963c57010f218edc2cc3c229b5e4d0f"),
    Credential("10", "franck", hash="c4d15867c66cc7c09bbef86c2166e0d7"),
    Credential("11", "sccm-client-push", hash="72f5cfa80f07819ccbcfb72feb9eb9b7"),
    Credential("12", "sccm-account-da", hash="a36708091f53bd872528841b744b4a82"),
    Credential("13", "sccm-naa", hash="c22b315c040ae6e0efee3518d830362b"),
    Credential("14", "sccm-sql", hash="3fbc46823c86acd0b25f24e164e9397c"),
    Credential("15", "DC$", hash="0b65cc18dde1c5548f06b8db074a76b3"),
    Credential("16", "MECM$", hash="252633c7d64b63b0578d11fb79bedfa5"),
    Credential("17", "MSSQL$", hash="16727c64fb06edb9ead3c06ab9a8b25b"),
    Credential("18", "CLIENT$", hash="4f242e2b3279eeb5cdb7a19fdab2f038"),
]
CREDENTIALS_TEST_VALUE_KDBX = [
    Credential("1", USERNAME_TEST_VALUE, PASSWORD_TEST_VALUE),
    Credential("2", USERNAME_TEST_VALUE + "2", PASSWORD_TEST_VALUE + "2"),
]
CREDENTIAL1 = Credential(username=USERNAME_TEST_VALUE, hash=HASH_TEST_VALUE)
CREDENTIAL2 = Credential(
    username=USERNAME_TEST_VALUE + "2",
    password=PASSWORD_TEST_VALUE,
    hash=HASH_TEST_VALUE,
    domain=DOMAIN_TEST_VALUE,
)

HOSTS_TEST_VALUE = [
    Host("1", IP_TEST_VALUE, HOSTNAME_TEST_VALUE, ROLE_TEST_VALUE),
    Host("2", IP_TEST_VALUE + "2"),
    Host("3", IP_TEST_VALUE + "2", HOSTNAME_TEST_VALUE + "2"),
    Host("4", IP_TEST_VALUE + "3"),
]

TEST_ARTIFACTS_PATH = Path(__file__).parent / "artifacts"
TEST_HOSTS_CSV_COMMA = TEST_ARTIFACTS_PATH / "hosts_comma.csv"
TEST_HOSTS_CSV_COLON = TEST_ARTIFACTS_PATH / "hosts_colon.csv"
TEST_HOSTS_JSON = TEST_ARTIFACTS_PATH / "hosts.json"
TEST_CREDS_CSV_COMMA = TEST_ARTIFACTS_PATH / "creds_comma.csv"
TEST_CREDS_CSV_COLON = TEST_ARTIFACTS_PATH / "creds_colon.csv"
TEST_CREDS_CSV_EXPORT = TEST_ARTIFACTS_PATH / "creds_export.csv"
TEST_CREDS_JSON = TEST_ARTIFACTS_PATH / "creds.json"
TEST_CREDS_PYPYKATZ_JSON = TEST_ARTIFACTS_PATH / "pypykatz.json"
TEST_CREDS_SECRETSDUMP = TEST_ARTIFACTS_PATH / "secretsdump.dsv"
TEST_CREDS_KDBX = TEST_ARTIFACTS_PATH / "import.kdbx"
TEST_CREDS_KDBX_KEYFILE = TEST_ARTIFACTS_PATH / "import.key"


async def select_input_and_enter_text(pilot, input_id, input_text):
    await pilot.click(input_id)
    for character in list(input_text):
        if character == "\n":
            character = Keys.Enter

        await pilot.press(character)


async def select_input_erase_and_enter_text(pilot, input_id, input_text):
    await pilot.click(input_id)
    await pilot.press(Keys.ControlK)
    await pilot.press(*list(input_text))


async def select_select_index(pilot, input_id, select_index):
    await pilot.click(input_id)

    for i in range(0, select_index - 1):
        await pilot.press(Keys.Down)

    await pilot.press(Keys.Enter)


def delete_all_entries(kp: PyKeePass):
    entries = kp.find_entries()

    for entry in entries:
        kp.delete_entry(entry)

    kp.save()
