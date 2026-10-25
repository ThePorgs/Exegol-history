from sqlalchemy import Engine

from exegol_history.config.config import AppConfig
from exegol_history.connectors.metasploit.metasploit_sync import MetasploitSyncer
from exegol_history.connectors.netexec.netexec_sync import NetexecSyncer
from exegol_history.db_api.creds import add_credentials
from exegol_history.db_api.hosts import add_hosts


def sync_objects(
    engine: Engine,
    config: AppConfig,
    sync_credentials: bool = False,
    sync_hosts: bool = False,
):
    credentials = []
    hosts = []

    for connector in config.sync:
        if (
            connector.CONNECTOR_NAME == NetexecSyncer.CONNECTOR_NAME
            and connector.enabled
        ):
            syncer = NetexecSyncer(
                engine, connector.workspace_path, sync_credentials, sync_hosts
            )
            (tmp1, tmp2) = syncer.sync()
            credentials += tmp1
            hosts += tmp2
        elif (
            connector.CONNECTOR_NAME == MetasploitSyncer.CONNECTOR_NAME
            and connector.enabled
        ):
            syncer = MetasploitSyncer(engine, connector.db_config_path)
            (tmp1, tmp2) = syncer.sync()
            credentials += tmp1
            hosts += tmp2

    add_credentials(engine, credentials)
    add_hosts(engine, hosts)
