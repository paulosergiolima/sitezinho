import datetime
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON
from .database import db

class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    votes: Mapped[list] = mapped_column(JSON)
    created: Mapped[datetime.datetime] = mapped_column(DateTime)

    def __init__(self, *, username: str, votes: list, created: datetime.datetime):
        self.username = username
        self.votes = votes
        self.created = created