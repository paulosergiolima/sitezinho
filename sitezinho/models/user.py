import datetime
from typing import List
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import db

class User(db.Model):
    __tablename__ = "user_table"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    votes: Mapped[List["Vote"]] = relationship(back_populates="user", cascade="all, delete")
    created: Mapped[datetime.datetime] = mapped_column(DateTime)


class Vote(db.Model):
    __tablename__ = "vote_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    image_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )
    created: Mapped[datetime.datetime] = mapped_column(DateTime)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))
    user: Mapped["User"] = relationship(back_populates="votes")
