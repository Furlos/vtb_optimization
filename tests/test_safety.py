"""Safety checks for the destructive SQL benchmark (no database required)."""
import pytest

from main import (
    PostgresMassiveOLAPOptimizer,
    get_connection_params,
    require_demo_confirmation,
)


def test_connection_credentials_must_be_set(monkeypatch):
    monkeypatch.delenv("PGPASSWORD", raising=False)
    with pytest.raises(RuntimeError, match="PGPASSWORD"):
        get_connection_params()


def test_configuration_uses_environment(monkeypatch):
    monkeypatch.setenv("PGPASSWORD", "in-memory-test-only")
    monkeypatch.setenv("PGDATABASE", "isolated_test_db")
    params = get_connection_params()
    assert params["database"] == "isolated_test_db"
    assert params["password"] == "in-memory-test-only"


def test_recreation_never_runs_without_explicit_acknowledgement(monkeypatch):
    monkeypatch.delenv("ALLOW_DESTRUCTIVE_DEMO", raising=False)
    monkeypatch.delenv("DEMO_DB_CONFIRM", raising=False)
    demo = PostgresMassiveOLAPOptimizer({"database": "isolated_test_db"})
    # It must fail BEFORE psycopg2.connect or any DROP TABLE.
    with pytest.raises(RuntimeError, match="DROPS"):
        demo.create_massive_test_data()


def test_acknowledgement_requires_exact_database_match(monkeypatch):
    monkeypatch.setenv("ALLOW_DESTRUCTIVE_DEMO", "YES")
    monkeypatch.setenv("DEMO_DB_CONFIRM", "other_db")
    with pytest.raises(RuntimeError, match="database"):
        require_demo_confirmation({"database": "isolated_test_db"})


def test_matching_acknowledgement(monkeypatch):
    monkeypatch.setenv("ALLOW_DESTRUCTIVE_DEMO", "YES")
    monkeypatch.setenv("DEMO_DB_CONFIRM", "isolated_test_db")
    require_demo_confirmation({"database": "isolated_test_db"})
