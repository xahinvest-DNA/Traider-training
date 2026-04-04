from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone

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


REVIEW_SEQUENCE_FIELDS = [
    ("setup_tag", "reviewed setup"),
    ("compliance_label", "compliance label"),
    ("entry_timing_label", "entry timing"),
    ("market_context_label", "market context"),
    ("exit_quality_label", "exit quality"),
    ("review_clarity_label", "review clarity"),
]


def build_trade_review_result(
    trade: TradeRecord,
    chart_snapshots: list[ChartSnapshotRecord],
    pre_trade_notes: list[PreTradeNoteRecord],
    post_trade_reviews: list[PostTradeReviewRecord],
    behavioral_flags: list[BehavioralFlagRecord],
    rule_violations: list[RuleViolationRecord],
    executions: list[ExecutionRecord],
) -> dict:
    snapshot_index = {snapshot.snapshot_id: snapshot for snapshot in chart_snapshots}
    trade_notes = [note for note in pre_trade_notes if note.trade_id == trade.trade_id]
    trade_reviews = [review for review in post_trade_reviews if review.trade_id == trade.trade_id]
    trade_flags = [flag for flag in behavioral_flags if flag.trade_id == trade.trade_id]
    trade_violations = [violation for violation in rule_violations if violation.trade_id == trade.trade_id]
    trade_executions = [execution for execution in executions if execution.trade_id == trade.trade_id]

    latest_note = trade_notes[-1] if trade_notes else None
    latest_review = trade_reviews[-1] if trade_reviews else None
    latest_note_snapshot = _resolve_snapshot_summary(
        latest_note.chart_snapshot_ref if latest_note else None,
        snapshot_index,
    )
    latest_review_snapshots = _resolve_snapshot_summaries(
        latest_review.chart_snapshot_refs if latest_review else (),
        snapshot_index,
    )
    linked_snapshot_summaries = _merge_snapshot_summaries(latest_note_snapshot, latest_review_snapshots)
    review_status = _review_status(trade, trade_reviews)
    method_facets = _build_method_facets(latest_review)
    intent_delta = _build_intent_delta(latest_note, latest_review, method_facets)
    review_completeness = _build_review_completeness(latest_review, method_facets)
    review_rule_context = _build_review_rule_context(
        setup_tag=(latest_review.setup_tag if latest_review and latest_review.setup_tag else latest_note.setup_tag if latest_note else None),
        compliance_label=latest_review.compliance_label if latest_review else None,
        intent_delta=intent_delta,
        behavioral_flag_codes=[flag.flag_code for flag in trade_flags],
        rule_violation_codes=[violation.rule_code for violation in trade_violations],
    )
    review_discipline_cue = _build_review_discipline_cue(review_rule_context)
    review_discipline_badge = _build_review_discipline_badge(review_discipline_cue)
    review_discipline_token = _build_review_discipline_token(review_discipline_badge)
    review_discipline_marker = _build_review_discipline_marker(review_discipline_token)
    review_discipline_glyph = _build_review_discipline_glyph(review_discipline_marker)
    review_discipline_sigil = _build_review_discipline_sigil(review_discipline_glyph)
    review_discipline_seal = _build_review_discipline_seal(review_discipline_sigil)
    review_discipline_crest = _build_review_discipline_crest(review_discipline_seal)
    review_discipline_emblem = _build_review_discipline_emblem(review_discipline_crest)
    review_discipline_reason = _build_review_discipline_reason(
        review_rule_context,
        review_discipline_cue,
        review_discipline_badge,
        review_discipline_emblem,
    )
    review_dataset_quality_link = _build_review_dataset_quality_link(trade_executions)
    review_evidence_status = _build_bill_williams_review_evidence_status(
        latest_note=latest_note,
        latest_review=latest_review,
        latest_note_snapshot=latest_note_snapshot,
        latest_review_snapshots=latest_review_snapshots,
        linked_snapshot_summaries=linked_snapshot_summaries,
        method_facets=method_facets,
    )
    review_evidence_follow_up = _build_bill_williams_review_evidence_follow_up(
        evidence_status=review_evidence_status["evidence_status"],
        latest_note_snapshot=latest_note_snapshot,
        latest_review_snapshots=latest_review_snapshots,
    )
    current_trade_review_digest = _build_current_trade_review_digest(
        review_status=review_status,
        intent_delta=intent_delta,
        review_completeness=review_completeness,
        review_rule_context=review_rule_context,
        review_discipline_reason=review_discipline_reason,
        review_evidence_status=review_evidence_status,
        review_evidence_follow_up=review_evidence_follow_up,
    )

    return {
        "trade_id": trade.trade_id,
        "session_id": trade.session_id,
        "instrument_id": trade.instrument_id,
        "side": trade.side,
        "status": trade.status,
        "opened_at": trade.opened_at,
        "closed_at": trade.closed_at,
        "close_reason": trade.close_reason,
        "stop_loss": trade.stop_loss,
        "take_profit": trade.take_profit,
        "has_initial_trade_protection": trade.stop_loss is not None or trade.take_profit is not None,
        "realised_pnl": trade.realised_pnl,
        "total_trade_cost": trade.total_trade_cost,
        "holding_time_seconds": _holding_time_seconds(trade),
        "outcome_label": _outcome_label(trade),
        "review_status": review_status,
        "setup_tag": (
            latest_review.setup_tag if latest_review and latest_review.setup_tag else latest_note.setup_tag if latest_note else None
        ),
        "compliance_label": latest_review.compliance_label if latest_review else None,
        "review_tags": list(latest_review.review_tags) if latest_review else [],
        "method_facets": method_facets,
        "has_method_facets": any(value is not None for value in method_facets.values()),
        "intent_delta": intent_delta,
        "review_completeness": review_completeness,
        "review_rule_context": review_rule_context,
        "review_discipline_cue": review_discipline_cue,
        "review_discipline_badge": review_discipline_badge,
        "review_discipline_token": review_discipline_token,
        "review_discipline_marker": review_discipline_marker,
        "review_discipline_glyph": review_discipline_glyph,
        "review_discipline_sigil": review_discipline_sigil,
        "review_discipline_seal": review_discipline_seal,
        "review_discipline_crest": review_discipline_crest,
        "review_discipline_emblem": review_discipline_emblem,
        "review_discipline_reason": review_discipline_reason,
        "review_dataset_quality_link": review_dataset_quality_link,
        "bill_williams_review_evidence_status": review_evidence_status["evidence_status"],
        "bill_williams_review_evidence_text": review_evidence_status["evidence_text"],
        "has_bill_williams_review_evidence": review_evidence_status["has_bill_williams_review_evidence"],
        "bill_williams_review_evidence_follow_up_status": review_evidence_follow_up["follow_up_status"],
        "bill_williams_review_evidence_follow_up_text": review_evidence_follow_up["follow_up_text"],
        "current_trade_review_digest_status": current_trade_review_digest["digest_status"],
        "current_trade_review_digest_headline": current_trade_review_digest["digest_headline"],
        "current_trade_review_digest_primary_gap": current_trade_review_digest["digest_primary_gap"],
        "current_trade_review_digest_next_step": current_trade_review_digest["digest_next_step"],
        "pre_trade_note_count": len(trade_notes),
        "post_trade_review_count": len(trade_reviews),
        "behavioral_flag_count": len(trade_flags),
        "rule_violation_count": len(trade_violations),
        "behavioral_flag_codes": [flag.flag_code for flag in trade_flags],
        "rule_violation_codes": [violation.rule_code for violation in trade_violations],
        "has_pre_trade_note": bool(trade_notes),
        "has_post_trade_review": bool(trade_reviews),
        "has_behavioral_flags": bool(trade_flags),
        "has_rule_violations": bool(trade_violations),
        "has_linked_chart_snapshots": bool(linked_snapshot_summaries),
        "linked_chart_snapshot_count": len(linked_snapshot_summaries),
        "linked_chart_snapshot_ids": [summary["snapshot_id"] for summary in linked_snapshot_summaries],
        "latest_pre_trade_note_snapshot": latest_note_snapshot,
        "latest_post_trade_review_snapshots": latest_review_snapshots,
        "latest_pre_trade_note": asdict(latest_note) if latest_note else None,
        "latest_post_trade_review": asdict(latest_review) if latest_review else None,
    }


def build_session_review_output(
    training_session: TrainingSessionRecord,
    trades: list[TradeRecord],
    chart_snapshots: list[ChartSnapshotRecord],
    pre_trade_notes: list[PreTradeNoteRecord],
    post_trade_reviews: list[PostTradeReviewRecord],
    behavioral_flags: list[BehavioralFlagRecord],
    rule_violations: list[RuleViolationRecord],
    executions: list[ExecutionRecord],
) -> dict:
    closed_trades = [trade for trade in trades if trade.status == "closed"]
    trade_results = [
        build_trade_review_result(
            trade=trade,
            chart_snapshots=chart_snapshots,
            pre_trade_notes=pre_trade_notes,
            post_trade_reviews=post_trade_reviews,
            behavioral_flags=behavioral_flags,
            rule_violations=rule_violations,
            executions=executions,
        )
        for trade in closed_trades
    ]
    reviewed_trade_count = sum(1 for result in trade_results if result["review_status"] == "reviewed")
    pending_review_trade_count = sum(1 for result in trade_results if result["review_status"] == "pending_review")
    review_field_coverage = _build_review_field_coverage(trade_results)
    review_weak_spots = _build_review_weak_spots(review_field_coverage)
    trade_results = [
        {**result, "review_sequence": _build_review_sequence(result, review_field_coverage)}
        for result in trade_results
    ]
    win_trade_count = sum(1 for result in trade_results if result["outcome_label"] == "win")
    loss_trade_count = sum(1 for result in trade_results if result["outcome_label"] == "loss")
    flat_trade_count = sum(1 for result in trade_results if result["outcome_label"] == "flat")
    total_holding_time_seconds = sum(result["holding_time_seconds"] or 0 for result in trade_results)

    return {
        "session_id": training_session.session_id,
        "derived_only": True,
        "closed_trade_count": len(closed_trades),
        "reviewed_trade_count": reviewed_trade_count,
        "pending_review_trade_count": pending_review_trade_count,
        "session_net_realised_pnl": sum(trade.realised_pnl for trade in closed_trades),
        "session_total_trade_cost": sum(trade.total_trade_cost for trade in closed_trades),
        "win_trade_count": win_trade_count,
        "loss_trade_count": loss_trade_count,
        "flat_trade_count": flat_trade_count,
        "total_holding_time_seconds": total_holding_time_seconds,
        "average_holding_time_seconds": (
            total_holding_time_seconds / len(closed_trades) if closed_trades else None
        ),
        "review_completion_ratio": (
            reviewed_trade_count / len(closed_trades) if closed_trades else None
        ),
        "behavioral_flag_count": len(behavioral_flags),
        "rule_violation_count": len(rule_violations),
        "trades_with_linked_chart_snapshots_count": sum(
            1 for result in trade_results if result["has_linked_chart_snapshots"]
        ),
        "reviewed_trades_with_bw_evidence_count": sum(
            1 for result in trade_results if result["bill_williams_review_evidence_status"] == "linked_evidence_present"
        ),
        "reviewed_trades_missing_bw_evidence_count": sum(
            1
            for result in trade_results
            if result["bill_williams_review_evidence_status"] in {"linked_evidence_missing", "linked_evidence_partial"}
        ),
        "reviewed_trades_requiring_bw_evidence_follow_up_count": sum(
            1
            for result in trade_results
            if result["bill_williams_review_evidence_follow_up_status"]
            in {"link_any_chart_evidence", "link_pre_trade_snapshot", "link_review_snapshot"}
        ),
        "trades_with_method_facets_count": sum(
            1 for result in trade_results if result["has_method_facets"]
        ),
        "intent_confirmed_count": sum(1 for result in trade_results if result["intent_delta"]["delta_status"] == "intent_confirmed"),
        "intent_refined_count": sum(1 for result in trade_results if result["intent_delta"]["delta_status"] == "intent_refined"),
        "intent_changed_count": sum(1 for result in trade_results if result["intent_delta"]["delta_status"] == "intent_changed"),
        "intent_missing_count": sum(1 for result in trade_results if result["intent_delta"]["delta_status"] == "intent_missing"),
        "review_missing_count": sum(1 for result in trade_results if result["intent_delta"]["delta_status"] == "review_missing"),
        "review_complete_count": sum(1 for result in trade_results if result["review_completeness"]["completeness_status"] == "complete"),
        "review_partial_count": sum(1 for result in trade_results if result["review_completeness"]["completeness_status"] == "partial"),
        "review_sparse_count": sum(1 for result in trade_results if result["review_completeness"]["completeness_status"] == "sparse"),
        "review_pending_completeness_count": sum(1 for result in trade_results if result["review_completeness"]["completeness_status"] == "review_missing"),
        "review_field_coverage": review_field_coverage,
        "review_weak_spots": review_weak_spots,
        "trade_results": trade_results,
        "latest_trade_result": trade_results[-1] if trade_results else None,
    }


