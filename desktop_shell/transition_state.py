from __future__ import annotations

from typing import Any


def build_transition_state_view(
    journal_view: dict[str, Any],
    trading_view: dict[str, Any] | None = None,
) -> dict[str, Any]:
    finalization = journal_view["session_finalization"]
    summary = journal_view.get("session_review_summary") or {}
    dataset_quality = journal_view.get("dataset_quality_context") or {}
    quality_link = finalization.get("dataset_quality_finalization_link") or {}
    recovery_note = journal_view.get("dataset_quality_recovery_note") or {}
    recovery_ack = journal_view.get("dataset_quality_recovery_acknowledgment") or {}

    pending_entry = bool(trading_view and trading_view.get("entry_pending_present") and not trading_view.get("active_trade_present"))`r`n    pending_stop_entry = bool(trading_view and trading_view.get("pending_stop_present") and not trading_view.get("active_trade_present"))
    active_trade = bool(trading_view and trading_view.get("active_trade_present"))
    partially_closed = bool(trading_view and trading_view.get("trade_partially_closed"))
    clean_context = _is_clean_dataset_context(dataset_quality)

    finalization_link_status = str(quality_link.get("link_status") or "no_finalization_link")
    finalization_link_text = str(quality_link.get("link_text") or "none")
    recovery_note_status = str(recovery_note.get("note_status") or "no_recovery_note")
    recovery_note_text = str(recovery_note.get("note_text") or "none")
    recovery_ack_status = str(recovery_ack.get("acknowledgment_status") or "not_applicable")
    recovery_ack_text = str(recovery_ack.get("status_text") or recovery_ack.get("prompt_text") or "none")
    recovery_acknowledged_at = str(recovery_ack.get("acknowledged_at") or "none")

    if clean_context and finalization_link_status != "no_finalization_link":
        finalization_link_status, finalization_link_text = _build_clean_finalization_link_text(
            finalization=finalization,
            pending_entry=pending_entry,
            active_trade=active_trade,
        )
        if finalization.get("is_session_finalized") and journal_view.get("recovered"):
            recovery_note_status = "recovered_clean_context"
            recovery_note_text = "Recovery note: reopened finalized session returns with clean dataset context."
        else:
            recovery_note_status = "no_recovery_note"
            recovery_note_text = "none"
        recovery_ack_status = "not_applicable"
        recovery_ack_text = "none"

    lifecycle_label, lifecycle_text = _build_lifecycle_state_text(
        finalization=finalization,
        summary=summary,
        pending_entry=pending_entry,
        active_trade=active_trade,
        partially_closed=partially_closed,
    )

    return {
        "pending_entry_staged": pending_entry,
        "active_trade_open": active_trade,
        "trade_partially_closed": partially_closed,
        "lifecycle_label": lifecycle_label,
        "lifecycle_text": lifecycle_text,
        "finalization_link_status": finalization_link_status,
        "finalization_link_text": finalization_link_text,
        "recovery_note_status": recovery_note_status,
        "recovery_note_text": recovery_note_text,
        "recovery_acknowledgment_status": recovery_ack_status,
        "recovery_acknowledgment_text": recovery_ack_text,
        "recovery_acknowledged_at": recovery_acknowledged_at,
    }


def _is_clean_dataset_context(dataset_quality: dict[str, Any]) -> bool:
    return str(dataset_quality.get("context_status") or "") == "clean_context"


def _build_clean_finalization_link_text(
    finalization: dict[str, Any],
    pending_entry: bool,
    active_trade: bool,
) -> tuple[str, str]:
    if finalization.get("is_session_finalized"):
        return (
            "finalized_clean_context",
            "Finalization link: session closed with clean dataset context.",
        )
    if pending_entry:
        return (
            "blocked_clean_context",
            "Finalization link: clean dataset context is blocked by a staged pending entry.",
        )
    if active_trade:
        return (
            "blocked_clean_context",
            "Finalization link: clean dataset context is blocked by an open trade.",
        )
    if finalization.get("replay_running"):
        return (
            "blocked_clean_context",
            "Finalization link: clean dataset context is blocked while replay is still running.",
        )
    if finalization.get("pending_review_trade_count"):
        return (
            "pending_clean_context",
            "Finalization link: clean dataset context is ready once pending reviews are completed.",
        )
    if finalization.get("can_finalize_without_force"):
        return (
            "ready_clean_context",
            "Finalization link: clean dataset context is ready for standard finalization.",
        )
    return (
        "clean_context",
        "Finalization link: clean dataset context remains aligned with the current session state.",
    )


def _build_lifecycle_state_text(
    finalization: dict[str, Any],
    summary: dict[str, Any],
    pending_entry: bool,
    active_trade: bool,
    partially_closed: bool,
) -> tuple[str, str]:
    if pending_entry:
        return (
            "pending_entry_staged",
            "Pending entry is staged; no active trade is open yet.",
        )
    if active_trade and partially_closed:
        return (
            "active_trade_partially_closed",
            "Active trade remains open after a partial close.",
        )
    if active_trade:
        return (
            "active_trade_open",
            "Active trade is open.",
        )
    if finalization.get("is_session_finalized") and finalization.get("replay_running") is False:
        if summary.get("pending_review_trade_count"):
            return (
                "finalized_with_pending_review",
                "Session is finalized, but the historical session result still includes pending review items.",
            )
        return (
            "session_finalized",
            "Session is finalized.",
        )
    if summary.get("pending_review_trade_count"):
        return (
            "review_pending",
            "Trade is closed and review is still pending.",
        )
    return (
        "idle",
        "No trade lifecycle is currently in progress.",
    )

