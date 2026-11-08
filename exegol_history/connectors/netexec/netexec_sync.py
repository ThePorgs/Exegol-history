from contextlib import closing
import os
import sqlite3
from enum import Enum
from pathlib import Path

from sqlalchemy import Engine, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session

from exegol_history.db_api.creds import Credential
from exegol_history.db_api.hosts import Host
from exegol_history.db_api.sync_nxc_time import SyncNxcTime


class NetexecCredType(Enum):
    HASH = "hash"
    PASSWORD = "plaintext"
    KEY = "key"


CREDTYPE_FIELDS = {
    NetexecCredType.HASH.value: "hash",
    NetexecCredType.PASSWORD.value: "password",
}


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
                "SELECT username, password, domain FROM users",
                "SELECT ip, hostname FROM hosts",
            ),
        }

    def sync(self) -> tuple[list[Credential], list[Credential], list[Host]]:
        if not self.workspaces_dir.exists():
            raise RuntimeError(
                f"No workspaces directory found at {self.workspaces_dir}"
            )

        return [
            self.process_workspace(w)
            for w in self.workspaces_dir.iterdir()
            if w.is_dir()
        ]

    @staticmethod
    def is_domain_credentials(db_file: str):
        return db_file in [
            "rdp.db",
            "smb.db",
            "wmi.db",
            "winrm.db",
            "mssql.db",
            "ldap.db",
        ]

    def last_sync(self, path: str) -> float:
        with Session(self.engine) as session:
            timestamp = session.scalar(
                select(SyncNxcTime.timestamp).where(SyncNxcTime.filename == str(path))
            )
        return float(timestamp) if timestamp is not None else 0.0

    def save_sync(self, path: str, timestamp: float) -> None:
        query = insert(SyncNxcTime).values(filename=str(path), timestamp=timestamp)
        query = query.on_conflict_do_update(
            index_elements=["filename"], set_={"timestamp": query.excluded.timestamp}
        )
        with Session(self.engine) as session:
            session.execute(query)
            session.commit()

    def process_workspace(
        self, workspace_path: Path
    ) -> tuple[list[Credential], list[Credential], list[Host]]:
        credentials, domain_credentials, hosts = [], [], []

        for db_file, (credentials_query, hosts_query) in self.db_files.items():
            db_file_path = workspace_path / Path(db_file)

            if not db_file_path.is_file():
                continue

            modified = os.path.getmtime(db_file_path)

            # If the file didn't changed since last sync, skip it
            if self.last_sync(db_file_path) >= modified:
                continue

            try:
                if self.sync_credentials and credentials_query:
                    extracted_credentials = self.extract_credentials(
                        db_file_path, credentials_query
                    )

                    if NetexecSyncer.is_domain_credentials(
                        db_file
                    ):  # If it's a domain credential, rules of conflict are different
                        domain_credentials += extracted_credentials
                    else:
                        credentials += extracted_credentials

                if self.sync_hosts:
                    hosts += self.extract_hosts(db_file_path, hosts_query)
            except sqlite3.Error as e:
                print(e)
                continue

            self.save_sync(db_file_path, modified)

        return credentials, domain_credentials, hosts

    @staticmethod
    def query_rows(db_file_path: Path, query: str) -> list[dict]:
        """Rows as {column: value}, so callers don't depend on column order."""
        with closing(sqlite3.connect(db_file_path)) as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def extract_credentials(self, db_file_path: Path, query: str) -> list[dict]:
        credentials = []

        for row in self.query_rows(db_file_path, query):
            # Tables without a "credtype" column only store plaintext passwords
            field = CREDTYPE_FIELDS.get(
                row.get("credtype", NetexecCredType.PASSWORD.value)
            )

            if not field or not row["password"]:
                continue

            credential = Credential.dict(
                username=row["username"],
                domain=row.get("domain") or "",
                sync_key="domain" if "domain" in row else "password",
            )
            credential[field] = row["password"]
            credentials.append(credential)

        return credentials

    def extract_hosts(self, db_file_path: Path, query: str) -> list[dict]:
        hosts = []

        for row in self.query_rows(db_file_path, query):
            hostname = row.get("hostname") or row.get("host") or ""
            domain = row.get("domain")

            # FQDN only if the domain is a real domain
            if hostname and domain and hostname != domain:
                hostname = f"{hostname}.{domain}"

            hosts.append(Host.dict(ip=row.get("ip") or "", hostname=hostname))

        return hosts
