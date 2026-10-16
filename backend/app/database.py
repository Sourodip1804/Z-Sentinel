from __future__ import annotations

import logging
from typing import Any, Optional

from pymongo import ASCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError

from .config import get_settings

logger = logging.getLogger("zsentinel")

_client: Optional[Any] = None


class DatabaseUnavailable(Exception):
    pass


def _build_client(uri: str):
    if uri.startswith("mongomock://"):
        import mongomock

        return mongomock.MongoClient()
    return MongoClient(uri, serverSelectionTimeoutMS=4000)


def is_mock_database() -> bool:
    if _client is None:
        return False
    return "mongomock" in type(_client).__module__


def init_mongo(client: Optional[Any] = None, allow_fallback: bool = True) -> Database:
    global _client
    settings = get_settings()
    if client is not None:
        _client = client
    else:
        try:
            _client = _build_client(settings.mongodb_uri)
            if not settings.mongodb_uri.startswith("mongomock://"):
                _client.admin.command("ping")
        except PyMongoError as exc:
            if allow_fallback and getattr(settings, "mongodb_fallback_mock", True):
                import mongomock

                logger.warning(
                    "MongoDB is unavailable at %s (%s). Falling back to in-memory mongomock database. "
                    "Transactions will be stored in memory for this session.",
                    settings.mongodb_uri,
                    exc,
                )
                _client = mongomock.MongoClient()
            else:
                _client = None
                raise DatabaseUnavailable(
                    "MongoDB is unavailable. Set MONGODB_URI to Atlas or start local MongoDB. "
                    f"Details: {exc}"
                ) from exc
    database = _client[settings.mongodb_database]
    ensure_indexes(database["transactions"])
    logger.info(
        "MongoDB connected database=%s mode=%s",
        settings.mongodb_database,
        "mock" if is_mock_database() else "live",
    )
    return database


def close_mongo() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None


def get_client():
    if _client is None:
        raise DatabaseUnavailable("MongoDB client is not initialized.")
    return _client


def get_database() -> Database:
    settings = get_settings()
    return get_client()[settings.mongodb_database]


def transactions_collection() -> Collection:
    return get_database()["transactions"]


def ping_mongo() -> bool:
    try:
        if _client is None:
            return False
        if not is_mock_database():
            get_client().admin.command("ping")
            return True
        return True
    except Exception:
        return False


def ensure_indexes(collection: Collection) -> None:
    collection.create_index("transaction_id", unique=True, name="uniq_transaction_id")
    try:
        collection.create_index(
            "paypal_event_id",
            unique=True,
            name="uniq_paypal_event_id",
            partialFilterExpression={"paypal_event_id": {"$type": "string"}},
        )
    except Exception:
        collection.create_index(
            "paypal_event_id",
            unique=True,
            sparse=True,
            name="uniq_paypal_event_id",
        )
    collection.create_index([("timestamp", ASCENDING)], name="idx_timestamp")
    collection.create_index("risk_level", name="idx_risk_level")
    collection.create_index("decision", name="idx_decision")
