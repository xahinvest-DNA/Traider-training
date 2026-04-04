from __future__ import annotations

from .journal_runtime import LocalJournalRuntime
from .replay_session import ReplaySession
from .trading_loop import MinimalTradingLoop


def build_desktop_replay_view(session: ReplaySession) -> dict:
    state = session.state
    dataset_quality = _build_dataset_quality_context(
        session.dataset.quality_report,
        last_execution=session.get_execution_snapshot(),
    )
    return {
        "dataset_id": state.dataset_id,
        "instrument_id": state.instrument_id,
        "market_profile": state.market_profile,
        "replay_mode": state.replay_mode,
        "active_timeframe": state.active_timeframe,
        "synchronized_timeframes": list(state.synchronized_timeframes),
        "simulation_time": state.simulation_time,
        "dataset_start_time": state.dataset_start_time,
        "dataset_end_time": state.dataset_end_time,
        "time_cursor": state.time_cursor,
        "speed_multiplier": state.speed_multiplier,
        "is_paused": state.is_paused,
        "is_finished": state.is_finished,
        "allowed_controls": session.get_allowed_controls(),
        "chart_context": session.get_chart_context(),
        "dataset_quality": dataset_quality,
        "status": (
            "finished"
            if state.is_finished
            else "paused"
            if state.is_paused
            else "running"
        ),
    }


def build_desktop_trading_view(trading_loop: MinimalTradingLoop) -> dict:
    projection = trading_loop.build_desktop_projection()
    projection["dataset_quality_context"] = _build_dataset_quality_context(
        trading_loop.replay_session.dataset.quality_report,
        last_execution=trading_loop.state.last_execution,
    )
    return projection


def build_desktop_journal_view(journal_runtime: LocalJournalRuntime) -> dict:
    projection = journal_runtime.build_desktop_projection()
    projection["dataset_quality_context"] = _build_dataset_quality_context(
        journal_runtime.replay_session.dataset.quality_report,
        last_execution=journal_runtime.trading_loop.state.last_execution,
    )
    projection["dataset_quality_recovery_note"] = _build_dataset_quality_recovery_note(
        finalization=projection.get("session_finalization") or {},
        recovered=journal_runtime.recovered,
    )
    projection["dataset_quality_recovery_acknowledgment"] = _build_dataset_quality_recovery_acknowledgment(
        finalization=projection.get("session_finalization") or {},
        recovered=journal_runtime.recovered,
        acknowledged_at=journal_runtime.training_session.recovery_context_acknowledged_at,
    )
    return projection


def _build_dataset_quality_context(quality_report: dict, last_execution) -> dict:
    warnings = [str(value) for value in quality_report.get("warnings", [])]
    dataset_flags = [str(flag) for flag in quality_report.get("data_quality_flags", [])]
    liquidity_flags = [str(flag) for flag in quality_report.get("liquidity_flags", [])]
    execution_quality_flags = _coerce_flags(last_execution, "data_quality_flags")
    execution_liquidity_flags = _coerce_flags(last_execution, "liquidity_flags")
    execution_flags = execution_quality_flags + execution_liquidity_flags
    warning_preview = str(quality_report.get("warning_preview") or (", ".join(warnings[:3]) if warnings else "none"))
    execution_flag_preview = ", ".join(execution_flags) if execution_flags else "none"

    if execution_flags:
        context_status = "execution_warning_context"
        context_text = (
            f"Dataset warnings remain active: {warning_preview}. "
            f"Latest execution context flags: {execution_flag_preview}."
        )
    elif warnings:
        context_status = "warned_dataset"
        context_text = f"Dataset imported with warnings: {warning_preview}."
    else:
        context_status = "clean_context"
        context_text = "Dataset quality context is clean for the current session."

    return {
        "status": str(quality_report.get("status") or "unknown"),
        "warning_count": int(quality_report.get("warning_count") or len(warnings)),
        "warning_preview": warning_preview,
        "warnings": warnings,
        "data_quality_flags": dataset_flags,
        "liquidity_flags": liquidity_flags,
        "execution_flag_count": len(execution_flags),
        "execution_flag_preview": execution_flag_preview,
        "execution_data_quality_flags": execution_quality_flags,
        "execution_liquidity_flags": execution_liquidity_flags,
        "context_status": context_status,
        "context_text": context_text,
    }


def _build_dataset_quality_recovery_note(finalization: dict, recovered: bool) -> dict:
    quality_link = finalization.get("dataset_quality_finalization_link") or {}
    link_text = quality_link.get("link_text")
    if not recovered or not finalization.get("is_session_finalized") or not link_text:
        return {
            "note_status": "no_recovery_note",
            "note_text": None,
        }
    return {
        "note_status": "recovered_warned_close_context",
        "note_text": f"Recovery note: reopened finalized session still carries warned dataset close context. {link_text}",
    }


def _build_dataset_quality_recovery_acknowledgment(
    finalization: dict,
    recovered: bool,
    acknowledged_at: str | None,
) -> dict:
    quality_link = finalization.get("dataset_quality_finalization_link") or {}
    link_text = quality_link.get("link_text")
    if not recovered or not finalization.get("is_session_finalized") or not link_text:
        return {
            "acknowledgment_status": "not_applicable",
            "acknowledged_at": acknowledged_at,
            "status_text": None,
            "prompt_text": None,
        }
    if acknowledged_at:
        return {
            "acknowledgment_status": "acknowledged",
            "acknowledged_at": acknowledged_at,
            "status_text": "Reopened warning already reviewed for this session.",
            "prompt_text": None,
        }
    return {
        "acknowledgment_status": "acknowledgment_needed",
        "acknowledged_at": None,
        "status_text": "Review the reopened warning before starting a new local session.",
        "prompt_text": "Mark the reopened warning as reviewed when you are ready to move on.",
    }


def _coerce_flags(last_execution, field_name: str) -> list[str]:
    if last_execution is None:
        return []
    if hasattr(last_execution, field_name):
        value = getattr(last_execution, field_name)
    elif isinstance(last_execution, dict):
        value = last_execution.get(field_name, [])
    else:
        value = []
    return [str(flag) for flag in value or []]
