from __future__ import annotations

from typing import Any

from .transition_state import build_transition_state_view


def build_button_state_map(
    replay_view: dict[str, Any],
    trading_view: dict[str, Any],
    journal_view: dict[str, Any],
) -> dict[str, bool]:
    allowed_replay = replay_view["allowed_controls"]
    finalization = journal_view["session_finalization"]
    transition_state = build_transition_state_view(journal_view, trading_view)
    is_finalized = finalization["is_session_finalized"]
    has_closed_trade = journal_view["derived_review_output"]["closed_trade_count"] > 0
    review_pending = journal_view["review_pending_trade_id"] is not None
    replay_status = replay_view["status"]
    entry_available = not trading_view["active_trade_present"] and not trading_view.get("entry_pending_present")

    return {
        "play": replay_status == "paused" and allowed_replay["can_play"] and not is_finalized,
        "pause": replay_status == "running" and allowed_replay["can_pause"] and not is_finalized,
        "advance": replay_status != "finished" and not is_finalized,
        "set_speed": allowed_replay["can_change_speed"] and not is_finalized,
        "buy": entry_available and replay_status != "finished" and not is_finalized,
        "sell": entry_available and replay_status != "finished" and not is_finalized,
        "buy_stop": entry_available and replay_status != "finished" and not is_finalized,
        "sell_stop": entry_available and replay_status != "finished" and not is_finalized,
        "cancel_entry": trading_view.get("pending_entry_cancel_available", False) and not is_finalized,
        "close": trading_view["manual_close_available"] and not is_finalized,
        "partial_close": trading_view.get("partial_close_available", False) and not is_finalized,
        "finalize": finalization["can_finalize_without_force"] and not is_finalized,
        "force_finalize": finalization["can_finalize_with_force"] and not is_finalized,
        "acknowledge_recovery": transition_state["recovery_acknowledgment_status"] == "acknowledgment_needed",
        "add_note": not is_finalized,
        "add_review": review_pending and not is_finalized,
        "add_flag": has_closed_trade and not is_finalized,
        "add_violation": has_closed_trade and not is_finalized,
    }


def build_control_hint_lines(button_state_map: dict[str, bool]) -> list[str]:
    def yn(key: str) -> str:
        return "yes" if button_state_map[key] else "no"

    return [
        "Control availability:",
        f"Replay -> Play {yn('play')} | Pause {yn('pause')} | Advance {yn('advance')} | Speed {yn('set_speed')}",
        f"Trade -> Buy {yn('buy')} | Sell {yn('sell')} | BuyStop {yn('buy_stop')} | SellStop {yn('sell_stop')} | Cancel pending {yn('cancel_entry')} | Partial close {yn('partial_close')} | Close {yn('close')}",
        f"Review -> Note {yn('add_note')} | Review {yn('add_review')} | Flag {yn('add_flag')} | Violation {yn('add_violation')}",
        f"Session -> Finalize {yn('finalize')} | Force finalize {yn('force_finalize')} | Review warning {yn('acknowledge_recovery')}",
    ]
