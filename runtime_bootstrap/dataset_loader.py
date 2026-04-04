from __future__ import annotations

import json
from pathlib import Path

from .errors import (
    CorruptedMetadataError,
    DatasetNotFoundError,
    EmptyTickStreamError,
    InvalidManifestError,
    UnsupportedSchemaVersionError,
)
from .types import NormalizedDataset, SUPPORTED_DATASET_SCHEMA, Tick


def _load_json(path: Path) -> dict | list:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise DatasetNotFoundError(f"Missing dataset artifact: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CorruptedMetadataError(f"Corrupted JSON artifact: {path}") from exc


def load_normalized_dataset(dataset_handle: str | Path) -> NormalizedDataset:
    root = Path(dataset_handle)
    if not root.exists():
        raise DatasetNotFoundError(f"Dataset handle not found: {root}")

    manifest = _load_json(root / "manifest.json")
    quality_report = _load_json(root / "quality_report.json")
    ticks_payload = _load_json(root / "ticks.json")

    if not isinstance(manifest, dict):
        raise InvalidManifestError("Manifest must be a JSON object")
    if not isinstance(quality_report, dict):
        raise CorruptedMetadataError("Quality report must be a JSON object")
    if not isinstance(ticks_payload, list):
        raise CorruptedMetadataError("Ticks payload must be a JSON array")

    schema_version = str(manifest.get("schema_version", ""))
    if schema_version != SUPPORTED_DATASET_SCHEMA:
        raise UnsupportedSchemaVersionError(
            f"Unsupported schema_version: {schema_version}"
        )

    required_fields = [
        "dataset_id",
        "instrument_id",
        "market_profile",
        "timezone_canonical",
        "price_precision",
        "dataset_start_time",
        "dataset_end_time",
        "active_timeframe",
        "synchronized_timeframes",
    ]
    missing = [field for field in required_fields if field not in manifest]
    if missing:
        raise InvalidManifestError(f"Manifest missing required fields: {missing}")

    ticks: list[Tick] = []
    for index, raw_tick in enumerate(ticks_payload):
        if not isinstance(raw_tick, dict):
            raise CorruptedMetadataError(f"Tick #{index} is not an object")
        for field in ("timestamp", "bid", "ask"):
            if field not in raw_tick:
                raise CorruptedMetadataError(f"Tick #{index} missing field: {field}")
        ticks.append(
            Tick(
                timestamp=str(raw_tick["timestamp"]),
                bid=float(raw_tick["bid"]),
                ask=float(raw_tick["ask"]),
                source_id=(
                    str(raw_tick["source_id"]) if raw_tick.get("source_id") is not None else None
                ),
            )
        )

    if not ticks:
        raise EmptyTickStreamError("Normalized dataset contains no ticks")

    if ticks[0].timestamp != str(manifest["dataset_start_time"]):
        raise CorruptedMetadataError(
            "dataset_start_time does not match the first normalized tick"
        )
    if ticks[-1].timestamp != str(manifest["dataset_end_time"]):
        raise CorruptedMetadataError(
            "dataset_end_time does not match the last normalized tick"
        )

    return NormalizedDataset(
        dataset_id=str(manifest["dataset_id"]),
        schema_version=schema_version,
        instrument_id=str(manifest["instrument_id"]),
        market_profile=str(manifest["market_profile"]),
        timezone_canonical=str(manifest["timezone_canonical"]),
        price_precision=int(manifest["price_precision"]),
        dataset_start_time=str(manifest["dataset_start_time"]),
        dataset_end_time=str(manifest["dataset_end_time"]),
        active_timeframe=str(manifest["active_timeframe"]),
        synchronized_timeframes=tuple(str(v) for v in manifest["synchronized_timeframes"]),
        manifest=manifest,
        quality_report=quality_report,
        ticks=tuple(ticks),
    )
