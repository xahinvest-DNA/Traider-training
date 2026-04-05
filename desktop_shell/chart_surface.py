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
    lines = ["Recent bars:"]
    bars = build_price_bar_model(chart_context["recent_points"])
    for bar in bars[-limit:]:
        lines.append(
            f"{bar['timestamp']}  o={bar['open']:.5f}  h={bar['high']:.5f}  l={bar['low']:.5f}  c={bar['close']:.5f}"
        )
    if len(lines) == 1:
        lines.append("Not enough points for bars yet")
    return lines


def build_price_bar_model(
    recent_points: list[dict[str, Any]],
    group_size: int = 1,
) -> list[dict[str, Any]]:
    if len(recent_points) < 2:
        return []

    if group_size <= 1:
        bars: list[dict[str, Any]] = []
        previous_close = float(recent_points[0]["mid"])
        for point in recent_points[1:]:
            open_price = previous_close
            close_price = float(point["mid"])
            high_price = max(open_price, close_price, float(point["ask"]))
            low_price = min(open_price, close_price, float(point["bid"]))
            bars.append(
                {
                    "index": len(bars),
                    "timestamp": point["timestamp"],
                    "open": open_price,
                    "high": high_price,
                    "low": low_price,
                    "close": close_price,
                    "median": (high_price + low_price) / 2,
                }
            )
            previous_close = close_price
        return bars

    bars: list[dict[str, Any]] = []
    for index in range(0, len(recent_points), group_size):
        chunk = recent_points[index : index + group_size]
        if len(chunk) < 2:
            continue
        high_price = max(point["ask"] for point in chunk)
        low_price = min(point["bid"] for point in chunk)
        bars.append(
            {
                "index": len(bars),
                "timestamp": chunk[-1]["timestamp"],
                "open": chunk[0]["mid"],
                "high": high_price,
                "low": low_price,
                "close": chunk[-1]["mid"],
                "median": (high_price + low_price) / 2,
            }
        )
    return bars


def build_alligator_lines(bars: list[dict[str, Any]]) -> dict[str, list[float | None]]:
    medians = [float(bar["median"]) for bar in bars]
    return {
        "jaw": _build_shifted_sma(medians, period=13, shift=8),
        "teeth": _build_shifted_sma(medians, period=8, shift=5),
        "lips": _build_shifted_sma(medians, period=5, shift=3),
    }


def build_fractal_markers(bars: list[dict[str, Any]]) -> dict[str, list[dict[str, float | int]]]:
    up_markers: list[dict[str, float | int]] = []
    down_markers: list[dict[str, float | int]] = []
    for index in range(2, len(bars) - 2):
        window = bars[index - 2 : index + 3]
        center = bars[index]
        if center["high"] == max(bar["high"] for bar in window) and sum(1 for bar in window if bar["high"] == center["high"]) == 1:
            up_markers.append({"index": index, "value": float(center["high"])})
        if center["low"] == min(bar["low"] for bar in window) and sum(1 for bar in window if bar["low"] == center["low"]) == 1:
            down_markers.append({"index": index, "value": float(center["low"])})
    return {"up": up_markers, "down": down_markers}


def build_ao_values(bars: list[dict[str, Any]]) -> list[float]:
    medians = [float(bar["median"]) for bar in bars]
    ao_values: list[float] = []
    for index in range(len(medians)):
        fast_period = min(5, index + 1)
        slow_period = min(34, index + 1)
        fast = sum(medians[index - fast_period + 1 : index + 1]) / fast_period
        slow = sum(medians[index - slow_period + 1 : index + 1]) / slow_period
        ao_values.append(fast - slow)
    return ao_values


def build_chart_visual_summary(chart_context: dict[str, Any]) -> list[str]:
    bars = build_price_bar_model(chart_context["recent_points"])
    alligator = build_alligator_lines(bars)
    fractals = build_fractal_markers(bars)
    ao_values = build_ao_values(bars)
    return [
        f"Bars: {len(bars)} | Mode: bar chart only",
        f"Alligator: jaw {sum(value is not None for value in alligator['jaw'])} | teeth {sum(value is not None for value in alligator['teeth'])} | lips {sum(value is not None for value in alligator['lips'])}",
        f"Fractals: up {len(fractals['up'])} | down {len(fractals['down'])}",
        f"AO pane: {len(ao_values)} histogram bars",
    ]


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