def build_session_review_summary(
    training_session: TrainingSessionRecord,
    review_output: dict,
    finalization_projection: dict,
) -> dict:
    trade_results = review_output["trade_results"]
    latest_trade_result = review_output["latest_trade_result"]
    latest_reviewed_trade = next(
        (result for result in reversed(trade_results) if result["review_status"] == "reviewed"),
        None,
    )
    latest_pending_trade = next(
        (result for result in reversed(trade_results) if result["review_status"] == "pending_review"),
        None,
    )
    review_progress = _build_review_progress(review_output["review_weak_spots"], latest_reviewed_trade)
    review_momentum = _build_review_momentum(trade_results)
    review_stability = _build_review_stability(review_momentum)
    review_swings = _build_review_swings(review_momentum)
    review_floor = _build_review_floor(review_momentum)
    review_ceiling = _build_review_ceiling(review_momentum)
    review_band = _build_review_band(review_floor, review_ceiling)
    review_headroom = _build_review_headroom(review_ceiling, review_band)
    review_pressure = _build_review_pressure(review_floor, review_band, review_headroom)
    review_target = _build_review_target(review_pressure, review_output["review_weak_spots"], latest_trade_result)
    review_focus = _build_review_focus(review_target, latest_trade_result, review_pressure)
    review_cue = _build_review_cue(review_focus)
    review_badge = _build_review_badge(review_cue, review_focus)
    review_pill = _build_review_pill(review_badge, review_cue)
    review_chip = _build_review_chip(review_pill, review_badge)
    review_tag = _build_review_tag(review_chip, review_pill)
    review_token = _build_review_token(review_tag, review_chip)
    review_marker = _build_review_marker(review_token, review_tag)
    review_glyph = _build_review_glyph(review_marker, review_token)
    review_sigil = _build_review_sigil(review_glyph, review_marker)
    review_seal = _build_review_seal(review_sigil, review_glyph)
    review_crest = _build_review_crest(review_seal, review_sigil)
    review_emblem = _build_review_emblem(review_crest, review_seal)
    review_insignia = _build_review_insignia(review_emblem, review_crest)
    review_standard = _build_review_standard(review_insignia, review_emblem)
    review_banner = _build_review_banner(review_standard, review_insignia)
    review_pennant = _build_review_pennant(review_banner, review_standard)
    review_streamer = _build_review_streamer(review_pennant, review_banner)
    review_rule_context = _build_session_review_rule_context(latest_trade_result)
    review_discipline_cue = _build_review_discipline_cue(review_rule_context)
    review_discipline_badge = _build_review_discipline_badge(review_discipline_cue)
    review_discipline_token = _build_review_discipline_token(review_discipline_badge)
    review_discipline_marker = _build_review_discipline_marker(review_discipline_token)
    review_discipline_glyph = _build_review_discipline_glyph(review_discipline_marker)
    review_discipline_sigil = _build_review_discipline_sigil(review_discipline_glyph)
    review_discipline_seal = _build_review_discipline_seal(review_discipline_sigil)
    review_discipline_crest = _build_review_discipline_crest(review_discipline_seal)
    review_discipline_emblem = _build_review_discipline_emblem(review_discipline_crest)
    review_discipline_reason = _build_review_discipline_reason(
        review_rule_context,
        review_discipline_cue,
        review_discipline_badge,
        review_discipline_emblem,
    )
    review_dataset_quality_link = _build_session_review_dataset_quality_link(latest_trade_result)

    return {
        "session_id": training_session.session_id,
        "derived_only": True,
        "session_status": training_session.status,
        "finalization_status": finalization_projection["finalization_status"],
        "is_session_finalized": finalization_projection["is_session_finalized"],
        "finalization_reason": finalization_projection["finalization_reason"],
        "summary_status": _summary_status(finalization_projection, review_output),
        "closed_trade_count": review_output["closed_trade_count"],
        "reviewed_trade_count": review_output["reviewed_trade_count"],
        "pending_review_trade_count": review_output["pending_review_trade_count"],
        "pending_review_trade_ids": list(finalization_projection["pending_review_trade_ids"]),
        "review_completion_ratio": review_output["review_completion_ratio"],
        "behavioral_flag_count": review_output["behavioral_flag_count"],
        "rule_violation_count": review_output["rule_violation_count"],
        "trades_with_linked_chart_snapshots_count": review_output["trades_with_linked_chart_snapshots_count"],
        "trades_with_method_facets_count": review_output["trades_with_method_facets_count"],
        "intent_confirmed_count": review_output["intent_confirmed_count"],
        "intent_refined_count": review_output["intent_refined_count"],
        "intent_changed_count": review_output["intent_changed_count"],
        "intent_missing_count": review_output["intent_missing_count"],
        "review_missing_count": review_output["review_missing_count"],
        "review_complete_count": review_output["review_complete_count"],
        "review_partial_count": review_output["review_partial_count"],
        "review_sparse_count": review_output["review_sparse_count"],
        "review_pending_completeness_count": review_output["review_pending_completeness_count"],
        "review_field_coverage": review_output["review_field_coverage"],
        "review_weak_spots": review_output["review_weak_spots"],
        "review_progress": review_progress,
        "review_momentum": review_momentum,
        "review_stability": review_stability,
        "review_swings": review_swings,
        "review_floor": review_floor,
        "review_ceiling": review_ceiling,
        "review_band": review_band,
        "review_headroom": review_headroom,
        "review_pressure": review_pressure,
        "review_target": review_target,
        "review_focus": review_focus,
        "review_cue": review_cue,
        "review_badge": review_badge,
        "review_pill": review_pill,
        "review_chip": review_chip,
        "review_tag": review_tag,
        "review_token": review_token,
        "review_marker": review_marker,
        "review_glyph": review_glyph,
        "review_sigil": review_sigil,
        "review_seal": review_seal,
        "review_crest": review_crest,
        "review_emblem": review_emblem,
        "review_insignia": review_insignia,
        "review_standard": review_standard,
        "review_banner": review_banner,
        "review_pennant": review_pennant,
        "review_streamer": review_streamer,
        "review_rule_context": review_rule_context,
        "review_discipline_cue": review_discipline_cue,
        "review_discipline_badge": review_discipline_badge,
        "review_discipline_token": review_discipline_token,
        "review_discipline_marker": review_discipline_marker,
        "review_discipline_glyph": review_discipline_glyph,
        "review_discipline_sigil": review_discipline_sigil,
        "review_discipline_seal": review_discipline_seal,
        "review_discipline_crest": review_discipline_crest,
        "review_discipline_emblem": review_discipline_emblem,
        "review_discipline_reason": review_discipline_reason,
        "review_dataset_quality_link": review_dataset_quality_link,
        "requires_force_to_finalize": finalization_projection["requires_force_to_finalize"],
        "can_finalize_without_force": finalization_projection["can_finalize_without_force"],
        "can_finalize_with_force": finalization_projection["can_finalize_with_force"],
        "reviewed_trades_with_bw_evidence_count": review_output["reviewed_trades_with_bw_evidence_count"],
        "reviewed_trades_missing_bw_evidence_count": review_output["reviewed_trades_missing_bw_evidence_count"],
        "reviewed_trades_requiring_bw_evidence_follow_up_count": review_output["reviewed_trades_requiring_bw_evidence_follow_up_count"],
        "latest_trade_id": latest_trade_result["trade_id"] if latest_trade_result else None,
        "latest_trade_outcome_label": latest_trade_result["outcome_label"] if latest_trade_result else None,
        "latest_review_status": latest_trade_result["review_status"] if latest_trade_result else None,
        "latest_setup_tag": latest_trade_result["setup_tag"] if latest_trade_result else None,
        "latest_compliance_label": latest_trade_result["compliance_label"] if latest_trade_result else None,
        "latest_method_facets": latest_trade_result["method_facets"] if latest_trade_result else None,
        "latest_intent_delta": latest_trade_result["intent_delta"] if latest_trade_result else None,
        "latest_review_completeness": latest_trade_result["review_completeness"] if latest_trade_result else None,
        "latest_review_sequence": latest_trade_result["review_sequence"] if latest_trade_result else None,
        "latest_bill_williams_review_evidence_status": (
            latest_trade_result["bill_williams_review_evidence_status"] if latest_trade_result else "not_applicable"
        ),
        "latest_bill_williams_review_evidence_text": (
            latest_trade_result["bill_williams_review_evidence_text"] if latest_trade_result else None
        ),
        "latest_bill_williams_review_evidence_follow_up_status": (
            latest_trade_result["bill_williams_review_evidence_follow_up_status"]
            if latest_trade_result
            else "not_applicable"
        ),
        "latest_bill_williams_review_evidence_follow_up_text": (
            latest_trade_result["bill_williams_review_evidence_follow_up_text"] if latest_trade_result else None
        ),
        "latest_current_trade_review_digest_status": (
            latest_trade_result["current_trade_review_digest_status"] if latest_trade_result else "not_applicable"
        ),
        "latest_current_trade_review_digest_headline": (
            latest_trade_result["current_trade_review_digest_headline"] if latest_trade_result else None
        ),
        "latest_current_trade_review_digest_primary_gap": (
            latest_trade_result["current_trade_review_digest_primary_gap"] if latest_trade_result else None
        ),
        "latest_current_trade_review_digest_next_step": (
            latest_trade_result["current_trade_review_digest_next_step"] if latest_trade_result else None
        ),
        "latest_linked_chart_snapshot_count": (
            latest_trade_result["linked_chart_snapshot_count"] if latest_trade_result else 0
        ),
        "latest_reviewed_trade_id": latest_reviewed_trade["trade_id"] if latest_reviewed_trade else None,
        "latest_pending_review_trade_id": latest_pending_trade["trade_id"] if latest_pending_trade else None,
    }


