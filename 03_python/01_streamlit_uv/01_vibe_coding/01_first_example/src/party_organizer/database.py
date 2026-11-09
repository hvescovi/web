import os
import sqlite3

import streamlit as st
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import sessionmaker

from party_organizer.models import Base


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    try:
        secret_url = st.secrets.get("DATABASE_URL")
    except FileNotFoundError:
        secret_url = None

    if secret_url:
        return str(secret_url)
    return "sqlite:///./party_organizer.db"


def create_database_engine(database_url: str) -> Engine:
    engine_options: dict[str, object] = {"pool_pre_ping": True}
    if database_url.startswith("sqlite"):
        engine_options["connect_args"] = {"check_same_thread": False}
    engine = create_engine(database_url, **engine_options)

    if database_url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def enable_sqlite_foreign_keys(
            connection: sqlite3.Connection, _connection_record: object
        ) -> None:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


engine = create_database_engine(get_database_url())
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
