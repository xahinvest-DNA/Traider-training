from __future__ import annotations

from typing import Any


def build_workflow_guidance_lines(
    replay_view: dict[str, Any],
    trading_view: dict[str, Any],
    journal_view: dict[str, Any],
) -> list[str]:
    summary = journal_view["session_review_summary"]
    finalization = journal_view["session_finalization"]
    dataset_quality = journal_view.get("dataset_quality_context") or replay_view.get("dataset_quality") or {}
    recovery_ack = journal_view.get("dataset_quality_recovery_acknowledgment") or {}
    latest_trade_id = summary.get("latest_trade_id") or "-"
    latest_trade_result = journal_view["derived_review_output"].get("latest_trade_result")

    if finalization["is_session_finalized"]:
        lines = [
            "Workflow guidance:",
            "Session finalized. Review the latest result or restart with a new local session.",
            f"Finalization reason: {finalization['finalization_reason'] or '-'}",
        ]
        quality_link = finalization.get("dataset_quality_finalization_link") or {}
        recovery_note = journal_view.get("dataset_quality_recovery_note") or {}
        if quality_link.get("link_text"):
            lines.append(quality_link["link_text"])
        if recovery_note.get("note_text"):
            lines.append(recovery_note["note_text"])
        _append_recovery_acknowledgment_guidance(lines, recovery_ack)
        return _append_dataset_quality_context(lines, dataset_quality)

    if trading_view["active_trade_present"]:
        if replay_view["status"] == "paused":
            lines = [
                "Workflow guidance:",
                "Active trade is open. Advance replay or resume playback to manage it.",
                "Close the trade before trying to finalize the session.",
            ]
            return _append_dataset_quality_context(lines, dataset_quality)
        lines = [
            "Workflow guidance:",
            "Active trade is open while replay is running.",
            "Monitor the trade and use manual close when you are ready.",
        ]
        return _append_dataset_quality_context(lines, dataset_quality)

    if summary["pending_review_trade_count"] > 0:
        return _build_review_prompt_lines(
            summary,
            latest_trade_result,
            latest_trade_id,
            pending_review=True,
            dataset_quality=dataset_quality,
        )

    if latest_trade_result is not None:
        completeness = latest_trade_result.get("review_completeness", {})
        if latest_trade_result.get("review_status") == "reviewed" and completeness.get("completeness_status") in {"partial", "sparse"}:
            return _build_review_prompt_lines(
                summary,
                latest_trade_result,
                latest_trade_id,
                pending_review=False,
                dataset_quality=dataset_quality,
            )

    if latest_trade_result is not None:
        follow_up_status = latest_trade_result.get("bill_williams_review_evidence_follow_up_status")
        if follow_up_status in {"link_any_chart_evidence", "link_pre_trade_snapshot", "link_review_snapshot"}:
            lines = [
                "Workflow guidance:",
                "Latest Bill Williams review still needs linked chart evidence.",
                f"Latest reviewed trade: {summary.get('latest_reviewed_trade_id') or latest_trade_id}",
            ]
            _append_review_messages(lines, summary, latest_trade_result)
            return _append_dataset_quality_context(lines, dataset_quality)

    if summary["closed_trade_count"] > 0 and finalization["can_finalize_without_force"]:
        lines = [
            "Workflow guidance:",
            "The current session is review-complete and ready for standard finalization.",
            f"Latest reviewed trade: {summary.get('latest_reviewed_trade_id') or latest_trade_id}",
        ]
        _append_review_messages(lines, summary, latest_trade_result)
        return _append_dataset_quality_context(lines, dataset_quality)

    if journal_view["pre_trade_note_count"] > 0:
        lines = [
            "Workflow guidance:",
            "Pre-trade context is already captured.",
            "Open a trade when you are ready, or continue replay observation.",
        ]
        return _append_dataset_quality_context(lines, dataset_quality)

    lines = [
        "Workflow guidance:",
        "No trade is active and no review is pending.",
        "Add a PreTradeNote or open a trade to continue the local training loop.",
    ]
    return _append_dataset_quality_context(lines, dataset_quality)


