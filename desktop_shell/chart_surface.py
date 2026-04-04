from __future__ import annotations

from typing import Any


def build_replay_header_lines(replay_view: dict[str, Any]) -> list[str]:
    lines = [
        f"Instrument: {replay_view['instrument_id']}",
        f"Timeframe: {replay_view['active_timeframe']}",
        f"Mode: {replay_view['replay_mode']}",
        f"Status: {replay_view['status']}",
        f"Simulation time: {replay_view['simulation_time']}",
    ]
    dataset_quality = replay_view.get("dataset_quality") or {}
    warning_count = int(dataset_quality.get("warning_count") or 0)
    if warning_count:
        lines.append(f"Import warnings: {dataset_quality.get('status') or 'accepted_with_warnings'} ({warning_count})")
        lines.append(f"Warning preview: {dataset_quality.get('warning_preview') or '-'}")
    return lines


def build_tick_table_lines(chart_context: dict[str, Any], limit: int = 8) -> list[str]:
    lines = ["Recent ticks:"]
    for point in chart_context["recent_points"][-limit:]:
        lines.append(
            f"{point['timestamp']}  bid={point['bid']:.5f}  ask={point['ask']:.5f}  mid={point['mid']:.5f}"
        )
    return lines


def build_mid_price_line_points(
    recent_points: list[dict[str, Any]],
    width: int,
    height: int,
    padding: int = 16,
) -> list[tuple[float, float]]:
    if width <= padding * 2 or height <= padding * 2 or len(recent_points) < 2:
        return []

    mids = [point["mid"] for point in recent_points]
    min_mid = min(mids)
    max_mid = max(mids)
    x_span = max(1, len(recent_points) - 1)
    usable_width = width - padding * 2
    usable_height = height - padding * 2

    if max_mid == min_mid:
        baseline = padding + usable_height / 2
        return [
            (padding + usable_width * (index / x_span), baseline)
            for index in range(len(recent_points))
        ]

    points: list[tuple[float, float]] = []
    for index, point in enumerate(recent_points):
        x = padding + usable_width * (index / x_span)
        normalized = (point["mid"] - min_mid) / (max_mid - min_mid)
        y = padding + usable_height * (1 - normalized)
        points.append((x, y))
    return points


def flatten_canvas_points(points: list[tuple[float, float]]) -> list[float]:
    flattened: list[float] = []
    for x, y in points:
        flattened.extend((x, y))
    return flattened
