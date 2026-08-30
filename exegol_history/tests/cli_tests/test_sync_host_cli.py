import time
from unittest.mock import patch
from exegol_history.cli.arguments import parse_arguments
from exegol_history.cli.functions import SYNC_SUBCOMMAND, cli_sync_objects
from sqlalchemy import Engine
from exegol_history.config.config import AppConfig
from exegol_history.connectors.netexec.netexec_sync import NetexecSyncer
from exegol_history.db_api.hosts import Host, add_hosts, get_hosts
from exegol_history.tests.common import (
    HOSTNAME_TEST_VALUE,
    IP_TEST_VALUE,
    ROLE_TEST_VALUE,
    SQLITE3_PATCH_PATH,
    get_sync_connector_index,
)

NETEXEC_HOSTS_COLUMNS = [["ip"], ["hostname"]]


def generate_hosts(number_of_object: int = 2000):
    hosts = []
    hosts_rows = []

    for i in range(1, number_of_object):
        ip = IP_TEST_VALUE + str(i)
        hostname = HOSTNAME_TEST_VALUE
        hosts.append(Host(host_id=i, ip=ip, hostname=hostname))

        hosts_rows.append((ip, hostname))

    return (hosts, hosts_rows)


# Syncing should not take too much time for large amount of credentials
def test_sync_host_netexec_big(engine: Engine, load_mock_config: AppConfig):
    load_mock_config.sync[
        get_sync_connector_index(load_mock_config, NetexecSyncer.CONNECTOR_NAME)
    ].enabled = True
    (hosts, hosts_row) = generate_hosts()

    start_time = time.time()

    with patch(SQLITE3_PATCH_PATH) as mocksqlite3:
        mocksqlite3.connect().cursor().fetchall.return_value = hosts_row
        mocksqlite3.connect().cursor().description = NETEXEC_HOSTS_COLUMNS

        command_line = f"{SYNC_SUBCOMMAND}".split()
        parse_arguments().parse_args(command_line)
        cli_sync_objects(engine, load_mock_config, {}, False, True)

    end_time = time.time()

    assert get_hosts(engine) == hosts
    assert (end_time - start_time) < 1


def test_sync_host_netexec(engine: Engine, load_mock_config: AppConfig):
    load_mock_config.sync[
        get_sync_connector_index(load_mock_config, NetexecSyncer.CONNECTOR_NAME)
    ].enabled = True

    with patch(SQLITE3_PATCH_PATH) as mocksqlite3:
        mocksqlite3.connect().cursor().fetchall.return_value = [
            (IP_TEST_VALUE, HOSTNAME_TEST_VALUE)
        ]
        mocksqlite3.connect().cursor().description = NETEXEC_HOSTS_COLUMNS

        command_line = f"{SYNC_SUBCOMMAND}".split()
        parse_arguments().parse_args(command_line)
        cli_sync_objects(engine, load_mock_config, {}, False, True)

    assert get_hosts(engine) == [
        Host(host_id=1, ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE)
    ]


def test_sync_host_netexec_empty(engine: Engine, load_mock_config: AppConfig):
    load_mock_config.sync[
        get_sync_connector_index(load_mock_config, NetexecSyncer.CONNECTOR_NAME)
    ].enabled = True

    with patch(SQLITE3_PATCH_PATH) as mocksqlite3:
        mocksqlite3.connect().cursor().fetchall.return_value = []
        mocksqlite3.connect().cursor().description = NETEXEC_HOSTS_COLUMNS

        command_line = f"{SYNC_SUBCOMMAND}".split()
        parse_arguments().parse_args(command_line)
        cli_sync_objects(engine, load_mock_config, {}, False, True)

    assert not get_hosts(engine)


def test_sync_host_netexec_keeps_manually_set_role(
    engine: Engine, load_mock_config: AppConfig
):
    load_mock_config.sync[
        get_sync_connector_index(load_mock_config, NetexecSyncer.CONNECTOR_NAME)
    ].enabled = True

    add_hosts(
        engine,
        [
            Host(
                ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE, role=ROLE_TEST_VALUE
            ).as_dict()
        ],
    )
    assert get_hosts(engine) == [
        Host(1, ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE, role=ROLE_TEST_VALUE)
    ]

    with patch(SQLITE3_PATCH_PATH) as mocksqlite3:
        mocksqlite3.connect().cursor().fetchall.return_value = [
            (IP_TEST_VALUE, HOSTNAME_TEST_VALUE)
        ]
        mocksqlite3.connect().cursor().description = NETEXEC_HOSTS_COLUMNS

        command_line = f"{SYNC_SUBCOMMAND}".split()
        parse_arguments().parse_args(command_line)
        cli_sync_objects(engine, load_mock_config, {}, False, True)

    assert get_hosts(engine) == [
        Host(1, ip=IP_TEST_VALUE, hostname=HOSTNAME_TEST_VALUE, role=ROLE_TEST_VALUE)
    ]