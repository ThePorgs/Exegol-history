from sqlalchemy import Engine, UniqueConstraint
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Mapped, Session, mapped_column

from exegol_history.db_api.base import (
    Base,
    delete_rows,
    get_rows,
    keep_existing_if_empty,
    update_rows,
)


class Host(Base):
    __tablename__ = "hosts"
    __table_args__ = (UniqueConstraint("ip", "hostname"),)

    host_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ip: Mapped[str] = mapped_column(nullable=True)
    hostname: Mapped[str] = mapped_column(nullable=True)
    role: Mapped[str] = mapped_column(nullable=True)

    def __init__(
        self,
        host_id: int = None,
        ip: str = "",
        hostname: str = "",
        role: str = "",
    ):
        self.host_id = host_id
        self.ip = ip
        self.hostname = hostname.lower()
        self.role = role

    def __eq__(self, value):
        return (
            (self.host_id == value.host_id)
            and (self.ip == value.ip)
            and (self.hostname.lower() == value.hostname.lower())
            and (self.role == value.role)
        )

    def __iter__(self):
        return iter([self.host_id, self.ip, self.hostname, self.role])

    @staticmethod
    def dict(
        host_id: int = None, ip: str = "", hostname: str = "", role: str = ""
    ) -> dict:
        return {
            "host_id": host_id,
            "ip": ip,
            "hostname": hostname.lower(),
            "role": role,
        }


def add_hosts(engine: Engine, hosts: list[dict]):
    if not hosts:
        return

    query = insert(Host)
    query = query.on_conflict_do_update(
        index_elements=["ip", "hostname"],
        set_={"role": keep_existing_if_empty(query, Host, "role")},
    )

    with Session(engine) as session:
        session.execute(query, hosts)
        session.commit()

def get_hosts(engine: Engine, host_id: str = None) -> list[Host]:
    return get_rows(engine, Host, host_id)


def delete_hosts(engine: Engine, host_ids: list[str]):
    delete_rows(engine, Host, host_ids)


def edit_hosts(engine: Engine, hosts: list):
    update_rows(engine, Host, hosts)