def _summary_status(finalization_projection: dict, review_output: dict) -> str:
    pending_review_trade_count = review_output["pending_review_trade_count"]
    closed_trade_count = review_output["closed_trade_count"]
    if finalization_projection["is_session_finalized"]:
        if pending_review_trade_count:
            return "finalized_with_pending_review"
        return "finalized_review_complete"
    if pending_review_trade_count:
        return "review_pending"
    if closed_trade_count and review_output["reviewed_trade_count"] == closed_trade_count:
        return "review_complete"
    if closed_trade_count == 0:
        return "no_closed_trades"
    return "open_in_progress"


def _review_status(trade: TradeRecord, trade_reviews: list[PostTradeReviewRecord]) -> str:
    if trade.status != "closed":
        return "not_ready"
    if trade_reviews:
        return "reviewed"
    return "pending_review"


def _outcome_label(trade: TradeRecord) -> str:
    if trade.status != "closed":
        return "open"
    if trade.realised_pnl > 0:
        return "win"
    if trade.realised_pnl < 0:
        return "loss"
    return "flat"


def _holding_time_seconds(trade: TradeRecord) -> int | None:
    if not trade.closed_at:
        return None
    opened_at = _parse_utc(trade.opened_at)
    closed_at = _parse_utc(trade.closed_at)
    return int((closed_at - opened_at).total_seconds())


def _build_method_facets(review: PostTradeReviewRecord | None) -> dict:
    if review is None:
        return {
            "setup_variant": None,
            "entry_timing_label": None,
            "market_context_label": None,
            "exit_quality_label": None,
            "review_clarity_label": None,
        }
    return {
        "setup_variant": review.setup_variant,
        "entry_timing_label": review.entry_timing_label,
        "market_context_label": review.market_context_label,
        "exit_quality_label": review.exit_quality_label,
        "review_clarity_label": review.review_clarity_label,
    }


def _build_session_review_rule_context(latest_trade_result: dict | None) -> dict:
    if latest_trade_result is None:
        return {
            "context_status": "no_review_rule_context",
            "context_text": None,
            "setup_tag": None,
            "compliance_label": None,
            "behavioral_flag_codes": [],
            "rule_violation_codes": [],
        }
    return dict(latest_trade_result.get("review_rule_context") or {
        "context_status": "no_review_rule_context",
        "context_text": None,
        "setup_tag": latest_trade_result.get("setup_tag"),
        "compliance_label": latest_trade_result.get("compliance_label"),
        "behavioral_flag_codes": list(latest_trade_result.get("behavioral_flag_codes", [])),
        "rule_violation_codes": list(latest_trade_result.get("rule_violation_codes", [])),
    })


def _build_review_rule_context(
    setup_tag: str | None,
    compliance_label: str | None,
    intent_delta: dict,
    behavioral_flag_codes: list[str],
    rule_violation_codes: list[str],
) -> dict:
    delta_status = intent_delta.get("delta_status")
    discipline_codes = behavioral_flag_codes + rule_violation_codes
    discipline_text = ", ".join(discipline_codes) if discipline_codes else None

    if setup_tag is None and compliance_label is None and delta_status == "review_missing":
        context_status = "review_missing_rule_context"
        context_text = "No reviewed Bill Williams rule context yet because the trade still has no post-trade review."
    elif delta_status == "intent_changed":
        context_status = "intent_changed_rule_context"
        context_text = (
            f"Reviewed setup shifted from {intent_delta.get('declared_setup_tag') or '-'} to {intent_delta.get('reviewed_setup_tag') or setup_tag or '-'}; "
            "re-check whether the original Bill Williams intent was too coarse or the trade plan drifted."
        )
    elif compliance_label and compliance_label != "valid_setup":
        context_status = "compliance_break_rule_context"
        context_text = (
            f"Reviewed setup {setup_tag or '-'} is marked {compliance_label}; "
            + (f"discipline pressure also showed through {discipline_text}." if discipline_text else "check the method rule context before treating the trade as valid.")
        )
    elif discipline_codes:
        context_status = "valid_setup_discipline_break"
        context_text = f"Reviewed setup {setup_tag or '-'} stayed valid, but discipline slipped through {discipline_text}."
    elif delta_status in {"intent_confirmed", "intent_refined"} and compliance_label == "valid_setup":
        context_status = "aligned_rule_context"
        context_text = f"Reviewed setup {setup_tag or '-'} stayed aligned with declared intent and no discipline breaks were captured."
    elif delta_status == "intent_missing":
        context_status = "intent_missing_rule_context"
        context_text = f"Reviewed setup {setup_tag or '-'} is present, but no declared pre-trade Bill Williams intent was captured."
    else:
        context_status = "partial_rule_context"
        context_text = f"Bill Williams rule context for {setup_tag or '-'} is still partial; complete review and discipline notes before drawing stronger conclusions."

    return {
        "context_status": context_status,
        "context_text": context_text,
        "setup_tag": setup_tag,
        "compliance_label": compliance_label,
        "behavioral_flag_codes": list(behavioral_flag_codes),
        "rule_violation_codes": list(rule_violation_codes),
    }


def _build_intent_delta(
    note: PreTradeNoteRecord | None,
    review: PostTradeReviewRecord | None,
    method_facets: dict,
) -> dict:
    declared_setup_tag = note.setup_tag if note else None
    reviewed_setup_tag = review.setup_tag if review else None
    has_declared_intent = declared_setup_tag is not None
    has_reviewed_intent = reviewed_setup_tag is not None
    has_method_refinement = any(value is not None for value in method_facets.values())

    if has_declared_intent and not review:
        delta_status = "review_missing"
    elif not has_declared_intent and has_reviewed_intent:
        delta_status = "intent_missing"
    elif not has_declared_intent and not has_reviewed_intent:
        delta_status = "both_missing"
    elif declared_setup_tag != reviewed_setup_tag:
        delta_status = "intent_changed"
    elif has_method_refinement:
        delta_status = "intent_refined"
    else:
        delta_status = "intent_confirmed"

    return {
        "declared_setup_tag": declared_setup_tag,
        "reviewed_setup_tag": reviewed_setup_tag,
        "delta_status": delta_status,
        "has_declared_intent": has_declared_intent,
        "has_reviewed_intent": has_reviewed_intent,
        "setup_tag_changed": has_declared_intent and has_reviewed_intent and declared_setup_tag != reviewed_setup_tag,
        "method_facets_refine_intent": has_method_refinement,
    }


def _build_review_completeness(review: PostTradeReviewRecord | None, method_facets: dict) -> dict:
    required_parts = {
        "setup_tag": review.setup_tag if review else None,
        "compliance_label": review.compliance_label if review else None,
        "entry_timing_label": method_facets["entry_timing_label"],
        "market_context_label": method_facets["market_context_label"],
        "exit_quality_label": method_facets["exit_quality_label"],
        "review_clarity_label": method_facets["review_clarity_label"],
    }
    missing_parts = [part for part, value in required_parts.items() if value is None]
    filled_part_count = sum(1 for value in required_parts.values() if value is not None)
    total_part_count = len(required_parts)

    if review is None:
        completeness_status = "review_missing"
    elif filled_part_count == total_part_count:
        completeness_status = "complete"
    elif filled_part_count >= 3:
        completeness_status = "partial"
    else:
        completeness_status = "sparse"

    return {
        "completeness_status": completeness_status,
        "filled_part_count": filled_part_count,
        "total_part_count": total_part_count,
        "missing_parts": missing_parts,
        "is_review_complete": completeness_status == "complete",
    }


def _build_review_ceiling(review_momentum: dict) -> dict:
    score_sequence = review_momentum.get("score_sequence", [])
    if not score_sequence:
        return {
            "ceiling_status": "insufficient_history",
            "max_recent_score": None,
            "advisory_prompt": None,
        }

    max_recent_score = max(score_sequence)
    if max_recent_score >= 3:
        ceiling_status = "high_ceiling"
        advisory_prompt = "Recent Bill Williams review quality is reaching a high ceiling."
    elif max_recent_score == 2:
        ceiling_status = "moderate_ceiling"
        advisory_prompt = "Recent Bill Williams review quality is reaching a moderate ceiling."
    else:
        ceiling_status = "low_ceiling"
        advisory_prompt = "Recent Bill Williams review quality is still capped by a low ceiling."

    return {
        "ceiling_status": ceiling_status,
        "max_recent_score": max_recent_score,
        "advisory_prompt": advisory_prompt,
    }


def _build_review_band(review_floor: dict, review_ceiling: dict) -> dict:
    min_recent_score = review_floor.get("min_recent_score")
    max_recent_score = review_ceiling.get("max_recent_score")
    if min_recent_score is None or max_recent_score is None:
        return {
            "band_status": "insufficient_history",
            "min_recent_score": min_recent_score,
            "max_recent_score": max_recent_score,
            "band_width": None,
            "corridor_label": None,
            "advisory_prompt": None,
        }

    band_width = max_recent_score - min_recent_score
    corridor_label = f"{min_recent_score}-{max_recent_score}"
    if band_width == 0:
        band_status = "tight_band"
        advisory_prompt = f"Recent Bill Williams review quality is holding a tight band at {corridor_label}."
    elif band_width == 1:
        band_status = "controlled_band"
        advisory_prompt = f"Recent Bill Williams review quality is moving inside a controlled band of {corridor_label}."
    else:
        band_status = "wide_band"
        advisory_prompt = f"Recent Bill Williams review quality is spanning a wide band of {corridor_label}."

    return {
        "band_status": band_status,
        "min_recent_score": min_recent_score,
        "max_recent_score": max_recent_score,
        "band_width": band_width,
        "corridor_label": corridor_label,
        "advisory_prompt": advisory_prompt,
    }


def _build_review_headroom(review_ceiling: dict, review_band: dict) -> dict:
    max_recent_score = review_ceiling.get("max_recent_score")
    corridor_label = review_band.get("corridor_label")
    max_possible_recent_score = 3
    if max_recent_score is None:
        return {
            "headroom_status": "insufficient_history",
            "max_recent_score": None,
            "max_possible_recent_score": max_possible_recent_score,
            "remaining_headroom": None,
            "corridor_label": corridor_label,
            "advisory_prompt": None,
        }

    remaining_headroom = max(0, max_possible_recent_score - max_recent_score)
    if remaining_headroom <= 0:
        headroom_status = "no_headroom"
        advisory_prompt = "Recent Bill Williams review quality is already touching the current bounded ceiling."
    elif remaining_headroom == 1:
        headroom_status = "narrow_headroom"
        advisory_prompt = "Recent Bill Williams review quality still has a narrow step of headroom above the current ceiling."
    else:
        headroom_status = "open_headroom"
        advisory_prompt = "Recent Bill Williams review quality still has open headroom above the current ceiling."

    return {
        "headroom_status": headroom_status,
        "max_recent_score": max_recent_score,
        "max_possible_recent_score": max_possible_recent_score,
        "remaining_headroom": remaining_headroom,
        "corridor_label": corridor_label,
        "advisory_prompt": advisory_prompt,
    }