def _build_review_prompt_lines(
    summary: dict[str, Any],
    latest_trade_result: dict[str, Any] | None,
    latest_trade_id: str,
    pending_review: bool,
    dataset_quality: dict[str, Any],
) -> list[str]:
    prompt_lines = [
        "Workflow guidance:",
        (
            f"Add PostTradeReview for {summary.get('latest_pending_review_trade_id') or latest_trade_id}."
            if pending_review
            else f"Refine PostTradeReview for {summary.get('latest_reviewed_trade_id') or latest_trade_id}."
        ),
    ]
    if latest_trade_result is None:
        prompt_lines.append("Use Force Finalize only if you intentionally want to close the session with pending review.")
        return _append_dataset_quality_context(prompt_lines, dataset_quality)

    intent_delta = latest_trade_result.get("intent_delta", {})
    completeness = latest_trade_result.get("review_completeness", {})
    delta_status = intent_delta.get("delta_status")
    missing_parts = completeness.get("missing_parts", [])

    if delta_status == "review_missing":
        prompt_lines.append("Start by confirming reviewed setup and compliance for the closed trade.")
    elif delta_status == "intent_changed":
        prompt_lines.append("Explain why the reviewed setup differs from the declared pre-trade intent.")
    elif delta_status == "intent_refined":
        prompt_lines.append("Clarify what changed between the declared setup and the reviewed interpretation.")

    if missing_parts:
        prompt_lines.append(f"Next missing review parts: {', '.join(missing_parts)}")
    elif pending_review:
        prompt_lines.append("Start by confirming reviewed setup and compliance for the closed trade.")
    else:
        prompt_lines.append("Review detail is sufficient. Standard Finalize is available when you are ready.")

    _append_review_messages(prompt_lines, summary, latest_trade_result)

    if pending_review:
        prompt_lines.append("Use Force Finalize only if you intentionally want to close the session with pending review.")
    else:
        follow_up_status = latest_trade_result.get("bill_williams_review_evidence_follow_up_status")
        if follow_up_status in {"link_any_chart_evidence", "link_pre_trade_snapshot", "link_review_snapshot"}:
            prompt_lines.append("Complete the linked chart evidence step before treating this review as fully backed.")
        elif not missing_parts:
            prompt_lines.append("Review detail is sufficient. Standard Finalize is available when you are ready.")
    return _append_dataset_quality_context(prompt_lines, dataset_quality)


