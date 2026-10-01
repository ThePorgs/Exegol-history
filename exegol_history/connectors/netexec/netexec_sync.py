import sqlite3
from enum import Enum
from pathlib import Path
from sqlalchemy import Engine
from exegol_history.db_api.creds import Credential
from exegol_history.db_api.hosts import Host


class NetexecCredType(Enum):
    HASH = "hash"
    PASSWORD = "plaintext"
    KEY = "key"


class NetexecSyncer:
    CONNECTOR_NAME = "netexec"

    def __init__(
        self,
        engine: Engine,
        workspace_path: str,
        sync_credentials: bool = False,
        sync_hosts: bool = False,
    ):
        self.workspaces_dir = Path(workspace_path).expanduser()
        self.engine = engine
        self.sync_credentials = sync_credentials
        self.sync_hosts = sync_hosts
        self.db_files = {
            "smb.db": (
                "SELECT username, password, domain, credtype FROM users",
                "SELECT ip, hostname, domain FROM hosts",
            ),
            "ftp.db": (
                "SELECT username, password FROM credentials",
                "SELECT host FROM hosts",
            ),
            "mssql.db": (
                "SELECT username, password, domain, credtype FROM users",
                "SELECT ip, hostname, domain FROM hosts",
            ),
            "ssh.db": (
                "SELECT username, password, credtype FROM credentials",
                "SELECT host FROM hosts",
            ),
            "winrm.db": (
                "SELECT username, password, domain, credtype FROM users",
                "SELECT ip, hostname, domain FROM hosts",
            ),
            "ldap.db": (
                "SELECT username, password, domain, credtype FROM users",
                "SELECT ip, hostname, domain FROM hosts",
            ),
            "rdp.db": (
                # "SELECT username, password FROM credentials",
                "",
                "SELECT ip, hostname, domain FROM hosts",
            ),
            "nfs.db": (
                "SELECT username, password FROM credentials",
                "SELECT ip, hostname FROM hosts",
            ),
            "vnc.db": (
                "SELECT username, password FROM credentials",
                "SELECT ip, hostname FROM hosts",
            ),
            "wmi.db": (
                "SELECT username, password FROM credentials",
                "SELECT ip, hostname FROM hosts",
            ),
        }

    def sync(self) -> tuple[list[dict], list[dict]]:
        if self.workspaces_dir.exists():
            for workspace in self.workspaces_dir.iterdir():
                if workspace.is_dir():
                    return self.process_workspace(workspace)
        else:
            raise (
                RuntimeError(f"No workspaces directory found at {self.workspaces_dir}")
            )

    def process_workspace(self, workspace_path: Path) -> tuple[list[dict], list[dict]]:
        credentials = []
        hosts = []

        for db_file, queries in self.db_files.items():
            db_file_path = workspace_path / Path(db_file)

            if db_file_path.is_file():
                if self.sync_credentials:
                    try:
                        credentials += self.extract_credentials(
                            db_file_path, queries[0]
                        )
                    except Exception:
                        continue

                if self.sync_hosts and (
                    db_file not in ["ftp.db", "ssh.db"]
                ):  # Need to fix FTP and SSH in Netexec
                    try:
                        hosts += self.extract_hosts(db_file_path, queries[1])
                    except Exception:
                        continue

        return (credentials, hosts)

    def extract_credentials(self, db_file_path: str, query: str) -> list[dict]:
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()
        credentials = []

        cursor.execute(query)

        columns = [desc[0] for desc in cursor.description]

        for row in cursor.fetchall():
            username = password = domain = credtype = None

            if ("domain" in columns) and ("credtype" in columns):
                username, password, domain, credtype = row
            elif "credtype" in columns:
                username, password, credtype = row
            else:
                username, password = row

            credential = Credential.dict(None, username, None, None, domain)

            if credtype == NetexecCredType.HASH.value:
                credential["hash"] = password
            elif credtype == NetexecCredType.PASSWORD.value:
                credential["password"] = password
            else: # Do not sync other nxc creds type (e.g: SSH key)
                continue

            credentials.append(credential)

        conn.close()

        return credentials

    def extract_hosts(self, db_file_path: str, query: str) -> list[dict]:
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()
        hosts = []

        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]

        for row in cursor.fetchall():
            ip = hostname = None

            if "domain" in columns:
                ip, hostname, domain = row
                hostname = hostname + "." + domain
            elif "ip" in columns:
                ip, hostname = row
            else:
                hostname = row

            hosts.append(Host.dict(ip=ip, hostname=hostname))

        conn.close()

        return hosts