def _build_review_glyph(review_marker: dict, review_token: dict) -> dict:
    marker_status = review_marker.get("marker_status")
    marker_text = review_marker.get("marker_text")
    token_text = review_token.get("token_text")

    glyph_status_map = {
        "tighten_marker": "tighten_glyph",
        "raise_floor_marker": "raise_floor_glyph",
        "push_ceiling_marker": "push_ceiling_glyph",
        "sequence_marker": "sequence_glyph",
        "hold_quality_marker": "hold_quality_glyph",
    }
    glyph_status = glyph_status_map.get(marker_status, "no_review_glyph")
    glyph_text = marker_text or token_text

    return {
        "glyph_status": glyph_status,
        "glyph_text": glyph_text,
    }


def _build_review_sigil(review_glyph: dict, review_marker: dict) -> dict:
    glyph_status = review_glyph.get("glyph_status")
    glyph_text = review_glyph.get("glyph_text")
    marker_text = review_marker.get("marker_text")

    sigil_status_map = {
        "tighten_glyph": "tighten_sigil",
        "raise_floor_glyph": "raise_floor_sigil",
        "push_ceiling_glyph": "push_ceiling_sigil",
        "sequence_glyph": "sequence_sigil",
        "hold_quality_glyph": "hold_quality_sigil",
    }
    sigil_status = sigil_status_map.get(glyph_status, "no_review_sigil")
    sigil_text = glyph_text or marker_text

    return {
        "sigil_status": sigil_status,
        "sigil_text": sigil_text,
    }


def _build_review_seal(review_sigil: dict, review_glyph: dict) -> dict:
    sigil_status = review_sigil.get("sigil_status")
    sigil_text = review_sigil.get("sigil_text")
    glyph_text = review_glyph.get("glyph_text")

    seal_status_map = {
        "tighten_sigil": "tighten_seal",
        "raise_floor_sigil": "raise_floor_seal",
        "push_ceiling_sigil": "push_ceiling_seal",
        "sequence_sigil": "sequence_seal",
        "hold_quality_sigil": "hold_quality_seal",
    }
    seal_status = seal_status_map.get(sigil_status, "no_review_seal")
    seal_text = sigil_text or glyph_text

    return {
        "seal_status": seal_status,
        "seal_text": seal_text,
    }


def _build_review_crest(review_seal: dict, review_sigil: dict) -> dict:
    seal_status = review_seal.get("seal_status")
    seal_text = review_seal.get("seal_text")
    sigil_text = review_sigil.get("sigil_text")

    crest_status_map = {
        "tighten_seal": "tighten_crest",
        "raise_floor_seal": "raise_floor_crest",
        "push_ceiling_seal": "push_ceiling_crest",
        "sequence_seal": "sequence_crest",
        "hold_quality_seal": "hold_quality_crest",
    }
    crest_status = crest_status_map.get(seal_status, "no_review_crest")
    crest_text = seal_text or sigil_text

    return {
        "crest_status": crest_status,
        "crest_text": crest_text,
    }


def _build_review_emblem(review_crest: dict, review_seal: dict) -> dict:
    crest_status = review_crest.get("crest_status")
    crest_text = review_crest.get("crest_text")
    seal_text = review_seal.get("seal_text")

    emblem_status_map = {
        "tighten_crest": "tighten_emblem",
        "raise_floor_crest": "raise_floor_emblem",
        "push_ceiling_crest": "push_ceiling_emblem",
        "sequence_crest": "sequence_emblem",
        "hold_quality_crest": "hold_quality_emblem",
    }
    emblem_status = emblem_status_map.get(crest_status, "no_review_emblem")
    emblem_text = crest_text or seal_text

    return {
        "emblem_status": emblem_status,
        "emblem_text": emblem_text,
    }


def _build_review_insignia(review_emblem: dict, review_crest: dict) -> dict:
    emblem_status = review_emblem.get("emblem_status")
    emblem_text = review_emblem.get("emblem_text")
    crest_text = review_crest.get("crest_text")

    insignia_status_map = {
        "tighten_emblem": "tighten_insignia",
        "raise_floor_emblem": "raise_floor_insignia",
        "push_ceiling_emblem": "push_ceiling_insignia",
        "sequence_emblem": "sequence_insignia",
        "hold_quality_emblem": "hold_quality_insignia",
    }
    insignia_status = insignia_status_map.get(emblem_status, "no_review_insignia")
    insignia_text = emblem_text or crest_text

    return {
        "insignia_status": insignia_status,
        "insignia_text": insignia_text,
    }


def _build_review_standard(review_insignia: dict, review_emblem: dict) -> dict:
    insignia_status = review_insignia.get("insignia_status")
    insignia_text = review_insignia.get("insignia_text")
    emblem_text = review_emblem.get("emblem_text")

    standard_status_map = {
        "tighten_insignia": "tighten_standard",
        "raise_floor_insignia": "raise_floor_standard",
        "push_ceiling_insignia": "push_ceiling_standard",
        "sequence_insignia": "sequence_standard",
        "hold_quality_insignia": "hold_quality_standard",
    }
    standard_status = standard_status_map.get(insignia_status, "no_review_standard")
    standard_text = insignia_text or emblem_text

    return {
        "standard_status": standard_status,
        "standard_text": standard_text,
    }


def _build_review_banner(review_standard: dict, review_insignia: dict) -> dict:
    standard_status = review_standard.get("standard_status")
    standard_text = review_standard.get("standard_text")
    insignia_text = review_insignia.get("insignia_text")

    banner_status_map = {
        "tighten_standard": "tighten_banner",
        "raise_floor_standard": "raise_floor_banner",
        "push_ceiling_standard": "push_ceiling_banner",
        "sequence_standard": "sequence_banner",
        "hold_quality_standard": "hold_quality_banner",
    }
    banner_status = banner_status_map.get(standard_status, "no_review_banner")
    banner_text = standard_text or insignia_text

    return {
        "banner_status": banner_status,
        "banner_text": banner_text,
    }


def _build_review_pennant(review_banner: dict, review_standard: dict) -> dict:
    banner_status = review_banner.get("banner_status")
    banner_text = review_banner.get("banner_text")
    standard_text = review_standard.get("standard_text")

    pennant_status_map = {
        "tighten_banner": "tighten_pennant",
        "raise_floor_banner": "raise_floor_pennant",
        "push_ceiling_banner": "push_ceiling_pennant",
        "sequence_banner": "sequence_pennant",
        "hold_quality_banner": "hold_quality_pennant",
    }
    pennant_status = pennant_status_map.get(banner_status, "no_review_pennant")
    pennant_text = banner_text or standard_text

    return {
        "pennant_status": pennant_status,
        "pennant_text": pennant_text,
    }


def _build_review_discipline_badge(review_discipline_cue: dict) -> dict:
    cue_status = review_discipline_cue.get("cue_status")
    cue_text = review_discipline_cue.get("cue_text")

    badge_status_map = {
        "discipline_guard_up": "guarded_badge",
        "method_guard_up": "method_guard_badge",
        "intent_recheck": "intent_recheck_badge",
        "discipline_clear": "clear_badge",
        "declare_intent_first": "declare_first_badge",
        "review_first": "review_first_badge",
        "complete_context": "complete_context_badge",
    }
    badge_status = badge_status_map.get(cue_status, "no_discipline_badge")

    badge_text_map = {
        "guarded_badge": "Discipline badge: Guard execution.",
        "method_guard_badge": "Discipline badge: Re-check method rules.",
        "intent_recheck_badge": "Discipline badge: Re-check intent drift.",
        "clear_badge": "Discipline badge: Discipline clear.",
        "declare_first_badge": "Discipline badge: Declare intent first.",
        "review_first_badge": "Discipline badge: Review first.",
        "complete_context_badge": "Discipline badge: Complete context.",
        "no_discipline_badge": cue_text,
    }
    badge_text = badge_text_map.get(badge_status, cue_text)

    return {
        "badge_status": badge_status,
        "badge_text": badge_text,
    }


def _build_review_discipline_token(review_discipline_badge: dict) -> dict:
    badge_status = review_discipline_badge.get("badge_status")
    badge_text = review_discipline_badge.get("badge_text")

    token_status_map = {
        "guarded_badge": "guard_execution_token",
        "method_guard_badge": "recheck_rules_token",
        "intent_recheck_badge": "recheck_intent_token",
        "clear_badge": "discipline_clear_token",
        "declare_first_badge": "declare_intent_token",
        "review_first_badge": "review_required_token",
        "complete_context_badge": "complete_context_token",
    }
    token_status = token_status_map.get(badge_status, "no_discipline_token")

    token_text_map = {
        "guard_execution_token": "Discipline token: Guard execution.",
        "recheck_rules_token": "Discipline token: Re-check rules.",
        "recheck_intent_token": "Discipline token: Re-check intent.",
        "discipline_clear_token": "Discipline token: Discipline clear.",
        "declare_intent_token": "Discipline token: Declare intent.",
        "review_required_token": "Discipline token: Review required.",
        "complete_context_token": "Discipline token: Complete context.",
        "no_discipline_token": badge_text,
    }
    token_text = token_text_map.get(token_status, badge_text)

    return {
        "token_status": token_status,
        "token_text": token_text,
    }


def _build_review_discipline_marker(review_discipline_token: dict) -> dict:
    token_status = review_discipline_token.get("token_status")
    token_text = review_discipline_token.get("token_text")

    marker_status_map = {
        "guard_execution_token": "guard_execution_marker",
        "recheck_rules_token": "recheck_rules_marker",
        "recheck_intent_token": "recheck_intent_marker",
        "discipline_clear_token": "discipline_clear_marker",
        "declare_intent_token": "declare_intent_marker",
        "review_required_token": "review_required_marker",
        "complete_context_token": "complete_context_marker",
    }
    marker_status = marker_status_map.get(token_status, "no_discipline_marker")

    marker_text_map = {
        "guard_execution_marker": "Discipline marker: Guard execution path.",
        "recheck_rules_marker": "Discipline marker: Re-check rule path.",
        "recheck_intent_marker": "Discipline marker: Re-check intent path.",
        "discipline_clear_marker": "Discipline marker: Discipline path clear.",
        "declare_intent_marker": "Discipline marker: Declare intent path.",
        "review_required_marker": "Discipline marker: Review path first.",
        "complete_context_marker": "Discipline marker: Complete context path.",
        "no_discipline_marker": token_text,
    }
    marker_text = marker_text_map.get(marker_status, token_text)

    return {
        "marker_status": marker_status,
        "marker_text": marker_text,
    }