def build_bar_segments(
    bars: list[dict[str, Any]],
    width: int,
    height: int,
    padding: int = 16,
) -> list[dict[str, float]]:
    if width <= padding * 2 or height <= padding * 2 or not bars:
        return []
    low = min(float(bar["low"]) for bar in bars)
    high = max(float(bar["high"]) for bar in bars)
    if high == low:
        high += 0.00001
    usable_width = width - padding * 2
    usable_height = height - padding * 2
    spacing = usable_width / max(1, len(bars))
    body_half = max(3.0, spacing * 0.22)
    segments: list[dict[str, float]] = []
    for index, bar in enumerate(bars):
        center_x = padding + spacing * (index + 0.5)
        segments.append(
            {
                "x": center_x,
                "left": center_x - body_half,
                "right": center_x + body_half,
                "high_y": _scale_value(float(bar["high"]), low, high, padding, usable_height),
                "low_y": _scale_value(float(bar["low"]), low, high, padding, usable_height),
                "open_y": _scale_value(float(bar["open"]), low, high, padding, usable_height),
                "close_y": _scale_value(float(bar["close"]), low, high, padding, usable_height),
                "index": float(index),
            }
        )
    return segments


def build_overlay_line_points(
    values: list[float | None],
    width: int,
    height: int,
    low: float,
    high: float,
    padding: int = 16,
) -> list[tuple[float, float]]:
    if width <= padding * 2 or height <= padding * 2 or not values:
        return []
    usable_width = width - padding * 2
    usable_height = height - padding * 2
    x_span = max(1, len(values) - 1)
    points: list[tuple[float, float]] = []
    for index, value in enumerate(values):
        if value is None:
            continue
        x = padding + usable_width * (index / x_span)
        y = _scale_value(float(value), low, high, padding, usable_height)
        points.append((x, y))
    return points


def build_fractal_canvas_markers(
    fractals: dict[str, list[dict[str, float | int]]],
    width: int,
    height: int,
    low: float,
    high: float,
    bar_count: int,
    padding: int = 16,
) -> dict[str, list[tuple[float, float]]]:
    if bar_count <= 0:
        return {"up": [], "down": []}
    usable_width = width - padding * 2
    usable_height = height - padding * 2
    x_span = max(1, bar_count - 1)

    def map_marker(marker: dict[str, float | int], offset: float) -> tuple[float, float]:
        index = int(marker["index"])
        x = padding + usable_width * (index / x_span)
        y = _scale_value(float(marker["value"]), low, high, padding, usable_height) + offset
        return (x, y)

    return {
        "up": [map_marker(marker, -10.0) for marker in fractals["up"]],
        "down": [map_marker(marker, 10.0) for marker in fractals["down"]],
    }


def build_ao_histogram_segments(
    ao_values: list[float],
    width: int,
    height: int,
    padding: int = 12,
) -> list[dict[str, float]]:
    if width <= padding * 2 or height <= padding * 2 or not ao_values:
        return []
    minimum = min(min(ao_values), 0.0)
    maximum = max(max(ao_values), 0.0)
    if maximum == minimum:
        maximum += 0.00001
    usable_width = width - padding * 2
    usable_height = height - padding * 2
    spacing = usable_width / max(1, len(ao_values))
    bar_width = max(3.0, spacing * 0.7)
    zero_y = _scale_value(0.0, minimum, maximum, padding, usable_height)
    segments: list[dict[str, float]] = []
    for index, value in enumerate(ao_values):
        center_x = padding + spacing * (index + 0.5)
        value_y = _scale_value(value, minimum, maximum, padding, usable_height)
        segments.append(
            {
                "left": center_x - bar_width / 2,
                "right": center_x + bar_width / 2,
                "top": min(zero_y, value_y),
                "bottom": max(zero_y, value_y),
                "value": value,
                "zero_y": zero_y,
            }
        )
    return segments


def flatten_canvas_points(points: list[tuple[float, float]]) -> list[float]:
    flattened: list[float] = []
    for x, y in points:
        flattened.extend((x, y))
    return flattened


def _build_shifted_sma(values: list[float], period: int, shift: int) -> list[float | None]:
    shifted: list[float | None] = [None] * len(values)
    if not values:
        return shifted
    effective_period = min(period, len(values))
    effective_shift = min(shift, max(0, len(values) - 1))
    for index in range(len(values)):
        current_period = min(effective_period, index + 1)
        average = sum(values[index - current_period + 1 : index + 1]) / current_period
        shifted_index = min(len(values) - 1, index + effective_shift)
        shifted[shifted_index] = average
    return shifted


def _scale_value(value: float, low: float, high: float, padding: int, usable_height: int) -> float:
    normalized = (value - low) / (high - low)
    return padding + usable_height * (1 - normalized)
