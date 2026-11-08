from sqlalchemy import Engine, Index, text
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Mapped, Session, mapped_column

from exegol_history.db_api.base import (
    Base,
    delete_rows,
    get_rows,
    keep_existing_if_empty,
    update_rows,
)

DOMAIN_KEYED = text("sync_key = 'domain'")
PASSWORD_KEYED = text("sync_key = 'password'")
CONFLICT_RULES = {
    "domain": (["username", "domain"], DOMAIN_KEYED, ["password", "hash"]),
    "password": (["username", "password"], PASSWORD_KEYED, ["hash", "domain"]),
}


class Credential(Base):
    __tablename__ = "credentials"
    __table_args__ = (
        Index(
            "uq_synced_username_domain",
            "username",
            "domain",
            unique=True,
            sqlite_where=DOMAIN_KEYED,
        ),
        Index(
            "uq_synced_username_password",
            "username",
            "password",
            unique=True,
            sqlite_where=PASSWORD_KEYED,
        ),
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
        self.domain = domain.lower()
        self.sync_key = sync_key

    def __eq__(self, value):
        return (
            (self.credential_id == value.credential_id)
            and (self.username == value.username)
            and (self.password == value.password)
            and (self.hash == value.hash)
            and (self.domain.lower() == value.domain.lower())
            and (self.sync_key == value.sync_key)
        )

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
            "domain": domain.lower(),
            "sync_key": sync_key,
        }


def add_credentials(engine: Engine, credentials: list[dict], sync_key: str = ""):
    if not credentials:
        return

    query = insert(Credential)
    if sync_key in CONFLICT_RULES:
        index_elements, index_where, completed = CONFLICT_RULES[sync_key]
        query = query.on_conflict_do_update(
            index_elements=index_elements,
            index_where=index_where,
            set_={c: keep_existing_if_empty(query, Credential, c) for c in completed},
        )

    with Session(engine) as session:
        session.execute(query, credentials)
        session.commit()


def get_credentials(
    engine: Engine, credential_id: str = None, redacted: bool = False
) -> list[Credential]:
    credentials = get_rows(engine, Credential, credential_id)

    if redacted:
        for credential in credentials:
            credential.password = credential.hash = Credential.REDACT_SEPARATOR * 8

    return credentials


def delete_credentials(engine: Engine, credential_ids: list[str]):
    delete_rows(engine, Credential, credential_ids)


def edit_credentials(engine: Engine, credentials: list):
    update_rows(engine, Credential, credentials)
