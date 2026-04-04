from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from runtime_bootstrap import (
    LocalJournalRuntime,
    MinimalTradingLoop,
    build_desktop_journal_view,
    build_desktop_replay_view,
    build_desktop_trading_view,
    create_replay_session,
    load_normalized_dataset,
)
from runtime_bootstrap.errors import (
    ActiveTradeExistsError,
    EmptyTickStreamError,
    InvalidJournalValueError,
    SessionFinalizationError,
    ModeRestrictionError,
    NoActivePositionError,
    OutOfBoundsSeekError,
    ReplayFinishedError,
    TradingModeRestrictionError,
    UnsupportedSchemaVersionError,
)

FIXTURE = Path("runtime_bootstrap/fixtures/eurusd_sample")
TMP_ROOT = Path("tests/.tmp_runtime")


def _reset_dir(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


def test_load_normalized_dataset_from_fixture() -> None:
    dataset = load_normalized_dataset(FIXTURE)
    assert dataset.dataset_id == "eurusd-sample-v1"
    assert dataset.instrument_id == "EURUSD"
    assert len(dataset.ticks) == 6


def test_create_replay_session_bootstrap_state() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    view = build_desktop_replay_view(session)
    assert view["dataset_id"] == "eurusd-sample-v1"
    assert view["instrument_id"] == "EURUSD"
    assert view["simulation_time"] == "2025-01-02T10:00:00Z"
    assert view["status"] == "paused"
    assert view["allowed_controls"]["can_play"] is True


def test_training_mode_playback_reaches_finished_state() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    session.play()
    while not session.state.is_finished:
        session.advance_frame()
    view = build_desktop_replay_view(session)
    assert view["status"] == "finished"
    assert view["simulation_time"] == "2025-01-02T10:00:07Z"
    with pytest.raises(ReplayFinishedError):
        session.play()


def test_exam_mode_rejects_seek() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="exam")
    with pytest.raises(ModeRestrictionError):
        session.seek_to("2025-01-02T10:00:04Z")


def test_training_mode_seek_allows_jump_inside_bounds() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    session.seek_to("2025-01-02T10:00:04Z")
    view = build_desktop_replay_view(session)
    assert view["simulation_time"] == "2025-01-02T10:00:04Z"
    assert view["time_cursor"] == 3


def test_seek_out_of_bounds_fails() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    with pytest.raises(OutOfBoundsSeekError):
        session.seek_to("2025-01-02T09:59:59Z")


def test_speed_change_does_not_skip_events() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    session.set_speed(3)
    session.play()
    session.advance_frame()
    tick_events = [event for event in session.events if event.event_type == "TickArrived"]
    assert len(tick_events) == 3
    assert tick_events[0].simulation_time == "2025-01-02T10:00:01Z"
    assert tick_events[1].simulation_time == "2025-01-02T10:00:03Z"
    assert tick_events[2].simulation_time == "2025-01-02T10:00:04Z"


def test_unsupported_schema_version_fails() -> None:
    dataset_dir = _reset_dir(TMP_ROOT / "invalid_schema")
    dataset_dir.joinpath("manifest.json").write_text(
        FIXTURE.joinpath("manifest.json").read_text(encoding="utf-8-sig").replace(
            "replay-dataset/v1", "replay-dataset/v999"
        ),
        encoding="utf-8",
    )
    dataset_dir.joinpath("quality_report.json").write_text(
        FIXTURE.joinpath("quality_report.json").read_text(encoding="utf-8-sig"),
        encoding="utf-8",
    )
    dataset_dir.joinpath("ticks.json").write_text(
        FIXTURE.joinpath("ticks.json").read_text(encoding="utf-8-sig"),
        encoding="utf-8",
    )
    with pytest.raises(UnsupportedSchemaVersionError):
        load_normalized_dataset(dataset_dir)


def test_empty_tick_stream_fails() -> None:
    dataset_dir = _reset_dir(TMP_ROOT / "empty_ticks")
    dataset_dir.joinpath("manifest.json").write_text(
        FIXTURE.joinpath("manifest.json").read_text(encoding="utf-8-sig"),
        encoding="utf-8",
    )
    dataset_dir.joinpath("quality_report.json").write_text(
        FIXTURE.joinpath("quality_report.json").read_text(encoding="utf-8-sig"),
        encoding="utf-8",
    )
    dataset_dir.joinpath("ticks.json").write_text("[]", encoding="utf-8")
    with pytest.raises(EmptyTickStreamError):
        load_normalized_dataset(dataset_dir)


def test_market_entry_fills_only_on_next_post_tick_snapshot() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal_dir = _reset_dir(TMP_ROOT / "entry_fill_journal")
    journal = LocalJournalRuntime(session, trading, journal_dir)

    order = trading.buy_market(volume=1.0)
    assert order.order_type == "BuyMarket"
    assert order.session_id == journal.training_session.session_id
    assert trading.state.lifecycle_state == "EntryRequested"
    assert trading.get_active_trade_count() == 0

    session.play()
    session.advance_frame()

    assert trading.state.lifecycle_state == "PositionOpened"
    assert trading.get_active_trade_count() == 1
    assert trading.state.position is not None
    assert trading.state.position.opened_at == "2025-01-02T10:00:01Z"
    assert trading.state.position.average_entry_price == 1.10360
    assert len(trading.state.executions) == 1
    assert trading.state.executions[0].execution_type == "entry_fill"
    assert trading.state.executions[0].timestamp == "2025-01-02T10:00:01Z"
    assert trading.state.trades[0].session_id == journal.training_session.session_id


def test_second_independent_entry_is_rejected_while_trade_active() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "active_trade_journal"))
    trading.sell_market()
    session.play()
    session.advance_frame()

    with pytest.raises(ActiveTradeExistsError):
        trading.buy_market()


def test_manual_close_requires_open_position_and_fills_on_next_post_tick() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "manual_close_journal"))

    with pytest.raises(NoActivePositionError):
        trading.manual_close()

    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()

    close_order = trading.manual_close()
    assert close_order.order_type == "ManualClose"
    assert trading.state.lifecycle_state == "CloseRequested"
    assert trading.get_active_trade_count() == 1

    session.advance_frame()

    assert trading.state.lifecycle_state == "Terminal"
    assert trading.get_active_trade_count() == 0
    assert trading.state.position is not None
    assert trading.state.position.status == "closed"
    assert trading.state.position.closed_at == "2025-01-02T10:00:03Z"
    assert len(trading.state.executions) == 2
    assert trading.state.executions[-1].execution_type == "manual_close_fill"
    assert trading.state.executions[-1].timestamp == "2025-01-02T10:00:03Z"
    assert trading.state.trades[-1].status == "closed"
    assert trading.state.trades[-1].close_reason == "manual_close"


def test_required_entities_and_desktop_projection_are_consistent_after_close() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "projection_journal"))
    trading.sell_market(volume=2.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()

    assert len(trading.state.orders) == 2
    assert trading.state.position is not None
    assert len(trading.state.trades) == 1
    assert len(trading.state.executions) == 2
    assert trading.state.trades[0].trade_id == trading.state.position.trade_id
    assert all(execution.trade_id == trading.state.trades[0].trade_id for execution in trading.state.executions)

    view = build_desktop_trading_view(trading)
    assert view["active_trade_present"] is False
    assert view["trade_status"] == "closed"
    assert view["last_execution_outcome"]["execution_type"] == "manual_close_fill"
    assert view["manual_close_available"] is False
    assert view["session_context"]["session_id"] == journal.training_session.session_id


def test_review_replay_does_not_allow_trading_actions() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="review_replay")
    trading = MinimalTradingLoop(session)
    LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "review_mode_journal"))

    with pytest.raises(TradingModeRestrictionError):
        trading.buy_market()


def test_pre_trade_note_late_binds_to_trade_when_position_opens() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "note_binding_journal"))

    note = journal.create_pre_trade_note(
        content="Wait for clean breakout and low spread",
        setup_tag="BW_FRACTAL_LONG",
        thesis_summary="breakout continuation",
        risk_plan="manual close if momentum fades",
    )
    assert note.trade_id is None

    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()

    assert journal.pre_trade_notes[-1].trade_id == trading.state.trades[-1].trade_id
    journal_view = build_desktop_journal_view(journal)
    assert journal_view["has_pre_trade_note"] is True
    assert journal_view["last_pre_trade_note"]["trade_id"] == trading.state.trades[-1].trade_id
    assert journal_view["last_pre_trade_note"]["setup_tag"] == "BW_FRACTAL_LONG"


def test_post_trade_review_is_linked_after_trade_close() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "review_link_journal"))

    journal.create_pre_trade_note(content="Planned long on momentum", setup_tag="BW_3WM_LONG")
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()

    review = journal.create_post_trade_review(
        content="Entry was fine, exit was slightly early",
        setup_tag="BW_3WM_LONG",
        compliance_label="late_entry",
        discipline_assessment="discipline_kept",
        improvement_actions="hold until first clear weakness",
        review_tags=("setup_late", "exit_too_early"),
    )

    assert review.trade_id == trading.state.trades[-1].trade_id
    journal_view = build_desktop_journal_view(journal)
    assert journal_view["has_post_trade_review"] is True
    assert journal_view["review_pending_trade_id"] is None
    assert journal_view["last_post_trade_review"]["trade_id"] == trading.state.trades[-1].trade_id
    assert journal_view["last_post_trade_review"]["setup_tag"] == "BW_3WM_LONG"
    assert journal_view["last_post_trade_review"]["compliance_label"] == "late_entry"


def test_local_runtime_recovers_session_trade_note_and_review_after_restart() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "recovery_journal")

    session_1 = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_1 = MinimalTradingLoop(session_1)
    journal_1 = LocalJournalRuntime(session_1, trading_1, storage_dir)

    note = journal_1.create_pre_trade_note(content="Long bias above local high", setup_tag="BW_1WM_LONG")
    trading_1.buy_market(volume=1.0)
    session_1.play()
    session_1.advance_frame()
    trading_1.manual_close()
    session_1.advance_frame()
    review = journal_1.create_post_trade_review(content="Review persisted locally", setup_tag="BW_1WM_LONG", compliance_label="valid_setup", review_tags=("setup_clear",))

    session_2 = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_2 = MinimalTradingLoop(session_2)
    journal_2 = LocalJournalRuntime(session_2, trading_2, storage_dir)

    journal_view = build_desktop_journal_view(journal_2)
    trading_view = build_desktop_trading_view(trading_2)

    assert journal_2.recovered is True
    assert journal_2.training_session.session_id == journal_1.training_session.session_id
    assert journal_2.pre_trade_notes[0].note_id == note.note_id
    assert journal_2.post_trade_reviews[0].review_id == review.review_id
    assert journal_2.pre_trade_notes[0].trade_id == trading_2.state.trades[0].trade_id
    assert journal_2.post_trade_reviews[0].trade_id == trading_2.state.trades[0].trade_id
    assert session_2.state.simulation_time == "2025-01-02T10:00:03Z"
    assert trading_view["trade_status"] == "closed"
    assert journal_view["session_id"] == journal_1.training_session.session_id
    assert journal_view["has_pre_trade_note"] is True
    assert journal_view["has_post_trade_review"] is True



def test_bill_williams_review_fields_persist_and_recover() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "bw_recovery_journal")

    session_1 = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_1 = MinimalTradingLoop(session_1)
    journal_1 = LocalJournalRuntime(session_1, trading_1, storage_dir)

    journal_1.create_pre_trade_note(
        content="Fractal breakout with alligator support",
        setup_tag="BW_FRACTAL_LONG",
    )
    trading_1.buy_market(volume=1.0)
    session_1.play()
    session_1.advance_frame()
    trading_1.manual_close()
    session_1.advance_frame()
    journal_1.create_post_trade_review(
        content="Method context was valid but entry slightly late",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="late_entry",
        review_tags=("setup_late", "fractal_context_valid"),
    )

    session_2 = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_2 = MinimalTradingLoop(session_2)
    journal_2 = LocalJournalRuntime(session_2, trading_2, storage_dir)

    assert journal_2.pre_trade_notes[-1].setup_tag == "BW_FRACTAL_LONG"
    assert journal_2.post_trade_reviews[-1].setup_tag == "BW_FRACTAL_LONG"
    assert journal_2.post_trade_reviews[-1].compliance_label == "late_entry"
    assert journal_2.post_trade_reviews[-1].review_tags == ("setup_late", "fractal_context_valid")


