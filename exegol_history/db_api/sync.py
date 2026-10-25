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
    domain_credentials = []
    hosts = []

    for connector in config.sync:
        if (
            connector.CONNECTOR_NAME == NetexecSyncer.CONNECTOR_NAME
            and connector.enabled
        ):
            syncer = NetexecSyncer(
                engine, connector.workspace_path, sync_credentials, sync_hosts
            )

            for result in syncer.sync():
                (synced_credentials, synced_domain_credentials, synced_hosts) = result
                credentials += synced_credentials
                domain_credentials += synced_domain_credentials
                hosts += synced_hosts
        elif (
            connector.CONNECTOR_NAME == MetasploitSyncer.CONNECTOR_NAME
            and connector.enabled
        ):
            syncer = MetasploitSyncer(engine, connector.db_config_path)
            (synced_credentials, synced_hosts) = syncer.sync()
            credentials += synced_credentials
            hosts += synced_hosts

    add_credentials(engine, credentials, "domain")
    add_credentials(engine, domain_credentials, "password")
    add_hosts(engine, hosts)
