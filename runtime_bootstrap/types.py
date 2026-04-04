from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SUPPORTED_DATASET_SCHEMA = "replay-dataset/v1"
SUPPORTED_REPLAY_MODES = {"training", "exam", "review_replay"}
JOURNAL_SCHEMA_VERSION = "journal-schema/v1"


@dataclass(frozen=True)
class Tick:
    timestamp: str
    bid: float
    ask: float
    source_id: str | None = None

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2.0


@dataclass(frozen=True)
class NormalizedDataset:
    dataset_id: str
    schema_version: str
    instrument_id: str
    market_profile: str
    timezone_canonical: str
    price_precision: int
    dataset_start_time: str
    dataset_end_time: str
    active_timeframe: str
    synchronized_timeframes: tuple[str, ...]
    manifest: dict[str, Any]
    quality_report: dict[str, Any]
    ticks: tuple[Tick, ...]


@dataclass
class ReplayState:
    dataset_id: str
    instrument_id: str
    market_profile: str
    replay_mode: str
    active_timeframe: str
    synchronized_timeframes: tuple[str, ...]
    dataset_start_time: str
    dataset_end_time: str
    time_cursor: int
    simulation_time: str
    speed_multiplier: float
    is_paused: bool
    is_finished: bool
    current_tick: Tick
    recent_ticks: list[Tick] = field(default_factory=list)
    error_state: str | None = None


@dataclass(frozen=True)
class ReplayEvent:
    event_type: str
    simulation_time: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class ExecutionSnapshot:
    timestamp: str
    symbol: str
    bid: float
    ask: float
    mid: float
    active_timeframe: str
    synchronized_timeframes: tuple[str, ...]
    replay_mode: str
    market_session_state: str
    data_quality_flags: tuple[str, ...]
    liquidity_flags: tuple[str, ...]
    dataset_position: int


@dataclass
class OrderRecord:
    order_id: str
    session_id: str
    trade_id: str | None
    instrument_id: str
    order_type: str
    side: str
    status: str
    requested_volume: float
    created_at: str
    replay_mode: str
    stop_loss: float | None = None
    take_profit: float | None = None
    filled_at: str | None = None
    rejection_reason: str | None = None


@dataclass
class PositionRecord:
    position_id: str
    session_id: str
    trade_id: str
    instrument_id: str
    side: str
    status: str
    total_opened_volume: float
    current_open_volume: float
    average_entry_price: float
    opened_at: str
    stop_loss: float | None = None
    take_profit: float | None = None
    closed_at: str | None = None
    average_exit_price: float | None = None
    close_reason: str | None = None
    last_snapshot_timestamp: str | None = None
    last_snapshot_tick_index: int | None = None


@dataclass
class TradeRecord:
    trade_id: str
    session_id: str
    instrument_id: str
    symbol: str
    replay_mode: str
    timeframe_context: str
    side: str
    status: str
    opened_at: str
    average_entry_price: float
    volume_opened: float
    volume_closed: float
    realised_pnl: float
    total_trade_cost: float
    entry_price: float | None = None
    exit_price: float | None = None
    average_exit_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    close_reason: str | None = None
    closed_at: str | None = None


@dataclass(frozen=True)
class ExecutionRecord:
    execution_id: str
    session_id: str
    trade_id: str
    order_id: str
    instrument_id: str
    timestamp: str
    execution_type: str
    reason: str
    side: str
    volume: float
    fill_price: float
    bid: float
    ask: float
    spread: float
    slippage: float
    commission_component: float
    swap_component: float
    snapshot_timestamp: str
    snapshot_tick_index: int
    market_session_state: str
    data_quality_flags: tuple[str, ...]
    liquidity_flags: tuple[str, ...]
    dataset_position_reference: int


@dataclass
class TradingState:
    lifecycle_state: str = "Idle"
    active_trade_id: str | None = None
    active_position_id: str | None = None
    pending_order_id: str | None = None
    pending_close_order_id: str | None = None
    orders: list[OrderRecord] = field(default_factory=list)
    position: PositionRecord | None = None
    trades: list[TradeRecord] = field(default_factory=list)
    executions: list[ExecutionRecord] = field(default_factory=list)
    last_execution: ExecutionRecord | None = None


@dataclass
class TrainingSessionRecord:
    session_id: str
    mode: str
    session_type: str
    instrument_id: str
    symbol: str
    market_profile: str
    dataset_id: str
    started_at: str
    status: str
    created_at: str
    schema_version: str = JOURNAL_SCHEMA_VERSION
    ended_at: str | None = None
    active_timeframe: str | None = None
    synchronized_timeframes: tuple[str, ...] = field(default_factory=tuple)
    start_simulation_time: str | None = None
    end_simulation_time: str | None = None
    finalization_status: str = "open"
    finalized_at: str | None = None
    finalization_reason: str | None = None
    recovery_context_acknowledged_at: str | None = None
    updated_at: str | None = None


@dataclass
class ChartSnapshotRecord:
    snapshot_id: str
    session_id: str
    captured_at: str
    artifact_type: str
    artifact_ref: str
    schema_version: str = JOURNAL_SCHEMA_VERSION
    trade_id: str | None = None
    execution_id: str | None = None
    simulation_time: str | None = None
    timeframe_context: str | None = None
    instrument_id: str | None = None
    snapshot_role: str | None = None
    annotation_ref: str | None = None
    created_at: str | None = None


@dataclass
class PreTradeNoteRecord:
    note_id: str
    session_id: str
    note_type: str
    content: str
    note_timestamp: str
    created_at: str
    schema_version: str = JOURNAL_SCHEMA_VERSION
    trade_id: str | None = None
    instrument_id: str | None = None
    timeframe_context: str | None = None
    setup_tag: str | None = None
    thesis_summary: str | None = None
    risk_plan: str | None = None
    chart_snapshot_ref: str | None = None
    updated_at: str | None = None


@dataclass
class PostTradeReviewRecord:
    review_id: str
    session_id: str
    review_type: str
    content: str
    review_timestamp: str
    created_at: str
    schema_version: str = JOURNAL_SCHEMA_VERSION
    trade_id: str | None = None
    setup_tag: str | None = None
    compliance_label: str | None = None
    setup_variant: str | None = None
    entry_timing_label: str | None = None
    market_context_label: str | None = None
    exit_quality_label: str | None = None
    review_clarity_label: str | None = None
    outcome_assessment: str | None = None
    discipline_assessment: str | None = None
    improvement_actions: str | None = None
    review_tags: tuple[str, ...] = field(default_factory=tuple)
    chart_snapshot_refs: tuple[str, ...] = field(default_factory=tuple)
    updated_at: str | None = None


@dataclass
class BehavioralFlagRecord:
    flag_id: str
    session_id: str
    flag_code: str
    source: str
    scope: str
    severity: str
    flag_timestamp: str
    created_at: str
    schema_version: str = JOURNAL_SCHEMA_VERSION
    trade_id: str | None = None
    execution_id: str | None = None
    note_ref: str | None = None
    review_ref: str | None = None
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    description: str | None = None
    confidence_score: float | None = None
    resolved_at: str | None = None
    updated_at: str | None = None


@dataclass
class RuleViolationRecord:
    violation_id: str
    session_id: str
    rule_code: str
    scope: str
    severity: str
    source: str
    violation_timestamp: str
    created_at: str
    schema_version: str = JOURNAL_SCHEMA_VERSION
    trade_id: str | None = None
    execution_id: str | None = None
    description: str | None = None
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    hard_rule: bool | None = None
    related_note_ref: str | None = None
    related_review_ref: str | None = None
    updated_at: str | None = None