def test_invalid_bill_williams_values_are_rejected() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_invalid_journal"))

    with pytest.raises(InvalidJournalValueError):
        journal.create_pre_trade_note(content="Bad setup tag", setup_tag="NOT_A_BW_TAG")

    journal.create_pre_trade_note(content="Valid plan", setup_tag="BW_2WM_LONG")
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()

    with pytest.raises(InvalidJournalValueError):
        journal.create_post_trade_review(
            content="Bad compliance label",
            setup_tag="BW_2WM_LONG",
            compliance_label="not_a_label",
        )

    with pytest.raises(InvalidJournalValueError):
        journal.create_post_trade_review(
            content="Bad review tag",
            setup_tag="BW_2WM_LONG",
            compliance_label="valid_setup",
            review_tags=("not_a_review_tag",),
        )







def test_bill_williams_review_facets_persist_into_projection_and_recover() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "bw_review_depth_recovery_journal")

    session_1 = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_1 = MinimalTradingLoop(session_1)
    journal_1 = LocalJournalRuntime(session_1, trading_1, storage_dir)

    journal_1.create_pre_trade_note(content="Variant plan", setup_tag="BW_FRACTAL_LONG")
    trading_1.buy_market(volume=1.0)
    session_1.play()
    session_1.advance_frame()
    trading_1.manual_close()
    session_1.advance_frame()
    journal_1.create_post_trade_review(
        content="Facet-rich review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
        setup_variant="fractal_breakout",
        entry_timing_label="slightly_late_entry",
        market_context_label="acceptable_context",
        exit_quality_label="slightly_early_exit",
        review_clarity_label="high_clarity",
        review_tags=("setup_clear",),
    )

    trade_result_1 = build_desktop_journal_view(journal_1)["derived_review_output"]["latest_trade_result"]
    assert trade_result_1["has_method_facets"] is True
    assert trade_result_1["method_facets"] == {
        "setup_variant": "fractal_breakout",
        "entry_timing_label": "slightly_late_entry",
        "market_context_label": "acceptable_context",
        "exit_quality_label": "slightly_early_exit",
        "review_clarity_label": "high_clarity",
    }

    session_2 = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_2 = MinimalTradingLoop(session_2)
    journal_2 = LocalJournalRuntime(session_2, trading_2, storage_dir)

    recovered_review = journal_2.post_trade_reviews[-1]
    recovered_result = build_desktop_journal_view(journal_2)["derived_review_output"]["latest_trade_result"]
    recovered_summary = build_desktop_journal_view(journal_2)["session_review_summary"]

    assert recovered_review.setup_variant == "fractal_breakout"
    assert recovered_review.entry_timing_label == "slightly_late_entry"
    assert recovered_review.market_context_label == "acceptable_context"
    assert recovered_review.exit_quality_label == "slightly_early_exit"
    assert recovered_review.review_clarity_label == "high_clarity"
    assert recovered_result["method_facets"]["setup_variant"] == "fractal_breakout"
    assert recovered_summary["latest_method_facets"]["exit_quality_label"] == "slightly_early_exit"
    assert recovered_summary["trades_with_method_facets_count"] == 1


def test_invalid_bill_williams_review_facets_are_rejected() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_depth_invalid_journal"))

    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()

    with pytest.raises(InvalidJournalValueError):
        journal.create_post_trade_review(
            content="Bad setup variant",
            setup_variant="not_a_variant",
        )

    with pytest.raises(InvalidJournalValueError):
        journal.create_post_trade_review(
            content="Bad entry timing",
            entry_timing_label="not_a_timing",
        )

    with pytest.raises(InvalidJournalValueError):
        journal.create_post_trade_review(
            content="Bad market context",
            market_context_label="not_a_context",
        )

    with pytest.raises(InvalidJournalValueError):
        journal.create_post_trade_review(
            content="Bad exit quality",
            exit_quality_label="not_an_exit_quality",
        )

    with pytest.raises(InvalidJournalValueError):
        journal.create_post_trade_review(
            content="Bad clarity",
            review_clarity_label="not_a_clarity",
        )


def test_manual_behavioral_flag_and_rule_violation_link_to_review_and_trade() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "flags_review_journal"))

    journal.create_pre_trade_note(content="Plan", setup_tag="BW_FRACTAL_LONG")
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    review = journal.create_post_trade_review(
        content="Review with findings",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="weak_setup",
        review_tags=("setup_weak",),
    )

    flag = journal.create_behavioral_flag(
        flag_code="impulsive_entry",
        review_ref=review.review_id,
        description="Entry was rushed despite valid setup idea",
    )
    violation = journal.create_rule_violation(
        rule_code="manual_plan_deviation",
        related_review_ref=review.review_id,
        description="Plan changed at the last moment",
    )

    journal_view = build_desktop_journal_view(journal)
    assert flag.trade_id == trading.state.trades[-1].trade_id
    assert flag.review_ref == review.review_id
    assert violation.trade_id == trading.state.trades[-1].trade_id
    assert violation.related_review_ref == review.review_id
    assert journal_view["behavioral_flag_count"] == 1
    assert journal_view["rule_violation_count"] == 1
    assert journal_view["last_behavioral_flag"]["flag_code"] == "impulsive_entry"
    assert journal_view["last_rule_violation"]["rule_code"] == "manual_plan_deviation"


def test_invalid_flags_and_violations_are_rejected() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "flags_invalid_journal"))

    with pytest.raises(InvalidJournalValueError):
        journal.create_behavioral_flag(flag_code="not_a_flag")

    with pytest.raises(InvalidJournalValueError):
        journal.create_rule_violation(rule_code="not_a_rule")

    with pytest.raises(InvalidJournalValueError):
        journal.create_behavioral_flag(flag_code="impulsive_entry", scope="execution")

    with pytest.raises(InvalidJournalValueError):
        journal.create_rule_violation(rule_code="manual_plan_deviation", scope="execution")

    with pytest.raises(InvalidJournalValueError):
        journal.create_behavioral_flag(flag_code="impulsive_entry", scope="trade")

    with pytest.raises(InvalidJournalValueError):
        journal.create_rule_violation(rule_code="manual_plan_deviation", scope="trade")


def test_flags_and_violations_recover_after_restart() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "flags_recovery_journal")

    session_1 = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_1 = MinimalTradingLoop(session_1)
    journal_1 = LocalJournalRuntime(session_1, trading_1, storage_dir)

    trading_1.buy_market(volume=1.0)
    session_1.play()
    session_1.advance_frame()
    trading_1.manual_close()
    session_1.advance_frame()
    review = journal_1.create_post_trade_review(content="Review before restart")
    flag = journal_1.create_behavioral_flag(flag_code="premature_exit", review_ref=review.review_id)
    violation = journal_1.create_rule_violation(rule_code="manual_plan_deviation", related_review_ref=review.review_id)

    session_2 = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_2 = MinimalTradingLoop(session_2)
    journal_2 = LocalJournalRuntime(session_2, trading_2, storage_dir)

    assert journal_2.recovered is True
    assert journal_2.behavioral_flags[0].flag_id == flag.flag_id
    assert journal_2.rule_violations[0].violation_id == violation.violation_id
    assert journal_2.behavioral_flags[0].review_ref == review.review_id
    assert journal_2.rule_violations[0].related_review_ref == review.review_id
    assert journal_2.behavioral_flags[0].trade_id == trading_2.state.trades[0].trade_id
    assert journal_2.rule_violations[0].trade_id == trading_2.state.trades[0].trade_id

def test_derived_review_output_summarizes_closed_trade_review_findings() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "derived_review_journal"))

    journal.create_pre_trade_note(
        content="Structured long plan",
        setup_tag="BW_FRACTAL_LONG",
        thesis_summary="fractal breakout",
    )
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    review = journal.create_post_trade_review(
        content="Setup valid, exit rushed",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="late_entry",
        review_tags=("setup_late", "exit_too_early"),
    )
    journal.create_behavioral_flag(flag_code="premature_exit", review_ref=review.review_id)
    journal.create_rule_violation(rule_code="manual_plan_deviation", related_review_ref=review.review_id)

    journal_view = build_desktop_journal_view(journal)
    derived_output = journal_view["derived_review_output"]
    trade_result = derived_output["latest_trade_result"]

    assert derived_output["derived_only"] is True
    assert derived_output["closed_trade_count"] == 1
    assert derived_output["reviewed_trade_count"] == 1
    assert derived_output["pending_review_trade_count"] == 0
    assert trade_result["trade_id"] == trading.state.trades[-1].trade_id
    assert trade_result["review_status"] == "reviewed"
    assert trade_result["outcome_label"] == "loss"
    assert trade_result["holding_time_seconds"] == 2
    assert trade_result["setup_tag"] == "BW_FRACTAL_LONG"
    assert trade_result["compliance_label"] == "late_entry"
    assert trade_result["review_tags"] == ["setup_late", "exit_too_early"]
    assert trade_result["behavioral_flag_codes"] == ["premature_exit"]
    assert trade_result["rule_violation_codes"] == ["manual_plan_deviation"]
    assert trade_result["review_rule_context"]["context_status"] == "compliance_break_rule_context"
    assert "premature_exit, manual_plan_deviation" in trade_result["review_rule_context"]["context_text"]


