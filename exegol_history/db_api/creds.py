import sqlalchemy
from sqlalchemy import Engine, Index, UniqueConstraint, func, select, text
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Mapped, Session, mapped_column

from exegol_history.db_api.base import Base
from exegol_history.db_api.utils import MESSAGE_ID_NOT_EXIST, OBJECT_ALREADY_EXIST

DOMAIN_KEYED = text("sync_key = 'domain'")
PASSWORD_KEYED = text("sync_key = 'password'")

class Credential(Base):
    __tablename__ = "credentials"
    __table_args__ = (
        Index("uq_synced_username_domain", "username", "domain", unique=True, sqlite_where=DOMAIN_KEYED),
        Index("uq_synced_username_password", "username", "password", unique=True, sqlite_where=PASSWORD_KEYED),
    )

    credential_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(nullable=True)
    password: Mapped[str] = mapped_column(nullable=True)
    hash: Mapped[str] = mapped_column(nullable=True)
    domain: Mapped[str] = mapped_column(nullable=True)
    sync_key: Mapped[str] = mapped_column(nullable=True)

    REDACT_SEPARATOR = "*"

    def __init__(
        self,
        credential_id: int = None,
        username: str = "",
        password: str = "",
        hash: str = "",
        domain: str = "",
        sync_key: str = "",
    ):
        self.credential_id = credential_id
        self.username = username
        self.password = password
        self.hash = hash
        self.domain = domain
        self.synced = sync_key

    def __eq__(self, value):
        return (
            (self.credential_id == value.credential_id)
            and (self.username == value.username)
            and (self.password == value.password)
            and (self.hash == value.hash)
            and (self.domain == value.domain)
            and (self.sync_key == value.sync_key)
        )

    def __repr__(self) -> str:
        return f"Credential(credential_id={self.credential_id}, username={self.username}, password={self.password}, hash={self.hash}, domain={self.domain}, sync_key={self.sync_key})"

    # Reference: https://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json
    def as_dict(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

    def __iter__(self):
        return iter(
            [self.credential_id, self.username, self.password, self.hash, self.domain]
        )

    @staticmethod
    def dict(
        credential_id: int = None,
        username: str = "",
        password: str = "",
        hash: str = "",
        domain: str = "",
        sync_key: str = "",
    ) -> dict:
        return {
            "credential_id": credential_id,
            "username": username,
            "password": password,
            "hash": hash,
            "domain": domain,
            "sync_key": sync_key
        }


def add_credentials(engine: Engine, credentials: list[dict], sync_key: str = ""):
    if not credentials:
        return

    with Session(engine) as session:
        query = insert(Credential)

        if sync_key == "domain":
            query = query.on_conflict_do_update(
                index_elements=["username", "domain"],
                index_where=DOMAIN_KEYED,
                set_={
                    "password": func.coalesce(
                        func.nullif(query.excluded.password, ""), Credential.password
                    ),
                    "hash": func.coalesce(
                        func.nullif(query.excluded.hash, ""), Credential.hash
                    ),
                },
            )
        elif sync_key == "password":
            query = query.on_conflict_do_update(
                index_elements=["username", "password"],
                index_where=PASSWORD_KEYED,
                set_={
                    "hash": func.coalesce(
                        func.nullif(query.excluded.hash, ""), Credential.hash
                    ),
                    "domain": func.coalesce(
                        func.nullif(query.excluded.domain, ""), Credential.domain
                    ),
                },
            )

        session.execute(query, credentials)
        session.commit()


def get_credentials(
    engine: Engine, credential_id: str = None, redacted: bool = False
) -> list[Credential]:
    credentials = []

    if credential_id:
        query = select(Credential).where(Credential.credential_id == credential_id)
    else:
        query = select(Credential)

    with Session(engine) as session:
        for credential in session.scalars(query):
            if redacted:
                credential.password = Credential.REDACT_SEPARATOR * 8
                credential.hash = Credential.REDACT_SEPARATOR * 8

            credentials.append(credential)

        return credentials


def delete_credentials(engine: Engine, credential_ids: list[str] = list()):
    with Session(engine) as session:
        query = Credential.__table__.delete().where(
            Credential.credential_id.in_(credential_ids)
        )
        result = session.execute(query)

        session.commit()

    if result.rowcount <= 0:
        raise RuntimeError(MESSAGE_ID_NOT_EXIST)


def edit_credentials(engine: Engine, credentials: list[Credential]):
    with Session(engine) as session:
        try:
            session.bulk_update_mappings(Credential, credentials)
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            raise RuntimeError(OBJECT_ALREADY_EXIST)
        except Exception:
            raise RuntimeError(MESSAGE_ID_NOT_EXIST)
