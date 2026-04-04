from __future__ import annotations

from .types import (
    BehavioralFlagRecord,
    ChartSnapshotRecord,
    ExecutionRecord,
    PostTradeReviewRecord,
    PreTradeNoteRecord,
    RuleViolationRecord,
    TradeRecord,
    TrainingSessionRecord,
)


def build_session_timeline_projection(
    training_session: TrainingSessionRecord,
    trades: list[TradeRecord],
    executions: list[ExecutionRecord],
    chart_snapshots: list[ChartSnapshotRecord],
    pre_trade_notes: list[PreTradeNoteRecord],
    post_trade_reviews: list[PostTradeReviewRecord],
    behavioral_flags: list[BehavioralFlagRecord],
    rule_violations: list[RuleViolationRecord],
) -> dict:
    snapshot_index = {snapshot.snapshot_id: snapshot for snapshot in chart_snapshots}
    items: list[dict] = [_build_session_started_item(training_session)]
    items.extend(_build_chart_snapshot_items(chart_snapshots))
    items.extend(_build_trade_items(trades))
    items.extend(_build_execution_items(executions))
    items.extend(_build_note_items(pre_trade_notes, snapshot_index))
    items.extend(_build_review_items(post_trade_reviews, snapshot_index))
    items.extend(_build_behavioral_flag_items(behavioral_flags))
    items.extend(_build_rule_violation_items(rule_violations))

    ordered_items = sorted(items, key=_timeline_sort_key)
    return {
        "session_id": training_session.session_id,
        "derived_only": True,
        "timeline_item_count": len(ordered_items),
        "timeline_items": ordered_items,
        "latest_timeline_item": ordered_items[-1] if ordered_items else None,
    }


def _build_session_started_item(training_session: TrainingSessionRecord) -> dict:
    return {
        "timeline_id": f"session:{training_session.session_id}:started",
        "event_type": "session_started",
        "session_id": training_session.session_id,
        "trade_id": None,
        "execution_id": None,
        "timestamp": training_session.started_at,
        "snapshot_tick_index": -1,
        "title": "Training session started",
        "payload": {
            "mode": training_session.mode,
            "instrument_id": training_session.instrument_id,
            "dataset_id": training_session.dataset_id,
            "status": training_session.status,
        },
    }


def _build_trade_items(trades: list[TradeRecord]) -> list[dict]:
    items: list[dict] = []
    for trade in trades:
        items.append(
            {
                "timeline_id": f"trade:{trade.trade_id}:opened",
                "event_type": "trade_opened",
                "session_id": trade.session_id,
                "trade_id": trade.trade_id,
                "execution_id": None,
                "timestamp": trade.opened_at,
                "snapshot_tick_index": -1,
                "title": "Trade opened",
                "payload": {
                    "side": trade.side,
                    "status": trade.status,
                    "average_entry_price": trade.average_entry_price,
                    "volume_opened": trade.volume_opened,
                },
            }
        )
        if trade.closed_at:
            items.append(
                {
                    "timeline_id": f"trade:{trade.trade_id}:closed",
                    "event_type": "trade_closed",
                    "session_id": trade.session_id,
                    "trade_id": trade.trade_id,
                    "execution_id": None,
                    "timestamp": trade.closed_at,
                    "snapshot_tick_index": -1,
                    "title": "Trade closed",
                    "payload": {
                        "side": trade.side,
                        "close_reason": trade.close_reason,
                        "realised_pnl": trade.realised_pnl,
                        "total_trade_cost": trade.total_trade_cost,
                        "average_exit_price": trade.average_exit_price,
                    },
                }
            )
    return items


def _build_chart_snapshot_items(chart_snapshots: list[ChartSnapshotRecord]) -> list[dict]:
    return [
        {
            "timeline_id": f"snapshot:{snapshot.snapshot_id}",
            "event_type": "chart_snapshot",
            "session_id": snapshot.session_id,
            "trade_id": snapshot.trade_id,
            "execution_id": snapshot.execution_id,
            "timestamp": snapshot.captured_at,
            "snapshot_tick_index": -1,
            "title": "Chart snapshot captured",
            "payload": _snapshot_summary(snapshot),
        }
        for snapshot in chart_snapshots
    ]


def _build_execution_items(executions: list[ExecutionRecord]) -> list[dict]:
    return [
        {
            "timeline_id": f"execution:{execution.execution_id}",
            "event_type": "execution",
            "session_id": execution.session_id,
            "trade_id": execution.trade_id,
            "execution_id": execution.execution_id,
            "timestamp": execution.timestamp,
            "snapshot_tick_index": execution.snapshot_tick_index,
            "title": f"Execution: {execution.execution_type}",
            "payload": {
                "execution_type": execution.execution_type,
                "reason": execution.reason,
                "side": execution.side,
                "fill_price": execution.fill_price,
                "volume": execution.volume,
                "spread": execution.spread,
                "dataset_position_reference": execution.dataset_position_reference,
            },
        }
        for execution in executions
    ]


