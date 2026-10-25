import time
from unittest.mock import patch

from sqlalchemy import Engine

from exegol_history.cli.arguments import parse_arguments
from exegol_history.cli.constants import SYNC_SUBCOMMAND
from exegol_history.cli.functions import cli_sync_objects
from exegol_history.config.config import AppConfig
from exegol_history.connectors.metasploit.metasploit_sync import MetasploitSyncer
from exegol_history.connectors.metasploit.utils import MetasploitCredentialType
from exegol_history.connectors.netexec.netexec_sync import (
    NetexecCredType,
    NetexecSyncer,
)
from exegol_history.db_api.creds import Credential, get_credentials
from exegol_history.tests.common import (
    DOMAIN_TEST_VALUE,
    GET_PG_DB_INFOS_PATCH_PATH,
    HASH_TEST_VALUE,
    NXC_DB_TIMESTAMP,
    PASSWORD_TEST_VALUE,
    PSYCOPG_PATCH_PATH,
    SQLITE3_PATCH_PATH,
    USERNAME_TEST_VALUE,
    get_sync_connector_index,
)

NETEXEC_CREDENTIALS_COLUMNS = [["username"], ["password"], ["domain"], ["credtype"]]


def generate_credentials(
    number_of_object: int = 2000, connector_type: str = NetexecSyncer.CONNECTOR_NAME
):
    credentials = []
    credential_rows = []

    for i in range(1, number_of_object):
        username = USERNAME_TEST_VALUE + str(i)
        password = PASSWORD_TEST_VALUE
        domain = DOMAIN_TEST_VALUE
        credentials.append(
            Credential(
                credential_id=i,
                username=username,
                password=password,
                domain=domain,
                sync_key="domain",
            )
        )

        if connector_type == NetexecSyncer.CONNECTOR_NAME:
            credential_rows.append(
                (
                    username,
                    password,
                    domain,
                    NetexecCredType.PASSWORD.value,
                )
            )
        elif connector_type == MetasploitSyncer.CONNECTOR_NAME:
            credential_rows.append(
                (
                    None,
                    USERNAME_TEST_VALUE + str(i),
                    PASSWORD_TEST_VALUE,
                    MetasploitCredentialType.Password,
                    DOMAIN_TEST_VALUE,
                )
            )

    return (credentials, credential_rows)


# Syncing should not take too much time for large amount of credentials
def test_sync_credential_netexec_big(engine: Engine, load_mock_config: AppConfig):
    load_mock_config.sync[
        get_sync_connector_index(load_mock_config, NetexecSyncer.CONNECTOR_NAME)
    ].enabled = True
    (credentials, credential_rows) = generate_credentials()

    start_time = time.time()

    with patch(SQLITE3_PATCH_PATH) as mocksqlite3:
        mocksqlite3.connect().cursor().fetchall.return_value = credential_rows
        mocksqlite3.connect().cursor().description = NETEXEC_CREDENTIALS_COLUMNS

        with patch("os.path.getmtime") as getmtime:
            getmtime.return_value = NXC_DB_TIMESTAMP
            command_line = f"{SYNC_SUBCOMMAND}".split()
            parse_arguments().parse_args(command_line)
            cli_sync_objects(engine, load_mock_config, {}, True, False)

    end_time = time.time()

    assert get_credentials(engine) == credentials
    assert (end_time - start_time) < 1


# Here we are also updating some random credential
def test_sync_credential_netexec_big_update(
    engine: Engine, load_mock_config: AppConfig
):
    load_mock_config.sync[
        get_sync_connector_index(load_mock_config, NetexecSyncer.CONNECTOR_NAME)
    ].enabled = True
    (credentials, credential_rows) = generate_credentials()

    with patch(SQLITE3_PATCH_PATH) as mocksqlite3:
        mocksqlite3.connect().cursor().fetchall.return_value = credential_rows
        mocksqlite3.connect().cursor().description = NETEXEC_CREDENTIALS_COLUMNS

        with patch("os.path.getmtime") as getmtime:
            getmtime.return_value = NXC_DB_TIMESTAMP
            command_line = f"{SYNC_SUBCOMMAND}".split()
            parse_arguments().parse_args(command_line)
            cli_sync_objects(engine, load_mock_config, {}, True, False)

    # Updating some credential
    credentials[456].password = PASSWORD_TEST_VALUE + "53465456775675"
    credential_rows[456] = (
        USERNAME_TEST_VALUE + "457",
        PASSWORD_TEST_VALUE + "53465456775675",
        DOMAIN_TEST_VALUE,
        NetexecCredType.PASSWORD.value,
    )

    credentials[865].password = PASSWORD_TEST_VALUE + "21312123412"
    credential_rows[865] = (
        USERNAME_TEST_VALUE + "866",
        PASSWORD_TEST_VALUE + "21312123412",
        DOMAIN_TEST_VALUE,
        NetexecCredType.PASSWORD.value,
    )

    start_time = time.time()

    with patch(SQLITE3_PATCH_PATH) as mocksqlite3:
        mocksqlite3.connect().cursor().fetchall.return_value = credential_rows
        mocksqlite3.connect().cursor().description = NETEXEC_CREDENTIALS_COLUMNS

        with patch("os.path.getmtime") as getmtime:
            getmtime.return_value = NXC_DB_TIMESTAMP + 100.0
            command_line = f"{SYNC_SUBCOMMAND}".split()
            parse_arguments().parse_args(command_line)
            cli_sync_objects(engine, load_mock_config, {}, True, False)

    end_time = time.time()

    assert get_credentials(engine) == credentials
    assert (end_time - start_time) < 1


