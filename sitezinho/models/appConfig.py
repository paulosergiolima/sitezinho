import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sitezinho.models.database import db

class AppConfig(db.Model):
    """Model to store application configuration settings"""
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    config_key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    config_value: Mapped[str] = mapped_column(String(255), nullable=False)
    created: Mapped[datetime.datetime] = mapped_column(DateTime)
    updated: Mapped[datetime.datetime] = mapped_column(DateTime)

    def __init__(self, *, config_key: str, config_value: str):
        self.config_key = config_key
        self.config_value = config_value
        self.created = datetime.datetime.now(ZoneInfo("America/Sao_Paulo"))
        self.updated = datetime.datetime.now(ZoneInfo("America/Sao_Paulo"))