def _build_review_discipline_glyph(review_discipline_marker: dict) -> dict:
    marker_status = review_discipline_marker.get("marker_status")
    marker_text = review_discipline_marker.get("marker_text")

    glyph_status_map = {
        "guard_execution_marker": "guard_execution_glyph",
        "recheck_rules_marker": "recheck_rules_glyph",
        "recheck_intent_marker": "recheck_intent_glyph",
        "discipline_clear_marker": "discipline_clear_glyph",
        "declare_intent_marker": "declare_intent_glyph",
        "review_required_marker": "review_required_glyph",
        "complete_context_marker": "complete_context_glyph",
    }
    glyph_status = glyph_status_map.get(marker_status, "no_discipline_glyph")

    glyph_text_map = {
        "guard_execution_glyph": "Discipline glyph: Guard execution line.",
        "recheck_rules_glyph": "Discipline glyph: Re-check rule line.",
        "recheck_intent_glyph": "Discipline glyph: Re-check intent line.",
        "discipline_clear_glyph": "Discipline glyph: Discipline line clear.",
        "declare_intent_glyph": "Discipline glyph: Declare intent line.",
        "review_required_glyph": "Discipline glyph: Review line first.",
        "complete_context_glyph": "Discipline glyph: Complete context line.",
        "no_discipline_glyph": marker_text,
    }
    glyph_text = glyph_text_map.get(glyph_status, marker_text)

    return {
        "glyph_status": glyph_status,
        "glyph_text": glyph_text,
    }


def _build_review_discipline_sigil(review_discipline_glyph: dict) -> dict:
    glyph_status = review_discipline_glyph.get("glyph_status")
    glyph_text = review_discipline_glyph.get("glyph_text")

    sigil_status_map = {
        "guard_execution_glyph": "guard_execution_sigil",
        "recheck_rules_glyph": "recheck_rules_sigil",
        "recheck_intent_glyph": "recheck_intent_sigil",
        "discipline_clear_glyph": "discipline_clear_sigil",
        "declare_intent_glyph": "declare_intent_sigil",
        "review_required_glyph": "review_required_sigil",
        "complete_context_glyph": "complete_context_sigil",
    }
    sigil_status = sigil_status_map.get(glyph_status, "no_discipline_sigil")

    sigil_text_map = {
        "guard_execution_sigil": "Discipline sigil: Guard execution signal.",
        "recheck_rules_sigil": "Discipline sigil: Re-check rule signal.",
        "recheck_intent_sigil": "Discipline sigil: Re-check intent signal.",
        "discipline_clear_sigil": "Discipline sigil: Discipline signal clear.",
        "declare_intent_sigil": "Discipline sigil: Declare intent signal.",
        "review_required_sigil": "Discipline sigil: Review signal first.",
        "complete_context_sigil": "Discipline sigil: Complete context signal.",
        "no_discipline_sigil": glyph_text,
    }
    sigil_text = sigil_text_map.get(sigil_status, glyph_text)

    return {
        "sigil_status": sigil_status,
        "sigil_text": sigil_text,
    }


def _build_review_discipline_seal(review_discipline_sigil: dict) -> dict:
    sigil_status = review_discipline_sigil.get("sigil_status")
    sigil_text = review_discipline_sigil.get("sigil_text")

    seal_status_map = {
        "guard_execution_sigil": "guard_execution_seal",
        "recheck_rules_sigil": "recheck_rules_seal",
        "recheck_intent_sigil": "recheck_intent_seal",
        "discipline_clear_sigil": "discipline_clear_seal",
        "declare_intent_sigil": "declare_intent_seal",
        "review_required_sigil": "review_required_seal",
        "complete_context_sigil": "complete_context_seal",
    }
    seal_status = seal_status_map.get(sigil_status, "no_discipline_seal")

    seal_text_map = {
        "guard_execution_seal": "Discipline seal: Guard execution lock.",
        "recheck_rules_seal": "Discipline seal: Re-check rule lock.",
        "recheck_intent_seal": "Discipline seal: Re-check intent lock.",
        "discipline_clear_seal": "Discipline seal: Discipline lock clear.",
        "declare_intent_seal": "Discipline seal: Declare intent lock.",
        "review_required_seal": "Discipline seal: Review lock first.",
        "complete_context_seal": "Discipline seal: Complete context lock.",
        "no_discipline_seal": sigil_text,
    }
    seal_text = seal_text_map.get(seal_status, sigil_text)

    return {
        "seal_status": seal_status,
        "seal_text": seal_text,
    }


def _build_review_discipline_crest(review_discipline_seal: dict) -> dict:
    seal_status = review_discipline_seal.get("seal_status")
    seal_text = review_discipline_seal.get("seal_text")

    crest_status_map = {
        "guard_execution_seal": "guard_execution_crest",
        "recheck_rules_seal": "recheck_rules_crest",
        "recheck_intent_seal": "recheck_intent_crest",
        "discipline_clear_seal": "discipline_clear_crest",
        "declare_intent_seal": "declare_intent_crest",
        "review_required_seal": "review_required_crest",
        "complete_context_seal": "complete_context_crest",
    }
    crest_status = crest_status_map.get(seal_status, "no_discipline_crest")

    crest_text_map = {
        "guard_execution_crest": "Discipline crest: Guard execution frame.",
        "recheck_rules_crest": "Discipline crest: Re-check rule frame.",
        "recheck_intent_crest": "Discipline crest: Re-check intent frame.",
        "discipline_clear_crest": "Discipline crest: Discipline frame clear.",
        "declare_intent_crest": "Discipline crest: Declare intent frame.",
        "review_required_crest": "Discipline crest: Review frame first.",
        "complete_context_crest": "Discipline crest: Complete context frame.",
        "no_discipline_crest": seal_text,
    }
    crest_text = crest_text_map.get(crest_status, seal_text)

    return {
        "crest_status": crest_status,
        "crest_text": crest_text,
    }


def _build_review_discipline_emblem(review_discipline_crest: dict) -> dict:
    crest_status = review_discipline_crest.get("crest_status")
    crest_text = review_discipline_crest.get("crest_text")

    emblem_status_map = {
        "guard_execution_crest": "guard_execution_emblem",
        "recheck_rules_crest": "recheck_rules_emblem",
        "recheck_intent_crest": "recheck_intent_emblem",
        "discipline_clear_crest": "discipline_clear_emblem",
        "declare_intent_crest": "declare_intent_emblem",
        "review_required_crest": "review_required_emblem",
        "complete_context_crest": "complete_context_emblem",
    }
    emblem_status = emblem_status_map.get(crest_status, "no_discipline_emblem")

    emblem_text_map = {
        "guard_execution_emblem": "Discipline emblem: Guard execution badge.",
        "recheck_rules_emblem": "Discipline emblem: Re-check rule badge.",
        "recheck_intent_emblem": "Discipline emblem: Re-check intent badge.",
        "discipline_clear_emblem": "Discipline emblem: Discipline badge clear.",
        "declare_intent_emblem": "Discipline emblem: Declare intent badge.",
        "review_required_emblem": "Discipline emblem: Review badge first.",
        "complete_context_emblem": "Discipline emblem: Complete context badge.",
        "no_discipline_emblem": crest_text,
    }
    emblem_text = emblem_text_map.get(emblem_status, crest_text)

    return {
        "emblem_status": emblem_status,
        "emblem_text": emblem_text,
    }


def _build_review_dataset_quality_link(trade_executions: list[ExecutionRecord]) -> dict:
    quality_flags: list[str] = []
    liquidity_flags: list[str] = []
    for execution in trade_executions:
        quality_flags.extend(str(flag) for flag in execution.data_quality_flags)
        liquidity_flags.extend(str(flag) for flag in execution.liquidity_flags)
    quality_flags = list(dict.fromkeys(quality_flags))
    liquidity_flags = list(dict.fromkeys(liquidity_flags))
    combined_flags = quality_flags + liquidity_flags
    if not combined_flags:
        return {
            "link_status": "clean_review_link",
            "link_text": "Review link: dataset quality stayed clean through the current trade lifecycle.",
            "quality_flags": [],
            "liquidity_flags": [],
        }
    combined_preview = ", ".join(combined_flags)
    return {
        "link_status": "warned_execution_review_link",
        "link_text": f"Review link: warned dataset context touched this trade through {combined_preview}.",
        "quality_flags": quality_flags,
        "liquidity_flags": liquidity_flags,
    }



def _build_session_review_dataset_quality_link(latest_trade_result: dict | None) -> dict:
    if latest_trade_result is None:
        return {
            "link_status": "no_review_link",
            "link_text": None,
            "quality_flags": [],
            "liquidity_flags": [],
        }
    return dict(latest_trade_result.get("review_dataset_quality_link") or {
        "link_status": "no_review_link",
        "link_text": None,
        "quality_flags": [],
        "liquidity_flags": [],
    })


def _build_review_discipline_reason(
    review_rule_context: dict,
    review_discipline_cue: dict,
    review_discipline_badge: dict,
    review_discipline_emblem: dict,
) -> dict:
    context_status = review_rule_context.get("context_status")
    setup_tag = review_rule_context.get("setup_tag") or "-"
    discipline_codes = list(review_rule_context.get("behavioral_flag_codes") or []) + list(
        review_rule_context.get("rule_violation_codes") or []
    )
    discipline_text = ", ".join(discipline_codes) if discipline_codes else "no discipline breaks"
    cue_status = review_discipline_cue.get("cue_status")
    badge_status = review_discipline_badge.get("badge_status")
    emblem_status = review_discipline_emblem.get("emblem_status")

    if context_status == "valid_setup_discipline_break":
        reason_status = "guard_execution_reason"
        reason_text = f"Discipline reason: setup {setup_tag} stayed valid, but execution discipline slipped through {discipline_text}."
    elif context_status == "compliance_break_rule_context":
        reason_status = "recheck_rules_reason"
        reason_text = f"Discipline reason: reviewed method compliance broke before discipline could be treated as clear; re-check {setup_tag} against the rule context and {discipline_text}."
    elif context_status == "intent_changed_rule_context":
        reason_status = "recheck_intent_reason"
        reason_text = f"Discipline reason: the reviewed setup drifted from declared intent, so discipline stays gated by intent drift before judging {discipline_text}."
    elif context_status == "aligned_rule_context":
        reason_status = "discipline_clear_reason"
        reason_text = f"Discipline reason: declared intent, reviewed setup, and discipline signals align for {setup_tag}."
    elif context_status == "intent_missing_rule_context":
        reason_status = "declare_intent_reason"
        reason_text = "Discipline reason: no declared method intent was captured, so discipline cannot be grounded cleanly yet."
    elif context_status == "review_missing_rule_context":
        reason_status = "review_required_reason"
        reason_text = "Discipline reason: the post-trade review is still missing, so discipline remains provisional."
    elif context_status == "partial_rule_context":
        reason_status = "complete_context_reason"
        reason_text = "Discipline reason: the current review still lacks rule context, so discipline feedback remains partial."
    else:
        reason_status = "no_discipline_reason"
        reason_text = (
            review_rule_context.get("context_text")
            or review_discipline_emblem.get("emblem_text")
            or review_discipline_badge.get("badge_text")
            or review_discipline_cue.get("cue_text")
        )

    return {
        "reason_status": reason_status,
        "reason_text": reason_text,
        "context_status": context_status,
        "cue_status": cue_status,
        "badge_status": badge_status,
        "emblem_status": emblem_status,
    }


