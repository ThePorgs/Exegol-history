import psycopg

from pykeepass import PyKeePass
from exegol_history.db_api.creds import add_credential
from rich.console import Console
from exegol_history.connectors.msf.utils import (
    is_private_data_hash,
    MSF_DB_CREDENTIAL_QUERY,
    MetasploitCredentialType,
)


def sync_credentials(
    kp: PyKeePass,
    msf_db_name: str,
    msf_db_port: int,
    msf_db_username: str,
    msf_db_password: str,
):
    console = Console(soft_wrap=True)
    number_of_synchronized = 0

    with psycopg.connect(
        f"dbname={msf_db_name} user={msf_db_username} port={msf_db_port} password={msf_db_password} host=localhost"
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(MSF_DB_CREDENTIAL_QUERY)

            for record in cur:
                username = record[1]
                password = ""
                hash = ""
                private_data = record[2]
                private_data_type = record[3]
                domain = record[4]

                if not username:
                    console.print(
                        f"[[bold yellow]![/bold yellow]] The MSF record id {record[0]} was not synchronized because the username was not set."
                    )
                    continue

                if is_private_data_hash(private_data_type):
                    hash = private_data
                elif private_data_type == MetasploitCredentialType.Password:
                    password = private_data

                add_credential(kp, username, password, hash, domain)
                number_of_synchronized += 1

            conn.commit()

    console.print(
        f"[[bold green]+[/bold green]] {number_of_synchronized} credentials synchronized !"
    )