def _append_review_messages(lines: list[str], summary: dict[str, Any], latest_trade_result: dict[str, Any] | None) -> None:
    message_fields = [
        summary.get("latest_current_trade_review_digest_headline"),
        summary.get("latest_current_trade_review_digest_primary_gap"),
        summary.get("latest_current_trade_review_digest_next_step"),
        (summary.get("review_weak_spots") or {}).get("advisory_prompt"),
        (summary.get("review_progress") or {}).get("advisory_prompt"),
        (summary.get("review_momentum") or {}).get("advisory_prompt"),
        (summary.get("review_stability") or {}).get("advisory_prompt"),
        (summary.get("review_swings") or {}).get("advisory_prompt"),
        (summary.get("review_floor") or {}).get("advisory_prompt"),
        (summary.get("review_ceiling") or {}).get("advisory_prompt"),
        (summary.get("review_band") or {}).get("advisory_prompt"),
        (summary.get("review_headroom") or {}).get("advisory_prompt"),
        (summary.get("review_pressure") or {}).get("advisory_prompt"),
        (summary.get("review_target") or {}).get("target_prompt"),
        (summary.get("review_focus") or {}).get("focus_label"),
        (summary.get("review_focus") or {}).get("focus_prompt"),
        (summary.get("review_cue") or {}).get("cue_text"),
        (summary.get("review_badge") or {}).get("badge_text"),
        (summary.get("review_pill") or {}).get("pill_text"),
        (summary.get("review_chip") or {}).get("chip_text"),
        (summary.get("review_tag") or {}).get("tag_text"),
        (summary.get("review_token") or {}).get("token_text"),
        (summary.get("review_marker") or {}).get("marker_text"),
        (summary.get("review_glyph") or {}).get("glyph_text"),
        (summary.get("review_sigil") or {}).get("sigil_text"),
        (summary.get("review_seal") or {}).get("seal_text"),
        (summary.get("review_crest") or {}).get("crest_text"),
        (summary.get("review_emblem") or {}).get("emblem_text"),
        (summary.get("review_insignia") or {}).get("insignia_text"),
        (summary.get("review_standard") or {}).get("standard_text"),
        (summary.get("review_banner") or {}).get("banner_text"),
        (summary.get("review_pennant") or {}).get("pennant_text"),
        (summary.get("review_streamer") or {}).get("streamer_text"),
        (summary.get("review_rule_context") or {}).get("context_text"),
        (summary.get("review_discipline_cue") or {}).get("cue_text"),
        (summary.get("review_discipline_badge") or {}).get("badge_text"),
        (summary.get("review_discipline_token") or {}).get("token_text"),
        (summary.get("review_discipline_marker") or {}).get("marker_text"),
        (summary.get("review_discipline_glyph") or {}).get("glyph_text"),
        (summary.get("review_discipline_sigil") or {}).get("sigil_text"),
        (summary.get("review_discipline_seal") or {}).get("seal_text"),
        (summary.get("review_discipline_crest") or {}).get("crest_text"),
        (summary.get("review_discipline_emblem") or {}).get("emblem_text"),
        (summary.get("review_discipline_reason") or {}).get("reason_text"),
        (summary.get("review_dataset_quality_link") or {}).get("link_text"),
        summary.get("latest_bill_williams_review_evidence_follow_up_text"),
    ]
    weak_spots = summary.get("review_weak_spots") or {}
    top_weak_spot_fields = list(weak_spots.get("top_weak_spot_fields") or [])
    if top_weak_spot_fields:
        message_fields.append(f"Session weak spots: {', '.join(top_weak_spot_fields)}")
    if latest_trade_result is not None:
        review_sequence = latest_trade_result.get("review_sequence") or {}
        recommended_order = list(review_sequence.get("recommended_missing_order") or [])
        if recommended_order:
            message_fields.append(f"Recommended review order: {' -> '.join(recommended_order)}")
        message_fields.extend([
            latest_trade_result.get("current_trade_review_digest_headline"),
            latest_trade_result.get("current_trade_review_digest_primary_gap"),
            latest_trade_result.get("current_trade_review_digest_next_step"),
            review_sequence.get("next_prompt"),
            (latest_trade_result.get("review_rule_context") or {}).get("context_text"),
            (latest_trade_result.get("review_discipline_cue") or {}).get("cue_text"),
            (latest_trade_result.get("review_discipline_badge") or {}).get("badge_text"),
            (latest_trade_result.get("review_discipline_token") or {}).get("token_text"),
            (latest_trade_result.get("review_discipline_marker") or {}).get("marker_text"),
            (latest_trade_result.get("review_discipline_glyph") or {}).get("glyph_text"),
            (latest_trade_result.get("review_discipline_sigil") or {}).get("sigil_text"),
            (latest_trade_result.get("review_discipline_seal") or {}).get("seal_text"),
            (latest_trade_result.get("review_discipline_crest") or {}).get("crest_text"),
            (latest_trade_result.get("review_discipline_emblem") or {}).get("emblem_text"),
            (latest_trade_result.get("review_discipline_reason") or {}).get("reason_text"),
            (latest_trade_result.get("review_dataset_quality_link") or {}).get("link_text"),
            latest_trade_result.get("bill_williams_review_evidence_follow_up_text"),
        ])
    seen: set[str] = set()
    for message in message_fields:
        if message and message not in seen:
            lines.append(str(message))
            seen.add(str(message))


