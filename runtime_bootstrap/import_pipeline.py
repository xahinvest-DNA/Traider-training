from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .errors import (
    CorruptedMetadataError,
    DatasetImportError,
    DatasetNotFoundError,
    InvalidManifestError,
)
from .types import SUPPORTED_DATASET_SCHEMA, Tick


DEFAULT_GAP_WARNING_SECONDS = 60


def import_raw_dataset(
    raw_dataset_path: str | Path,
    output_root: str | Path,
    *,
    instrument_id: str | None = None,
    market_profile: str = "FX/CFD",
    price_precision: int = 5,
    timezone_canonical: str = "UTC",
    active_timeframe: str = "M1",
    synchronized_timeframes: Iterable[str] = ("M1", "M5"),
    source_type: str = "user_supplied",
    source_id: str | None = None,
    gap_warning_seconds: int = DEFAULT_GAP_WARNING_SECONDS,
) -> Path:
    raw_path = Path(raw_dataset_path)
    if not raw_path.exists():
        raise DatasetNotFoundError(f"Raw dataset not found: {raw_path}")
    if raw_path.is_dir():
        raise DatasetImportError(f"Raw dataset path must be a file: {raw_path}")
    if price_precision < 0:
        raise InvalidManifestError("price_precision must be non-negative")

    raw_rows = _load_raw_rows(raw_path)
    if not raw_rows:
        raise DatasetImportError("Raw dataset contains no rows")

    normalized_rows, quality_details = _normalize_rows(
        raw_rows,
        price_precision=price_precision,
        gap_warning_seconds=gap_warning_seconds,
    )

    synchronized_timeframes = tuple(str(value) for value in synchronized_timeframes)
    if not synchronized_timeframes:
        raise InvalidManifestError("synchronized_timeframes must not be empty")

    effective_instrument_id = _derive_instrument_id(raw_path, instrument_id)
    checksum = _compute_checksum(normalized_rows)
    dataset_id = f"{_slugify(raw_path.stem)}-{checksum[:8]}-v1"
    output_dir = Path(output_root) / dataset_id
    output_dir.mkdir(parents=True, exist_ok=True)

    imported_at = _format_timestamp(datetime.now(timezone.utc))
    manifest = {
        "schema_version": SUPPORTED_DATASET_SCHEMA,
        "dataset_id": dataset_id,
        "instrument_id": effective_instrument_id,
        "market_profile": market_profile,
        "timezone_canonical": timezone_canonical,
        "price_precision": price_precision,
        "dataset_start_time": normalized_rows[0].timestamp,
        "dataset_end_time": normalized_rows[-1].timestamp,
        "active_timeframe": active_timeframe,
        "synchronized_timeframes": list(synchronized_timeframes),
        "quality_report_ref": "quality_report.json",
        "ticks_ref": "ticks.json",
        "source_type": source_type,
        "source_id": source_id or raw_path.name,
        "raw_input_ref": str(raw_path),
        "imported_at": imported_at,
        "checksum": checksum,
        "quality_summary": quality_details["status"],
        "warning_count": quality_details["warning_count"],
    }
    quality_report = {
        "dataset_id": dataset_id,
        "status": quality_details["status"],
        "warnings": quality_details["warnings"],
        "warning_count": quality_details["warning_count"],
        "warning_preview": quality_details["warning_preview"],
        "errors": [],
        "timezone_canonical": timezone_canonical,
        "normalized_precision": price_precision,
        "raw_row_count": len(raw_rows),
        "tick_count": len(normalized_rows),
        "source_type": source_type,
        "source_id": source_id or raw_path.name,
        "duplicate_tick_count": quality_details["duplicate_tick_count"],
        "duplicate_timestamp_count": quality_details["duplicate_timestamp_count"],
        "unexpected_gap_count": quality_details["unexpected_gap_count"],
        "repaired_out_of_order_count": quality_details["repaired_out_of_order_count"],
        "data_quality_flags": quality_details["data_quality_flags"],
        "liquidity_flags": quality_details["liquidity_flags"],
    }
    ticks_payload = [asdict(tick) for tick in normalized_rows]

    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "quality_report.json").write_text(
        json.dumps(quality_report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "ticks.json").write_text(
        json.dumps(ticks_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output_dir


def run_import(argv: list[str] | None = None) -> str:
    parser = argparse.ArgumentParser(description="Import raw tick data into a normalized replay dataset")
    parser.add_argument("raw_dataset", help="Path to raw CSV, TSV, or JSON tick file")
    parser.add_argument("--output-root", required=True, help="Directory where the normalized dataset will be written")
    parser.add_argument("--instrument", default=None, help="Instrument id override")
    parser.add_argument("--profile", default="FX/CFD", help="Market profile label")
    parser.add_argument("--precision", type=int, default=5, help="Normalized price precision")
    parser.add_argument("--timezone", default="UTC", help="Canonical timezone stored in the manifest")
    parser.add_argument("--active-timeframe", default="M1", help="Primary timeframe label")
    parser.add_argument(
        "--sync-timeframes",
        nargs="+",
        default=["M1", "M5"],
        help="Synchronized timeframe labels",
    )
    args = parser.parse_args(argv)

    output_dir = import_raw_dataset(
        args.raw_dataset,
        args.output_root,
        instrument_id=args.instrument,
        market_profile=args.profile,
        price_precision=args.precision,
        timezone_canonical=args.timezone,
        active_timeframe=args.active_timeframe,
        synchronized_timeframes=args.sync_timeframes,
    )
    return str(output_dir)


def main(argv: list[str] | None = None) -> None:
    print(run_import(argv))


def _load_raw_rows(raw_path: Path) -> list[dict[str, Any]]:
    suffix = raw_path.suffix.lower()
    if suffix in {".csv", ".tsv"}:
        delimiter = "\t" if suffix == ".tsv" else ","
        with raw_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=delimiter)
            rows = [dict(row) for row in reader]
    elif suffix == ".json":
        try:
            payload = json.loads(raw_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            raise CorruptedMetadataError(f"Corrupted raw dataset JSON: {raw_path}") from exc
        if isinstance(payload, list):
            rows = [dict(row) if isinstance(row, dict) else {"value": row} for row in payload]
        else:
            raise DatasetImportError("Raw JSON dataset must be an array of tick objects")
    else:
        raise DatasetImportError(f"Unsupported raw dataset format: {raw_path.suffix or raw_path.name}")

    return rows


def _normalize_rows(
    raw_rows: list[dict[str, Any]],
    *,
    price_precision: int,
    gap_warning_seconds: int,
) -> tuple[list[Tick], dict[str, Any]]:
    prepared_rows: list[dict[str, Any]] = []
    out_of_order_count = 0
    previous_original_timestamp: datetime | None = None

    for index, row in enumerate(raw_rows):
        if not isinstance(row, dict):
            raise DatasetImportError(f"Raw row #{index} is not an object")
        timestamp_raw = row.get("timestamp")
        bid_raw = row.get("bid")
        ask_raw = row.get("ask")
        if timestamp_raw in (None, "") or bid_raw in (None, "") or ask_raw in (None, ""):
            raise DatasetImportError(f"Raw row #{index} must contain timestamp, bid, and ask")
        timestamp = _parse_timestamp(str(timestamp_raw))
        if previous_original_timestamp and timestamp < previous_original_timestamp:
            out_of_order_count += 1
        previous_original_timestamp = timestamp
        try:
            bid_value = float(bid_raw)
            ask_value = float(ask_raw)
        except (TypeError, ValueError) as exc:
            raise DatasetImportError(f"Raw row #{index} contains non-numeric bid/ask") from exc
        if not math.isfinite(bid_value) or not math.isfinite(ask_value):
            raise DatasetImportError(f"Raw row #{index} contains non-finite bid/ask")
        bid = round(bid_value, price_precision)
        ask = round(ask_value, price_precision)
        if ask < bid:
            raise DatasetImportError(f"Raw row #{index} has ask below bid")
        prepared_rows.append(
            {
                "timestamp": timestamp,
                "bid": bid,
                "ask": ask,
                "source_id": _coerce_optional_str(row.get("source_id") or row.get("sourceId")),
            }
        )

    if out_of_order_count > max(10, len(prepared_rows) // 5):
        raise DatasetImportError("Raw dataset contains too many out-of-order ticks to repair safely")

    prepared_rows.sort(key=lambda row: (row["timestamp"], row["bid"], row["ask"], row["source_id"] or ""))

    duplicate_tick_count = 0
    duplicate_timestamp_count = 0
    unexpected_gap_count = 0
    previous_row: dict[str, Any] | None = None
    normalized_ticks: list[Tick] = []

    for row in prepared_rows:
        if previous_row is not None:
            if row["timestamp"] == previous_row["timestamp"]:
                duplicate_timestamp_count += 1
                if row["bid"] == previous_row["bid"] and row["ask"] == previous_row["ask"]:
                    duplicate_tick_count += 1
            gap_seconds = (row["timestamp"] - previous_row["timestamp"]).total_seconds()
            if gap_seconds > gap_warning_seconds:
                unexpected_gap_count += 1

        normalized_ticks.append(
            Tick(
                timestamp=_format_timestamp(row["timestamp"]),
                bid=row["bid"],
                ask=row["ask"],
                source_id=row["source_id"],
            )
        )
        previous_row = row

    warnings: list[str] = []
    data_quality_flags: list[str] = []
    liquidity_flags: list[str] = []
    if out_of_order_count:
        warnings.append(f"repaired_out_of_order_ticks:{out_of_order_count}")
        data_quality_flags.append("repaired_out_of_order_ticks")
    if duplicate_timestamp_count:
        warnings.append(f"duplicate_timestamps:{duplicate_timestamp_count}")
        data_quality_flags.append("duplicate_timestamps")
    if duplicate_tick_count:
        warnings.append(f"duplicate_ticks:{duplicate_tick_count}")
        data_quality_flags.append("duplicate_ticks")
    if unexpected_gap_count:
        warnings.append(f"unexpected_gaps:{unexpected_gap_count}")
        liquidity_flags.append("unexpected_gap")

    status = "accepted_with_warnings" if warnings else "accepted"
    warning_preview = ", ".join(warnings[:3]) if warnings else "none"
    return normalized_ticks, {
        "status": status,
        "warnings": warnings,
        "warning_count": len(warnings),
        "warning_preview": warning_preview,
        "duplicate_tick_count": duplicate_tick_count,
        "duplicate_timestamp_count": duplicate_timestamp_count,
        "unexpected_gap_count": unexpected_gap_count,
        "repaired_out_of_order_count": out_of_order_count,
        "data_quality_flags": data_quality_flags,
        "liquidity_flags": liquidity_flags,
    }


def _parse_timestamp(raw_value: str) -> datetime:
    normalized = raw_value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise DatasetImportError(f"Unparseable timestamp: {raw_value}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    else:
        parsed = parsed.astimezone(timezone.utc)
    return parsed


def _format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _compute_checksum(ticks: list[Tick]) -> str:
    payload = json.dumps([asdict(tick) for tick in ticks], ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _derive_instrument_id(raw_path: Path, instrument_id: str | None) -> str:
    if instrument_id:
        return instrument_id.upper()
    inferred = re.sub(r"[^A-Za-z0-9]+", "", raw_path.stem).upper()
    return inferred or "UNKNOWN"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return slug or "dataset"


def _coerce_optional_str(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value)