def _build_review_discipline_cue(review_rule_context: dict) -> dict:
    context_status = review_rule_context.get("context_status")
    context_text = review_rule_context.get("context_text")

    cue_status_map = {
        "valid_setup_discipline_break": "discipline_guard_up",
        "compliance_break_rule_context": "method_guard_up",
        "intent_changed_rule_context": "intent_recheck",
        "aligned_rule_context": "discipline_clear",
        "intent_missing_rule_context": "declare_intent_first",
        "review_missing_rule_context": "review_first",
        "partial_rule_context": "complete_context",
    }
    cue_status = cue_status_map.get(context_status, "no_discipline_cue")

    cue_text_map = {
        "discipline_guard_up": "Discipline cue: protect execution discipline around an otherwise valid setup.",
        "method_guard_up": "Discipline cue: re-check Bill Williams rule validity before trusting the setup.",
        "intent_recheck": "Discipline cue: re-check why reviewed setup drifted from declared intent.",
        "discipline_clear": "Discipline cue: method intent and discipline are currently aligned.",
        "declare_intent_first": "Discipline cue: capture declared setup intent before leaning on reviewed conclusions.",
        "review_first": "Discipline cue: complete the post-trade review before drawing discipline conclusions.",
        "complete_context": "Discipline cue: complete the remaining rule context before extracting a sharper discipline lesson.",
        "no_discipline_cue": context_text,
    }
    cue_text = cue_text_map.get(cue_status, context_text)

    return {
        "cue_status": cue_status,
        "cue_text": cue_text,
    }


def _build_review_streamer(review_pennant: dict, review_banner: dict) -> dict:
    pennant_status = review_pennant.get("pennant_status")
    pennant_text = review_pennant.get("pennant_text")
    banner_text = review_banner.get("banner_text")

    streamer_status_map = {
        "tighten_pennant": "tighten_streamer",
        "raise_floor_pennant": "raise_floor_streamer",
        "push_ceiling_pennant": "push_ceiling_streamer",
        "sequence_pennant": "sequence_streamer",
        "hold_quality_pennant": "hold_quality_streamer",
    }
    streamer_status = streamer_status_map.get(pennant_status, "no_review_streamer")
    streamer_text = pennant_text or banner_text

    return {
        "streamer_status": streamer_status,
        "streamer_text": streamer_text,
    }


def _build_review_marker(review_token: dict, review_tag: dict) -> dict:
    token_status = review_token.get("token_status")
    token_text = review_token.get("token_text")
    tag_text = review_tag.get("tag_text")

    marker_status_map = {
        "tighten_token": "tighten_marker",
        "raise_floor_token": "raise_floor_marker",
        "push_ceiling_token": "push_ceiling_marker",
        "sequence_token": "sequence_marker",
        "hold_quality_token": "hold_quality_marker",
    }
    marker_status = marker_status_map.get(token_status, "no_review_marker")
    marker_text = token_text or tag_text

    return {
        "marker_status": marker_status,
        "marker_text": marker_text,
    }


def _build_review_token(review_tag: dict, review_chip: dict) -> dict:
    tag_status = review_tag.get("tag_status")
    tag_text = review_tag.get("tag_text")
    chip_text = review_chip.get("chip_text")

    token_status_map = {
        "tighten_tag": "tighten_token",
        "raise_floor_tag": "raise_floor_token",
        "push_ceiling_tag": "push_ceiling_token",
        "sequence_tag": "sequence_token",
        "hold_quality_tag": "hold_quality_token",
    }
    token_status = token_status_map.get(tag_status, "no_review_token")
    token_text = tag_text or chip_text

    return {
        "token_status": token_status,
        "token_text": token_text,
    }


def _build_review_tag(review_chip: dict, review_pill: dict) -> dict:
    chip_status = review_chip.get("chip_status")
    chip_text = review_chip.get("chip_text")
    pill_text = review_pill.get("pill_text")

    tag_status_map = {
        "tighten_chip": "tighten_tag",
        "raise_floor_chip": "raise_floor_tag",
        "push_ceiling_chip": "push_ceiling_tag",
        "sequence_chip": "sequence_tag",
        "hold_quality_chip": "hold_quality_tag",
    }
    tag_status = tag_status_map.get(chip_status, "no_review_tag")
    tag_text = chip_text or pill_text

    return {
        "tag_status": tag_status,
        "tag_text": tag_text,
    }


def _build_review_chip(review_pill: dict, review_badge: dict) -> dict:
    pill_status = review_pill.get("pill_status")
    pill_text = review_pill.get("pill_text")
    badge_text = review_badge.get("badge_text")

    chip_status_map = {
        "tighten_pill": "tighten_chip",
        "raise_floor_pill": "raise_floor_chip",
        "push_ceiling_pill": "push_ceiling_chip",
        "sequence_pill": "sequence_chip",
        "hold_quality_pill": "hold_quality_chip",
    }
    chip_status = chip_status_map.get(pill_status, "no_review_chip")
    chip_text = pill_text or badge_text

    return {
        "chip_status": chip_status,
        "chip_text": chip_text,
    }


def _build_review_pill(review_badge: dict, review_cue: dict) -> dict:
    badge_status = review_badge.get("badge_status")
    badge_text = review_badge.get("badge_text")
    cue_text = review_cue.get("cue_text")

    pill_status_map = {
        "tighten_badge": "tighten_pill",
        "raise_floor_badge": "raise_floor_pill",
        "push_ceiling_badge": "push_ceiling_pill",
        "sequence_badge": "sequence_pill",
        "hold_quality_badge": "hold_quality_pill",
    }
    pill_status = pill_status_map.get(badge_status, "no_review_pill")
    pill_text = badge_text or cue_text

    return {
        "pill_status": pill_status,
        "pill_text": pill_text,
    }


def _build_review_badge(review_cue: dict, review_focus: dict) -> dict:
    cue_status = review_cue.get("cue_status")
    cue_text = review_cue.get("cue_text")
    focus_status = review_focus.get("focus_status")

    badge_status_map = {
        "tighten_cue": "tighten_badge",
        "raise_floor_cue": "raise_floor_badge",
        "push_ceiling_cue": "push_ceiling_badge",
        "sequence_cue": "sequence_badge",
        "hold_quality_cue": "hold_quality_badge",
    }
    badge_status = badge_status_map.get(cue_status, "no_review_badge")
    badge_text = cue_text

    if badge_text is None and focus_status == "hold_quality_focus":
        badge_text = "Hold current quality"

    return {
        "badge_status": badge_status,
        "badge_text": badge_text,
    }


def _build_review_cue(review_focus: dict) -> dict:
    focus_status = review_focus.get("focus_status")
    focus_label = review_focus.get("focus_label")

    if focus_status == "tighten_focus":
        cue_status = "tighten_cue"
        cue_text = focus_label or "Tighten review focus"
    elif focus_status == "raise_floor_focus":
        cue_status = "raise_floor_cue"
        cue_text = focus_label or "Raise review floor"
    elif focus_status == "push_ceiling_focus":
        cue_status = "push_ceiling_cue"
        cue_text = focus_label or "Push review ceiling"
    elif focus_status == "sequence_focus":
        cue_status = "sequence_cue"
        cue_text = focus_label or "Continue next review step"
    elif focus_status == "hold_quality_focus":
        cue_status = "hold_quality_cue"
        cue_text = "Hold current quality"
    else:
        cue_status = "no_review_cue"
        cue_text = None

    return {
        "cue_status": cue_status,
        "cue_text": cue_text,
    }


def _build_review_focus(review_target: dict, latest_trade_result: dict | None, review_pressure: dict) -> dict:
    latest_sequence = (latest_trade_result or {}).get("review_sequence", {})
    target_field = review_target.get("target_field")
    next_field = latest_sequence.get("next_field")
    pressure_target = review_pressure.get("pressure_target")

    if latest_trade_result is None:
        return {
            "focus_status": "no_review_focus",
            "focus_label": None,
            "focus_prompt": None,
        }

    focus_field = target_field or next_field
    if focus_field and pressure_target == "tighten_band":
        focus_status = "tighten_focus"
        focus_label = f"Tighten around {focus_field}"
        focus_prompt = f"Keep today's review focus tight around {focus_field} before broadening to other fields."
    elif focus_field and pressure_target == "raise_floor":
        focus_status = "raise_floor_focus"
        focus_label = f"Raise floor via {focus_field}"
        focus_prompt = f"Keep today's review focus on lifting the floor through {focus_field}."
    elif focus_field and pressure_target == "push_ceiling":
        focus_status = "push_ceiling_focus"
        focus_label = f"Push ceiling via {focus_field}"
        focus_prompt = f"Keep today's review focus on pushing the ceiling through {focus_field}."
    elif focus_field:
        focus_status = "sequence_focus"
        focus_label = f"Continue with {focus_field}"
        focus_prompt = latest_sequence.get("next_prompt") or f"Keep today's review focus on {focus_field}."
    else:
        focus_status = "hold_quality_focus"
        focus_label = "Hold current quality corridor"
        focus_prompt = "Keep today's review focus on holding the current quality corridor without losing consistency."

    return {
        "focus_status": focus_status,
        "focus_label": focus_label,
        "focus_prompt": focus_prompt,
    }


def _build_review_target(review_pressure: dict, review_weak_spots: dict, latest_trade_result: dict | None) -> dict:
    pressure_target = review_pressure.get("pressure_target")
    weak_fields = list(review_weak_spots.get("top_weak_spot_fields", []))
    latest_sequence = (latest_trade_result or {}).get("review_sequence", {})
    next_field = latest_sequence.get("next_field")

    if latest_trade_result is None:
        return {
            "target_status": "no_review_target",
            "target_field": None,
            "target_prompt": None,
        }

    if pressure_target == "raise_floor" and weak_fields:
        target_status = "weak_spot_target"
        target_field = weak_fields[0]
        target_prompt = f"Raise the review floor by filling the weakest field next: {target_field}."
    elif pressure_target == "tighten_band" and weak_fields:
        target_status = "tighten_band_target"
        target_field = weak_fields[0]
        target_prompt = f"Tighten the recent quality band by reducing drift in: {target_field}."
    elif pressure_target == "push_ceiling" and next_field:
        target_status = "ceiling_target"
        target_field = next_field
        target_prompt = f"Push the review ceiling by advancing the next field cleanly: {target_field}."
    elif next_field:
        target_status = "sequence_target"
        target_field = next_field
        target_prompt = latest_sequence.get("next_prompt") or f"Continue with the next review field: {target_field}."
    else:
        target_status = "hold_quality_target"
        target_field = None
        target_prompt = "Hold the current review quality corridor without losing completeness or consistency."

    return {
        "target_status": target_status,
        "target_field": target_field,
        "target_prompt": target_prompt,
    }


