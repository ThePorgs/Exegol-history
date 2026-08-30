import sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy import func, select, UniqueConstraint, Engine
from exegol_history.db_api.base import Base
from exegol_history.db_api.utils import MESSAGE_ID_NOT_EXIST, OBJECT_ALREADY_EXIST
from sqlalchemy.dialects.sqlite import insert


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
        ip: str = None,
        hostname: str = None,
        role: str = None,
    ):
        self.host_id = host_id
        self.ip = ip
        self.hostname = hostname
        self.role = role

    def __eq__(self, value):
        return (
            (self.host_id == value.host_id)
            and (self.ip == value.ip)
            and (self.hostname == value.hostname)
            and (self.role == value.role)
        )

    # Reference: https://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json
    def as_dict(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

    def __repr__(self) -> str:
        return f"Host(host_id={self.host_id}, ip={self.ip}, hostname={self.hostname}, role={self.role})"

    def __iter__(self):
        return iter([self.host_id, self.ip, self.hostname, self.role])

    @staticmethod
    def dict(
        host_id: int = None, ip: str = None, hostname: str = None, role: str = None
    ) -> dict:
        return {
            "host_id": host_id,
            "ip": ip,
            "hostname": hostname,
            "role": role,
        }


def add_hosts(engine: Engine, hosts: list[dict]):
    if not hosts:
        return

    with Session(engine) as session:
        query = insert(Host).values(hosts)
        query = query.on_conflict_do_update(
            index_elements=["ip", "hostname"],
            set_={
                "ip": query.excluded.ip,
                "hostname": query.excluded.hostname,
                "role": func.coalesce(func.nullif(query.excluded.role, ""), Host.role),
            },
        )
        session.execute(query)
        session.commit()


def get_hosts(engine: Engine, host_id: str = None) -> list[Host]:
    hosts = []

    if host_id:
        query = select(Host).where(Host.host_id == host_id)
    else:
        query = select(Host)

    with Session(engine) as session:
        for host in session.scalars(query):
            session.expunge(host)
            hosts.append(host)

        return hosts


def delete_hosts(engine: Engine, host_ids: list[str] = list()):
    with Session(engine) as session:
        query = Host.__table__.delete().where(Host.host_id.in_(host_ids))
        result = session.execute(query)

        session.commit()

    if result.rowcount <= 0:
        raise RuntimeError(MESSAGE_ID_NOT_EXIST)


def edit_hosts(engine: Engine, hosts: list[Host]):
    with Session(engine) as session:
        try:
            session.bulk_update_mappings(Host, hosts)
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            raise RuntimeError(OBJECT_ALREADY_EXIST)
        except Exception:
            raise RuntimeError(MESSAGE_ID_NOT_EXIST)