def test_bill_williams_review_rule_context_links_intent_compliance_and_discipline() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_rule_context"))

    journal.create_pre_trade_note(content="Fractal intent", setup_tag="BW_FRACTAL_LONG")
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    review = journal.create_post_trade_review(
        content="Valid setup but weak discipline",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    journal.create_behavioral_flag(flag_code="premature_exit", review_ref=review.review_id)
    journal.create_rule_violation(rule_code="manual_plan_deviation", related_review_ref=review.review_id)

    summary = build_desktop_journal_view(journal)["session_review_summary"]
    rule_context = summary["review_rule_context"]

    assert rule_context["context_status"] == "valid_setup_discipline_break"
    assert rule_context["setup_tag"] == "BW_FRACTAL_LONG"
    assert rule_context["compliance_label"] == "valid_setup"
    assert rule_context["behavioral_flag_codes"] == ["premature_exit"]
    assert rule_context["rule_violation_codes"] == ["manual_plan_deviation"]
    assert rule_context["context_text"] == "Reviewed setup BW_FRACTAL_LONG stayed valid, but discipline slipped through premature_exit, manual_plan_deviation."


def test_bill_williams_review_discipline_cue_distills_rule_context() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_discipline_cue"))

    journal.create_pre_trade_note(content="Fractal intent", setup_tag="BW_FRACTAL_LONG")
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    review = journal.create_post_trade_review(
        content="Valid setup but weak discipline",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    journal.create_behavioral_flag(flag_code="premature_exit", review_ref=review.review_id)
    journal.create_rule_violation(rule_code="manual_plan_deviation", related_review_ref=review.review_id)

    cue = build_desktop_journal_view(journal)["session_review_summary"]["review_discipline_cue"]

    assert cue["cue_status"] == "discipline_guard_up"
    assert cue["cue_text"] == "Discipline cue: protect execution discipline around an otherwise valid setup."


def test_bill_williams_review_discipline_badge_compacts_discipline_cue() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_discipline_badge"))

    journal.create_pre_trade_note(content="Fractal intent", setup_tag="BW_FRACTAL_LONG")
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    review = journal.create_post_trade_review(
        content="Valid setup but weak discipline",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    journal.create_behavioral_flag(flag_code="premature_exit", review_ref=review.review_id)
    journal.create_rule_violation(rule_code="manual_plan_deviation", related_review_ref=review.review_id)

    badge = build_desktop_journal_view(journal)["session_review_summary"]["review_discipline_badge"]

    assert badge["badge_status"] == "guarded_badge"
    assert badge["badge_text"] == "Discipline badge: Guard execution."


def test_bill_williams_review_discipline_token_distills_badge() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_discipline_token"))

    journal.create_pre_trade_note(content="Fractal intent", setup_tag="BW_FRACTAL_LONG")
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    review = journal.create_post_trade_review(
        content="Valid setup but weak discipline",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    journal.create_behavioral_flag(flag_code="premature_exit", review_ref=review.review_id)
    journal.create_rule_violation(rule_code="manual_plan_deviation", related_review_ref=review.review_id)

    journal_view = build_desktop_journal_view(journal)
    token = journal_view["session_review_summary"]["review_discipline_token"]
    latest_trade_token = journal_view["derived_review_output"]["latest_trade_result"]["review_discipline_token"]

    assert token["token_status"] == "guard_execution_token"
    assert token["token_text"] == "Discipline token: Guard execution."
    assert latest_trade_token == token


def test_bill_williams_review_discipline_marker_distills_token() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_discipline_marker"))

    journal.create_pre_trade_note(content="Fractal intent", setup_tag="BW_FRACTAL_LONG")
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    review = journal.create_post_trade_review(
        content="Valid setup but weak discipline",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    journal.create_behavioral_flag(flag_code="premature_exit", review_ref=review.review_id)
    journal.create_rule_violation(rule_code="manual_plan_deviation", related_review_ref=review.review_id)

    journal_view = build_desktop_journal_view(journal)
    marker = journal_view["session_review_summary"]["review_discipline_marker"]
    latest_trade_marker = journal_view["derived_review_output"]["latest_trade_result"]["review_discipline_marker"]

    assert marker["marker_status"] == "guard_execution_marker"
    assert marker["marker_text"] == "Discipline marker: Guard execution path."
    assert latest_trade_marker == marker


def test_bill_williams_review_discipline_glyph_distills_marker() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_discipline_glyph"))

    journal.create_pre_trade_note(content="Fractal intent", setup_tag="BW_FRACTAL_LONG")
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    review = journal.create_post_trade_review(
        content="Valid setup but weak discipline",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    journal.create_behavioral_flag(flag_code="premature_exit", review_ref=review.review_id)
    journal.create_rule_violation(rule_code="manual_plan_deviation", related_review_ref=review.review_id)

    journal_view = build_desktop_journal_view(journal)
    glyph = journal_view["session_review_summary"]["review_discipline_glyph"]
    latest_trade_glyph = journal_view["derived_review_output"]["latest_trade_result"]["review_discipline_glyph"]

    assert glyph["glyph_status"] == "guard_execution_glyph"
    assert glyph["glyph_text"] == "Discipline glyph: Guard execution line."
    assert latest_trade_glyph == glyph


def test_bill_williams_review_discipline_sigil_distills_glyph() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_discipline_sigil"))

    journal.create_pre_trade_note(content="Fractal intent", setup_tag="BW_FRACTAL_LONG")
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    review = journal.create_post_trade_review(
        content="Valid setup but weak discipline",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    journal.create_behavioral_flag(flag_code="premature_exit", review_ref=review.review_id)
    journal.create_rule_violation(rule_code="manual_plan_deviation", related_review_ref=review.review_id)

    journal_view = build_desktop_journal_view(journal)
    sigil = journal_view["session_review_summary"]["review_discipline_sigil"]
    latest_trade_sigil = journal_view["derived_review_output"]["latest_trade_result"]["review_discipline_sigil"]

    assert sigil["sigil_status"] == "guard_execution_sigil"
    assert sigil["sigil_text"] == "Discipline sigil: Guard execution signal."
    assert latest_trade_sigil == sigil


def test_bill_williams_review_discipline_seal_distills_sigil() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_discipline_seal"))

    journal.create_pre_trade_note(content="Fractal intent", setup_tag="BW_FRACTAL_LONG")
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    review = journal.create_post_trade_review(
        content="Valid setup but weak discipline",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    journal.create_behavioral_flag(flag_code="premature_exit", review_ref=review.review_id)
    journal.create_rule_violation(rule_code="manual_plan_deviation", related_review_ref=review.review_id)

    journal_view = build_desktop_journal_view(journal)
    seal = journal_view["session_review_summary"]["review_discipline_seal"]
    latest_trade_seal = journal_view["derived_review_output"]["latest_trade_result"]["review_discipline_seal"]

    assert seal["seal_status"] == "guard_execution_seal"
    assert seal["seal_text"] == "Discipline seal: Guard execution lock."
    assert latest_trade_seal == seal


def test_bill_williams_review_discipline_crest_distills_seal() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_discipline_crest"))

    journal.create_pre_trade_note(content="Fractal intent", setup_tag="BW_FRACTAL_LONG")
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    review = journal.create_post_trade_review(
        content="Valid setup but weak discipline",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    journal.create_behavioral_flag(flag_code="premature_exit", review_ref=review.review_id)
    journal.create_rule_violation(rule_code="manual_plan_deviation", related_review_ref=review.review_id)

    journal_view = build_desktop_journal_view(journal)
    crest = journal_view["session_review_summary"]["review_discipline_crest"]
    latest_trade_crest = journal_view["derived_review_output"]["latest_trade_result"]["review_discipline_crest"]

    assert crest["crest_status"] == "guard_execution_crest"
    assert crest["crest_text"] == "Discipline crest: Guard execution frame."
    assert latest_trade_crest == crest


def test_bill_williams_review_discipline_emblem_distills_crest() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_discipline_emblem"))

    journal.create_pre_trade_note(content="Fractal intent", setup_tag="BW_FRACTAL_LONG")
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    review = journal.create_post_trade_review(
        content="Valid setup but weak discipline",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    journal.create_behavioral_flag(flag_code="premature_exit", review_ref=review.review_id)
    journal.create_rule_violation(rule_code="manual_plan_deviation", related_review_ref=review.review_id)

    journal_view = build_desktop_journal_view(journal)
    emblem = journal_view["session_review_summary"]["review_discipline_emblem"]
    latest_trade_emblem = journal_view["derived_review_output"]["latest_trade_result"]["review_discipline_emblem"]

    assert emblem["emblem_status"] == "guard_execution_emblem"
    assert emblem["emblem_text"] == "Discipline emblem: Guard execution badge."
    assert latest_trade_emblem == emblem


def test_derived_review_output_marks_closed_trade_without_review_as_pending() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "pending_review_journal"))

    trading.sell_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()

    journal_view = build_desktop_journal_view(journal)
    derived_output = journal_view["derived_review_output"]
    trade_result = derived_output["latest_trade_result"]

    assert derived_output["closed_trade_count"] == 1
    assert derived_output["reviewed_trade_count"] == 0
    assert derived_output["pending_review_trade_count"] == 1
    assert trade_result["review_status"] == "pending_review"
    assert trade_result["has_post_trade_review"] is False
    assert trade_result["outcome_label"] == "loss"


def test_derived_review_output_recovers_after_restart() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "derived_review_recovery_journal")

    session_1 = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_1 = MinimalTradingLoop(session_1)
    journal_1 = LocalJournalRuntime(session_1, trading_1, storage_dir)

    journal_1.create_pre_trade_note(content="Recovery plan", setup_tag="BW_1WM_LONG")
    trading_1.buy_market(volume=1.0)
    session_1.play()
    session_1.advance_frame()
    trading_1.manual_close()
    session_1.advance_frame()
    journal_1.create_post_trade_review(
        content="Recovered review output",
        setup_tag="BW_1WM_LONG",
        compliance_label="valid_setup",
        review_tags=("setup_clear",),
    )

    session_2 = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_2 = MinimalTradingLoop(session_2)
    journal_2 = LocalJournalRuntime(session_2, trading_2, storage_dir)

    derived_output = build_desktop_journal_view(journal_2)["derived_review_output"]
    trade_result = derived_output["latest_trade_result"]

    assert journal_2.recovered is True
    assert derived_output["reviewed_trade_count"] == 1
    assert trade_result["trade_id"] == trading_2.state.trades[0].trade_id
    assert trade_result["setup_tag"] == "BW_1WM_LONG"
    assert trade_result["compliance_label"] == "valid_setup"
    assert trade_result["review_status"] == "reviewed"



def test_bill_williams_review_delta_derives_declared_vs_reviewed_statuses() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_delta_journal"))

    journal.create_pre_trade_note(content="Fractal long plan", setup_tag="BW_FRACTAL_LONG")
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    journal.create_post_trade_review(
        content="Same setup but refined review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
        setup_variant="fractal_breakout",
        entry_timing_label="timely_entry",
    )

    refined_result = build_desktop_journal_view(journal)["derived_review_output"]["latest_trade_result"]
    refined_summary = build_desktop_journal_view(journal)["session_review_summary"]

    assert refined_result["intent_delta"]["delta_status"] == "intent_refined"
    assert refined_result["intent_delta"]["declared_setup_tag"] == "BW_FRACTAL_LONG"
    assert refined_result["intent_delta"]["reviewed_setup_tag"] == "BW_FRACTAL_LONG"
    assert refined_summary["intent_refined_count"] == 1
    assert refined_summary["latest_intent_delta"]["delta_status"] == "intent_refined"



def test_bill_williams_review_delta_handles_changed_and_missing_intent_states() -> None:
    # intent_changed
    session_a = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_a = MinimalTradingLoop(session_a)
    journal_a = LocalJournalRuntime(session_a, trading_a, _reset_dir(TMP_ROOT / "bw_review_delta_changed_journal"))
    journal_a.create_pre_trade_note(content="Initial 1WM idea", setup_tag="BW_1WM_LONG")
    trading_a.buy_market(volume=1.0)
    session_a.play()
    session_a.advance_frame()
    trading_a.manual_close()
    session_a.advance_frame()
    journal_a.create_post_trade_review(
        content="Actually closer to fractal breakout",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    changed_result = build_desktop_journal_view(journal_a)["derived_review_output"]["latest_trade_result"]
    assert changed_result["intent_delta"]["delta_status"] == "intent_changed"
    assert changed_result["intent_delta"]["setup_tag_changed"] is True

    # intent_missing
    session_b = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_b = MinimalTradingLoop(session_b)
    journal_b = LocalJournalRuntime(session_b, trading_b, _reset_dir(TMP_ROOT / "bw_review_delta_missing_journal"))
    trading_b.buy_market(volume=1.0)
    session_b.play()
    session_b.advance_frame()
    trading_b.manual_close()
    session_b.advance_frame()
    journal_b.create_post_trade_review(
        content="Reviewed without declared note intent",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    missing_result = build_desktop_journal_view(journal_b)["derived_review_output"]["latest_trade_result"]
    assert missing_result["intent_delta"]["delta_status"] == "intent_missing"

    # review_missing
    session_c = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_c = MinimalTradingLoop(session_c)
    journal_c = LocalJournalRuntime(session_c, trading_c, _reset_dir(TMP_ROOT / "bw_review_delta_review_missing_journal"))
    journal_c.create_pre_trade_note(content="Declared but not reviewed yet", setup_tag="BW_FRACTAL_LONG")
    trading_c.buy_market(volume=1.0)
    session_c.play()
    session_c.advance_frame()
    trading_c.manual_close()
    session_c.advance_frame()
    review_missing_result = build_desktop_journal_view(journal_c)["derived_review_output"]["latest_trade_result"]
    review_missing_summary = build_desktop_journal_view(journal_c)["session_review_summary"]
    assert review_missing_result["intent_delta"]["delta_status"] == "review_missing"
    assert review_missing_summary["review_missing_count"] == 1




def test_bill_williams_review_completeness_derives_complete_partial_sparse_and_missing() -> None:
    # complete
    session_a = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_a = MinimalTradingLoop(session_a)
    journal_a = LocalJournalRuntime(session_a, trading_a, _reset_dir(TMP_ROOT / "bw_review_completeness_complete_journal"))
    trading_a.buy_market(volume=1.0)
    session_a.play()
    session_a.advance_frame()
    trading_a.manual_close()
    session_a.advance_frame()
    journal_a.create_post_trade_review(
        content="Complete review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
        entry_timing_label="timely_entry",
        market_context_label="clean_context",
        exit_quality_label="disciplined_exit",
        review_clarity_label="high_clarity",
    )
    complete_result = build_desktop_journal_view(journal_a)["derived_review_output"]["latest_trade_result"]
    assert complete_result["review_completeness"]["completeness_status"] == "complete"
    assert complete_result["review_completeness"]["missing_parts"] == []

    # partial
    session_b = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_b = MinimalTradingLoop(session_b)
    journal_b = LocalJournalRuntime(session_b, trading_b, _reset_dir(TMP_ROOT / "bw_review_completeness_partial_journal"))
    trading_b.buy_market(volume=1.0)
    session_b.play()
    session_b.advance_frame()
    trading_b.manual_close()
    session_b.advance_frame()
    journal_b.create_post_trade_review(
        content="Partial review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
        entry_timing_label="timely_entry",
    )
    partial_result = build_desktop_journal_view(journal_b)["derived_review_output"]["latest_trade_result"]
    assert partial_result["review_completeness"]["completeness_status"] == "partial"
    assert "market_context_label" in partial_result["review_completeness"]["missing_parts"]
    assert "exit_quality_label" in partial_result["review_completeness"]["missing_parts"]

    # sparse
    session_c = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_c = MinimalTradingLoop(session_c)
    journal_c = LocalJournalRuntime(session_c, trading_c, _reset_dir(TMP_ROOT / "bw_review_completeness_sparse_journal"))
    trading_c.buy_market(volume=1.0)
    session_c.play()
    session_c.advance_frame()
    trading_c.manual_close()
    session_c.advance_frame()
    journal_c.create_post_trade_review(
        content="Sparse review",
        setup_tag="BW_FRACTAL_LONG",
    )
    sparse_result = build_desktop_journal_view(journal_c)["derived_review_output"]["latest_trade_result"]
    sparse_summary = build_desktop_journal_view(journal_c)["session_review_summary"]
    assert sparse_result["review_completeness"]["completeness_status"] == "sparse"
    assert sparse_summary["review_sparse_count"] == 1

    # review_missing
    session_d = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_d = MinimalTradingLoop(session_d)
    journal_d = LocalJournalRuntime(session_d, trading_d, _reset_dir(TMP_ROOT / "bw_review_completeness_missing_journal"))
    trading_d.buy_market(volume=1.0)
    session_d.play()
    session_d.advance_frame()
    trading_d.manual_close()
    session_d.advance_frame()
    missing_result = build_desktop_journal_view(journal_d)["derived_review_output"]["latest_trade_result"]
    missing_summary = build_desktop_journal_view(journal_d)["session_review_summary"]
    assert missing_result["review_completeness"]["completeness_status"] == "review_missing"
    assert missing_summary["review_pending_completeness_count"] == 1




def test_bill_williams_review_prompts_can_be_derived_from_delta_and_completeness_state() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_prompts_journal"))

    journal.create_pre_trade_note(content="Declared 1WM plan", setup_tag="BW_1WM_LONG")
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    journal.create_post_trade_review(
        content="Reviewed as different setup and still incomplete",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )

    latest_trade_result = build_desktop_journal_view(journal)["derived_review_output"]["latest_trade_result"]
    assert latest_trade_result["intent_delta"]["delta_status"] == "intent_changed"
    assert latest_trade_result["review_completeness"]["completeness_status"] == "sparse"
    assert latest_trade_result["review_completeness"]["missing_parts"] == [
        "entry_timing_label",
        "market_context_label",
        "exit_quality_label",
        "review_clarity_label",
    ]




def test_bill_williams_review_coverage_counts_filled_fields_across_reviewed_trades() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_coverage_journal"))

    # reviewed trade 1: complete
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    journal.create_post_trade_review(
        content="Complete review one",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
        entry_timing_label="timely_entry",
        market_context_label="clean_context",
        exit_quality_label="disciplined_exit",
        review_clarity_label="high_clarity",
    )

    # reviewed trade 2: partial
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    journal.create_post_trade_review(
        content="Partial review two",
        setup_tag="BW_1WM_LONG",
        compliance_label="valid_setup",
        entry_timing_label="timely_entry",
    )

    derived = build_desktop_journal_view(journal)["derived_review_output"]
    summary = build_desktop_journal_view(journal)["session_review_summary"]
    coverage = derived["review_field_coverage"]

    assert coverage["total_reviewed_trades"] == 2
    assert coverage["setup_tag_coverage_count"] == 2
    assert coverage["compliance_label_coverage_count"] == 2
    assert coverage["entry_timing_coverage_count"] == 2
    assert coverage["market_context_coverage_count"] == 1
    assert coverage["exit_quality_coverage_count"] == 1
    assert coverage["review_clarity_coverage_count"] == 1
    assert coverage["market_context_coverage_ratio"] == pytest.approx(0.5)
    assert summary["review_field_coverage"]["exit_quality_coverage_count"] == 1


def test_session_result_metrics_are_derived_from_closed_trades() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "session_metrics_journal"))

    trading.sell_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    journal.create_post_trade_review(content="First trade reviewed")

    trading.buy_market(volume=1.0)
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()

    derived_output = build_desktop_journal_view(journal)["derived_review_output"]

    assert derived_output["closed_trade_count"] == 2
    assert derived_output["reviewed_trade_count"] == 1
    assert derived_output["pending_review_trade_count"] == 1
    assert derived_output["win_trade_count"] == 0
    assert derived_output["loss_trade_count"] == 2
    assert derived_output["flat_trade_count"] == 0
    assert derived_output["session_net_realised_pnl"] == pytest.approx(-0.00022)
    assert derived_output["session_total_trade_cost"] == pytest.approx(0.00048)
    assert derived_output["total_holding_time_seconds"] == 4
    assert derived_output["average_holding_time_seconds"] == pytest.approx(2.0)
    assert derived_output["review_completion_ratio"] == pytest.approx(0.5)


def test_session_result_metrics_recover_after_restart() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "session_metrics_recovery_journal")

    session_1 = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_1 = MinimalTradingLoop(session_1)
    journal_1 = LocalJournalRuntime(session_1, trading_1, storage_dir)

    trading_1.sell_market(volume=1.0)
    session_1.play()
    session_1.advance_frame()
    trading_1.manual_close()
    session_1.advance_frame()
    journal_1.create_post_trade_review(content="Persisted session metrics review")

    session_2 = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_2 = MinimalTradingLoop(session_2)
    journal_2 = LocalJournalRuntime(session_2, trading_2, storage_dir)

    derived_output = build_desktop_journal_view(journal_2)["derived_review_output"]

    assert journal_2.recovered is True
    assert derived_output["closed_trade_count"] == 1
    assert derived_output["reviewed_trade_count"] == 1
    assert derived_output["pending_review_trade_count"] == 0
    assert derived_output["loss_trade_count"] == 1
    assert derived_output["session_net_realised_pnl"] == pytest.approx(-0.00016)
    assert derived_output["session_total_trade_cost"] == pytest.approx(0.00024)
    assert derived_output["review_completion_ratio"] == pytest.approx(1.0)


def test_session_timeline_projection_orders_trade_review_events() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "timeline_journal"))

    note = journal.create_pre_trade_note(content="Timeline plan", setup_tag="BW_FRACTAL_LONG")
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    review = journal.create_post_trade_review(content="Timeline review", setup_tag="BW_FRACTAL_LONG")
    flag = journal.create_behavioral_flag(flag_code="premature_exit", review_ref=review.review_id)
    violation = journal.create_rule_violation(rule_code="manual_plan_deviation", related_review_ref=review.review_id)

    timeline = build_desktop_journal_view(journal)["session_timeline"]
    event_types = [item["event_type"] for item in timeline["timeline_items"]]

    assert timeline["derived_only"] is True
    assert timeline["timeline_item_count"] == 9
    assert event_types == [
        "session_started",
        "pre_trade_note",
        "trade_opened",
        "execution",
        "trade_closed",
        "post_trade_review",
        "behavioral_flag",
        "rule_violation",
        "execution",
    ]
    assert timeline["timeline_items"][1]["payload"]["content"] == "Timeline plan"
    assert timeline["latest_timeline_item"]["event_type"] == "execution"
    assert timeline["latest_timeline_item"]["payload"]["execution_type"] == "manual_close_fill"
    assert any(item["timeline_id"] == f"note:{note.note_id}" for item in timeline["timeline_items"])
    assert any(item["timeline_id"] == f"review:{review.review_id}" for item in timeline["timeline_items"])
    assert any(item["timeline_id"] == f"flag:{flag.flag_id}" for item in timeline["timeline_items"])


def test_session_timeline_projection_recovers_after_restart() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "timeline_recovery_journal")

    session_1 = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_1 = MinimalTradingLoop(session_1)
    journal_1 = LocalJournalRuntime(session_1, trading_1, storage_dir)

    journal_1.create_pre_trade_note(content="Recovery timeline note")
    trading_1.sell_market(volume=1.0)
    session_1.play()
    session_1.advance_frame()
    trading_1.manual_close()
    session_1.advance_frame()
    journal_1.create_post_trade_review(content="Recovery timeline review")

    session_2 = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_2 = MinimalTradingLoop(session_2)
    journal_2 = LocalJournalRuntime(session_2, trading_2, storage_dir)

    timeline = build_desktop_journal_view(journal_2)["session_timeline"]

    assert journal_2.recovered is True
    assert timeline["timeline_item_count"] == 7
    assert timeline["timeline_items"][0]["event_type"] == "session_started"
    assert timeline["timeline_items"][-1]["event_type"] == "execution"
    assert any(item["event_type"] == "execution" for item in timeline["timeline_items"])
    assert any(item["event_type"] == "trade_closed" for item in timeline["timeline_items"])

def test_chart_snapshot_can_be_linked_to_note_and_review() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "snapshot_link_journal"))

    snapshot = journal.create_chart_snapshot(
        artifact_ref="snapshots/session-1/pre-entry.png",
        snapshot_role="pre_entry_context",
    )
    note = journal.create_pre_trade_note(
        content="Plan with chart reference",
        chart_snapshot_ref=snapshot.snapshot_id,
    )

    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()

    review_snapshot = journal.create_chart_snapshot(
        artifact_ref="snapshots/session-1/review.png",
        snapshot_role="review_context",
    )
    review = journal.create_post_trade_review(
        content="Review with chart reference",
        chart_snapshot_refs=(review_snapshot.snapshot_id,),
    )

    journal_view = build_desktop_journal_view(journal)
    timeline = journal_view["session_timeline"]
    snapshot_items = [item for item in timeline["timeline_items"] if item["event_type"] == "chart_snapshot"]
    note_item = next(item for item in timeline["timeline_items"] if item["timeline_id"] == f"note:{note.note_id}")
    review_item = next(item for item in timeline["timeline_items"] if item["timeline_id"] == f"review:{review.review_id}")

    assert snapshot.trade_id is None
    assert note.chart_snapshot_ref == snapshot.snapshot_id
    assert review.chart_snapshot_refs == (review_snapshot.snapshot_id,)
    assert journal_view["chart_snapshot_count"] == 2
    assert journal_view["has_chart_snapshots"] is True
    assert journal_view["last_chart_snapshot"]["snapshot_id"] == review_snapshot.snapshot_id
    assert len(snapshot_items) == 2
    assert snapshot_items[0]["payload"]["artifact_ref"] == "snapshots/session-1/pre-entry.png"
    assert note_item["payload"]["linked_chart_snapshot"]["snapshot_id"] == snapshot.snapshot_id
    assert review_item["payload"]["linked_chart_snapshots"][0]["snapshot_id"] == review_snapshot.snapshot_id
    assert review_item["payload"]["linked_chart_snapshot_count"] == 1


def test_chart_snapshot_recovers_after_restart() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "snapshot_recovery_journal")

    session_1 = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_1 = MinimalTradingLoop(session_1)
    journal_1 = LocalJournalRuntime(session_1, trading_1, storage_dir)

    snapshot = journal_1.create_chart_snapshot(
        artifact_ref="snapshots/session-2/review.png",
        snapshot_role="review_context",
    )
    note = journal_1.create_pre_trade_note(content="Recovered note", chart_snapshot_ref=snapshot.snapshot_id)

    session_2 = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_2 = MinimalTradingLoop(session_2)
    journal_2 = LocalJournalRuntime(session_2, trading_2, storage_dir)

    journal_view = build_desktop_journal_view(journal_2)
    timeline = journal_view["session_timeline"]
    note_item = next(item for item in timeline["timeline_items"] if item["timeline_id"] == f"note:{note.note_id}")
    snapshot_item = next(item for item in timeline["timeline_items"] if item["timeline_id"] == f"snapshot:{snapshot.snapshot_id}")

    assert journal_2.recovered is True
    assert journal_2.chart_snapshots[0].snapshot_id == snapshot.snapshot_id
    assert journal_2.pre_trade_notes[0].chart_snapshot_ref == snapshot.snapshot_id
    assert journal_view["chart_snapshot_count"] == 1
    assert journal_view["last_chart_snapshot"]["artifact_ref"] == "snapshots/session-2/review.png"
    assert snapshot_item["payload"]["snapshot_role"] == "review_context"
    assert note_item["payload"]["linked_chart_snapshot"]["artifact_ref"] == "snapshots/session-2/review.png"






