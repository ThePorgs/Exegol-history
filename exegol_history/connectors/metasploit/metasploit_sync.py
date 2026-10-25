from sqlalchemy import Engine

from exegol_history.connectors.metasploit.utils import (
    MSF_DB_CREDENTIAL_QUERY,
    MetasploitCredentialType,
    get_msf_postgres_db_infos,
    is_private_data_hash,
)
from exegol_history.db_api.creds import Credential


class MetasploitSyncer:
    CONNECTOR_NAME = "metasploit"

    def __init__(self, engine: Engine, db_config_path: str):
        (
            self.msf_db_name,
            self.msf_db_port,
            self.msf_db_username,
            self.msf_db_password,
        ) = get_msf_postgres_db_infos(db_config_path)
        self.engine = engine

    def sync(self):
        # Lazy import: psycopg costs ~60 ms and is only needed when syncing
        import psycopg
        from psycopg.errors import UndefinedTable

        try:
            conn = psycopg.connect(
                f"dbname={self.msf_db_name} user={self.msf_db_username} port={self.msf_db_port} password={self.msf_db_password} host=localhost"
            )
            cursor = conn.cursor()
            credentials = []

            try:
                cursor.execute(MSF_DB_CREDENTIAL_QUERY)
            except UndefinedTable:
                return  # If the table is not there, it means the Metasploit DB is empty

            for record in cursor.fetchall():
                username = record[1]
                password = ""
                hash = ""
                private_data = record[2]
                private_data_type = record[3]
                domain = record[4]

                if is_private_data_hash(private_data_type):
                    hash = private_data
                elif private_data_type == MetasploitCredentialType.Password:
                    password = private_data

                credentials.append(
                    Credential.dict(
                        username=username,
                        password=password,
                        hash=hash,
                        domain=domain,
                        sync_key="domain",
                    )
                )

            conn.close()
            return (credentials, [])
        except Exception as e:
            raise (e)