def build_finalization_blocker_lines(journal_view: dict[str, Any]) -> list[str]:
    finalization = journal_view["session_finalization"]
    quality_link = finalization.get("dataset_quality_finalization_link") or {}
    blockers = ["Finalization blockers:"]

    if finalization["is_session_finalized"]:
        recovery_ack = journal_view.get("dataset_quality_recovery_acknowledgment") or {}
        if quality_link.get("link_status"):
            blockers.append(f"Finalization dataset link: {quality_link.get('link_status')}")
        if quality_link.get("link_text"):
            blockers.append(quality_link.get("link_text"))
        _append_recovery_acknowledgment_blocker_lines(blockers, recovery_ack)
        blockers.append("Session already finalized.")
        blockers.append(f"Reason: {finalization['finalization_reason'] or '-'}")
        return blockers

    if finalization["replay_running"]:
        blockers.append("Replay is still running.")
    if finalization["active_trade_present"]:
        blockers.append("An active trade is still open.")
    if finalization["pending_review_trade_count"]:
        blockers.append(f"Pending reviews: {', '.join(finalization['pending_review_trade_ids'])}")

    if len(blockers) == 1:
        blockers.append("No blockers. Standard Finalize is available.")
    blockers.append(f"Force finalize available: {'yes' if finalization['can_finalize_with_force'] else 'no'}")
    if quality_link.get("link_status"):
        blockers.append(f"Finalization dataset link: {quality_link.get('link_status')}")
    if quality_link.get("link_text"):
        blockers.append(quality_link.get("link_text"))
    return blockers


def build_action_feedback_lines(feedback: dict[str, str] | None, journal_view: dict[str, Any] | None = None) -> list[str]:
    recovery_feedback = _build_recovery_feedback(journal_view)
    if not feedback and not recovery_feedback:
        return [
            "Recent action:",
            "No action yet in this desktop session.",
        ]
    active_feedback = feedback or recovery_feedback or {}
    detail = active_feedback.get("detail")
    lines = [
        "Recent action:",
        f"{active_feedback.get('level', 'info').upper()}: {active_feedback.get('summary', '-')}",
    ]
    if detail:
        lines.append(detail)
    if feedback and recovery_feedback:
        lines.append(f"{recovery_feedback.get('level', 'info').upper()}: {recovery_feedback.get('summary', '-')}")
        if recovery_feedback.get("detail"):
            lines.append(recovery_feedback["detail"])
    return lines


def _build_recovery_feedback(journal_view: dict[str, Any] | None) -> dict[str, str] | None:
    if not journal_view:
        return None
    recovery_note = journal_view.get("dataset_quality_recovery_note") or {}
    note_text = recovery_note.get("note_text")
    recovery_ack = journal_view.get("dataset_quality_recovery_acknowledgment") or {}
    ack_status = recovery_ack.get("acknowledgment_status")
    if ack_status == "acknowledgment_needed" and note_text:
        return {
            "level": "info",
            "summary": "Review reopened warning",
            "detail": str(note_text),
        }
    if ack_status == "acknowledged":
        return {
            "level": "info",
            "summary": "Reopened warning reviewed",
            "detail": str(recovery_ack.get("status_text") or "The reopened warning was already reviewed for this session."),
        }
    return None


def _append_dataset_quality_context(lines: list[str], dataset_quality: dict[str, Any]) -> list[str]:
    context_status = dataset_quality.get("context_status")
    context_text = dataset_quality.get("context_text")
    if context_status:
        lines.append(f"Dataset quality context: {context_status}")
    if context_text:
        lines.append(context_text)
    return lines


def _append_recovery_acknowledgment_guidance(lines: list[str], recovery_ack: dict[str, Any]) -> None:
    status = recovery_ack.get("acknowledgment_status")
    if status == "acknowledgment_needed":
        if recovery_ack.get("status_text"):
            lines.append(recovery_ack["status_text"])
    elif status == "acknowledged" and recovery_ack.get("status_text"):
        lines.append(recovery_ack["status_text"])


def _append_recovery_acknowledgment_blocker_lines(lines: list[str], recovery_ack: dict[str, Any]) -> None:
    status = recovery_ack.get("acknowledgment_status")
    if status == "acknowledgment_needed":
        lines.append("Recovery follow-up: review needed")
    elif status == "acknowledged":
        lines.append("Recovery follow-up: already reviewed")