def test_session_finalization_blocks_with_pending_review_and_allows_force() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "session_finalization_journal"))

    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    session.pause()

    journal_view = build_desktop_journal_view(journal)
    finalization = journal_view["session_finalization"]

    assert finalization["is_session_finalized"] is False
    assert finalization["pending_review_trade_count"] == 1
    assert finalization["requires_force_to_finalize"] is True
    assert finalization["can_finalize_without_force"] is False
    assert finalization["can_finalize_with_force"] is True

    with pytest.raises(SessionFinalizationError):
        journal.finalize_session()

    finalized_session = journal.finalize_session(force=True, reason="user_forced_close")
    journal_view = build_desktop_journal_view(journal)
    finalization = journal_view["session_finalization"]

    assert finalized_session.finalization_status == "finalized"
    assert finalized_session.finalization_reason == "user_forced_close"
    assert finalization["is_session_finalized"] is True
    assert finalization["finalization_reason"] == "user_forced_close"


def test_session_finalization_blocks_running_replay_and_active_trade() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "session_finalization_blockers_journal"))

    session.play()
    with pytest.raises(SessionFinalizationError):
        journal.finalize_session()
    session.pause()

    trading.buy_market(volume=1.0)
    with pytest.raises(SessionFinalizationError):
        journal.finalize_session(force=True)


