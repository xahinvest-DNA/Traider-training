from __future__ import annotations

from typing import Any


def build_workspace_bar_lines(replay_view: dict[str, Any], trading_view: dict[str, Any]) -> list[str]:
    instrument = replay_view.get("instrument_id") or "-"
    dataset = replay_view.get("dataset_id") or "-"
    mode = replay_view.get("replay_mode") or "-"
    simulation_time = replay_view.get("simulation_time") or "-"
    replay_status = replay_view.get("status") or "-"
    speed = replay_view.get("speed_multiplier")
    trade_indicator = _build_trade_indicator(trading_view)
    return [
        f"Instrument: {instrument} | Dataset: {dataset} | Mode: {mode}",
        f"Time: {simulation_time} | Replay: {replay_status} | Speed: {speed if speed is not None else '-'}x | Trade: {trade_indicator}",
    ]


def build_compact_context_lines(trading_view: dict[str, Any], journal_view: dict[str, Any]) -> list[str]:
    review_summary = journal_view.get("session_review_summary") or {}
    review_pending_trade_id = journal_view.get("review_pending_trade_id") or "-"
    pending_stop_present = trading_view.get("pending_stop_present")
    pending_stop_side = trading_view.get("pending_stop_side") or "-"
    pending_stop_trigger = trading_view.get("pending_stop_trigger_price")
    pending_entry_label = "yes" if trading_view.get("entry_pending_present") else "no"
    if pending_stop_present:
        pending_entry_label = f"yes ({pending_stop_side} stop @ {pending_stop_trigger if pending_stop_trigger is not None else '-'})"
    stop_loss = trading_view.get("current_stop_loss")
    if stop_loss is None:
        stop_loss = trading_view.get("pending_stop_stop_loss")
    take_profit = trading_view.get("current_take_profit")
    if take_profit is None:
        take_profit = trading_view.get("pending_stop_take_profit")
    return [
        f"Active trade: {'yes' if trading_view.get('active_trade_present') else 'no'}",
        f"Pending entry: {pending_entry_label}",
        f"Side: {trading_view.get('trade_side') or '-'}",
        f"Entry: {trading_view.get('average_entry_price') if trading_view.get('average_entry_price') is not None else '-'}",
        f"Volume / remaining: {trading_view.get('total_opened_volume', 0.0)} / {trading_view.get('current_open_volume', 0.0)}",
        f"SL / TP: {stop_loss if stop_loss is not None else '-'} / {take_profit if take_profit is not None else '-'}",
        f"Review needed: {'yes' if review_summary.get('pending_review_trade_count', 0) else 'no'} ({review_pending_trade_id})",
    ]


def build_review_entry_lines(journal_view: dict[str, Any]) -> list[str]:
    review_summary = journal_view.get("session_review_summary") or {}
    pending_trade_id = journal_view.get("review_pending_trade_id") or "-"
    pending_review_count = review_summary.get("pending_review_trade_count", 0)
    if pending_review_count:
        next_step = "open PostTradeReview for the latest closed trade"
    elif journal_view.get("session_status") == "active":
        next_step = "PreTradeNote is available before the next trade"
    else:
        next_step = "review is up to date for the current session"
    return [
        f"PreTradeNotes: {journal_view.get('pre_trade_note_count', 0)} | PostTradeReviews: {journal_view.get('post_trade_review_count', 0)}",
        f"Review pending trade: {pending_trade_id}",
        f"Review status: {'pending' if pending_review_count else 'ready'}",
        f"Next review action: {next_step}",
    ]


def build_main_screen_layout_spec() -> dict[str, Any]:
    return {
        "screen_reading_order": [
            "chart_area",
            "replay_and_trading_actions",
            "compact_context",
            "review_entry",
            "secondary_debug",
        ],
        "primary_surface_allows": [
            "compact_replay_state",
            "compact_trade_session_state",
            "compact_review_availability",
            "compact_action_warning",
            "compact_action_snapshot",
            "chart_first_emphasis",
        ],
        "primary_surface_excludes": [
            "long_readiness_prose",
            "long_recovery_prose",
            "long_finalization_prose",
            "repeated_workflow_narration",
            "verbose_derived_explanations",
            "debug_like_text_blocks",
            "raw_chart_bar_dump",
        ],
        "compact_context_allowed_facts": [
            "active_trade",
            "pending_entry_state",
            "side",
            "entry",
            "volume",
            "remaining_open_volume",
            "stop_loss",
            "take_profit",
            "review_needed",
        ],
        "zones": {
            "top_bar": {
                "role": "replay_session_bar",
                "weight": "compact",
                "includes": [
                    "instrument_dataset",
                    "replay_mode",
                    "simulation_time",
                    "replay_status",
                    "speed",
                    "active_trade_indicator",
                    "replay_controls",
                ],
            },
            "chart_area": {
                "role": "primary",
                "dominance": "largest",
                "weight": 5,
                "primary_footer": "compact_chart_summary_only",
            },
            "right_workspace_rail": {
                "role": "trader_operating_rail",
                "weight": 2,
                "includes": [
                    "trade_state_snapshot",
                    "order_ticket_inputs",
                    "trade_action_groups",
                    "compact_trade_context",
                    "review_entry",
                ],
            },
            "secondary_debug": {
                "role": "secondary",
                "placement": "below_primary_workspace",
                "includes": [
                    "workflow_diagnostics",
                    "history_timeline",
                    "authoring_review_forms",
                    "debug_chart_detail",
                    "raw_state_tabs",
                ],
            },
        },
    }


def _build_trade_indicator(trading_view: dict[str, Any]) -> str:
    if trading_view.get("active_trade_present"):
        return f"active {trading_view.get('trade_side') or '-'}"
    if trading_view.get("pending_stop_present"):
        trigger = trading_view.get("pending_stop_trigger_price")
        return f"pending {trading_view.get('pending_stop_side') or '-'} stop @ {trigger if trigger is not None else '-'}"
    if trading_view.get("entry_pending_present"):
        return "pending market entry"
    return "flat"
