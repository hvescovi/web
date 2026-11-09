from party_organizer.database import create_database_engine, get_database_url


def test_environment_database_url_takes_precedence(monkeypatch) -> None:
    url = "mysql+pymysql://user:password@db.example.org:3306/festa"
    monkeypatch.setenv("DATABASE_URL", url)

    assert get_database_url() == url


def test_sqlite_engine_enables_foreign_keys() -> None:
    engine = create_database_engine("sqlite:///:memory:")
    try:
        with engine.connect() as connection:
            enabled = connection.exec_driver_sql("PRAGMA foreign_keys").scalar_one()
        assert enabled == 1
    finally:
        engine.dispose()


def test_mysql_engine_uses_pymysql_driver() -> None:
    engine = create_database_engine(
        "mysql+pymysql://user:password@localhost:3306/festa"
    )
    try:
        assert engine.dialect.name == "mysql"
        assert engine.dialect.driver == "pymysql"
    finally:
        engine.dispose()