def test_session_finalization_recovers_after_restart_and_blocks_new_mutations() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "session_finalization_recovery_journal")

    session_1 = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_1 = MinimalTradingLoop(session_1)
    journal_1 = LocalJournalRuntime(session_1, trading_1, storage_dir)

    journal_1.create_pre_trade_note(content="Reviewed before finalize")
    trading_1.sell_market(volume=1.0)
    session_1.play()
    session_1.advance_frame()
    trading_1.manual_close()
    session_1.advance_frame()
    session_1.pause()
    journal_1.create_post_trade_review(content="Ready to finalize")
    journal_1.finalize_session(reason="user_completed")

    session_2 = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_2 = MinimalTradingLoop(session_2)
    journal_2 = LocalJournalRuntime(session_2, trading_2, storage_dir)

    journal_view = build_desktop_journal_view(journal_2)
    finalization = journal_view["session_finalization"]

    assert journal_2.recovered is True
    assert journal_2.training_session.finalization_status == "finalized"
    assert journal_2.training_session.finalization_reason == "user_completed"
    assert finalization["is_session_finalized"] is True
    assert finalization["pending_review_trade_count"] == 0
    assert finalization["can_finalize_without_force"] is True

    with pytest.raises(SessionFinalizationError):
        journal_2.create_pre_trade_note(content="Too late after finalization")




def test_session_review_summary_compacts_open_review_state() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "session_review_summary_open_journal"))

    pre_snapshot = journal.create_chart_snapshot(
        artifact_ref="snapshots/session-summary/pre.png",
        snapshot_role="pre_entry_context",
    )
    journal.create_pre_trade_note(
        content="Summary plan",
        setup_tag="BW_FRACTAL_LONG",
        chart_snapshot_ref=pre_snapshot.snapshot_id,
    )
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    review_snapshot = journal.create_chart_snapshot(
        artifact_ref="snapshots/session-summary/review.png",
        snapshot_role="review_context",
    )
    review = journal.create_post_trade_review(
        content="Summary review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="late_entry",
        chart_snapshot_refs=(review_snapshot.snapshot_id,),
    )
    journal.create_behavioral_flag(flag_code="premature_exit", review_ref=review.review_id)
    journal.create_rule_violation(rule_code="manual_plan_deviation", related_review_ref=review.review_id)

    summary = build_desktop_journal_view(journal)["session_review_summary"]

    assert summary["derived_only"] is True
    assert summary["summary_status"] == "review_complete"
    assert summary["is_session_finalized"] is False
    assert summary["closed_trade_count"] == 1
    assert summary["reviewed_trade_count"] == 1
    assert summary["pending_review_trade_count"] == 0
    assert summary["behavioral_flag_count"] == 1
    assert summary["rule_violation_count"] == 1
    assert summary["trades_with_linked_chart_snapshots_count"] == 1
    assert summary["latest_review_status"] == "reviewed"
    assert summary["latest_setup_tag"] == "BW_FRACTAL_LONG"
    assert summary["latest_compliance_label"] == "late_entry"
    assert summary["latest_linked_chart_snapshot_count"] == 2
    assert summary["latest_reviewed_trade_id"] == trading.state.trades[-1].trade_id
    assert summary["latest_pending_review_trade_id"] is None
    assert summary["can_finalize_without_force"] is False
    assert summary["can_finalize_with_force"] is False


def test_session_review_summary_recovers_finalized_state_after_restart() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "session_review_summary_recovery_journal")

    session_1 = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_1 = MinimalTradingLoop(session_1)
    journal_1 = LocalJournalRuntime(session_1, trading_1, storage_dir)

    trading_1.sell_market(volume=1.0)
    session_1.play()
    session_1.advance_frame()
    trading_1.manual_close()
    session_1.advance_frame()
    session_1.pause()
    journal_1.create_post_trade_review(content="Final summary review")
    journal_1.finalize_session(reason="user_completed")

    session_2 = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_2 = MinimalTradingLoop(session_2)
    journal_2 = LocalJournalRuntime(session_2, trading_2, storage_dir)

    summary = build_desktop_journal_view(journal_2)["session_review_summary"]

    assert journal_2.recovered is True
    assert summary["summary_status"] == "finalized_review_complete"
    assert summary["is_session_finalized"] is True
    assert summary["finalization_reason"] == "user_completed"
    assert summary["closed_trade_count"] == 1
    assert summary["reviewed_trade_count"] == 1
    assert summary["pending_review_trade_count"] == 0
    assert summary["latest_trade_id"] == trading_2.state.trades[0].trade_id
    assert summary["latest_review_status"] == "reviewed"
    assert summary["latest_pending_review_trade_id"] is None
    assert summary["can_finalize_without_force"] is True

def test_mvp_acceptance_pass_end_to_end_local_first_workflow() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "mvp_acceptance_journal")

    session_1 = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_1 = MinimalTradingLoop(session_1)
    journal_1 = LocalJournalRuntime(session_1, trading_1, storage_dir)

    replay_view = build_desktop_replay_view(session_1)
    assert replay_view["dataset_id"] == "eurusd-sample-v1"
    assert replay_view["status"] == "paused"
    assert replay_view["instrument_id"] == "EURUSD"

    pre_snapshot = journal_1.create_chart_snapshot(
        artifact_ref="snapshots/mvp/pre-trade.png",
        snapshot_role="pre_entry_context",
    )
    note = journal_1.create_pre_trade_note(
        content="MVP acceptance trade idea",
        setup_tag="BW_FRACTAL_LONG",
        thesis_summary="breakout continuation with structure support",
        risk_plan="manual close on weakness",
        chart_snapshot_ref=pre_snapshot.snapshot_id,
    )

    order = trading_1.buy_market(volume=1.0)
    assert order.order_type == "BuyMarket"
    session_1.play()
    session_1.advance_frame()

    trading_view = build_desktop_trading_view(trading_1)
    assert trading_view["active_trade_present"] is True
    assert trading_view["trade_status"] == "open"

    close_order = trading_1.manual_close()
    assert close_order.order_type == "ManualClose"
    session_1.advance_frame()
    session_1.pause()

    review_snapshot = journal_1.create_chart_snapshot(
        artifact_ref="snapshots/mvp/post-trade.png",
        snapshot_role="review_context",
    )
    review = journal_1.create_post_trade_review(
        content="MVP acceptance review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
        discipline_assessment="discipline_kept",
        review_tags=("setup_clear",),
        chart_snapshot_refs=(review_snapshot.snapshot_id,),
    )
    journal_1.create_behavioral_flag(
        flag_code="premature_exit",
        review_ref=review.review_id,
        description="Exit was a little early but still documented",
    )
    journal_1.create_rule_violation(
        rule_code="manual_plan_deviation",
        related_review_ref=review.review_id,
        description="Exit timing deviated from the original note",
    )
    journal_1.finalize_session(reason="user_completed")

    journal_view_1 = build_desktop_journal_view(journal_1)
    trade_result_1 = journal_view_1["derived_review_output"]["latest_trade_result"]
    summary_1 = journal_view_1["session_review_summary"]
    finalization_1 = journal_view_1["session_finalization"]

    assert note.trade_id == trading_1.state.trades[0].trade_id
    assert trade_result_1["review_status"] == "reviewed"
    assert trade_result_1["setup_tag"] == "BW_FRACTAL_LONG"
    assert trade_result_1["linked_chart_snapshot_count"] == 2
    assert summary_1["summary_status"] == "finalized_review_complete"
    assert summary_1["reviewed_trade_count"] == 1
    assert summary_1["pending_review_trade_count"] == 0
    assert summary_1["behavioral_flag_count"] == 1
    assert summary_1["rule_violation_count"] == 1
    assert summary_1["trades_with_linked_chart_snapshots_count"] == 1
    assert finalization_1["is_session_finalized"] is True

    session_2 = create_replay_session(str(FIXTURE), replay_mode="training")
    trading_2 = MinimalTradingLoop(session_2)
    journal_2 = LocalJournalRuntime(session_2, trading_2, storage_dir)

    replay_view_2 = build_desktop_replay_view(session_2)
    trading_view_2 = build_desktop_trading_view(trading_2)
    journal_view_2 = build_desktop_journal_view(journal_2)
    trade_result_2 = journal_view_2["derived_review_output"]["latest_trade_result"]
    summary_2 = journal_view_2["session_review_summary"]
    finalization_2 = journal_view_2["session_finalization"]

    assert journal_2.recovered is True
    assert replay_view_2["simulation_time"] == "2025-01-02T10:00:03Z"
    assert trading_view_2["trade_status"] == "closed"
    assert trading_view_2["active_trade_present"] is False
    assert trade_result_2["trade_id"] == trading_2.state.trades[0].trade_id
    assert trade_result_2["review_status"] == "reviewed"
    assert trade_result_2["linked_chart_snapshot_count"] == 2
    assert journal_view_2["chart_snapshot_count"] == 2
    assert journal_view_2["pre_trade_note_count"] == 1
    assert journal_view_2["post_trade_review_count"] == 1
    assert summary_2["summary_status"] == "finalized_review_complete"
    assert summary_2["latest_trade_id"] == trading_2.state.trades[0].trade_id
    assert summary_2["latest_review_status"] == "reviewed"
    assert summary_2["latest_setup_tag"] == "BW_FRACTAL_LONG"
    assert summary_2["latest_compliance_label"] == "valid_setup"
    assert finalization_2["is_session_finalized"] is True
    assert finalization_2["finalization_reason"] == "user_completed"


def test_bill_williams_review_sequence_derives_next_field_and_order() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_sequence_journal"))

    journal.create_pre_trade_note(content="Declared fractal long", setup_tag="BW_FRACTAL_LONG")
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    journal.create_post_trade_review(
        content="Sequence review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
        entry_timing_label="timely_entry",
    )

    latest_trade_result = build_desktop_journal_view(journal)["derived_review_output"]["latest_trade_result"]
    review_sequence = latest_trade_result["review_sequence"]
    summary = build_desktop_journal_view(journal)["session_review_summary"]

    assert review_sequence["sequence_status"] == "in_progress"
    assert review_sequence["next_field"] == "market_context_label"
    assert review_sequence["recommended_missing_order"] == [
        "market_context_label",
        "exit_quality_label",
        "review_clarity_label",
    ]
    assert review_sequence["ordered_steps"][0]["field_name"] == "setup_tag"
    assert review_sequence["ordered_steps"][0]["step_status"] == "completed"
    assert review_sequence["ordered_steps"][3]["field_name"] == "market_context_label"
    assert review_sequence["ordered_steps"][3]["step_status"] == "next"
    assert review_sequence["next_prompt"] == "Describe market context before exit quality and clarity."
    assert summary["latest_review_sequence"]["next_field"] == "market_context_label"


def test_bill_williams_review_sequence_marks_review_missing_until_review_exists() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_sequence_missing_journal"))

    journal.create_pre_trade_note(content="Declared long", setup_tag="BW_FRACTAL_LONG")
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()

    latest_trade_result = build_desktop_journal_view(journal)["derived_review_output"]["latest_trade_result"]
    review_sequence = latest_trade_result["review_sequence"]

    assert latest_trade_result["review_status"] == "pending_review"
    assert review_sequence["sequence_status"] == "review_missing"
    assert review_sequence["next_field"] == "setup_tag"
    assert review_sequence["recommended_missing_order"][0] == "setup_tag"
    assert review_sequence["next_prompt"] == "Confirm the reviewed setup before any deeper Bill Williams review detail."


