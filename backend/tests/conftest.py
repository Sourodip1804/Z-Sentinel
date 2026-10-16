from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(ROOT / "ml"))

os.environ["MONGODB_URI"] = "mongomock://localhost"
os.environ["MONGODB_DATABASE"] = "zsentinel_test"
os.environ["FRONTEND_ORIGINS"] = "http://localhost:5173"
os.environ["PAYPAL_CLIENT_ID"] = ""
os.environ["PAYPAL_CLIENT_SECRET"] = ""
os.environ["PAYPAL_WEBHOOK_ID"] = ""

from app.config import get_settings  # noqa: E402

get_settings.cache_clear()


@pytest.fixture(scope="session")
def artifact_path():
    import train as train_mod

    path = ROOT / "ml" / "artifacts" / "zsentinel_pipeline_v1.joblib"
    if not path.exists():
        train_mod.main(quick=True)
    os.environ["MODEL_ARTIFACT_PATH"] = str(path)
    get_settings.cache_clear()
    return path


@pytest.fixture
def client(artifact_path, monkeypatch):
    monkeypatch.setenv("MONGODB_URI", "mongomock://localhost")
    monkeypatch.setenv("MONGODB_DATABASE", "zsentinel_test")
    monkeypatch.setenv("MODEL_ARTIFACT_PATH", str(artifact_path))
    get_settings.cache_clear()
    from app.database import close_mongo
    from app.main import app

    close_mongo()
    with TestClient(app) as test_client:
        yield test_client
    close_mongo()
    get_settings.cache_clear()