def _build_note_items(
    pre_trade_notes: list[PreTradeNoteRecord],
    snapshot_index: dict[str, ChartSnapshotRecord],
) -> list[dict]:
    return [
        {
            "timeline_id": f"note:{note.note_id}",
            "event_type": "pre_trade_note",
            "session_id": note.session_id,
            "trade_id": note.trade_id,
            "execution_id": None,
            "timestamp": note.note_timestamp,
            "snapshot_tick_index": -1,
            "title": "Pre-trade note",
            "payload": {
                "note_type": note.note_type,
                "setup_tag": note.setup_tag,
                "content": note.content,
                "thesis_summary": note.thesis_summary,
                "chart_snapshot_ref": note.chart_snapshot_ref,
                "has_chart_snapshot": note.chart_snapshot_ref is not None,
                "linked_chart_snapshot": _resolve_snapshot_summary(note.chart_snapshot_ref, snapshot_index),
            },
        }
        for note in pre_trade_notes
    ]


def _build_review_items(
    post_trade_reviews: list[PostTradeReviewRecord],
    snapshot_index: dict[str, ChartSnapshotRecord],
) -> list[dict]:
    return [
        {
            "timeline_id": f"review:{review.review_id}",
            "event_type": "post_trade_review",
            "session_id": review.session_id,
            "trade_id": review.trade_id,
            "execution_id": None,
            "timestamp": review.review_timestamp,
            "snapshot_tick_index": -1,
            "title": "Post-trade review",
            "payload": {
                "review_type": review.review_type,
                "setup_tag": review.setup_tag,
                "compliance_label": review.compliance_label,
                "review_tags": list(review.review_tags),
                "method_facets": {
                    "setup_variant": review.setup_variant,
                    "entry_timing_label": review.entry_timing_label,
                    "market_context_label": review.market_context_label,
                    "exit_quality_label": review.exit_quality_label,
                    "review_clarity_label": review.review_clarity_label,
                },
                "content": review.content,
                "chart_snapshot_refs": list(review.chart_snapshot_refs),
                "linked_chart_snapshots": _resolve_snapshot_summaries(review.chart_snapshot_refs, snapshot_index),
                "linked_chart_snapshot_count": len(review.chart_snapshot_refs),
            },
        }
        for review in post_trade_reviews
    ]


def _build_behavioral_flag_items(behavioral_flags: list[BehavioralFlagRecord]) -> list[dict]:
    return [
        {
            "timeline_id": f"flag:{flag.flag_id}",
            "event_type": "behavioral_flag",
            "session_id": flag.session_id,
            "trade_id": flag.trade_id,
            "execution_id": flag.execution_id,
            "timestamp": flag.flag_timestamp,
            "snapshot_tick_index": -1,
            "title": "Behavioral flag",
            "payload": {
                "flag_code": flag.flag_code,
                "scope": flag.scope,
                "severity": flag.severity,
                "source": flag.source,
                "review_ref": flag.review_ref,
                "description": flag.description,
            },
        }
        for flag in behavioral_flags
    ]


def _build_rule_violation_items(rule_violations: list[RuleViolationRecord]) -> list[dict]:
    return [
        {
            "timeline_id": f"violation:{violation.violation_id}",
            "event_type": "rule_violation",
            "session_id": violation.session_id,
            "trade_id": violation.trade_id,
            "execution_id": violation.execution_id,
            "timestamp": violation.violation_timestamp,
            "snapshot_tick_index": -1,
            "title": "Rule violation",
            "payload": {
                "rule_code": violation.rule_code,
                "scope": violation.scope,
                "severity": violation.severity,
                "source": violation.source,
                "related_review_ref": violation.related_review_ref,
                "description": violation.description,
            },
        }
        for violation in rule_violations
    ]


def _resolve_snapshot_summary(
    snapshot_ref: str | None,
    snapshot_index: dict[str, ChartSnapshotRecord],
) -> dict | None:
    if snapshot_ref is None:
        return None
    snapshot = snapshot_index.get(snapshot_ref)
    if snapshot is None:
        return None
    return _snapshot_summary(snapshot)


def _resolve_snapshot_summaries(
    snapshot_refs: tuple[str, ...],
    snapshot_index: dict[str, ChartSnapshotRecord],
) -> list[dict]:
    return [
        summary
        for summary in (_resolve_snapshot_summary(snapshot_ref, snapshot_index) for snapshot_ref in snapshot_refs)
        if summary is not None
    ]


def _snapshot_summary(snapshot: ChartSnapshotRecord) -> dict:
    return {
        "snapshot_id": snapshot.snapshot_id,
        "artifact_type": snapshot.artifact_type,
        "artifact_ref": snapshot.artifact_ref,
        "snapshot_role": snapshot.snapshot_role,
        "timeframe_context": snapshot.timeframe_context,
        "trade_id": snapshot.trade_id,
        "execution_id": snapshot.execution_id,
    }


def _timeline_sort_key(item: dict) -> tuple[str, int, int, str]:
    return (
        item["timestamp"],
        item.get("snapshot_tick_index", -1),
        _event_rank(item["event_type"]),
        item["timeline_id"],
    )


def _event_rank(event_type: str) -> int:
    ranks = {
        "session_started": 0,
        "chart_snapshot": 1,
        "pre_trade_note": 2,
        "trade_opened": 3,
        "execution": 4,
        "trade_closed": 5,
        "post_trade_review": 6,
        "behavioral_flag": 7,
        "rule_violation": 8,
    }
    return ranks.get(event_type, 99)
