from exegol_history.db_api.hosts import add_host
import psycopg

from pykeepass import PyKeePass
from rich.console import Console
from exegol_history.connectors.msf.utils import MSF_DB_HOST_QUERY

def sync_hosts(kp: PyKeePass, msf_db_name: str, msf_db_port: int, msf_db_username: str, msf_db_password: str):
    console = Console(soft_wrap=True)
    number_of_synchronized = 0

    with psycopg.connect(f"dbname={msf_db_name} user={msf_db_username} port={msf_db_port} password={msf_db_password} host=localhost") as conn:
        with conn.cursor() as cur:
            cur.execute(MSF_DB_HOST_QUERY)

            for record in cur:
                address = str(record[1])

                add_host(kp, address)
                number_of_synchronized += 1

            conn.commit()

    console.print(
        f"[[bold green]+[/bold green]] {number_of_synchronized} hosts synchronized !"
    )