def test_sync_credential_netexec(engine: Engine, load_mock_config: AppConfig):
    load_mock_config.sync[
        get_sync_connector_index(load_mock_config, NetexecSyncer.CONNECTOR_NAME)
    ].enabled = True
    with patch(SQLITE3_PATCH_PATH) as mocksqlite3:
        mocksqlite3.connect().cursor().fetchall.return_value = [
            (
                USERNAME_TEST_VALUE,
                PASSWORD_TEST_VALUE,
                DOMAIN_TEST_VALUE,
                NetexecCredType.PASSWORD.value,
            )
        ]
        mocksqlite3.connect().cursor().description = NETEXEC_CREDENTIALS_COLUMNS

        with patch("os.path.getmtime") as getmtime:
            getmtime.return_value = NXC_DB_TIMESTAMP
            command_line = f"{SYNC_SUBCOMMAND}".split()
            parse_arguments().parse_args(command_line)
            cli_sync_objects(engine, load_mock_config, {}, True, False)

    assert get_credentials(engine) == [
        Credential(
            credential_id=1,
            username=USERNAME_TEST_VALUE,
            password=PASSWORD_TEST_VALUE,
            domain=DOMAIN_TEST_VALUE,
            sync_key="domain",
        )
    ]


def test_sync_credential_netexec_hash(engine: Engine, load_mock_config: AppConfig):
    load_mock_config.sync[
        get_sync_connector_index(load_mock_config, NetexecSyncer.CONNECTOR_NAME)
    ].enabled = True
    with patch(SQLITE3_PATCH_PATH) as mocksqlite3:
        mocksqlite3.connect().cursor().fetchall.return_value = [
            (
                USERNAME_TEST_VALUE,
                PASSWORD_TEST_VALUE,
                DOMAIN_TEST_VALUE,
                NetexecCredType.PASSWORD.value,
            ),
            (
                USERNAME_TEST_VALUE,
                HASH_TEST_VALUE,
                DOMAIN_TEST_VALUE,
                NetexecCredType.HASH.value,
            ),
        ]
        mocksqlite3.connect().cursor().description = NETEXEC_CREDENTIALS_COLUMNS

        with patch("os.path.getmtime") as getmtime:
            getmtime.return_value = NXC_DB_TIMESTAMP
            command_line = f"{SYNC_SUBCOMMAND}".split()
            parse_arguments().parse_args(command_line)
            cli_sync_objects(engine, load_mock_config, {}, True, False)

    assert get_credentials(engine) == [
        Credential(
            credential_id=1,
            username=USERNAME_TEST_VALUE,
            password=PASSWORD_TEST_VALUE,
            hash=HASH_TEST_VALUE,
            domain=DOMAIN_TEST_VALUE,
            sync_key="domain",
        )
    ]


def test_sync_credential_netexec_empty(engine: Engine, load_mock_config: AppConfig):
    load_mock_config.sync[
        get_sync_connector_index(load_mock_config, NetexecSyncer.CONNECTOR_NAME)
    ].enabled = True
    with patch(SQLITE3_PATCH_PATH) as mocksqlite3:
        mocksqlite3.connect().cursor().fetchall.return_value = []
        mocksqlite3.connect().cursor().description = NETEXEC_CREDENTIALS_COLUMNS

        with patch("os.path.getmtime") as getmtime:
            getmtime.return_value = NXC_DB_TIMESTAMP
            command_line = f"{SYNC_SUBCOMMAND}".split()
            parse_arguments().parse_args(command_line)
            cli_sync_objects(engine, load_mock_config, {}, True, False)

    assert not get_credentials(engine)