def test_bill_williams_review_weak_spots_derives_underfilled_fields_from_coverage() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_weak_spots_journal"))

    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    journal.create_post_trade_review(
        content="Review one",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
        entry_timing_label="timely_entry",
        market_context_label="clean_context",
        exit_quality_label="disciplined_exit",
        review_clarity_label="high_clarity",
    )

    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    journal.create_post_trade_review(
        content="Review two",
        setup_tag="BW_1WM_LONG",
        compliance_label="valid_setup",
        entry_timing_label="timely_entry",
    )

    derived = build_desktop_journal_view(journal)["derived_review_output"]
    weak_spots = derived["review_weak_spots"]
    summary = build_desktop_journal_view(journal)["session_review_summary"]

    assert weak_spots["weak_spot_status"] == "underfilled_fields_present"
    assert weak_spots["underfilled_field_count"] == 3
    assert weak_spots["top_weak_spot_fields"] == [
        "exit_quality_label",
        "market_context_label",
        "review_clarity_label",
    ]
    assert weak_spots["top_weak_spot_details"][0]["coverage_count"] == 1
    assert weak_spots["top_weak_spot_details"][0]["coverage_ratio"] == 0.5
    assert weak_spots["advisory_prompt"] == "Session weak spots are concentrated in: exit_quality_label, market_context_label, review_clarity_label."
    assert summary["review_weak_spots"]["top_weak_spot_fields"][0] == "exit_quality_label"


def test_bill_williams_review_weak_spots_reports_fully_covered_session() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_weak_spots_complete_journal"))

    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    journal.create_post_trade_review(
        content="Complete review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
        entry_timing_label="timely_entry",
        market_context_label="clean_context",
        exit_quality_label="disciplined_exit",
        review_clarity_label="high_clarity",
    )

    weak_spots = build_desktop_journal_view(journal)["derived_review_output"]["review_weak_spots"]

    assert weak_spots["weak_spot_status"] == "fully_covered"
    assert weak_spots["top_weak_spot_fields"] == []
    assert weak_spots["advisory_prompt"] == "Current session coverage is strong across all Bill Williams review fields."


def test_bill_williams_review_progress_marks_latest_review_as_improving_weak_spots() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_progress_improving"))

    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    journal.create_post_trade_review(
        content="Sparse review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
        entry_timing_label="timely_entry",
    )

    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    journal.create_post_trade_review(
        content="Improving review",
        setup_tag="BW_1WM_LONG",
        compliance_label="valid_setup",
        entry_timing_label="timely_entry",
        market_context_label="clean_context",
        exit_quality_label="disciplined_exit",
        review_clarity_label="high_clarity",
    )

    summary = build_desktop_journal_view(journal)["session_review_summary"]
    progress = summary["review_progress"]

    assert progress["progress_status"] == "weak_spots_improved"
    assert progress["improved_fields"] == ["exit_quality_label", "market_context_label", "review_clarity_label"]
    assert progress["still_missing_fields"] == []
    assert progress["advisory_prompt"] == "Latest review improved all current weak spots: exit_quality_label, market_context_label, review_clarity_label."


def test_bill_williams_review_progress_marks_latest_review_as_still_missing_weak_spots() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_progress_missing"))

    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    journal.create_post_trade_review(
        content="Complete review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
        entry_timing_label="timely_entry",
        market_context_label="clean_context",
        exit_quality_label="disciplined_exit",
        review_clarity_label="high_clarity",
    )

    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    journal.create_post_trade_review(
        content="Partial review",
        setup_tag="BW_1WM_LONG",
        compliance_label="valid_setup",
        entry_timing_label="timely_entry",
    )

    summary = build_desktop_journal_view(journal)["session_review_summary"]
    progress = summary["review_progress"]

    assert progress["progress_status"] == "weak_spots_not_improved"
    assert progress["improved_fields"] == []
    assert progress["still_missing_fields"] == ["exit_quality_label", "market_context_label", "review_clarity_label"]
    assert progress["advisory_prompt"] == "Latest review still missed the current weak spots: exit_quality_label, market_context_label, review_clarity_label."


def test_bill_williams_review_momentum_derives_improving_recent_sequence() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_momentum_improving"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Partial", setup_tag="BW_1WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    momentum = build_desktop_journal_view(journal)["session_review_summary"]["review_momentum"]

    assert momentum["momentum_status"] == "improving"
    assert momentum["score_sequence"] == [1, 3]
    assert momentum["advisory_prompt"] == "Recent Bill Williams review quality is trending better across the latest reviewed trades."