def _build_review_pressure(review_floor: dict, review_band: dict, review_headroom: dict) -> dict:
    min_recent_score = review_floor.get("min_recent_score")
    band_width = review_band.get("band_width")
    remaining_headroom = review_headroom.get("remaining_headroom")

    if min_recent_score is None or band_width is None or remaining_headroom is None:
        return {
            "pressure_status": "insufficient_history",
            "pressure_target": None,
            "advisory_prompt": None,
        }

    if band_width >= 2:
        pressure_status = "tighten_band_pressure"
        pressure_target = "tighten_band"
        advisory_prompt = "Current Bill Williams review pressure is on tightening the recent quality band before pushing higher."
    elif min_recent_score <= 1:
        pressure_status = "raise_floor_pressure"
        pressure_target = "raise_floor"
        advisory_prompt = "Current Bill Williams review pressure is on raising the floor before chasing higher peaks."
    elif remaining_headroom > 0:
        pressure_status = "push_ceiling_pressure"
        pressure_target = "push_ceiling"
        advisory_prompt = "Current Bill Williams review pressure is on pushing the ceiling higher without losing the current floor."
    else:
        pressure_status = "hold_quality_pressure"
        pressure_target = "hold_quality"
        advisory_prompt = "Current Bill Williams review pressure is on holding the current quality corridor without backsliding."

    return {
        "pressure_status": pressure_status,
        "pressure_target": pressure_target,
        "advisory_prompt": advisory_prompt,
    }


def _build_review_floor(review_momentum: dict) -> dict:
    score_sequence = review_momentum.get("score_sequence", [])
    if not score_sequence:
        return {
            "floor_status": "insufficient_history",
            "min_recent_score": None,
            "advisory_prompt": None,
        }

    min_recent_score = min(score_sequence)
    if min_recent_score >= 3:
        floor_status = "strong_floor"
        advisory_prompt = "Recent Bill Williams review quality is holding a strong floor."
    elif min_recent_score == 2:
        floor_status = "moderate_floor"
        advisory_prompt = "Recent Bill Williams review quality is holding a moderate floor."
    else:
        floor_status = "fragile_floor"
        advisory_prompt = "Recent Bill Williams review quality is still resting on a fragile floor."

    return {
        "floor_status": floor_status,
        "min_recent_score": min_recent_score,
        "advisory_prompt": advisory_prompt,
    }


def _build_review_swings(review_momentum: dict) -> dict:
    score_sequence = review_momentum.get("score_sequence", [])
    reviewed_trade_window = review_momentum.get("reviewed_trade_window", [])
    if len(score_sequence) < 2:
        return {
            "swing_status": "insufficient_history",
            "max_adjacent_jump": None,
            "swing_pairs": [],
            "advisory_prompt": None,
        }

    swing_pairs = []
    max_adjacent_jump = 0
    for index in range(1, len(score_sequence)):
        previous_score = score_sequence[index - 1]
        current_score = score_sequence[index]
        jump = abs(current_score - previous_score)
        max_adjacent_jump = max(max_adjacent_jump, jump)
        if jump >= 2:
            swing_pairs.append({
                "from_trade_id": reviewed_trade_window[index - 1],
                "to_trade_id": reviewed_trade_window[index],
                "from_score": previous_score,
                "to_score": current_score,
                "score_jump": jump,
            })

    if swing_pairs:
        swing_status = "sharp_swings_detected"
        advisory_prompt = "Recent Bill Williams review quality shows sharp swings between neighboring reviewed trades."
    else:
        swing_status = "no_sharp_swings"
        advisory_prompt = "Recent Bill Williams review quality does not show sharp swings between neighboring reviewed trades."

    return {
        "swing_status": swing_status,
        "max_adjacent_jump": max_adjacent_jump,
        "swing_pairs": swing_pairs,
        "advisory_prompt": advisory_prompt,
    }


def _build_review_stability(review_momentum: dict) -> dict:
    score_sequence = review_momentum.get("score_sequence", [])
    if len(score_sequence) < 2:
        return {
            "stability_status": "insufficient_history",
            "score_spread": None,
            "advisory_prompt": None,
        }

    score_spread = max(score_sequence) - min(score_sequence)
    if score_spread <= 1:
        stability_status = "stable"
        advisory_prompt = "Recent Bill Williams review quality is relatively stable across the latest reviewed trades."
    else:
        stability_status = "uneven"
        advisory_prompt = "Recent Bill Williams review quality is uneven across the latest reviewed trades."

    return {
        "stability_status": stability_status,
        "score_spread": score_spread,
        "advisory_prompt": advisory_prompt,
    }


def _build_review_momentum(trade_results: list[dict]) -> dict:
    reviewed_results = [result for result in trade_results if result.get("review_status") == "reviewed"]
    recent_results = reviewed_results[-3:]

    if len(recent_results) < 2:
        return {
            "momentum_status": "insufficient_history",
            "reviewed_trade_window": [result["trade_id"] for result in recent_results],
            "score_sequence": [_review_momentum_score(result) for result in recent_results],
            "advisory_prompt": None,
        }

    score_sequence = [_review_momentum_score(result) for result in recent_results]
    first_score = score_sequence[0]
    last_score = score_sequence[-1]

    if last_score > first_score:
        momentum_status = "improving"
        advisory_prompt = "Recent Bill Williams review quality is trending better across the latest reviewed trades."
    elif last_score < first_score:
        momentum_status = "slipping"
        advisory_prompt = "Recent Bill Williams review quality is trending weaker across the latest reviewed trades."
    else:
        momentum_status = "flat"
        advisory_prompt = "Recent Bill Williams review quality is flat across the latest reviewed trades."

    return {
        "momentum_status": momentum_status,
        "reviewed_trade_window": [result["trade_id"] for result in recent_results],
        "score_sequence": score_sequence,
        "advisory_prompt": advisory_prompt,
    }


def _review_momentum_score(trade_result: dict) -> int:
    completeness = trade_result.get("review_completeness", {})
    status = completeness.get("completeness_status")
    score = {
        "review_missing": 0,
        "sparse": 1,
        "partial": 2,
        "complete": 3,
    }.get(status, 0)

    progress = trade_result.get("review_progress")
    if progress is None:
        return score
    progress_status = progress.get("progress_status")
    progress_bonus = {
        "weak_spots_not_improved": 0,
        "weak_spots_partially_improved": 1,
        "weak_spots_improved": 2,
        "no_active_weak_spots": 1,
    }.get(progress_status, 0)
    return score + progress_bonus


def _build_review_progress(weak_spots: dict, latest_reviewed_trade: dict | None) -> dict:
    weak_fields = weak_spots.get("top_weak_spot_fields", [])
    if latest_reviewed_trade is None:
        return {
            "progress_status": "no_reviewed_trade",
            "checked_fields": [],
            "improved_fields": [],
            "still_missing_fields": [],
            "advisory_prompt": None,
        }

    improved_fields = []
    still_missing_fields = []
    for field_name in weak_fields:
        value = _review_sequence_field_value(latest_reviewed_trade, field_name)
        if value is None:
            still_missing_fields.append(field_name)
        else:
            improved_fields.append(field_name)

    if not weak_fields:
        progress_status = "no_active_weak_spots"
        advisory_prompt = "No active Bill Williams weak spots are currently visible in this session."
    elif improved_fields and not still_missing_fields:
        progress_status = "weak_spots_improved"
        advisory_prompt = f"Latest review improved all current weak spots: {', '.join(improved_fields)}."
    elif improved_fields and still_missing_fields:
        progress_status = "weak_spots_partially_improved"
        advisory_prompt = f"Latest review improved {', '.join(improved_fields)} but still missed {', '.join(still_missing_fields)}."
    else:
        progress_status = "weak_spots_not_improved"
        advisory_prompt = f"Latest review still missed the current weak spots: {', '.join(still_missing_fields)}."

    return {
        "progress_status": progress_status,
        "checked_fields": list(weak_fields),
        "improved_fields": improved_fields,
        "still_missing_fields": still_missing_fields,
        "advisory_prompt": advisory_prompt,
    }


def _build_review_weak_spots(coverage: dict) -> dict:
    total_reviewed = coverage.get("total_reviewed_trades", 0)
    ordered_fields = _review_sequence_weakest_fields(coverage)

    field_ratio_map = {
        "setup_tag": coverage.get("setup_tag_coverage_ratio"),
        "compliance_label": coverage.get("compliance_label_coverage_ratio"),
        "entry_timing_label": coverage.get("entry_timing_coverage_ratio"),
        "market_context_label": coverage.get("market_context_coverage_ratio"),
        "exit_quality_label": coverage.get("exit_quality_coverage_ratio"),
        "review_clarity_label": coverage.get("review_clarity_coverage_ratio"),
    }
    field_count_map = {
        "setup_tag": coverage.get("setup_tag_coverage_count", 0),
        "compliance_label": coverage.get("compliance_label_coverage_count", 0),
        "entry_timing_label": coverage.get("entry_timing_coverage_count", 0),
        "market_context_label": coverage.get("market_context_coverage_count", 0),
        "exit_quality_label": coverage.get("exit_quality_coverage_count", 0),
        "review_clarity_label": coverage.get("review_clarity_coverage_count", 0),
    }
    display_map = dict(REVIEW_SEQUENCE_FIELDS)

    underfilled_fields = [field_name for field_name in ordered_fields if (field_ratio_map.get(field_name) or 0.0) < 1.0]
    top_weak_spots = underfilled_fields[:3]

    if total_reviewed == 0:
        weak_spot_status = "no_reviewed_trades"
    elif not underfilled_fields:
        weak_spot_status = "fully_covered"
    else:
        weak_spot_status = "underfilled_fields_present"

    return {
        "weak_spot_status": weak_spot_status,
        "total_reviewed_trades": total_reviewed,
        "underfilled_field_count": len(underfilled_fields),
        "top_weak_spot_fields": top_weak_spots,
        "top_weak_spot_details": [
            {
                "field_name": field_name,
                "display_name": display_map[field_name],
                "coverage_count": field_count_map[field_name],
                "coverage_ratio": field_ratio_map[field_name],
            }
            for field_name in top_weak_spots
        ],
        "advisory_prompt": _build_review_weak_spot_prompt(top_weak_spots, total_reviewed),
    }


def _build_review_weak_spot_prompt(top_weak_spots: list[str], total_reviewed: int) -> str | None:
    if total_reviewed == 0:
        return None
    if not top_weak_spots:
        return "Current session coverage is strong across all Bill Williams review fields."
    return f"Session weak spots are concentrated in: {', '.join(top_weak_spots)}."


