import importlib
from unittest import mock

import pytest
from sqlalchemy.orm import Session
from supabase import Client

from app.core import config as config_module
from app.core import database as database_module

TEST_ENV = {
    "SUPABASE_URL": "https://example.supabase.co",
    "SUPABASE_ANON_KEY": "test-anon-key",
    "SUPABASE_SERVICE_ROLE_KEY": "test-service-role-key",
    "DATABASE_URL": "postgresql+psycopg2://user:pass@localhost:5432/db",
}

RESTORE_ENV = {
    "SUPABASE_URL": "https://project.supabase.com",
    "SUPABASE_ANON_KEY": "anon-key",
    "SUPABASE_SERVICE_ROLE_KEY": "service-role-key",
    "DATABASE_URL": "postgresql+psycopg2://postgres:password@localhost:5432/postgres",
}


@pytest.fixture
def reload_database(monkeypatch):
    # Prevent a real .env file on disk from refilling variables we deliberately unset,
    # and avoid touching a real database or Supabase project during these tests.
    monkeypatch.setattr("dotenv.load_dotenv", lambda *args, **kwargs: None)
    for key, value in TEST_ENV.items():
        monkeypatch.setenv(key, value)

    importlib.reload(config_module)
    module = importlib.reload(database_module)

    yield module

    for key, value in RESTORE_ENV.items():
        monkeypatch.setenv(key, value)
    importlib.reload(config_module)
    importlib.reload(database_module)


def test_engine_is_configured_from_settings_database_url(reload_database):
    assert reload_database.engine.url.render_as_string(hide_password=False) == TEST_ENV["DATABASE_URL"]


def test_get_db_yields_a_session_bound_to_the_engine(reload_database):
    generator = reload_database.get_db()
    session = next(generator)

    assert isinstance(session, Session)
    assert session.get_bind() is reload_database.engine

    # Exhausting the generator must close the session without raising.
    with pytest.raises(StopIteration):
        next(generator)


def test_get_db_closes_the_session_on_early_generator_close(reload_database, monkeypatch):
    session_mock = mock.MagicMock(spec=Session)
    monkeypatch.setattr(reload_database, "SessionLocal", lambda: session_mock)

    generator = reload_database.get_db()
    yielded = next(generator)

    assert yielded is session_mock
    session_mock.close.assert_not_called()

    generator.close()

    session_mock.close.assert_called_once()


def test_get_supabase_returns_a_configured_client(reload_database):
    client = reload_database.get_supabase()

    assert isinstance(client, Client)