def test_bill_williams_review_momentum_derives_slipping_recent_sequence() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_momentum_slipping"))

    for kwargs in [
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
        dict(content="Partial", setup_tag="BW_1WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    momentum = build_desktop_journal_view(journal)["session_review_summary"]["review_momentum"]

    assert momentum["momentum_status"] == "slipping"
    assert momentum["score_sequence"] == [3, 1]
    assert momentum["advisory_prompt"] == "Recent Bill Williams review quality is trending weaker across the latest reviewed trades."


def test_bill_williams_review_stability_derives_stable_recent_scores() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_stability_stable"))

    for kwargs in [
        dict(content="Partial one", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
        dict(content="Partial two", setup_tag="BW_1WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    stability = build_desktop_journal_view(journal)["session_review_summary"]["review_stability"]

    assert stability["stability_status"] == "stable"
    assert stability["score_spread"] == 0
    assert stability["advisory_prompt"] == "Recent Bill Williams review quality is relatively stable across the latest reviewed trades."


def test_bill_williams_review_stability_derives_uneven_recent_scores() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_stability_uneven"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    stability = build_desktop_journal_view(journal)["session_review_summary"]["review_stability"]

    assert stability["stability_status"] == "uneven"
    assert stability["score_spread"] == 2
    assert stability["advisory_prompt"] == "Recent Bill Williams review quality is uneven across the latest reviewed trades."


def test_bill_williams_review_swings_detects_sharp_adjacent_jumps() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_swings_detected"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    swings = build_desktop_journal_view(journal)["session_review_summary"]["review_swings"]

    assert swings["swing_status"] == "sharp_swings_detected"
    assert swings["max_adjacent_jump"] == 2
    assert swings["swing_pairs"][0]["score_jump"] == 2
    assert swings["advisory_prompt"] == "Recent Bill Williams review quality shows sharp swings between neighboring reviewed trades."


def test_bill_williams_review_swings_reports_no_sharp_swings_for_small_jumps() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_swings_none"))

    for kwargs in [
        dict(content="Partial one", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
        dict(content="Partial two", setup_tag="BW_1WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    swings = build_desktop_journal_view(journal)["session_review_summary"]["review_swings"]

    assert swings["swing_status"] == "no_sharp_swings"
    assert swings["max_adjacent_jump"] == 0
    assert swings["swing_pairs"] == []
    assert swings["advisory_prompt"] == "Recent Bill Williams review quality does not show sharp swings between neighboring reviewed trades."


def test_bill_williams_review_floor_derives_fragile_floor_from_recent_scores() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_floor_fragile"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    floor = build_desktop_journal_view(journal)["session_review_summary"]["review_floor"]

    assert floor["floor_status"] == "fragile_floor"
    assert floor["min_recent_score"] == 1
    assert floor["advisory_prompt"] == "Recent Bill Williams review quality is still resting on a fragile floor."


def test_bill_williams_review_floor_derives_moderate_floor_from_recent_scores() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_floor_moderate"))

    for kwargs in [
        dict(content="Partial one", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
        dict(content="Partial two", setup_tag="BW_1WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    floor = build_desktop_journal_view(journal)["session_review_summary"]["review_floor"]

    assert floor["floor_status"] == "moderate_floor"
    assert floor["min_recent_score"] == 2
    assert floor["advisory_prompt"] == "Recent Bill Williams review quality is holding a moderate floor."


def test_bill_williams_review_ceiling_derives_high_ceiling_from_recent_scores() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_ceiling_high"))

    for kwargs in [
        dict(content="Partial", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    ceiling = build_desktop_journal_view(journal)["session_review_summary"]["review_ceiling"]

    assert ceiling["ceiling_status"] == "high_ceiling"
    assert ceiling["max_recent_score"] == 3
    assert ceiling["advisory_prompt"] == "Recent Bill Williams review quality is reaching a high ceiling."


def test_bill_williams_review_ceiling_derives_moderate_ceiling_from_recent_scores() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_ceiling_moderate"))

    for kwargs in [
        dict(content="Partial one", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
        dict(content="Partial two", setup_tag="BW_1WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    ceiling = build_desktop_journal_view(journal)["session_review_summary"]["review_ceiling"]

    assert ceiling["ceiling_status"] == "moderate_ceiling"
    assert ceiling["max_recent_score"] == 2
    assert ceiling["advisory_prompt"] == "Recent Bill Williams review quality is reaching a moderate ceiling."


def test_bill_williams_review_band_derives_controlled_corridor_from_recent_scores() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_band_controlled"))

    for kwargs in [
        dict(content="Partial", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    band = build_desktop_journal_view(journal)["session_review_summary"]["review_band"]

    assert band["band_status"] == "controlled_band"
    assert band["min_recent_score"] == 2
    assert band["max_recent_score"] == 3
    assert band["band_width"] == 1
    assert band["corridor_label"] == "2-3"
    assert band["advisory_prompt"] == "Recent Bill Williams review quality is moving inside a controlled band of 2-3."


def test_bill_williams_review_headroom_derives_narrow_headroom_from_recent_ceiling() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_headroom_narrow"))

    for kwargs in [
        dict(content="Partial one", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
        dict(content="Partial two", setup_tag="BW_1WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    headroom = build_desktop_journal_view(journal)["session_review_summary"]["review_headroom"]

    assert headroom["headroom_status"] == "narrow_headroom"
    assert headroom["max_recent_score"] == 2
    assert headroom["max_possible_recent_score"] == 3
    assert headroom["remaining_headroom"] == 1
    assert headroom["corridor_label"] == "2-2"
    assert headroom["advisory_prompt"] == "Recent Bill Williams review quality still has a narrow step of headroom above the current ceiling."


def test_bill_williams_review_pressure_prioritizes_tightening_wide_band() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_pressure_band"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    pressure = build_desktop_journal_view(journal)["session_review_summary"]["review_pressure"]

    assert pressure["pressure_status"] == "tighten_band_pressure"
    assert pressure["pressure_target"] == "tighten_band"
    assert pressure["advisory_prompt"] == "Current Bill Williams review pressure is on tightening the recent quality band before pushing higher."


def test_bill_williams_review_target_selects_weakest_field_from_pressure_state() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_target_field"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    target = build_desktop_journal_view(journal)["session_review_summary"]["review_target"]

    assert target["target_status"] == "tighten_band_target"
    assert target["target_field"] == "entry_timing_label"
    assert target["target_prompt"] == "Tighten the recent quality band by reducing drift in: entry_timing_label."


def test_bill_williams_review_focus_builds_compact_focus_from_target_field() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_focus_field"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    focus = build_desktop_journal_view(journal)["session_review_summary"]["review_focus"]

    assert focus["focus_status"] == "tighten_focus"
    assert focus["focus_label"] == "Tighten around entry_timing_label"
    assert focus["focus_prompt"] == "Keep today's review focus tight around entry_timing_label before broadening to other fields."


def test_bill_williams_review_cue_builds_short_operating_hint_from_focus() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_cue_field"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    cue = build_desktop_journal_view(journal)["session_review_summary"]["review_cue"]

    assert cue["cue_status"] == "tighten_cue"
    assert cue["cue_text"] == "Tighten around entry_timing_label"


def test_bill_williams_review_badge_builds_compact_display_carrier() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_badge_field"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    badge = build_desktop_journal_view(journal)["session_review_summary"]["review_badge"]

    assert badge["badge_status"] == "tighten_badge"
    assert badge["badge_text"] == "Tighten around entry_timing_label"


def test_bill_williams_review_pill_builds_compact_ui_carrier() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_pill_field"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    pill = build_desktop_journal_view(journal)["session_review_summary"]["review_pill"]

    assert pill["pill_status"] == "tighten_pill"
    assert pill["pill_text"] == "Tighten around entry_timing_label"


def test_bill_williams_review_chip_builds_small_ui_carrier() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_chip_field"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    chip = build_desktop_journal_view(journal)["session_review_summary"]["review_chip"]

    assert chip["chip_status"] == "tighten_chip"
    assert chip["chip_text"] == "Tighten around entry_timing_label"


def test_bill_williams_review_tag_builds_small_display_token() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_tag_field"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    tag = build_desktop_journal_view(journal)["session_review_summary"]["review_tag"]

    assert tag["tag_status"] == "tighten_tag"
    assert tag["tag_text"] == "Tighten around entry_timing_label"


def test_bill_williams_review_token_builds_small_display_carrier() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_token_field"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    token = build_desktop_journal_view(journal)["session_review_summary"]["review_token"]

    assert token["token_status"] == "tighten_token"
    assert token["token_text"] == "Tighten around entry_timing_label"


def test_bill_williams_review_marker_builds_small_status_carrier() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_marker_field"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    marker = build_desktop_journal_view(journal)["session_review_summary"]["review_marker"]

    assert marker["marker_status"] == "tighten_marker"
    assert marker["marker_text"] == "Tighten around entry_timing_label"


def test_bill_williams_review_glyph_builds_small_display_carrier() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_glyph_field"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    glyph = build_desktop_journal_view(journal)["session_review_summary"]["review_glyph"]

    assert glyph["glyph_status"] == "tighten_glyph"
    assert glyph["glyph_text"] == "Tighten around entry_timing_label"


def test_bill_williams_review_sigil_builds_small_display_carrier() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_sigil_field"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    sigil = build_desktop_journal_view(journal)["session_review_summary"]["review_sigil"]

    assert sigil["sigil_status"] == "tighten_sigil"
    assert sigil["sigil_text"] == "Tighten around entry_timing_label"


def test_bill_williams_review_seal_builds_small_display_carrier() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_seal_field"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    seal = build_desktop_journal_view(journal)["session_review_summary"]["review_seal"]

    assert seal["seal_status"] == "tighten_seal"
    assert seal["seal_text"] == "Tighten around entry_timing_label"


def test_bill_williams_review_crest_builds_small_display_carrier() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_crest_field"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    crest = build_desktop_journal_view(journal)["session_review_summary"]["review_crest"]

    assert crest["crest_status"] == "tighten_crest"
    assert crest["crest_text"] == "Tighten around entry_timing_label"


def test_bill_williams_review_emblem_builds_small_display_carrier() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_emblem_field"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    emblem = build_desktop_journal_view(journal)["session_review_summary"]["review_emblem"]

    assert emblem["emblem_status"] == "tighten_emblem"
    assert emblem["emblem_text"] == "Tighten around entry_timing_label"


def test_bill_williams_review_insignia_builds_small_display_carrier() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_insignia_field"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    insignia = build_desktop_journal_view(journal)["session_review_summary"]["review_insignia"]

    assert insignia["insignia_status"] == "tighten_insignia"
    assert insignia["insignia_text"] == "Tighten around entry_timing_label"


def test_bill_williams_review_standard_builds_small_display_carrier() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_standard_field"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    standard = build_desktop_journal_view(journal)["session_review_summary"]["review_standard"]

    assert standard["standard_status"] == "tighten_standard"
    assert standard["standard_text"] == "Tighten around entry_timing_label"


def test_bill_williams_review_banner_builds_small_display_carrier() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_banner_field"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    banner = build_desktop_journal_view(journal)["session_review_summary"]["review_banner"]

    assert banner["banner_status"] == "tighten_banner"
    assert banner["banner_text"] == "Tighten around entry_timing_label"


def test_bill_williams_review_pennant_builds_small_display_carrier() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_pennant_field"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    pennant = build_desktop_journal_view(journal)["session_review_summary"]["review_pennant"]

    assert pennant["pennant_status"] == "tighten_pennant"
    assert pennant["pennant_text"] == "Tighten around entry_timing_label"


def test_bill_williams_review_streamer_builds_small_display_carrier() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_streamer_field"))

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        trading.buy_market(volume=1.0)
        session.play()
        session.advance_frame()
        trading.manual_close()
        session.advance_frame()
        journal.create_post_trade_review(**kwargs)

    streamer = build_desktop_journal_view(journal)["session_review_summary"]["review_streamer"]

    assert streamer["streamer_status"] == "tighten_streamer"
    assert streamer["streamer_text"] == "Tighten around entry_timing_label"


def test_import_raw_dataset_builds_normalized_dataset_from_csv() -> None:
    from runtime_bootstrap import import_raw_dataset

    raw_dir = _reset_dir(TMP_ROOT / "raw_import_csv")
    raw_path = raw_dir / "eurusd_raw.csv"
    raw_path.write_text(
        "timestamp,bid,ask,source_id\n"
        "2025-01-02T10:00:01Z,1.10348,1.10360,raw\n"
        "2025-01-02T10:00:00Z,1.10345,1.10357,raw\n"
        "2025-01-02T10:02:30Z,1.10356,1.10368,raw\n",
        encoding="utf-8",
    )

    dataset_dir = import_raw_dataset(
        raw_path,
        raw_dir / "normalized",
        instrument_id="EURUSD",
        price_precision=5,
    )
    dataset = load_normalized_dataset(dataset_dir)

    assert dataset.instrument_id == "EURUSD"
    assert dataset.dataset_start_time == "2025-01-02T10:00:00Z"
    assert dataset.dataset_end_time == "2025-01-02T10:02:30Z"
    assert len(dataset.ticks) == 3
    assert dataset.manifest["warning_count"] == 2
    assert dataset.quality_report["status"] == "accepted_with_warnings"
    assert dataset.quality_report["warning_count"] == 2
    assert dataset.quality_report["warning_preview"] == "repaired_out_of_order_ticks:1, unexpected_gaps:1"
    assert dataset.quality_report["raw_row_count"] == 3
    assert "repaired_out_of_order_ticks:1" in dataset.quality_report["warnings"]
    assert "unexpected_gaps:1" in dataset.quality_report["warnings"]


def test_import_raw_dataset_rejects_inverted_spread_ticks() -> None:
    from runtime_bootstrap import import_raw_dataset
    from runtime_bootstrap.errors import DatasetImportError

    raw_dir = _reset_dir(TMP_ROOT / "raw_import_inverted_spread")
    raw_path = raw_dir / "eurusd_bad.csv"
    raw_path.write_text(
        "timestamp,bid,ask\n"
        "2025-01-02T10:00:00Z,1.10360,1.10345\n",
        encoding="utf-8",
    )

    with pytest.raises(DatasetImportError) as exc_info:
        import_raw_dataset(raw_path, raw_dir / "normalized", instrument_id="EURUSD")

    assert "ask below bid" in str(exc_info.value)


def test_dataset_quality_context_flows_into_trading_and_journal_projections_for_warned_dataset() -> None:
    from runtime_bootstrap import import_raw_dataset

    raw_dir = _reset_dir(TMP_ROOT / "dataset_quality_context_projection")
    raw_path = raw_dir / "eurusd_raw.csv"
    raw_path.write_text(
        "timestamp,bid,ask\n"
        "2025-01-02T10:00:01Z,1.10348,1.10360\n"
        "2025-01-02T10:00:00Z,1.10345,1.10357\n"
        "2025-01-02T10:02:30Z,1.10356,1.10368\n",
        encoding="utf-8",
    )
    dataset_dir = import_raw_dataset(raw_path, raw_dir / "normalized", instrument_id="EURUSD")
    session = create_replay_session(str(dataset_dir), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "dataset_quality_context_projection_state"))

    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()

    replay_view = build_desktop_replay_view(session)
    trading_view = build_desktop_trading_view(trading)
    journal_view = build_desktop_journal_view(journal)

    assert replay_view["dataset_quality"]["context_status"] == "execution_warning_context"
    assert trading_view["dataset_quality_context"]["context_status"] == "execution_warning_context"
    assert trading_view["dataset_quality_context"]["execution_flag_count"] == 2
    assert journal_view["dataset_quality_context"]["context_status"] == "execution_warning_context"
    assert "Dataset warnings remain active: repaired_out_of_order_ticks:1, unexpected_gaps:1." in journal_view["dataset_quality_context"]["context_text"]
    assert "Latest execution context flags: repaired_out_of_order_ticks, unexpected_gap." in journal_view["dataset_quality_context"]["context_text"]


def test_dataset_quality_finalization_link_surfaces_warned_context_at_session_close() -> None:
    from runtime_bootstrap import import_raw_dataset

    raw_dir = _reset_dir(TMP_ROOT / "dataset_quality_finalization_link")
    raw_path = raw_dir / "eurusd_raw.csv"
    raw_path.write_text(
        "timestamp,bid,ask\n"
        "2025-01-02T10:00:01Z,1.10348,1.10360\n"
        "2025-01-02T10:00:00Z,1.10345,1.10357\n"
        "2025-01-02T10:02:30Z,1.10356,1.10368\n",
        encoding="utf-8",
    )
    dataset_dir = import_raw_dataset(raw_path, raw_dir / "normalized", instrument_id="EURUSD")
    session = create_replay_session(str(dataset_dir), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "dataset_quality_finalization_link_state"))

    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    session.pause()
    journal.create_post_trade_review(content="Warned dataset review", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup")
    journal.finalize_session(reason="user_completed")

    finalization = build_desktop_journal_view(journal)["session_finalization"]
    link = finalization["dataset_quality_finalization_link"]

    assert link["link_status"] == "finalized_warned_link"
    assert "session closed with warned dataset context" in link["link_text"]
    assert "Review link: warned dataset context touched this trade through repaired_out_of_order_ticks, unexpected_gap." in link["link_text"]


def test_review_dataset_quality_link_distills_warned_execution_context_into_review_output() -> None:
    from runtime_bootstrap import import_raw_dataset

    raw_dir = _reset_dir(TMP_ROOT / "review_dataset_quality_link")
    raw_path = raw_dir / "eurusd_raw.csv"
    raw_path.write_text(
        "timestamp,bid,ask\n"
        "2025-01-02T10:00:01Z,1.10348,1.10360\n"
        "2025-01-02T10:00:00Z,1.10345,1.10357\n"
        "2025-01-02T10:02:30Z,1.10356,1.10368\n",
        encoding="utf-8",
    )
    dataset_dir = import_raw_dataset(raw_path, raw_dir / "normalized", instrument_id="EURUSD")
    session = create_replay_session(str(dataset_dir), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "review_dataset_quality_link_state"))

    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    journal.create_post_trade_review(content="Warned dataset review", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup")

    journal_view = build_desktop_journal_view(journal)
    latest_link = journal_view["derived_review_output"]["latest_trade_result"]["review_dataset_quality_link"]
    summary_link = journal_view["session_review_summary"]["review_dataset_quality_link"]

    assert latest_link["link_status"] == "warned_execution_review_link"
    assert latest_link["quality_flags"] == ["repaired_out_of_order_ticks"]
    assert latest_link["liquidity_flags"] == ["unexpected_gap"]
    assert latest_link["link_text"] == "Review link: warned dataset context touched this trade through repaired_out_of_order_ticks, unexpected_gap."
    assert summary_link == latest_link


def test_bill_williams_review_discipline_reason_distills_rule_context_and_emblem() -> None:
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, _reset_dir(TMP_ROOT / "bw_review_discipline_reason"))

    journal.create_pre_trade_note(content="Declared fractal long", setup_tag="BW_FRACTAL_LONG")
    trading.buy_market(volume=1.0)
    session.play()
    session.advance_frame()
    trading.manual_close()
    session.advance_frame()
    journal.create_post_trade_review(
        content="Valid setup, weak discipline",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    journal.create_behavioral_flag("premature_exit")
    journal.create_rule_violation("manual_plan_deviation")

    journal_view = build_desktop_journal_view(journal)
    summary_reason = journal_view["session_review_summary"]["review_discipline_reason"]
    latest_reason = journal_view["derived_review_output"]["latest_trade_result"]["review_discipline_reason"]

    assert summary_reason["reason_status"] == "guard_execution_reason"
    assert summary_reason["reason_text"] == (
        "Discipline reason: setup BW_FRACTAL_LONG stayed valid, but execution discipline slipped through "
        "premature_exit, manual_plan_deviation."
    )
    assert latest_reason == summary_reason

def test_dataset_quality_recovery_note_surfaces_after_reopening_finalized_warned_session() -> None:
    from runtime_bootstrap import import_raw_dataset

    raw_dir = _reset_dir(TMP_ROOT / "dataset_quality_recovery_note")
    raw_path = raw_dir / "eurusd_raw.csv"
    raw_path.write_text(
        "timestamp,bid,ask\n"
        "2025-01-02T10:00:01Z,1.10348,1.10360\n"
        "2025-01-02T10:00:00Z,1.10345,1.10357\n"
        "2025-01-02T10:02:30Z,1.10356,1.10368\n",
        encoding="utf-8",
    )
    dataset_dir = import_raw_dataset(raw_path, raw_dir / "normalized", instrument_id="EURUSD")
    storage_dir = _reset_dir(TMP_ROOT / "dataset_quality_recovery_note_state")

    session_1 = create_replay_session(str(dataset_dir), replay_mode="training")
    trading_1 = MinimalTradingLoop(session_1)
    journal_1 = LocalJournalRuntime(session_1, trading_1, storage_dir)

    trading_1.buy_market(volume=1.0)
    session_1.play()
    session_1.advance_frame()
    trading_1.manual_close()
    session_1.advance_frame()
    session_1.pause()
    journal_1.create_post_trade_review(content="Warned dataset review", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup")
    journal_1.finalize_session(reason="user_completed")

    session_2 = create_replay_session(str(dataset_dir), replay_mode="training")
    trading_2 = MinimalTradingLoop(session_2)
    journal_2 = LocalJournalRuntime(session_2, trading_2, storage_dir)

    journal_view = build_desktop_journal_view(journal_2)
    recovery_note = journal_view["dataset_quality_recovery_note"]

    assert journal_2.recovered is True
    assert journal_view["session_finalization"]["is_session_finalized"] is True
    assert recovery_note["note_status"] == "recovered_warned_close_context"
    assert "reopened finalized session still carries warned dataset close context" in recovery_note["note_text"]
    assert "Review link: warned dataset context touched this trade through repaired_out_of_order_ticks, unexpected_gap." in recovery_note["note_text"]


def test_dataset_quality_recovery_acknowledgment_persists_after_restart() -> None:
    from runtime_bootstrap import import_raw_dataset

    raw_dir = _reset_dir(TMP_ROOT / "dataset_quality_recovery_ack")
    raw_path = raw_dir / "eurusd_raw.csv"
    raw_path.write_text(
        "timestamp,bid,ask\n"
        "2025-01-02T10:00:01Z,1.10348,1.10360\n"
        "2025-01-02T10:00:00Z,1.10345,1.10357\n"
        "2025-01-02T10:02:30Z,1.10356,1.10368\n",
        encoding="utf-8",
    )
    dataset_dir = import_raw_dataset(raw_path, raw_dir / "normalized", instrument_id="EURUSD")
    storage_dir = _reset_dir(TMP_ROOT / "dataset_quality_recovery_ack_state")

    session_1 = create_replay_session(str(dataset_dir), replay_mode="training")
    trading_1 = MinimalTradingLoop(session_1)
    journal_1 = LocalJournalRuntime(session_1, trading_1, storage_dir)

    trading_1.buy_market(volume=1.0)
    session_1.play()
    session_1.advance_frame()
    trading_1.manual_close()
    session_1.advance_frame()
    session_1.pause()
    journal_1.create_post_trade_review(content="Warned dataset review", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup")
    journal_1.finalize_session(reason="user_completed")

    session_2 = create_replay_session(str(dataset_dir), replay_mode="training")
    trading_2 = MinimalTradingLoop(session_2)
    journal_2 = LocalJournalRuntime(session_2, trading_2, storage_dir)
    journal_view_2 = build_desktop_journal_view(journal_2)
    recovery_ack_2 = journal_view_2["dataset_quality_recovery_acknowledgment"]

    assert recovery_ack_2["acknowledgment_status"] == "acknowledgment_needed"
    assert recovery_ack_2["status_text"] == "Review the reopened warning before starting a new local session."
    assert recovery_ack_2["acknowledged_at"] is None

    journal_2.acknowledge_recovery_context()
    journal_view_after = build_desktop_journal_view(journal_2)
    recovery_ack_after = journal_view_after["dataset_quality_recovery_acknowledgment"]

    assert recovery_ack_after["acknowledgment_status"] == "acknowledged"
    assert recovery_ack_after["status_text"] == "Reopened warning already reviewed for this session."
    assert recovery_ack_after["acknowledged_at"] is not None

    session_3 = create_replay_session(str(dataset_dir), replay_mode="training")
    trading_3 = MinimalTradingLoop(session_3)
    journal_3 = LocalJournalRuntime(session_3, trading_3, storage_dir)
    recovery_ack_3 = build_desktop_journal_view(journal_3)["dataset_quality_recovery_acknowledgment"]

    assert recovery_ack_3["acknowledgment_status"] == "acknowledged"
    assert recovery_ack_3["acknowledged_at"] == recovery_ack_after["acknowledged_at"]


def test_dataset_quality_recovery_acknowledgment_is_not_exposed_without_warned_recovery_context() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "dataset_quality_recovery_ack_clean")
    session = create_replay_session(str(FIXTURE), replay_mode="training")
    trading = MinimalTradingLoop(session)
    journal = LocalJournalRuntime(session, trading, storage_dir)

    journal_view = build_desktop_journal_view(journal)
    recovery_ack = journal_view["dataset_quality_recovery_acknowledgment"]

    assert recovery_ack["acknowledgment_status"] == "not_applicable"
    assert recovery_ack["status_text"] is None

def test_bill_williams_review_evidence_status_derives_from_review_and_snapshot_context_and_recovers() -> None:
    from runtime_bootstrap import import_raw_dataset

    raw_dir = _reset_dir(TMP_ROOT / "bw_review_evidence_status_dataset")
    raw_path = raw_dir / "eurusd_long.csv"
    raw_path.write_text(
        "timestamp,bid,ask\n"
        "2025-01-02T10:00:00Z,1.10345,1.10357\n"
        "2025-01-02T10:00:01Z,1.10348,1.10360\n"
        "2025-01-02T10:00:02Z,1.10350,1.10362\n"
        "2025-01-02T10:00:03Z,1.10353,1.10365\n"
        "2025-01-02T10:00:04Z,1.10355,1.10367\n"
        "2025-01-02T10:00:05Z,1.10357,1.10369\n"
        "2025-01-02T10:00:06Z,1.10359,1.10371\n"
        "2025-01-02T10:00:07Z,1.10361,1.10373\n",
        encoding="utf-8",
    )
    dataset_dir = import_raw_dataset(raw_path, raw_dir / "normalized", instrument_id="EURUSD")
    storage_dir = _reset_dir(TMP_ROOT / "bw_review_evidence_status_state")

    session_1 = create_replay_session(str(dataset_dir), replay_mode="training")
    trading_1 = MinimalTradingLoop(session_1)
    journal_1 = LocalJournalRuntime(session_1, trading_1, storage_dir)

    pre_snapshot = journal_1.create_chart_snapshot(
        artifact_ref="snapshots/evidence/pre-present.png",
        snapshot_role="pre_entry_context",
    )
    journal_1.create_pre_trade_note(
        content="Evidence-backed note",
        setup_tag="BW_FRACTAL_LONG",
        chart_snapshot_ref=pre_snapshot.snapshot_id,
    )
    trading_1.buy_market(volume=1.0)
    session_1.play()
    session_1.advance_frame()
    trading_1.manual_close()
    session_1.advance_frame()
    review_snapshot = journal_1.create_chart_snapshot(
        artifact_ref="snapshots/evidence/review-present.png",
        snapshot_role="review_context",
    )
    journal_1.create_post_trade_review(
        content="Evidence-backed review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
        chart_snapshot_refs=(review_snapshot.snapshot_id,),
    )

    trading_1.buy_market(volume=1.0)
    session_1.advance_frame()
    trading_1.manual_close()
    session_1.advance_frame()
    journal_1.create_post_trade_review(
        content="Review without chart evidence",
        setup_tag="BW_1WM_LONG",
        compliance_label="valid_setup",
    )

    partial_snapshot = journal_1.create_chart_snapshot(
        artifact_ref="snapshots/evidence/pre-partial.png",
        snapshot_role="pre_entry_context",
    )
    journal_1.create_pre_trade_note(
        content="Partial evidence note",
        setup_tag="BW_2WM_LONG",
        chart_snapshot_ref=partial_snapshot.snapshot_id,
    )
    trading_1.buy_market(volume=1.0)
    session_1.advance_frame()
    trading_1.manual_close()
    session_1.advance_frame()
    journal_1.create_post_trade_review(
        content="Review with only pre-trade evidence",
        setup_tag="BW_2WM_LONG",
        compliance_label="valid_setup",
    )

    journal_view_1 = build_desktop_journal_view(journal_1)
    trade_results_1 = journal_view_1["derived_review_output"]["trade_results"]
    summary_1 = journal_view_1["session_review_summary"]

    assert [result["bill_williams_review_evidence_status"] for result in trade_results_1] == [
        "linked_evidence_present",
        "linked_evidence_missing",
        "linked_evidence_partial",
    ]
    assert [result["bill_williams_review_evidence_follow_up_status"] for result in trade_results_1] == [
        "follow_up_not_needed",
        "link_any_chart_evidence",
        "link_review_snapshot",
    ]
    assert trade_results_1[0]["bill_williams_review_evidence_text"] == "Bill Williams review is backed by linked chart context."
    assert trade_results_1[1]["bill_williams_review_evidence_text"] == "Bill Williams review is filled, but no linked chart evidence is attached yet."
    assert trade_results_1[2]["bill_williams_review_evidence_text"] == (
        "Bill Williams review has partial chart evidence; still missing review context."
    )
    assert trade_results_1[0]["bill_williams_review_evidence_follow_up_text"] is None
    assert trade_results_1[1]["bill_williams_review_evidence_follow_up_text"] == (
        "Link a pre-trade or review chart snapshot to back this Bill Williams review."
    )
    assert trade_results_1[2]["bill_williams_review_evidence_follow_up_text"] == (
        "Link a review-context snapshot to complete the Bill Williams review evidence."
    )
    assert trade_results_1[0]["has_bill_williams_review_evidence"] is True
    assert trade_results_1[1]["has_bill_williams_review_evidence"] is False
    assert trade_results_1[2]["has_bill_williams_review_evidence"] is False
    assert summary_1["reviewed_trades_with_bw_evidence_count"] == 1
    assert summary_1["reviewed_trades_missing_bw_evidence_count"] == 2
    assert summary_1["reviewed_trades_requiring_bw_evidence_follow_up_count"] == 2
    assert summary_1["latest_bill_williams_review_evidence_status"] == "linked_evidence_partial"
    assert summary_1["latest_bill_williams_review_evidence_text"] == (
        "Bill Williams review has partial chart evidence; still missing review context."
    )
    assert summary_1["latest_bill_williams_review_evidence_follow_up_status"] == "link_review_snapshot"
    assert summary_1["latest_bill_williams_review_evidence_follow_up_text"] == (
        "Link a review-context snapshot to complete the Bill Williams review evidence."
    )

    session_2 = create_replay_session(str(dataset_dir), replay_mode="training")
    trading_2 = MinimalTradingLoop(session_2)
    journal_2 = LocalJournalRuntime(session_2, trading_2, storage_dir)
    journal_view_2 = build_desktop_journal_view(journal_2)
    trade_results_2 = journal_view_2["derived_review_output"]["trade_results"]
    summary_2 = journal_view_2["session_review_summary"]

    assert [result["bill_williams_review_evidence_status"] for result in trade_results_2] == [
        "linked_evidence_present",
        "linked_evidence_missing",
        "linked_evidence_partial",
    ]
    assert [result["bill_williams_review_evidence_follow_up_status"] for result in trade_results_2] == [
        "follow_up_not_needed",
        "link_any_chart_evidence",
        "link_review_snapshot",
    ]
    assert summary_2["reviewed_trades_with_bw_evidence_count"] == 1
    assert summary_2["reviewed_trades_missing_bw_evidence_count"] == 2
    assert summary_2["reviewed_trades_requiring_bw_evidence_follow_up_count"] == 2
    assert summary_2["latest_bill_williams_review_evidence_status"] == "linked_evidence_partial"
    assert summary_2["latest_bill_williams_review_evidence_text"] == (
        "Bill Williams review has partial chart evidence; still missing review context."
    )
    assert summary_2["latest_bill_williams_review_evidence_follow_up_status"] == "link_review_snapshot"
    assert summary_2["latest_bill_williams_review_evidence_follow_up_text"] == (
        "Link a review-context snapshot to complete the Bill Williams review evidence."
    )
