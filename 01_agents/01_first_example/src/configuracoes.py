import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool

load_dotenv()


def _database_url() -> str:
    url = os.getenv("POSTGRES_URL_NON_POOLING")
    if not url:
        raise RuntimeError("Defina POSTGRES_URL_NON_POOLING no arquivo .env ou no ambiente.")
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    if not url.startswith("postgresql+psycopg://"):
        raise RuntimeError(
            "POSTGRES_URL_NON_POOLING deve usar postgres://, postgresql:// "
            "ou postgresql+psycopg://."
        )
    return url


class Base(DeclarativeBase):
    pass


engine = create_engine(_database_url(), poolclass=NullPool)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def create_app() -> Flask:
    app = Flask(__name__)
    origins = os.getenv("CORS_ORIGINS", "*")
    CORS(app, origins=[origin.strip() for origin in origins.split(",")])
    return app