def test_sync_credential_metasploit_big(engine: Engine, load_mock_config: AppConfig):
    load_mock_config.sync[
        get_sync_connector_index(load_mock_config, MetasploitSyncer.CONNECTOR_NAME)
    ].enabled = True
    (credentials, credentials_row) = generate_credentials(
        connector_type=MetasploitSyncer.CONNECTOR_NAME
    )

    start_time = time.time()

    with patch(PSYCOPG_PATCH_PATH) as mockpsycopg:
        with patch(GET_PG_DB_INFOS_PATCH_PATH) as get_msf_postgres_db_infos:
            mockpsycopg().cursor().fetchall.return_value = credentials_row
            get_msf_postgres_db_infos.return_value = ("", "", "", "")

            command_line = f"{SYNC_SUBCOMMAND}".split()
            parse_arguments().parse_args(command_line)
            cli_sync_objects(engine, load_mock_config, {}, True, False)

    end_time = time.time()

    assert get_credentials(engine) == credentials
    assert (end_time - start_time) < 1


def test_sync_credential_metasploit_big_update(
    engine: Engine, load_mock_config: AppConfig
):
    load_mock_config.sync[
        get_sync_connector_index(load_mock_config, MetasploitSyncer.CONNECTOR_NAME)
    ].enabled = True
    (credentials, credentials_row) = generate_credentials(
        connector_type=MetasploitSyncer.CONNECTOR_NAME
    )

    with patch(PSYCOPG_PATCH_PATH) as mockpsycopg:
        with patch(GET_PG_DB_INFOS_PATCH_PATH) as get_msf_postgres_db_infos:
            mockpsycopg().cursor().fetchall.return_value = credentials_row
            get_msf_postgres_db_infos.return_value = ("", "", "", "")

            command_line = f"{SYNC_SUBCOMMAND}".split()
            parse_arguments().parse_args(command_line)
            cli_sync_objects(engine, load_mock_config, {}, True, False)

    # Updating some credential
    credentials[456].password = PASSWORD_TEST_VALUE + "53465456775675"
    credentials_row[456] = (
        None,
        USERNAME_TEST_VALUE + "457",
        PASSWORD_TEST_VALUE + "53465456775675",
        MetasploitCredentialType.Password,
        DOMAIN_TEST_VALUE,
    )

    credentials[865].password = PASSWORD_TEST_VALUE + "21312123412"
    credentials_row[865] = (
        None,
        USERNAME_TEST_VALUE + "866",
        PASSWORD_TEST_VALUE + "21312123412",
        MetasploitCredentialType.Password,
        DOMAIN_TEST_VALUE,
    )

    start_time = time.time()

    with patch(PSYCOPG_PATCH_PATH) as mockpsycopg:
        with patch(GET_PG_DB_INFOS_PATCH_PATH) as get_msf_postgres_db_infos:
            mockpsycopg().cursor().fetchall.return_value = credentials_row
            get_msf_postgres_db_infos.return_value = ("", "", "", "")

            command_line = f"{SYNC_SUBCOMMAND}".split()
            parse_arguments().parse_args(command_line)
            cli_sync_objects(engine, load_mock_config, {}, True, False)

    end_time = time.time()

    assert get_credentials(engine) == credentials
    assert (end_time - start_time) < 1


"""

def test_sync_credential_metasploit(engine: Engine, load_mock_config: AppConfig):
    load_mock_config.sync[
        get_sync_connector_index(load_mock_config, MetasploitSyncer.CONNECTOR_NAME)
    ].enabled = True

    with patch(PSYCOPG_PATCH_PATH) as mockpsycopg:
        with patch(GET_PG_DB_INFOS_PATCH_PATH) as get_msf_postgres_db_infos:
            mockpsycopg().cursor().fetchall.return_value = [
                (
                    None,
                    USERNAME_TEST_VALUE,
                    PASSWORD_TEST_VALUE,
                    MetasploitCredentialType.Password,
                    DOMAIN_TEST_VALUE,
                )
            ]
            get_msf_postgres_db_infos.return_value = ("", "", "", "")

            command_line = f"{SYNC_SUBCOMMAND}".split()
            parse_arguments().parse_args(command_line)
            cli_sync_objects(engine, load_mock_config, {}, True, False)

    assert get_credentials(engine) == [
        Credential(
            credential_id=1,
            username=USERNAME_TEST_VALUE,
            password=PASSWORD_TEST_VALUE,
            domain=DOMAIN_TEST_VALUE,
        )
    ]


def test_sync_credential_metasploit_empty(engine: Engine, load_mock_config: AppConfig):
    load_mock_config.sync[
        get_sync_connector_index(load_mock_config, MetasploitSyncer.CONNECTOR_NAME)
    ].enabled = True

    with patch(PSYCOPG_PATCH_PATH) as mockpsycopg:
        with patch(GET_PG_DB_INFOS_PATCH_PATH) as get_msf_postgres_db_infos:
            mockpsycopg().cursor().fetchall.return_value = []
            get_msf_postgres_db_infos.return_value = ("", "", "", "")

            command_line = f"{SYNC_SUBCOMMAND}".split()
            parse_arguments().parse_args(command_line)
            cli_sync_objects(engine, load_mock_config, {}, True, False)

    assert not get_credentials(engine)
"""