def _build_review_sequence(trade_result: dict, coverage: dict) -> dict:
    missing_fields = []
    ordered_steps = []

    for rank, (field_name, display_name) in enumerate(REVIEW_SEQUENCE_FIELDS, start=1):
        value = _review_sequence_field_value(trade_result, field_name)
        if value is None:
            missing_fields.append(field_name)
        ordered_steps.append({
            "field_name": field_name,
            "display_name": display_name,
            "recommended_rank": rank,
            "value_present": value is not None,
            "value": value,
        })

    next_field = missing_fields[0] if missing_fields else None
    for step in ordered_steps:
        if step["value_present"]:
            step["step_status"] = "completed"
        elif step["field_name"] == next_field:
            step["step_status"] = "next"
        else:
            step["step_status"] = "pending"

    if trade_result["review_status"] != "reviewed":
        sequence_status = "review_missing"
    elif next_field is None:
        sequence_status = "complete"
    else:
        sequence_status = "in_progress"

    return {
        "sequence_status": sequence_status,
        "next_field": next_field,
        "next_prompt": _review_sequence_prompt(next_field, trade_result.get("intent_delta", {})),
        "recommended_missing_order": missing_fields,
        "ordered_steps": ordered_steps,
        "session_coverage_support": {
            "total_reviewed_trades": coverage.get("total_reviewed_trades", 0),
            "weakest_fields": _review_sequence_weakest_fields(coverage),
        },
    }


def _review_sequence_field_value(trade_result: dict, field_name: str):
    latest_review = trade_result.get("latest_post_trade_review") or {}
    if field_name in {"setup_tag", "compliance_label"}:
        return latest_review.get(field_name)
    return trade_result.get("method_facets", {}).get(field_name)


def _review_sequence_prompt(next_field: str | None, intent_delta: dict) -> str | None:
    if next_field is None:
        return None
    if next_field == "setup_tag":
        if intent_delta.get("delta_status") == "review_missing":
            return "Confirm the reviewed setup before any deeper Bill Williams review detail."
        return "Capture the reviewed setup before any deeper Bill Williams review detail."
    prompts = {
        "compliance_label": "Mark setup validity before adding method-detail fields.",
        "entry_timing_label": "Describe entry timing before broader context and exit judgment.",
        "market_context_label": "Describe market context before exit quality and clarity.",
        "exit_quality_label": "Evaluate exit quality after entry timing and context are clear.",
        "review_clarity_label": "Finish by rating review clarity after the concrete trade details are filled.",
    }
    return prompts[next_field]


def _review_sequence_weakest_fields(coverage: dict) -> list[str]:
    total_reviewed = coverage.get("total_reviewed_trades", 0)
    if not total_reviewed:
        return []

    field_map = {
        "setup_tag": coverage.get("setup_tag_coverage_ratio"),
        "compliance_label": coverage.get("compliance_label_coverage_ratio"),
        "entry_timing_label": coverage.get("entry_timing_coverage_ratio"),
        "market_context_label": coverage.get("market_context_coverage_ratio"),
        "exit_quality_label": coverage.get("exit_quality_coverage_ratio"),
        "review_clarity_label": coverage.get("review_clarity_coverage_ratio"),
    }
    return [
        field_name
        for field_name, _ in sorted(field_map.items(), key=lambda item: ((item[1] if item[1] is not None else 1.0), item[0]))
    ]



def _build_bill_williams_review_evidence_status(
    latest_note: PreTradeNoteRecord | None,
    latest_review: PostTradeReviewRecord | None,
    latest_note_snapshot: dict | None,
    latest_review_snapshots: list[dict],
    linked_snapshot_summaries: list[dict],
    method_facets: dict,
) -> dict:
    has_review_interpretation = (
        latest_review is not None
        and any(
            value is not None and value != ()
            for value in [
                latest_review.setup_tag,
                latest_review.compliance_label,
                *method_facets.values(),
            ]
        )
    )
    if not has_review_interpretation:
        return {
            "evidence_status": "not_applicable",
            "evidence_text": None,
            "has_bill_williams_review_evidence": False,
        }

    has_any_linked_evidence = bool(linked_snapshot_summaries)
    has_note_context = latest_note is not None
    has_review_context = latest_review is not None
    has_note_evidence = latest_note_snapshot is not None
    has_review_evidence = bool(latest_review_snapshots)

    if not has_any_linked_evidence:
        return {
            "evidence_status": "linked_evidence_missing",
            "evidence_text": "Bill Williams review is filled, but no linked chart evidence is attached yet.",
            "has_bill_williams_review_evidence": False,
        }

    if has_note_context and has_review_context and (not has_note_evidence or not has_review_evidence):
        missing_parts = []
        if not has_note_evidence:
            missing_parts.append("pre-trade context")
        if not has_review_evidence:
            missing_parts.append("review context")
        return {
            "evidence_status": "linked_evidence_partial",
            "evidence_text": (
                "Bill Williams review has partial chart evidence; still missing "
                f"{' and '.join(missing_parts)}."
            ),
            "has_bill_williams_review_evidence": False,
        }

    return {
        "evidence_status": "linked_evidence_present",
        "evidence_text": "Bill Williams review is backed by linked chart context.",
        "has_bill_williams_review_evidence": True,
    }

def _build_bill_williams_review_evidence_follow_up(
    evidence_status: str,
    latest_note_snapshot: dict | None,
    latest_review_snapshots: list[dict],
) -> dict:
    if evidence_status == "not_applicable":
        return {
            "follow_up_status": "not_applicable",
            "follow_up_text": None,
        }

    if evidence_status == "linked_evidence_present":
        return {
            "follow_up_status": "follow_up_not_needed",
            "follow_up_text": None,
        }

    if evidence_status == "linked_evidence_missing":
        return {
            "follow_up_status": "link_any_chart_evidence",
            "follow_up_text": "Link a pre-trade or review chart snapshot to back this Bill Williams review.",
        }

    if evidence_status == "linked_evidence_partial":
        if latest_note_snapshot is None:
            return {
                "follow_up_status": "link_pre_trade_snapshot",
                "follow_up_text": "Link a pre-trade chart snapshot to complete the Bill Williams review evidence.",
            }
        if not latest_review_snapshots:
            return {
                "follow_up_status": "link_review_snapshot",
                "follow_up_text": "Link a review-context snapshot to complete the Bill Williams review evidence.",
            }
        return {
            "follow_up_status": "link_any_chart_evidence",
            "follow_up_text": "Link the missing chart snapshot context to complete the Bill Williams review evidence.",
        }

    return {
        "follow_up_status": "not_applicable",
        "follow_up_text": None,
    }



def _build_current_trade_review_digest(
    review_status: str,
    intent_delta: dict,
    review_completeness: dict,
    review_rule_context: dict,
    review_discipline_reason: dict,
    review_evidence_status: dict,
    review_evidence_follow_up: dict,
) -> dict:
    if review_status != "reviewed":
        return {
            "digest_status": "pending_review",
            "digest_headline": "Post-trade review is still missing for this closed trade.",
            "digest_primary_gap": "pending review",
            "digest_next_step": "Add PostTradeReview to capture the trade takeaway.",
        }

    follow_up_status = review_evidence_follow_up.get("follow_up_status")
    if follow_up_status in {"link_any_chart_evidence", "link_pre_trade_snapshot", "link_review_snapshot"}:
        return {
            "digest_status": "reviewed_gap_open",
            "digest_headline": "Reviewed trade still needs linked chart evidence.",
            "digest_primary_gap": review_evidence_status.get("evidence_text") or "Linked chart evidence is still incomplete for this review.",
            "digest_next_step": review_evidence_follow_up.get("follow_up_text"),
        }

    completeness_status = review_completeness.get("completeness_status")
    missing_parts = list(review_completeness.get("missing_parts") or [])
    if completeness_status in {"partial", "sparse", "review_missing"} and missing_parts:
        next_field = missing_parts[0]
        return {
            "digest_status": "reviewed_gap_open",
            "digest_headline": "Reviewed trade is present, but key review parts are still missing.",
            "digest_primary_gap": f"Missing review parts: {', '.join(missing_parts)}.",
            "digest_next_step": _review_sequence_prompt(next_field, intent_delta),
        }

    reason_status = review_discipline_reason.get("reason_status")
    if reason_status in {
        "guard_execution_reason",
        "recheck_rules_reason",
        "recheck_intent_reason",
        "declare_intent_reason",
        "review_required_reason",
        "complete_context_reason",
    }:
        return {
            "digest_status": "reviewed_gap_open",
            "digest_headline": "Reviewed trade is clear enough, but rule or discipline pressure is still open.",
            "digest_primary_gap": review_discipline_reason.get("reason_text") or review_rule_context.get("context_text"),
            "digest_next_step": None,
        }

    setup_tag = review_rule_context.get("setup_tag") or "-"
    return {
        "digest_status": "reviewed_clear",
        "digest_headline": f"Reviewed trade takeaway is clear for {setup_tag}.",
        "digest_primary_gap": None,
        "digest_next_step": None,
    }


def _build_review_field_coverage(trade_results: list[dict]) -> dict:
    reviewed_results = [result for result in trade_results if result["review_status"] == "reviewed"]
    total_reviewed = len(reviewed_results)

    def count_field(field_name: str) -> int:
        if field_name in {"setup_tag", "compliance_label"}:
            return sum(1 for result in reviewed_results if result.get(field_name) is not None)
        return sum(1 for result in reviewed_results if result["method_facets"].get(field_name) is not None)

    field_counts = {
        "setup_tag": count_field("setup_tag"),
        "compliance_label": count_field("compliance_label"),
        "entry_timing_label": count_field("entry_timing_label"),
        "market_context_label": count_field("market_context_label"),
        "exit_quality_label": count_field("exit_quality_label"),
        "review_clarity_label": count_field("review_clarity_label"),
    }
    return {
        "total_reviewed_trades": total_reviewed,
        "setup_tag_coverage_count": field_counts["setup_tag"],
        "compliance_label_coverage_count": field_counts["compliance_label"],
        "entry_timing_coverage_count": field_counts["entry_timing_label"],
        "market_context_coverage_count": field_counts["market_context_label"],
        "exit_quality_coverage_count": field_counts["exit_quality_label"],
        "review_clarity_coverage_count": field_counts["review_clarity_label"],
        "setup_tag_coverage_ratio": (field_counts["setup_tag"] / total_reviewed) if total_reviewed else None,
        "compliance_label_coverage_ratio": (field_counts["compliance_label"] / total_reviewed) if total_reviewed else None,
        "entry_timing_coverage_ratio": (field_counts["entry_timing_label"] / total_reviewed) if total_reviewed else None,
        "market_context_coverage_ratio": (field_counts["market_context_label"] / total_reviewed) if total_reviewed else None,
        "exit_quality_coverage_ratio": (field_counts["exit_quality_label"] / total_reviewed) if total_reviewed else None,
        "review_clarity_coverage_ratio": (field_counts["review_clarity_label"] / total_reviewed) if total_reviewed else None,
    }


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


def _merge_snapshot_summaries(
    latest_note_snapshot: dict | None,
    latest_review_snapshots: list[dict],
) -> list[dict]:
    summaries = []
    seen_snapshot_ids: set[str] = set()
    for summary in ([latest_note_snapshot] if latest_note_snapshot else []) + latest_review_snapshots:
        snapshot_id = summary["snapshot_id"]
        if snapshot_id in seen_snapshot_ids:
            continue
        seen_snapshot_ids.add(snapshot_id)
        summaries.append(summary)
    return summaries


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


def _parse_utc(timestamp: str) -> datetime:
    if timestamp.endswith("Z"):
        timestamp = timestamp[:-1] + "+00:00"
    return datetime.fromisoformat(timestamp).astimezone(timezone.utc)
