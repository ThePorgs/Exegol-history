from sqlalchemy.orm import Mapped, mapped_column

from exegol_history.db_api.base import Base


class SyncNxcTime(Base):
    __tablename__ = "synctime"

    timestamp_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    timestamp: Mapped[float] = mapped_column(nullable=False)

    def __init__(
            self,
            timestamp_id: int = None,
            filename: str = "",
            timestamp: float = 0.0
        ):
            self.timestamp_id = timestamp_id
            self.filename = filename
            self.timestamp = timestamp
