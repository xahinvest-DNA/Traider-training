from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from uuid import uuid4

from .bill_williams import (
    validate_behavioral_flag_code,
    validate_compliance_label,
    validate_entry_timing_label,
    validate_exit_quality_label,
    validate_market_context_label,
    validate_flag_scope,
    validate_flag_severity,
    validate_flag_source,
    validate_review_clarity_label,
    validate_review_setup_variant,
    validate_review_tags,
    validate_rule_violation_code,
    validate_setup_tag,
    validate_violation_scope,
    validate_violation_severity,
    validate_violation_source,
)
from .errors import InvalidJournalValueError, SessionFinalizationError
from .review_projection import (
    build_current_trade_plan_context,
    build_session_review_output,
    build_session_review_summary,
)
from .timeline_projection import build_session_timeline_projection
from .replay_session import ReplaySession
from .trading_loop import MinimalTradingLoop
from .types import (
    BehavioralFlagRecord,
    ChartSnapshotRecord,
    ExecutionRecord,
    OrderRecord,
    PositionRecord,
    PostTradeReviewRecord,
    PreTradeNoteRecord,
    RuleViolationRecord,
    TradeRecord,
    TradingState,
    TrainingSessionRecord,
)


class LocalJournalRuntime:
    def __init__(
        self,
        replay_session: ReplaySession,
        trading_loop: MinimalTradingLoop,
        storage_dir: str | Path,
    ) -> None:
        self.replay_session = replay_session
        self.trading_loop = trading_loop
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.storage_path = self.storage_dir / "local_runtime_state.json"
        self.chart_snapshots: list[ChartSnapshotRecord] = []
        self.pre_trade_notes: list[PreTradeNoteRecord] = []
        self.post_trade_reviews: list[PostTradeReviewRecord] = []
        self.behavioral_flags: list[BehavioralFlagRecord] = []
        self.rule_violations: list[RuleViolationRecord] = []
        self.review_pending_trade_id: str | None = None
        self.recovered = False

        if self.storage_path.exists():
            self._load()
            self.recovered = True
        else:
            self.training_session = self._build_new_training_session()
            self.trading_loop.set_session_id(self.training_session.session_id)
            self._persist()

        self.replay_session.subscribe(self._on_replay_event)
        self.trading_loop.subscribe(self._on_trading_event)

    def _ensure_session_not_finalized(self, action: str) -> None:
        if self.training_session.finalization_status == "finalized":
            raise SessionFinalizationError(f"Cannot {action} after session finalization")

    def create_chart_snapshot(
        self,
        artifact_ref: str,
        artifact_type: str = "image_path",
        snapshot_role: str = "review_context",
        trade_id: str | None = None,
        execution_id: str | None = None,
        annotation_ref: str | None = None,
    ) -> ChartSnapshotRecord:
        self._ensure_session_not_finalized("create chart snapshot")
        now = self.replay_session.state.simulation_time
        resolved_trade_id = trade_id or self.trading_loop.state.active_trade_id or self.review_pending_trade_id or self._latest_closed_trade_id()
        snapshot = ChartSnapshotRecord(
            snapshot_id=self._next_id("snapshot"),
            session_id=self.training_session.session_id,
            captured_at=now,
            artifact_type=artifact_type,
            artifact_ref=artifact_ref,
            trade_id=resolved_trade_id,
            execution_id=execution_id,
            simulation_time=now,
            timeframe_context=self.replay_session.state.active_timeframe,
            instrument_id=self.replay_session.state.instrument_id,
            snapshot_role=snapshot_role,
            annotation_ref=annotation_ref,
            created_at=now,
        )
        self.chart_snapshots.append(snapshot)
        self.training_session.updated_at = now
        self._persist()
        return snapshot

    def create_pre_trade_note(
        self,
        content: str,
        note_type: str = "trade_intent",
        setup_tag: str | None = None,
        thesis_summary: str | None = None,
        risk_plan: str | None = None,
        chart_snapshot_ref: str | None = None,
    ) -> PreTradeNoteRecord:
        self._ensure_session_not_finalized("create pre-trade note")
        now = self.replay_session.state.simulation_time
        try:
            setup_tag = validate_setup_tag(setup_tag)
        except ValueError as exc:
            raise InvalidJournalValueError(str(exc)) from exc
        note = PreTradeNoteRecord(
            note_id=self._next_id("note"),
            session_id=self.training_session.session_id,
            note_type=note_type,
            content=content,
            note_timestamp=now,
            created_at=now,
            trade_id=self.trading_loop.state.active_trade_id,
            instrument_id=self.replay_session.state.instrument_id,
            timeframe_context=self.replay_session.state.active_timeframe,
            setup_tag=setup_tag,
            thesis_summary=thesis_summary,
            risk_plan=risk_plan,
            chart_snapshot_ref=chart_snapshot_ref,
        )
        self.pre_trade_notes.append(note)
        self.training_session.updated_at = now
        self._persist()
        return note

    def create_post_trade_review(
        self,
        content: str,
        review_type: str = "trade_review",
        trade_id: str | None = None,
        setup_tag: str | None = None,
        compliance_label: str | None = None,
        outcome_assessment: str | None = None,
        discipline_assessment: str | None = None,
        improvement_actions: str | None = None,
        review_tags: tuple[str, ...] | list[str] = (),
        chart_snapshot_refs: tuple[str, ...] | list[str] = (),
        setup_variant: str | None = None,
        entry_timing_label: str | None = None,
        market_context_label: str | None = None,
        exit_quality_label: str | None = None,
        review_clarity_label: str | None = None,
    ) -> PostTradeReviewRecord:
        self._ensure_session_not_finalized("create post-trade review")
        resolved_trade_id = trade_id or self.review_pending_trade_id or self._latest_closed_trade_id()
        if resolved_trade_id is None:
            raise InvalidJournalValueError("PostTradeReview requires a closed trade in the current local session")
        try:
            setup_tag = validate_setup_tag(setup_tag)
            compliance_label = validate_compliance_label(compliance_label)
            normalized_review_tags = validate_review_tags(review_tags)
            setup_variant = validate_review_setup_variant(setup_variant)
            entry_timing_label = validate_entry_timing_label(entry_timing_label)
            market_context_label = validate_market_context_label(market_context_label)
            exit_quality_label = validate_exit_quality_label(exit_quality_label)
            review_clarity_label = validate_review_clarity_label(review_clarity_label)
        except ValueError as exc:
            raise InvalidJournalValueError(str(exc)) from exc
        now = self.replay_session.state.simulation_time
        review = PostTradeReviewRecord(
            review_id=self._next_id("review"),
            session_id=self.training_session.session_id,
            review_type=review_type,
            content=content,
            review_timestamp=now,
            created_at=now,
            trade_id=resolved_trade_id,
            setup_tag=setup_tag,
            compliance_label=compliance_label,
            outcome_assessment=outcome_assessment,
            discipline_assessment=discipline_assessment,
            improvement_actions=improvement_actions,
            review_tags=normalized_review_tags,
            chart_snapshot_refs=tuple(chart_snapshot_refs),
            setup_variant=setup_variant,
            entry_timing_label=entry_timing_label,
            market_context_label=market_context_label,
            exit_quality_label=exit_quality_label,
            review_clarity_label=review_clarity_label,
        )
        self.post_trade_reviews.append(review)
        if self.review_pending_trade_id == resolved_trade_id:
            self.review_pending_trade_id = None
        self.training_session.updated_at = now
        self._persist()
        return review

    def create_behavioral_flag(
        self,
        flag_code: str,
        review_ref: str | None = None,
        scope: str = "trade",
        severity: str = "warning",
        source: str = "manual",
        trade_id: str | None = None,
        description: str | None = None,
    ) -> BehavioralFlagRecord:
        self._ensure_session_not_finalized("create behavioral flag")
        resolved_trade_id = trade_id or self.review_pending_trade_id or self._latest_closed_trade_id()
        try:
            flag_code = validate_behavioral_flag_code(flag_code)
            scope = validate_flag_scope(scope)
            severity = validate_flag_severity(severity)
            source = validate_flag_source(source)
        except ValueError as exc:
            raise InvalidJournalValueError(str(exc)) from exc
        if scope == "trade" and resolved_trade_id is None:
            raise InvalidJournalValueError("Trade-scoped BehavioralFlag requires tradeId in current review context")
        if scope == "execution":
            raise InvalidJournalValueError("Execution-scoped BehavioralFlag is outside current bounded slice")
        now = self.replay_session.state.simulation_time
        record = BehavioralFlagRecord(
            flag_id=self._next_id("flag"),
            session_id=self.training_session.session_id,
            flag_code=flag_code,
            source=source,
            scope=scope,
            severity=severity,
            flag_timestamp=now,
            created_at=now,
            trade_id=resolved_trade_id if scope == "trade" else None,
            review_ref=review_ref,
            description=description,
        )
        self.behavioral_flags.append(record)
        self.training_session.updated_at = now
        self._persist()
        return record

    def create_rule_violation(
        self,
        rule_code: str,
        related_review_ref: str | None = None,
        scope: str = "trade",
        severity: str = "soft",
        source: str = "manual_review",
        trade_id: str | None = None,
        description: str | None = None,
        hard_rule: bool | None = None,
    ) -> RuleViolationRecord:
        self._ensure_session_not_finalized("create rule violation")
        resolved_trade_id = trade_id or self.review_pending_trade_id or self._latest_closed_trade_id()
        try:
            rule_code = validate_rule_violation_code(rule_code)
            scope = validate_violation_scope(scope)
            severity = validate_violation_severity(severity)
            source = validate_violation_source(source)
        except ValueError as exc:
            raise InvalidJournalValueError(str(exc)) from exc
        if scope == "trade" and resolved_trade_id is None:
            raise InvalidJournalValueError("Trade-scoped RuleViolation requires tradeId in current review context")
        if scope == "execution":
            raise InvalidJournalValueError("Execution-scoped RuleViolation is outside current bounded slice")
        now = self.replay_session.state.simulation_time
        record = RuleViolationRecord(
            violation_id=self._next_id("violation"),
            session_id=self.training_session.session_id,
            rule_code=rule_code,
            scope=scope,
            severity=severity,
            source=source,
            violation_timestamp=now,
            created_at=now,
            trade_id=resolved_trade_id if scope == "trade" else None,
            description=description,
            hard_rule=hard_rule,
            related_review_ref=related_review_ref,
        )
        self.rule_violations.append(record)
        self.training_session.updated_at = now
        self._persist()
        return record

    def build_session_finalization_projection(self) -> dict:
        review_output = self.build_review_result_projection()
        pending_review_trade_ids = [
            result["trade_id"]
            for result in review_output["trade_results"]
            if result["review_status"] == "pending_review"
        ]
        active_trade_present = any((
            self.trading_loop.state.active_trade_id,
            self.trading_loop.state.pending_order_id,
            self.trading_loop.state.pending_close_order_id,
        ))
        replay_running = not self.replay_session.state.is_paused and not self.replay_session.state.is_finished
        dataset_quality_finalization_link = _build_dataset_quality_finalization_link(
            latest_trade_result=review_output.get("latest_trade_result"),
            pending_review_trade_ids=pending_review_trade_ids,
            active_trade_present=active_trade_present,
            replay_running=replay_running,
            is_session_finalized=self.training_session.finalization_status == "finalized",
        )
        return {
            "session_id": self.training_session.session_id,
            "finalization_status": self.training_session.finalization_status,
            "is_session_finalized": self.training_session.finalization_status == "finalized",
            "finalized_at": self.training_session.finalized_at,
            "finalization_reason": self.training_session.finalization_reason,
            "active_trade_present": active_trade_present,
            "replay_running": replay_running,
            "pending_review_trade_ids": pending_review_trade_ids,
            "pending_review_trade_count": len(pending_review_trade_ids),
            "requires_force_to_finalize": bool(pending_review_trade_ids),
            "can_finalize_without_force": not active_trade_present and not replay_running and not pending_review_trade_ids,
            "can_finalize_with_force": not active_trade_present and not replay_running,
            "dataset_quality_finalization_link": dataset_quality_finalization_link,
        }


    def acknowledge_recovery_context(self) -> TrainingSessionRecord:
        if not self._recovery_acknowledgment_is_required():
            return self.training_session
        now = self.replay_session.state.simulation_time
        self.training_session.recovery_context_acknowledged_at = now
        self.training_session.updated_at = now
        self._persist()
        return self.training_session


    def finalize_session(
        self,
        force: bool = False,
        reason: str = "user_completed",
    ) -> TrainingSessionRecord:
        projection = self.build_session_finalization_projection()
        if projection["is_session_finalized"]:
            return self.training_session
        if projection["active_trade_present"]:
            raise SessionFinalizationError("Cannot finalize session while an active trade is still open")
        if projection["replay_running"]:
            raise SessionFinalizationError("Cannot finalize session while replay is still running")
        if projection["pending_review_trade_count"] and not force:
            raise SessionFinalizationError("Cannot finalize session with pending post-trade reviews without force")
        now = self.replay_session.state.simulation_time
        self.training_session.finalization_status = "finalized"
        self.training_session.finalized_at = now
        self.training_session.finalization_reason = reason
        self.training_session.status = "completed"
        self.training_session.ended_at = self.training_session.ended_at or now
        self.training_session.end_simulation_time = self.training_session.end_simulation_time or now
        self.training_session.updated_at = now
        self._persist()
        return self.training_session

    def build_review_result_projection(self) -> dict:
        return build_session_review_output(
            training_session=self.training_session,
            trades=self.trading_loop.state.trades,
            chart_snapshots=self.chart_snapshots,
            pre_trade_notes=self.pre_trade_notes,
            post_trade_reviews=self.post_trade_reviews,
            behavioral_flags=self.behavioral_flags,
            rule_violations=self.rule_violations,
            executions=self.trading_loop.state.executions,
        )

    def build_session_timeline_projection(self) -> dict:
        return build_session_timeline_projection(
            training_session=self.training_session,
            trades=self.trading_loop.state.trades,
            executions=self.trading_loop.state.executions,
            chart_snapshots=self.chart_snapshots,
            pre_trade_notes=self.pre_trade_notes,
            post_trade_reviews=self.post_trade_reviews,
            behavioral_flags=self.behavioral_flags,
            rule_violations=self.rule_violations,
        )

    def build_session_review_summary_projection(self) -> dict:
        review_output = self.build_review_result_projection()
        finalization_projection = self.build_session_finalization_projection()
        return build_session_review_summary(
            training_session=self.training_session,
            review_output=review_output,
            finalization_projection=finalization_projection,
        )

    def build_desktop_projection(self) -> dict:
        finalization_projection = self.build_session_finalization_projection()
        review_output = self.build_review_result_projection()
        timeline_projection = self.build_session_timeline_projection()
        session_review_summary = build_session_review_summary(
            training_session=self.training_session,
            review_output=review_output,
            finalization_projection=finalization_projection,
        )
        return {
            "session_id": self.training_session.session_id,
            "session_status": self.training_session.status,
            "mode": self.training_session.mode,
            "dataset_id": self.training_session.dataset_id,
            "instrument_id": self.training_session.instrument_id,
            "active_timeframe": self.training_session.active_timeframe,
            "start_simulation_time": self.training_session.start_simulation_time,
            "end_simulation_time": self.training_session.end_simulation_time,
            "chart_snapshot_count": len(self.chart_snapshots),
            "pre_trade_note_count": len(self.pre_trade_notes),
            "post_trade_review_count": len(self.post_trade_reviews),
            "behavioral_flag_count": len(self.behavioral_flags),
            "rule_violation_count": len(self.rule_violations),
            "has_chart_snapshots": bool(self.chart_snapshots),
            "has_pre_trade_note": bool(self.pre_trade_notes),
            "has_post_trade_review": bool(self.post_trade_reviews),
            "has_behavioral_flags": bool(self.behavioral_flags),
            "has_rule_violations": bool(self.rule_violations),
            "last_chart_snapshot": asdict(self.chart_snapshots[-1]) if self.chart_snapshots else None,
            "last_pre_trade_note": asdict(self.pre_trade_notes[-1]) if self.pre_trade_notes else None,
            "last_post_trade_review": asdict(self.post_trade_reviews[-1]) if self.post_trade_reviews else None,
            "last_behavioral_flag": asdict(self.behavioral_flags[-1]) if self.behavioral_flags else None,
            "last_rule_violation": asdict(self.rule_violations[-1]) if self.rule_violations else None,
            "review_pending_trade_id": self.review_pending_trade_id,
            "current_trade_plan_context": build_current_trade_plan_context(
                self.trading_loop.state.trades,
                self.pre_trade_notes,
            ),
            "session_finalization": finalization_projection,
            "derived_review_output": review_output,
            "session_review_summary": session_review_summary,
            "session_timeline": timeline_projection,
            "recovered": self.recovered,
        }

    def _build_new_training_session(self) -> TrainingSessionRecord:
        now = self.replay_session.state.simulation_time
        return TrainingSessionRecord(
            session_id=self._next_id("session"),
            mode=self.replay_session.state.replay_mode,
            session_type="training_session",
            instrument_id=self.replay_session.state.instrument_id,
            symbol=self.replay_session.state.instrument_id,
            market_profile=self.replay_session.state.market_profile,
            dataset_id=self.replay_session.state.dataset_id,
            started_at=now,
            status="created",
            created_at=now,
            active_timeframe=self.replay_session.state.active_timeframe,
            synchronized_timeframes=self.replay_session.state.synchronized_timeframes,
            start_simulation_time=now,
        )

    def _on_replay_event(self, event) -> None:
        event_type = event.event_type
        now = self.replay_session.state.simulation_time
        self.training_session.active_timeframe = self.replay_session.state.active_timeframe
        self.training_session.synchronized_timeframes = self.replay_session.state.synchronized_timeframes
        self.training_session.updated_at = now
        if self.training_session.finalization_status == "finalized":
            self._persist()
            return
        if event_type == "ReplayResumed":
            self.training_session.status = "running"
        elif event_type == "ReplayPaused":
            self.training_session.status = "paused"
        elif event_type == "ReplayFinished":
            self.training_session.status = "completed"
            self.training_session.ended_at = now
            self.training_session.end_simulation_time = now
        self._persist()

    def _on_trading_event(self, event: dict) -> None:
        now = self.replay_session.state.simulation_time
        event_type = event["event_type"]
        if self.training_session.finalization_status == "finalized":
            self.training_session.updated_at = now
            self._persist()
            return
        if event_type == "PositionOpened":
            self.training_session.status = "running"
            self._late_bind_latest_pre_trade_note(event["payload"]["trade_id"], now)
        elif event_type == "PositionClosed":
            self.review_pending_trade_id = event["payload"]["trade_id"]
            self.training_session.status = "paused"
            self.training_session.end_simulation_time = now
            self.training_session.updated_at = now
            self._persist()
        elif event_type == "OrderPlaced":
            self.training_session.updated_at = now
            self._persist()

    def _late_bind_latest_pre_trade_note(self, trade_id: str, now: str) -> None:
        for note in reversed(self.pre_trade_notes):
            if note.trade_id is None:
                note.trade_id = trade_id
                note.updated_at = now
                break
        self.training_session.updated_at = now
        self._persist()

    def _latest_closed_trade_id(self) -> str | None:
        for trade in reversed(self.trading_loop.state.trades):
            if trade.status == "closed":
                return trade.trade_id
        return None

    def _recovery_acknowledgment_is_required(self) -> bool:
        if not self.recovered:
            return False
        projection = self.build_session_finalization_projection()
        link_text = (projection.get("dataset_quality_finalization_link") or {}).get("link_text")
        return bool(
            projection.get("is_session_finalized")
            and link_text
            and self.training_session.recovery_context_acknowledged_at is None
        )

    def _persist(self) -> None:
        payload = {
            "training_session": asdict(self.training_session),
            "chart_snapshots": [asdict(snapshot) for snapshot in self.chart_snapshots],
            "pre_trade_notes": [asdict(note) for note in self.pre_trade_notes],
            "post_trade_reviews": [asdict(review) for review in self.post_trade_reviews],
            "behavioral_flags": [asdict(flag) for flag in self.behavioral_flags],
            "rule_violations": [asdict(violation) for violation in self.rule_violations],
            "review_pending_trade_id": self.review_pending_trade_id,
            "trading_state": {
                "lifecycle_state": self.trading_loop.state.lifecycle_state,
                "active_trade_id": self.trading_loop.state.active_trade_id,
                "active_position_id": self.trading_loop.state.active_position_id,
                "pending_order_id": self.trading_loop.state.pending_order_id,
                "pending_close_order_id": self.trading_loop.state.pending_close_order_id,
                "orders": [asdict(order) for order in self.trading_loop.state.orders],
                "position": asdict(self.trading_loop.state.position) if self.trading_loop.state.position else None,
                "trades": [asdict(trade) for trade in self.trading_loop.state.trades],
                "executions": [asdict(execution) for execution in self.trading_loop.state.executions],
                "last_execution": asdict(self.trading_loop.state.last_execution) if self.trading_loop.state.last_execution else None,
            },
            "replay_state": {
                "time_cursor": self.replay_session.state.time_cursor,
                "simulation_time": self.replay_session.state.simulation_time,
                "active_timeframe": self.replay_session.state.active_timeframe,
                "synchronized_timeframes": list(self.replay_session.state.synchronized_timeframes),
                "is_paused": self.replay_session.state.is_paused,
                "is_finished": self.replay_session.state.is_finished,
                "speed_multiplier": self.replay_session.state.speed_multiplier,
            },
        }
        self.storage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _load(self) -> None:
        payload = json.loads(self.storage_path.read_text(encoding="utf-8"))
        training_session = payload["training_session"]
        self.training_session = TrainingSessionRecord(
            session_id=training_session["session_id"],
            mode=training_session["mode"],
            session_type=training_session["session_type"],
            instrument_id=training_session["instrument_id"],
            symbol=training_session["symbol"],
            market_profile=training_session["market_profile"],
            dataset_id=training_session["dataset_id"],
            started_at=training_session["started_at"],
            status=training_session["status"],
            created_at=training_session["created_at"],
            schema_version=training_session.get("schema_version", "journal-schema/v1"),
            ended_at=training_session.get("ended_at"),
            active_timeframe=training_session.get("active_timeframe"),
            synchronized_timeframes=tuple(training_session.get("synchronized_timeframes", [])),
            start_simulation_time=training_session.get("start_simulation_time"),
            end_simulation_time=training_session.get("end_simulation_time"),
            finalization_status=training_session.get("finalization_status", "open"),
            finalized_at=training_session.get("finalized_at"),
            finalization_reason=training_session.get("finalization_reason"),
            recovery_context_acknowledged_at=training_session.get("recovery_context_acknowledged_at"),
            updated_at=training_session.get("updated_at"),
        )
        self.chart_snapshots = [
            ChartSnapshotRecord(
                snapshot_id=snapshot["snapshot_id"],
                session_id=snapshot["session_id"],
                captured_at=snapshot["captured_at"],
                artifact_type=snapshot["artifact_type"],
                artifact_ref=snapshot["artifact_ref"],
                schema_version=snapshot.get("schema_version", "journal-schema/v1"),
                trade_id=snapshot.get("trade_id"),
                execution_id=snapshot.get("execution_id"),
                simulation_time=snapshot.get("simulation_time"),
                timeframe_context=snapshot.get("timeframe_context"),
                instrument_id=snapshot.get("instrument_id"),
                snapshot_role=snapshot.get("snapshot_role"),
                annotation_ref=snapshot.get("annotation_ref"),
                created_at=snapshot.get("created_at"),
            )
            for snapshot in payload.get("chart_snapshots", [])
        ]
        self.pre_trade_notes = [
            PreTradeNoteRecord(
                note_id=note["note_id"],
                session_id=note["session_id"],
                note_type=note["note_type"],
                content=note["content"],
                note_timestamp=note["note_timestamp"],
                created_at=note["created_at"],
                schema_version=note.get("schema_version", "journal-schema/v1"),
                trade_id=note.get("trade_id"),
                instrument_id=note.get("instrument_id"),
                timeframe_context=note.get("timeframe_context"),
                setup_tag=note.get("setup_tag"),
                thesis_summary=note.get("thesis_summary"),
                risk_plan=note.get("risk_plan"),
                chart_snapshot_ref=note.get("chart_snapshot_ref"),
                updated_at=note.get("updated_at"),
            )
            for note in payload.get("pre_trade_notes", [])
        ]
        self.post_trade_reviews = [
            PostTradeReviewRecord(
                review_id=review["review_id"],
                session_id=review["session_id"],
                review_type=review["review_type"],
                content=review["content"],
                review_timestamp=review["review_timestamp"],
                created_at=review["created_at"],
                schema_version=review.get("schema_version", "journal-schema/v1"),
                trade_id=review.get("trade_id"),
                setup_tag=review.get("setup_tag"),
                compliance_label=review.get("compliance_label"),
                outcome_assessment=review.get("outcome_assessment"),
                discipline_assessment=review.get("discipline_assessment"),
                improvement_actions=review.get("improvement_actions"),
                setup_variant=review.get("setup_variant"),
                entry_timing_label=review.get("entry_timing_label"),
                market_context_label=review.get("market_context_label"),
                exit_quality_label=review.get("exit_quality_label"),
                review_clarity_label=review.get("review_clarity_label"),
                review_tags=tuple(review.get("review_tags", [])),
                chart_snapshot_refs=tuple(review.get("chart_snapshot_refs", [])),
                updated_at=review.get("updated_at"),
            )
            for review in payload.get("post_trade_reviews", [])
        ]
        self.behavioral_flags = [
            BehavioralFlagRecord(
                flag_id=flag["flag_id"],
                session_id=flag["session_id"],
                flag_code=flag["flag_code"],
                source=flag["source"],
                scope=flag["scope"],
                severity=flag["severity"],
                flag_timestamp=flag["flag_timestamp"],
                created_at=flag["created_at"],
                schema_version=flag.get("schema_version", "journal-schema/v1"),
                trade_id=flag.get("trade_id"),
                execution_id=flag.get("execution_id"),
                note_ref=flag.get("note_ref"),
                review_ref=flag.get("review_ref"),
                evidence_refs=tuple(flag.get("evidence_refs", [])),
                description=flag.get("description"),
                confidence_score=flag.get("confidence_score"),
                resolved_at=flag.get("resolved_at"),
                updated_at=flag.get("updated_at"),
            )
            for flag in payload.get("behavioral_flags", [])
        ]
        self.rule_violations = [
            RuleViolationRecord(
                violation_id=violation["violation_id"],
                session_id=violation["session_id"],
                rule_code=violation["rule_code"],
                scope=violation["scope"],
                severity=violation["severity"],
                source=violation["source"],
                violation_timestamp=violation["violation_timestamp"],
                created_at=violation["created_at"],
                schema_version=violation.get("schema_version", "journal-schema/v1"),
                trade_id=violation.get("trade_id"),
                execution_id=violation.get("execution_id"),
                description=violation.get("description"),
                evidence_refs=tuple(violation.get("evidence_refs", [])),
                hard_rule=violation.get("hard_rule"),
                related_note_ref=violation.get("related_note_ref"),
                related_review_ref=violation.get("related_review_ref"),
                updated_at=violation.get("updated_at"),
            )
            for violation in payload.get("rule_violations", [])
        ]
        self.review_pending_trade_id = payload.get("review_pending_trade_id")
        self._restore_replay_state(payload.get("replay_state", {}))
        self._restore_trading_state(payload.get("trading_state", {}))
        self.trading_loop.set_session_id(self.training_session.session_id)

    def _restore_replay_state(self, replay_state: dict) -> None:
        time_cursor = int(replay_state.get("time_cursor", 0))
        time_cursor = max(0, min(time_cursor, len(self.replay_session.dataset.ticks) - 1))
        self.replay_session._set_cursor(time_cursor)
        self.replay_session.state.active_timeframe = replay_state.get(
            "active_timeframe", self.replay_session.state.active_timeframe
        )
        self.replay_session.state.synchronized_timeframes = tuple(
            replay_state.get("synchronized_timeframes", self.replay_session.state.synchronized_timeframes)
        )
        self.replay_session.state.is_paused = replay_state.get("is_paused", True)
        self.replay_session.state.is_finished = replay_state.get("is_finished", False)
        self.replay_session.state.speed_multiplier = float(replay_state.get("speed_multiplier", 1.0))

    def _restore_trading_state(self, trading_state: dict) -> None:
        state = TradingState(
            lifecycle_state=trading_state.get("lifecycle_state", "Idle"),
            active_trade_id=trading_state.get("active_trade_id"),
            active_position_id=trading_state.get("active_position_id"),
            pending_order_id=trading_state.get("pending_order_id"),
            pending_close_order_id=trading_state.get("pending_close_order_id"),
            orders=[OrderRecord(**record) for record in trading_state.get("orders", [])],
            position=PositionRecord(**trading_state["position"]) if trading_state.get("position") else None,
            trades=[TradeRecord(**record) for record in trading_state.get("trades", [])],
            executions=[
                ExecutionRecord(
                    execution_id=record["execution_id"],
                    session_id=record["session_id"],
                    trade_id=record["trade_id"],
                    order_id=record["order_id"],
                    instrument_id=record["instrument_id"],
                    timestamp=record["timestamp"],
                    execution_type=record["execution_type"],
                    reason=record["reason"],
                    side=record["side"],
                    volume=record["volume"],
                    fill_price=record["fill_price"],
                    bid=record["bid"],
                    ask=record["ask"],
                    spread=record["spread"],
                    slippage=record["slippage"],
                    commission_component=record["commission_component"],
                    swap_component=record["swap_component"],
                    snapshot_timestamp=record["snapshot_timestamp"],
                    snapshot_tick_index=record["snapshot_tick_index"],
                    market_session_state=record["market_session_state"],
                    data_quality_flags=tuple(record.get("data_quality_flags", [])),
                    liquidity_flags=tuple(record.get("liquidity_flags", [])),
                    dataset_position_reference=record["dataset_position_reference"],
                )
                for record in trading_state.get("executions", [])
            ],
            last_execution=(
                ExecutionRecord(
                    execution_id=trading_state["last_execution"]["execution_id"],
                    session_id=trading_state["last_execution"]["session_id"],
                    trade_id=trading_state["last_execution"]["trade_id"],
                    order_id=trading_state["last_execution"]["order_id"],
                    instrument_id=trading_state["last_execution"]["instrument_id"],
                    timestamp=trading_state["last_execution"]["timestamp"],
                    execution_type=trading_state["last_execution"]["execution_type"],
                    reason=trading_state["last_execution"]["reason"],
                    side=trading_state["last_execution"]["side"],
                    volume=trading_state["last_execution"]["volume"],
                    fill_price=trading_state["last_execution"]["fill_price"],
                    bid=trading_state["last_execution"]["bid"],
                    ask=trading_state["last_execution"]["ask"],
                    spread=trading_state["last_execution"]["spread"],
                    slippage=trading_state["last_execution"]["slippage"],
                    commission_component=trading_state["last_execution"]["commission_component"],
                    swap_component=trading_state["last_execution"]["swap_component"],
                    snapshot_timestamp=trading_state["last_execution"]["snapshot_timestamp"],
                    snapshot_tick_index=trading_state["last_execution"]["snapshot_tick_index"],
                    market_session_state=trading_state["last_execution"]["market_session_state"],
                    data_quality_flags=tuple(trading_state["last_execution"].get("data_quality_flags", [])),
                    liquidity_flags=tuple(trading_state["last_execution"].get("liquidity_flags", [])),
                    dataset_position_reference=trading_state["last_execution"]["dataset_position_reference"],
                )
                if trading_state.get("last_execution")
                else None
            ),
        )
        self.trading_loop.restore_state(state)

    @staticmethod
    def _next_id(prefix: str) -> str:
        return f"{prefix}-{uuid4().hex[:12]}"


def _build_dataset_quality_finalization_link(
    latest_trade_result: dict | None,
    pending_review_trade_ids: list[str],
    active_trade_present: bool,
    replay_running: bool,
    is_session_finalized: bool,
) -> dict:
    review_link = (latest_trade_result or {}).get("review_dataset_quality_link") or {}
    link_text = review_link.get("link_text")
    if not link_text:
        return {
            "link_status": "no_finalization_link",
            "link_text": None,
        }
    if is_session_finalized:
        status = "finalized_warned_link"
        text = f"Finalization link: session closed with warned dataset context. {link_text}"
    elif active_trade_present or replay_running:
        status = "blocked_warned_link"
        text = f"Finalization link: warned dataset context is active, but session close is still blocked. {link_text}"
    elif pending_review_trade_ids:
        status = "pending_warned_link"
        text = f"Finalization link: warned dataset context should be acknowledged before closing pending review trades. {link_text}"
    else:
        status = "ready_warned_link"
        text = f"Finalization link: warned dataset context remains relevant at session close. {link_text}"
    return {
        "link_status": status,
        "link_text": text,
    }

