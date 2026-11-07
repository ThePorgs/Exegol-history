import sqlalchemy
from sqlalchemy import Engine, delete, func, select
from sqlalchemy.orm import DeclarativeBase, Session

from exegol_history.db_api.utils import MESSAGE_ID_NOT_EXIST, OBJECT_ALREADY_EXIST


class Base(DeclarativeBase):
    def as_dict(self) -> dict:
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def __repr__(self) -> str:
        fields = ", ".join(f"{name}={value}" for name, value in self.as_dict().items())
        return f"{type(self).__name__}({fields})"


def primary_key(model):
    return model.__mapper__.primary_key[0]


def keep_existing_if_empty(query, model, column: str):
    """ON CONFLICT value: the new value, or the stored one if the new is empty."""
    return func.coalesce(func.nullif(getattr(query.excluded, column), ""), getattr(model, column))


def get_rows(engine: Engine, model, object_id=None) -> list:
    query = select(model)

    if object_id:
        query = query.where(primary_key(model) == object_id)

    with Session(engine) as session:
        rows = list(session.scalars(query))
        session.expunge_all()  # usable after the session is closed
        return rows


def delete_rows(engine: Engine, model, ids) -> None:
    with Session(engine) as session:
        result = session.execute(delete(model).where(primary_key(model).in_(ids)))
        session.commit()

    if result.rowcount <= 0:
        raise RuntimeError(MESSAGE_ID_NOT_EXIST)


def update_rows(engine: Engine, model, mappings: list) -> None:
    with Session(engine) as session:
        try:
            session.bulk_update_mappings(model, mappings)
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            raise RuntimeError(OBJECT_ALREADY_EXIST)
        except Exception:
            raise RuntimeError(MESSAGE_ID_NOT_EXIST)