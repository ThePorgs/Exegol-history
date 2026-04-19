import sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy import case, select, UniqueConstraint, Engine
from sqlalchemy.dialects.sqlite import insert
from exegol_history.db_api.base import Base
from exegol_history.db_api.utils import MESSAGE_ID_NOT_EXIST, OBJECT_ALREADY_EXIST


class Credential(Base):
    __tablename__ = "credentials"
    __table_args__ = (UniqueConstraint("username", "domain"),)

    credential_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(nullable=True)
    password: Mapped[str] = mapped_column(nullable=True)
    hash: Mapped[str] = mapped_column(nullable=True)
    domain: Mapped[str] = mapped_column(nullable=True)

    REDACT_SEPARATOR = "*"

    def __init__(
        self,
        credential_id: int = None,
        username: str = None,
        password: str = None,
        hash: str = None,
        domain: str = None,
    ):
        self.credential_id = credential_id
        self.username = username
        self.password = password
        self.hash = hash
        self.domain = domain

    def __eq__(self, value):
        return (
            (self.credential_id == value.credential_id)
            and (self.username == value.username)
            and (self.password == value.password)
            and (self.hash == value.hash)
            and (self.domain == value.domain)
        )

    def __repr__(self) -> str:
        return f"Credential(credential_id={self.credential_id}, username={self.username}, password={self.password}, hash={self.hash}, domain={self.domain})"

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
        username: str = None,
        password: str = None,
        hash: str = None,
        domain: str = None,
    ) -> dict:
        return {
            "credential_id": credential_id,
            "username": username,
            "password": password,
            "hash": hash,
            "domain": domain,
        }


def add_credentials(engine: Engine, credentials: list[dict]):
    if not credentials:
        return

    with Session(engine) as session:
        query = insert(Credential).values(credentials)
        query = query.on_conflict_do_update(
            index_elements=["username", "domain"],
            set_={
                "username": query.excluded.username,
                "password": case(
                    (query.excluded.password.isnot(None), query.excluded.password),
                    else_=Credential.password,
                ),
                "hash": case(
                    (query.excluded.hash.isnot(None), query.excluded.hash),
                    else_=Credential.hash,
                ),
                "domain": query.excluded.domain,
            },
        )
        session.execute(query)
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


def delete_all_credentials(engine: Engine):
    with Session(engine) as session:
        session.execute(Credential.__table__.delete())
        session.commit()


def edit_credentials(engine: Engine, credentials: list[Credential]):
    with Session(engine) as session:
        try:
            session.bulk_update_mappings(Credential, credentials)
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            raise RuntimeError(OBJECT_ALREADY_EXIST)
        except Exception:
            raise RuntimeError(MESSAGE_ID_NOT_EXIST)
