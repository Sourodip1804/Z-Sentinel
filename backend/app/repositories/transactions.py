from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from pymongo.errors import DuplicateKeyError, PyMongoError

from ..database import transactions_collection


class PersistenceError(Exception):
    pass


class DuplicateEventError(Exception):
    def __init__(self, existing: dict[str, Any]):
        super().__init__("Duplicate PayPal event")
        self.existing = existing


def _aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


class TransactionRepository:
    def insert(self, document: dict[str, Any]) -> dict[str, Any]:
        payload = dict(document)
        payload["timestamp"] = _aware(payload["timestamp"])
        if payload.get("paypal_event_id"):
            existing = self.find_by_paypal_event(payload["paypal_event_id"])
            if existing:
                raise DuplicateEventError(existing)
        try:
            transactions_collection().insert_one(payload)
        except DuplicateKeyError as exc:
            if payload.get("paypal_event_id"):
                existing = self.find_by_paypal_event(payload["paypal_event_id"])
                if existing:
                    raise DuplicateEventError(existing) from exc
            raise PersistenceError("Transaction ID already exists") from exc
        except PyMongoError as exc:
            raise PersistenceError(f"Failed to persist transaction: {exc}") from exc
        payload.pop("_id", None)
        return payload

    def find_by_id(self, transaction_id: str) -> Optional[dict[str, Any]]:
        doc = transactions_collection().find_one({"transaction_id": transaction_id}, {"_id": 0})
        return doc

    def find_by_paypal_event(self, event_id: str) -> Optional[dict[str, Any]]:
        return transactions_collection().find_one({"paypal_event_id": event_id}, {"_id": 0})

    def list_recent(
        self,
        page: int = 1,
        page_size: int = 20,
        risk_level: Optional[str] = None,
        decision: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], int]:
        query: dict[str, Any] = {}
        if risk_level:
            query["risk_level"] = risk_level
        if decision:
            query["decision"] = decision
        collection = transactions_collection()
        try:
            total = collection.count_documents(query)
            skip = max(page - 1, 0) * page_size
            cursor = (
                collection.find(query, {"_id": 0})
                .sort("timestamp", -1)
                .skip(skip)
                .limit(page_size)
            )
            return list(cursor), total
        except PyMongoError as exc:
            raise PersistenceError(f"Failed to query transactions: {exc}") from exc

    def stats(self) -> dict[str, Any]:
        collection = transactions_collection()
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_transactions": {"$sum": 1},
                        "high_risk_transactions": {
                            "$sum": {"$cond": [{"$eq": ["$risk_level", "HIGH"]}, 1, 0]}
                        },
                        "approved": {
                            "$sum": {"$cond": [{"$eq": ["$decision", "APPROVE"]}, 1, 0]}
                        },
                        "review": {
                            "$sum": {"$cond": [{"$eq": ["$decision", "REVIEW"]}, 1, 0]}
                        },
                        "blocked": {
                            "$sum": {"$cond": [{"$eq": ["$decision", "BLOCK"]}, 1, 0]}
                        },
                        "average_inference_ms": {"$avg": "$inference_time_ms"},
                    }
                }
            ]
            rows = list(collection.aggregate(pipeline))
        except PyMongoError as exc:
            raise PersistenceError(f"Failed to aggregate stats: {exc}") from exc
        if not rows:
            return {
                "total_transactions": 0,
                "high_risk_transactions": 0,
                "approved": 0,
                "review": 0,
                "blocked": 0,
                "average_inference_ms": 0.0,
            }
        row = rows[0]
        return {
            "total_transactions": int(row.get("total_transactions") or 0),
            "high_risk_transactions": int(row.get("high_risk_transactions") or 0),
            "approved": int(row.get("approved") or 0),
            "review": int(row.get("review") or 0),
            "blocked": int(row.get("blocked") or 0),
            "average_inference_ms": round(float(row.get("average_inference_ms") or 0), 2),
        }

    def risk_counts(self) -> dict[str, int]:
        collection = transactions_collection()
        try:
            pipeline = [{"$group": {"_id": "$risk_level", "count": {"$sum": 1}}}]
            rows = list(collection.aggregate(pipeline))
        except PyMongoError as exc:
            raise PersistenceError(f"Failed to aggregate risk: {exc}") from exc
        counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
        for row in rows:
            key = row.get("_id")
            if key in counts:
                counts[key] = int(row["count"])
        return counts
