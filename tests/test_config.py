import importlib

import pytest

from app.core import config as config_module

REQUIRED_VARS = {
    "SUPABASE_URL": "https://example.supabase.co",
    "SUPABASE_ANON_KEY": "test-anon-key",
    "SUPABASE_SERVICE_ROLE_KEY": "test-service-role-key",
    "DATABASE_URL": "postgresql+psycopg2://user:pass@localhost:5432/db",
}


@pytest.fixture
def reload_config(monkeypatch):
    # Prevent a real .env file on disk from refilling variables we deliberately unset.
    monkeypatch.setattr("dotenv.load_dotenv", lambda *args, **kwargs: None)

    yield lambda: importlib.reload(config_module)

    # Leave the module in a working state for any test collected after this one.
    for key, value in REQUIRED_VARS.items():
        monkeypatch.setenv(key, value)
    importlib.reload(config_module)


def test_settings_loads_values_from_environment(monkeypatch, reload_config):
    for key, value in REQUIRED_VARS.items():
        monkeypatch.setenv(key, value)

    module = reload_config()

    assert module.settings.SUPABASE_URL == REQUIRED_VARS["SUPABASE_URL"]
    assert module.settings.SUPABASE_ANON_KEY == REQUIRED_VARS["SUPABASE_ANON_KEY"]
    assert module.settings.SUPABASE_SERVICE_ROLE_KEY == REQUIRED_VARS["SUPABASE_SERVICE_ROLE_KEY"]
    assert module.settings.DATABASE_URL == REQUIRED_VARS["DATABASE_URL"]


@pytest.mark.parametrize("missing_var", list(REQUIRED_VARS))
def test_settings_raises_when_required_var_missing(monkeypatch, reload_config, missing_var):
    for key, value in REQUIRED_VARS.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv(missing_var, raising=False)

    with pytest.raises(RuntimeError, match=missing_var):
        reload_config()


def test_settings_raises_when_required_var_is_blank(monkeypatch, reload_config):
    for key, value in REQUIRED_VARS.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("SUPABASE_URL", "")

    with pytest.raises(RuntimeError, match="SUPABASE_URL"):
        reload_config()
