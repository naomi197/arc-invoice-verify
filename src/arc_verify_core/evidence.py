"""Stable JSON serialization and verification-result helpers."""
import hashlib
import json
from datetime import datetime, timezone


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def snapshot_hash(obj) -> str:
    return hashlib.sha256(canonical_json(obj).encode('utf-8')).hexdigest()


def verify_snapshot_hash(snapshot: dict, expected_hash: str) -> bool:
    return isinstance(expected_hash, str) and snapshot_hash(snapshot) == expected_hash


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')
