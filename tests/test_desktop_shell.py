from __future__ import annotations

import shutil
import subprocess

import pytest
import sys
from pathlib import Path

from desktop_shell import (
    DesktopLaunchConfig,
    DesktopReadinessSnapshot,
    MVPPausePointSnapshot,
    DesktopShellController,
    build_action_feedback_lines,
    build_primary_workflow_snapshot_lines,
    build_alligator_lines,
    build_ao_histogram_segments,
    build_ao_values,
    build_bar_segments,
    build_chart_visual_summary,
    build_primary_chart_footer_lines,
    build_fractal_markers,
    build_authoring_status_lines,
    build_button_state_map,
    build_compact_context_lines,
    build_control_hint_lines,
    build_controller_from_launch_config,
    build_controller_from_start_selection,
    build_default_launch_config,
    build_start_flow_options,
    build_finalization_blocker_lines,
    build_finalization_lines,
    build_history_status_lines,
    build_latest_result_lines,
    build_latest_trade_result_lines,
    build_mid_price_line_points,
    build_overlay_line_points,
    build_price_bar_model,
    build_main_screen_layout_spec,
    build_mvp_pause_point_snapshot,
    build_note_section_lines,
    build_readiness_snapshot,
    format_mvp_pause_point_report,
    build_replay_header_lines,
    build_review_entry_lines,
    build_workspace_bar_lines,
    format_readiness_report,
    build_review_section_lines,
    build_review_summary_lines,
    build_session_context_lines,
    build_tick_table_lines,
    build_timeline_preview_lines,
    build_trade_context_lines,
    build_workflow_guidance_lines,
    flatten_canvas_points,
    get_behavioral_flag_options,
    mvp_pause_point_to_json,
    readiness_snapshot_to_json,
    get_compliance_label_options,
    get_entry_timing_options,
    get_exit_quality_options,
    get_market_context_options,
    get_review_clarity_options,
    get_rule_violation_options,
    get_setup_tag_options,
    get_setup_variant_options,
    has_local_session_state,
    parse_launch_args,
    resolve_start_selection,
    run_mvp_pause_point_report,
    run_readiness_report,
)

FIXTURE = Path("runtime_bootstrap/fixtures/eurusd_sample")
TMP_ROOT = Path("tests/.tmp_desktop_shell")


def _reset_dir(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


def test_desktop_shell_launch_helpers_build_predictable_local_entry_config() -> None:
    default_config = build_default_launch_config(project_root=Path.cwd())
    assert default_config.dataset_handle.endswith("runtime_bootstrap\\fixtures\\eurusd_sample")
    assert default_config.storage_dir == Path.cwd() / "desktop_shell" / ".local_state"
    assert default_config.replay_mode == "training"

    parsed = parse_launch_args(
        argv=["--dataset", str(FIXTURE), "--storage", str(TMP_ROOT / "launch_storage"), "--mode", "exam"],
        project_root=Path.cwd(),
    )
    assert isinstance(parsed, DesktopLaunchConfig)
    assert parsed.dataset_handle == str(FIXTURE)
    assert parsed.storage_dir == TMP_ROOT / "launch_storage"
    assert parsed.replay_mode == "exam"

    controller = build_controller_from_launch_config(
        DesktopLaunchConfig(
            dataset_handle=str(FIXTURE),
            storage_dir=_reset_dir(TMP_ROOT / "launch_controller"),
            replay_mode="training",
        )
    )
    workspace = controller.get_workspace_view()
    assert isinstance(controller, DesktopShellController)
    assert workspace["replay"]["dataset_id"] == "eurusd-sample-v1"


def test_desktop_shell_start_flow_options_are_explicit_and_resume_is_not_implicit() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "startup_options")
    config = DesktopLaunchConfig(dataset_handle=str(FIXTURE), storage_dir=storage_dir, replay_mode="training")

    options_without_resume = build_start_flow_options(config)
    assert [option.label for option in options_without_resume] == [
        "Open prepared dataset",
        "Import raw historical data",
        "Start new session",
        "Resume last local session",
    ]
    assert options_without_resume[-1].enabled is False
    assert any("clean local session" in option.detail.lower() for option in options_without_resume[:2])

    DesktopShellController(dataset_handle=FIXTURE, storage_dir=storage_dir)
    assert has_local_session_state(storage_dir) is True
    options_with_resume = build_start_flow_options(config)
    assert options_with_resume[-1].enabled is True
    assert "Resume the last local session" in options_with_resume[-1].detail


def test_desktop_shell_launch_entrypoints_expose_help() -> None:
    result_module = subprocess.run(
        [sys.executable, "-m", "desktop_shell", "--help"],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )
    result_script = subprocess.run(
        [sys.executable, "run_desktop_shell.py", "--help"],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )
    result_gui_script = subprocess.run(
        [sys.executable, "run_desktop_shell_gui.py", "--help"],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result_module.returncode == 0
    assert result_script.returncode == 0
    assert result_gui_script.returncode == 0
    assert "Trader Trainer desktop shell" in result_module.stdout
    assert "--dataset" in result_module.stdout
    assert "Trader Trainer desktop shell" in result_script.stdout
    assert "--storage" in result_script.stdout
    assert "Trader Trainer desktop shell" in result_gui_script.stdout
    assert "--dataset" in result_gui_script.stdout


def test_desktop_shell_readiness_helpers_build_handoff_snapshot_and_report() -> None:
    config = DesktopLaunchConfig(
        dataset_handle=str(FIXTURE),
        storage_dir=_reset_dir(TMP_ROOT / "readiness_storage"),
        replay_mode="training",
    )
    snapshot = build_readiness_snapshot(config)
    report = format_readiness_report(snapshot)
    json_payload = readiness_snapshot_to_json(snapshot)

    assert isinstance(snapshot, DesktopReadinessSnapshot)
    assert snapshot.replay_status == "paused"
    assert snapshot.dataset_quality_status == "accepted"
    assert snapshot.import_warning_count == 0
    assert snapshot.summary_status == "no_closed_trades"
    assert "Desktop readiness" in report
    assert "Dataset quality: accepted" in report
    assert "python run_desktop_shell_gui.py" in report
    assert '"replay_status": "paused"' in json_payload

def test_desktop_shell_readiness_entrypoint_outputs_report() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "readiness_entrypoint")
    output = run_readiness_report(
        argv=["--dataset", str(FIXTURE), "--storage", str(storage_dir), "--mode", "training"]
    )
    output_json = run_readiness_report(
        argv=["--dataset", str(FIXTURE), "--storage", str(storage_dir), "--mode", "training", "--json"]
    )
    script_result = subprocess.run(
        [sys.executable, "print_desktop_readiness.py", "--dataset", str(FIXTURE), "--storage", str(storage_dir), "--mode", "training"],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert "Desktop readiness" in output
    assert '"replay_status": "paused"' in output_json
    assert script_result.returncode == 0
    assert "Desktop readiness" in script_result.stdout


def test_desktop_shell_pause_point_helpers_build_mvp_freeze_report() -> None:
    config = DesktopLaunchConfig(
        dataset_handle=str(FIXTURE),
        storage_dir=_reset_dir(TMP_ROOT / "pause_point_storage"),
        replay_mode="training",
    )
    snapshot = build_mvp_pause_point_snapshot(config)
    report = format_mvp_pause_point_report(snapshot)
    json_payload = mvp_pause_point_to_json(snapshot)

    assert isinstance(snapshot, MVPPausePointSnapshot)
    assert snapshot.mvp_status == "accepted"
    assert snapshot.desktop_status == "usable"
    assert "MVP pause point" in report
    assert "desktop remains thin projection consumer" in report
    assert '"mvp_status": "accepted"' in json_payload


def test_desktop_shell_pause_point_entrypoint_outputs_report() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "pause_point_entrypoint")
    output = run_mvp_pause_point_report(
        argv=["--dataset", str(FIXTURE), "--storage", str(storage_dir), "--mode", "training"]
    )
    output_json = run_mvp_pause_point_report(
        argv=["--dataset", str(FIXTURE), "--storage", str(storage_dir), "--mode", "training", "--json"]
    )
    script_result = subprocess.run(
        [sys.executable, "print_mvp_pause_point.py", "--dataset", str(FIXTURE), "--storage", str(storage_dir), "--mode", "training"],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert "MVP pause point" in output
    assert '"desktop_status": "usable"' in output_json
    assert script_result.returncode == 0
    assert "MVP pause point" in script_result.stdout


def test_desktop_shell_controller_bootstraps_workspace_views() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "bootstrap"),
    )

    workspace = controller.get_workspace_view()

    assert workspace["replay"]["dataset_id"] == "eurusd-sample-v1"
    assert workspace["replay"]["status"] == "paused"
    assert workspace["trading"]["active_trade_present"] is False
    assert workspace["journal"]["session_status"] in {"created", "paused"}
    assert workspace["journal"]["session_review_summary"]["summary_status"] == "no_closed_trades"


def test_desktop_shell_chart_surface_helpers_build_mandatory_bill_williams_boundary() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "chart_helpers"),
    )
    controller.play()
    for _ in range(40):
        controller.advance_frame()
    replay_view = controller.get_workspace_view()["replay"]
    chart_context = replay_view["chart_context"]

    header_lines = build_replay_header_lines(replay_view)
    footer_lines = build_tick_table_lines(chart_context, limit=3)
    bars = build_price_bar_model(chart_context["recent_points"])
    alligator = build_alligator_lines(bars)
    fractals = build_fractal_markers(bars)
    ao_values = build_ao_values(bars)
    bar_segments = build_bar_segments(bars, width=640, height=320)
    overlay_points = build_overlay_line_points(alligator["jaw"], width=640, height=320, low=min(float(bar["low"]) for bar in bars), high=max(float(bar["high"]) for bar in bars))
    ao_segments = build_ao_histogram_segments(ao_values, width=640, height=120)
    visual_summary = build_chart_visual_summary(chart_context)

    assert header_lines[0] == "Instrument: EURUSD"
    assert any(line.startswith("Simulation time:") for line in header_lines)
    assert footer_lines[0] == "Recent bars:"
    assert len(bars) >= 4
    assert all(set(bar.keys()) >= {"open", "high", "low", "close", "median"} for bar in bars)
    assert len(bar_segments) == len(bars)
    assert all(segment["high_y"] <= segment["low_y"] for segment in bar_segments)
    assert len(alligator["jaw"]) == len(bars)
    assert len(alligator["teeth"]) == len(bars)
    assert len(alligator["lips"]) == len(bars)
    assert any(value is not None for value in alligator["jaw"])
    assert any(value is not None for value in alligator["teeth"])
    assert any(value is not None for value in alligator["lips"])
    assert isinstance(fractals["up"], list)
    assert isinstance(fractals["down"], list)
    assert len(ao_values) == len(bars)
    assert len(ao_segments) == len(ao_values)
    assert overlay_points
    assert any(line == "Bars: {} | Mode: bar chart only".format(len(bars)) for line in visual_summary)
    assert any(line.startswith("AO pane:") for line in visual_summary)
    assert all("Replay trace" not in line for line in visual_summary)


def test_desktop_shell_context_surface_helpers_build_readable_blocks() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "context_helpers"),
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Context review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    workspace = controller.finalize_session()

    session_lines = build_session_context_lines(workspace["journal"])
    trade_lines = build_trade_context_lines(workspace["trading"])
    review_lines = build_review_summary_lines(workspace["journal"])
    finalization_lines = build_finalization_lines(workspace["journal"])
    latest_result_lines = build_latest_result_lines(workspace["journal"])

    assert session_lines[0].startswith("Session: ")
    assert any(line == "Finalization: finalized" for line in session_lines)
    assert any(line == "Trade status: closed" for line in trade_lines)
    assert any(line == "Summary status: finalized_review_complete" for line in review_lines)
    assert any(line == "Finalized: yes" for line in finalization_lines)
    assert any(line.startswith("Latest trade: trade-") for line in latest_result_lines)


def test_desktop_shell_authoring_helpers_expose_status_and_vocab() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "authoring_helpers"),
    )
    controller.create_pre_trade_note(
        content="Authoring note",
        setup_tag="BW_FRACTAL_LONG",
        thesis_summary="breakout continuation",
        risk_plan="manual close on weakness",
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Facet helper review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
        setup_variant="fractal_breakout",
        entry_timing_label="timely_entry",
        market_context_label="clean_context",
        exit_quality_label="disciplined_exit",
        review_clarity_label="high_clarity",
    )

    journal_view = controller.get_workspace_view()["journal"]
    authoring_lines = build_authoring_status_lines(journal_view)
    note_lines = build_note_section_lines(journal_view)
    review_lines = build_review_section_lines(journal_view)

    assert get_setup_tag_options()[0].startswith("BW_")
    assert "valid_setup" in get_compliance_label_options()
    assert "fractal_breakout" in get_setup_variant_options()
    assert "timely_entry" in get_entry_timing_options()
    assert "clean_context" in get_market_context_options()
    assert "disciplined_exit" in get_exit_quality_options()
    assert "high_clarity" in get_review_clarity_options()
    assert "premature_exit" in get_behavioral_flag_options()
    assert "manual_plan_deviation" in get_rule_violation_options()
    assert any(line.startswith("Latest method facets filled: 5/5") for line in authoring_lines)
    assert any(line.startswith("Last note id: note-") for line in note_lines)
    assert any("fractal_breakout" in line for line in review_lines)
    assert any("disciplined_exit / high_clarity" in line for line in review_lines)




def test_desktop_shell_review_depth_facets_flow_into_result_helpers() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_depth_helpers"),
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Desktop depth review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
        setup_variant="fractal_breakout",
        entry_timing_label="slightly_late_entry",
        market_context_label="acceptable_context",
        exit_quality_label="slightly_early_exit",
        review_clarity_label="medium_clarity",
    )

    journal_view = controller.get_workspace_view()["journal"]
    latest_result_lines = build_latest_result_lines(journal_view)
    history_lines = build_latest_trade_result_lines(journal_view)
    summary_lines = build_review_summary_lines(journal_view)

    assert any("Variant: fractal_breakout" == line for line in latest_result_lines)
    assert any("Entry/context: slightly_late_entry / acceptable_context" == line for line in latest_result_lines)
    assert any("Exit/clarity: slightly_early_exit / medium_clarity" == line for line in latest_result_lines)
    assert any("Variant: fractal_breakout" == line for line in history_lines)
    assert any("Method-facet trades: 1" == line for line in summary_lines)




def test_desktop_shell_review_delta_helpers_surface_declared_vs_reviewed_intent() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_delta_helpers"),
    )
    controller.create_pre_trade_note(
        content="Declared fractal long",
        setup_tag="BW_FRACTAL_LONG",
        thesis_summary="fractal breakout",
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Reviewed as same setup with refinement",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
        setup_variant="fractal_breakout",
        entry_timing_label="timely_entry",
    )

    journal_view = controller.get_workspace_view()["journal"]
    latest_result_lines = build_latest_result_lines(journal_view)
    history_lines = build_latest_trade_result_lines(journal_view)
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)

    assert any("Intent delta: intent_refined" == line for line in latest_result_lines)
    assert any("Declared/reviewed: BW_FRACTAL_LONG / BW_FRACTAL_LONG" == line for line in latest_result_lines)
    assert any("Intent delta: intent_refined" == line for line in history_lines)
    assert any("Declared / reviewed: BW_FRACTAL_LONG / BW_FRACTAL_LONG" == line for line in history_lines)
    assert any("Latest intent delta: intent_refined" == line for line in summary_lines)
    assert any("Intent confirmed/refined/changed: 0 / 1 / 0" == line for line in summary_lines)
    assert any("Intent confirmed/refined/changed: 0 / 1 / 0" == line for line in status_lines)




def test_desktop_shell_review_completeness_helpers_surface_missing_parts() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_completeness_helpers"),
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Partial desktop review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
        entry_timing_label="timely_entry",
    )

    journal_view = controller.get_workspace_view()["journal"]
    latest_result_lines = build_latest_result_lines(journal_view)
    history_lines = build_latest_trade_result_lines(journal_view)
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)

    assert any("Review completeness: partial (3/6)" == line for line in latest_result_lines)
    assert any("Missing review parts: market_context_label, exit_quality_label, review_clarity_label" == line for line in latest_result_lines)
    assert any("Review completeness: partial (3/6)" == line for line in history_lines)
    assert any("Missing parts: market_context_label, exit_quality_label, review_clarity_label" == line for line in history_lines)
    assert any("Latest completeness: partial" == line for line in summary_lines)
    assert any("Latest missing review parts: market_context_label, exit_quality_label, review_clarity_label" == line for line in summary_lines)
    assert any("Review complete/partial/sparse: 0 / 1 / 0" == line for line in status_lines)




def test_desktop_shell_review_coverage_helpers_surface_session_level_field_coverage() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_coverage_helpers"),
    )

    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Complete review one",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
        entry_timing_label="timely_entry",
        market_context_label="clean_context",
        exit_quality_label="disciplined_exit",
        review_clarity_label="high_clarity",
    )

    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Partial review two",
        setup_tag="BW_1WM_LONG",
        compliance_label="valid_setup",
        entry_timing_label="timely_entry",
    )

    journal_view = controller.get_workspace_view()["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)

    assert any("Coverage setup/compliance: 2/2 / 2/2" == line for line in summary_lines)
    assert any("Coverage entry/context: 2/2 / 1/2" == line for line in summary_lines)
    assert any("Coverage exit/clarity: 1/2 / 1/2" == line for line in summary_lines)
    assert any("Coverage setup/compliance: 2/2 / 2/2" == line for line in status_lines)
    assert any("Coverage entry/context: 2/2 / 1/2" == line for line in status_lines)


def test_desktop_shell_history_helpers_expose_current_session_result_and_timeline() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "history_helpers"),
    )
    controller.create_pre_trade_note(
        content="History note",
        setup_tag="BW_FRACTAL_LONG",
        thesis_summary="breakout continuation",
        risk_plan="manual close on weakness",
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="History review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )

    journal_view = controller.get_workspace_view()["journal"]
    status_lines = build_history_status_lines(journal_view)
    result_lines = build_latest_trade_result_lines(journal_view)
    timeline_lines = build_timeline_preview_lines(journal_view, limit=4)

    assert any(line == "Closed trades: 1" for line in status_lines)
    assert any(line.startswith("Latest timeline event: ") for line in status_lines)
    assert result_lines[0].startswith("Latest trade: trade-")
    assert any("valid_setup" in line for line in result_lines)
    assert timeline_lines[0].startswith("Timeline items: ")
    assert any("Post-trade review" in line for line in timeline_lines[1:])


def test_desktop_shell_workflow_helpers_surface_guidance_blockers_and_feedback() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "workflow_helpers"),
    )

    workspace = controller.get_workspace_view()
    guidance_lines = build_workflow_guidance_lines(workspace["replay"], workspace["trading"], workspace["journal"])
    blocker_lines = build_finalization_blocker_lines(workspace["journal"])
    feedback_lines = build_action_feedback_lines(
        {"level": "info", "summary": "Desktop shell ready", "detail": "Initial projections loaded."}
    )

    assert guidance_lines[0] == "Workflow guidance:"
    assert any("PreTradeNote" in line or "open a trade" in line for line in guidance_lines[1:])
    assert blocker_lines[0] == "Finalization blockers:"
    assert any("No blockers" in line for line in blocker_lines[1:])
    assert feedback_lines[1] == "INFO: Desktop shell ready"

    controller.create_pre_trade_note(
        content="Declared fractal plan",
        setup_tag="BW_FRACTAL_LONG",
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    pending_workspace = controller.get_workspace_view()
    pending_guidance = build_workflow_guidance_lines(
        pending_workspace["replay"],
        pending_workspace["trading"],
        pending_workspace["journal"],
    )
    pending_blockers = build_finalization_blocker_lines(pending_workspace["journal"])

    assert any("Add PostTradeReview" in line for line in pending_guidance)
    assert any("Start by confirming reviewed setup and compliance" in line for line in pending_guidance)
    assert any("Force Finalize" in line for line in pending_guidance)
    assert any("Pending reviews:" in line for line in pending_blockers)
    assert any("Force finalize available: yes" == line for line in pending_blockers)




def test_desktop_shell_review_prompt_guidance_surfaces_next_missing_parts() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_prompt_guidance"),
    )
    controller.create_pre_trade_note(
        content="Declared first wise man idea",
        setup_tag="BW_1WM_LONG",
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Changed interpretation with sparse review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )

    workspace = controller.get_workspace_view()
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        workspace["journal"],
    )

    assert any("Explain why the reviewed setup differs from the declared pre-trade intent." == line for line in guidance_lines)
    assert any("Next missing review parts: entry_timing_label, market_context_label, exit_quality_label, review_clarity_label" == line for line in guidance_lines)


def test_desktop_shell_control_helpers_surface_availability_map() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "control_helpers"),
    )
    initial_workspace = controller.get_workspace_view()
    initial_map = build_button_state_map(
        initial_workspace["replay"],
        initial_workspace["trading"],
        initial_workspace["journal"],
    )
    initial_lines = build_control_hint_lines(initial_map)

    assert initial_map["play"] is True
    assert initial_map["pause"] is False
    assert initial_map["buy"] is True
    assert initial_map["buy_stop"] is True
    assert initial_map["sell_stop"] is True
    assert initial_map["cancel_entry"] is False
    assert initial_map["close"] is False
    assert initial_map["add_review"] is False
    assert initial_map["finalize"] is True
    assert initial_lines[0] == "Control availability:"

    controller.buy_market()
    controller.play()
    controller.advance_frame()
    active_workspace = controller.get_workspace_view()
    active_map = build_button_state_map(
        active_workspace["replay"],
        active_workspace["trading"],
        active_workspace["journal"],
    )
    assert active_map["play"] is False
    assert active_map["pause"] is True
    assert active_map["buy"] is False
    assert active_map["buy_stop"] is False
    assert active_map["cancel_entry"] is False
    assert active_map["close"] is True
    assert active_map["finalize"] is False

    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    pending_workspace = controller.get_workspace_view()
    pending_map = build_button_state_map(
        pending_workspace["replay"],
        pending_workspace["trading"],
        pending_workspace["journal"],
    )
    assert pending_map["add_review"] is True
    assert pending_map["finalize"] is False
    assert pending_map["force_finalize"] is True


def test_desktop_shell_mvp_acceptance_smoke_pass() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "desktop_acceptance")

    controller_1 = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=storage_dir,
    )
    workspace_0 = controller_1.get_workspace_view()
    assert workspace_0["replay"]["status"] == "paused"
    assert workspace_0["trading"]["active_trade_present"] is False
    assert workspace_0["journal"]["session_review_summary"]["summary_status"] == "no_closed_trades"

    controller_1.create_pre_trade_note(
        content="Acceptance note",
        setup_tag="BW_FRACTAL_LONG",
        thesis_summary="breakout continuation",
        risk_plan="manual close on weakness",
    )
    pre_trade_workspace = controller_1.get_workspace_view()
    pre_trade_controls = build_button_state_map(
        pre_trade_workspace["replay"],
        pre_trade_workspace["trading"],
        pre_trade_workspace["journal"],
    )
    assert pre_trade_controls["buy"] is True
    assert pre_trade_controls["add_note"] is True

    controller_1.buy_market()
    controller_1.play()
    controller_1.advance_frame()
    active_workspace = controller_1.get_workspace_view()
    active_guidance = build_workflow_guidance_lines(
        active_workspace["replay"],
        active_workspace["trading"],
        active_workspace["journal"],
    )
    active_controls = build_button_state_map(
        active_workspace["replay"],
        active_workspace["trading"],
        active_workspace["journal"],
    )
    assert active_workspace["trading"]["active_trade_present"] is True
    assert active_controls["close"] is True
    assert any("Active trade is open" in line for line in active_guidance)

    controller_1.manual_close()
    controller_1.advance_frame()
    controller_1.pause()
    pending_workspace = controller_1.get_workspace_view()
    pending_guidance = build_workflow_guidance_lines(
        pending_workspace["replay"],
        pending_workspace["trading"],
        pending_workspace["journal"],
    )
    pending_controls = build_button_state_map(
        pending_workspace["replay"],
        pending_workspace["trading"],
        pending_workspace["journal"],
    )
    assert pending_workspace["journal"]["session_review_summary"]["summary_status"] == "review_pending"
    assert pending_controls["add_review"] is True
    assert pending_controls["finalize"] is False
    assert pending_controls["force_finalize"] is True
    assert any("Add PostTradeReview" in line for line in pending_guidance)

    controller_1.create_post_trade_review(
        content="Acceptance review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    controller_1.create_behavioral_flag("premature_exit")
    controller_1.create_rule_violation("manual_plan_deviation")
    reviewed_workspace = controller_1.get_workspace_view()
    latest_result_lines = build_latest_trade_result_lines(reviewed_workspace["journal"])
    history_lines = build_history_status_lines(reviewed_workspace["journal"])
    reviewed_controls = build_button_state_map(
        reviewed_workspace["replay"],
        reviewed_workspace["trading"],
        reviewed_workspace["journal"],
    )
    assert any("valid_setup" in line for line in latest_result_lines)
    assert any(line == "Closed trades: 1" for line in history_lines)
    assert reviewed_controls["finalize"] is True

    finalized_workspace = controller_1.finalize_session()
    finalized_guidance = build_workflow_guidance_lines(
        finalized_workspace["replay"],
        finalized_workspace["trading"],
        finalized_workspace["journal"],
    )
    finalized_controls = build_button_state_map(
        finalized_workspace["replay"],
        finalized_workspace["trading"],
        finalized_workspace["journal"],
    )
    assert finalized_workspace["journal"]["session_finalization"]["is_session_finalized"] is True
    assert finalized_workspace["journal"]["session_review_summary"]["summary_status"] == "finalized_review_complete"
    assert all(enabled is False for enabled in finalized_controls.values())
    assert any("Session finalized" in line for line in finalized_guidance)

    controller_2 = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=storage_dir,
    )
    recovered_workspace = controller_2.get_workspace_view()
    recovered_latest_result_lines = build_latest_trade_result_lines(recovered_workspace["journal"])
    recovered_history_lines = build_history_status_lines(recovered_workspace["journal"])
    assert recovered_workspace["journal"]["recovered"] is True
    assert recovered_workspace["journal"]["session_finalization"]["is_session_finalized"] is True
    assert recovered_workspace["journal"]["session_review_summary"]["summary_status"] == "finalized_review_complete"
    assert any("valid_setup" in line for line in recovered_latest_result_lines)
    assert any(line == "Closed trades: 1" for line in recovered_history_lines)


def test_desktop_shell_controller_runs_and_recovers_mvp_flow() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "mvp_flow")

    controller_1 = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=storage_dir,
    )
    controller_1.create_pre_trade_note(
        content="Desktop shell note",
        setup_tag="BW_FRACTAL_LONG",
        thesis_summary="breakout continuation",
        risk_plan="manual close on weakness",
    )
    controller_1.buy_market()
    controller_1.play()
    controller_1.advance_frame()
    controller_1.manual_close()
    controller_1.advance_frame()
    controller_1.pause()
    controller_1.create_post_trade_review(
        content="Desktop shell review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    controller_1.create_behavioral_flag("premature_exit")
    controller_1.create_rule_violation("manual_plan_deviation")
    workspace_1 = controller_1.finalize_session()

    assert workspace_1["journal"]["session_finalization"]["is_session_finalized"] is True
    assert workspace_1["journal"]["session_review_summary"]["summary_status"] == "finalized_review_complete"

    controller_2 = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=storage_dir,
    )
    workspace_2 = controller_2.get_workspace_view()

    assert workspace_2["journal"]["recovered"] is True
    assert workspace_2["replay"]["simulation_time"] == "2025-01-02T10:00:03Z"
    assert workspace_2["trading"]["trade_status"] == "closed"
    assert workspace_2["journal"]["post_trade_review_count"] == 1
    assert workspace_2["journal"]["behavioral_flag_count"] == 1
    assert workspace_2["journal"]["rule_violation_count"] == 1
    assert workspace_2["journal"]["session_review_summary"]["summary_status"] == "finalized_review_complete"


def test_desktop_shell_review_rule_context_helpers_surface_method_discipline_link() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_rule_context_helpers"),
    )
    controller.create_pre_trade_note(
        content="Declared fractal plan",
        setup_tag="BW_FRACTAL_LONG",
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Rule context helper review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    controller.create_behavioral_flag("premature_exit")
    controller.create_rule_violation("manual_plan_deviation")

    journal_view = controller.get_workspace_view()["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    latest_result_lines = build_latest_result_lines(journal_view)
    history_lines = build_latest_trade_result_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        controller.get_workspace_view()["replay"],
        controller.get_workspace_view()["trading"],
        journal_view,
    )

    expected = "Reviewed setup BW_FRACTAL_LONG stayed valid, but discipline slipped through premature_exit, manual_plan_deviation."
    assert any("Review rule context: valid_setup_discipline_break" == line for line in summary_lines)
    assert any(f"Rule context text: {expected}" == line for line in summary_lines)
    assert any("Rule context: valid_setup_discipline_break" == line for line in latest_result_lines)
    assert any(f"Rule context text: {expected}" == line for line in latest_result_lines)
    assert any("Rule context: valid_setup_discipline_break" == line for line in history_lines)
    assert any(f"Rule context text: {expected}" == line for line in history_lines)
    assert any("Review rule context: valid_setup_discipline_break" == line for line in status_lines)
    assert any(expected == line for line in guidance_lines)


def test_desktop_shell_review_discipline_cue_helpers_surface_compact_method_guard() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_discipline_cue_helpers"),
    )
    controller.create_pre_trade_note(
        content="Declared fractal plan",
        setup_tag="BW_FRACTAL_LONG",
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Discipline cue helper review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    controller.create_behavioral_flag("premature_exit")
    controller.create_rule_violation("manual_plan_deviation")

    journal_view = controller.get_workspace_view()["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        controller.get_workspace_view()["replay"],
        controller.get_workspace_view()["trading"],
        journal_view,
    )

    expected = "Discipline cue: protect execution discipline around an otherwise valid setup."
    assert any("Review discipline cue: discipline_guard_up" == line for line in summary_lines)
    assert any(f"Discipline cue text: {expected}" == line for line in summary_lines)
    assert any("Review discipline cue: discipline_guard_up" == line for line in status_lines)
    assert any(expected == line for line in guidance_lines)


def test_desktop_shell_review_discipline_badge_helpers_surface_compact_marker() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_discipline_badge_helpers"),
    )
    controller.create_pre_trade_note(
        content="Declared fractal plan",
        setup_tag="BW_FRACTAL_LONG",
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Discipline badge helper review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    controller.create_behavioral_flag("premature_exit")
    controller.create_rule_violation("manual_plan_deviation")

    journal_view = controller.get_workspace_view()["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        controller.get_workspace_view()["replay"],
        controller.get_workspace_view()["trading"],
        journal_view,
    )

    expected = "Discipline badge: Guard execution."
    assert any("Review discipline badge: guarded_badge" == line for line in summary_lines)
    assert any(f"Discipline badge text: {expected}" == line for line in summary_lines)
    assert any("Review discipline badge: guarded_badge" == line for line in status_lines)
    assert any(expected == line for line in guidance_lines)


def test_desktop_shell_review_discipline_token_helpers_surface_compact_token() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_discipline_token_helpers"),
    )
    controller.create_pre_trade_note(
        content="Declared fractal plan",
        setup_tag="BW_FRACTAL_LONG",
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Discipline token helper review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    controller.create_behavioral_flag("premature_exit")
    controller.create_rule_violation("manual_plan_deviation")

    journal_view = controller.get_workspace_view()["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    latest_result_lines = build_latest_result_lines(journal_view)
    history_lines = build_latest_trade_result_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        controller.get_workspace_view()["replay"],
        controller.get_workspace_view()["trading"],
        journal_view,
    )

    expected = "Discipline token: Guard execution."
    assert any("Review discipline token: guard_execution_token" == line for line in summary_lines)
    assert any(f"Discipline token text: {expected}" == line for line in summary_lines)
    assert any("Review discipline token: guard_execution_token" == line for line in latest_result_lines)
    assert any(f"Discipline token text: {expected}" == line for line in latest_result_lines)
    assert any("Review discipline token: guard_execution_token" == line for line in history_lines)
    assert any(f"Discipline token text: {expected}" == line for line in history_lines)
    assert any("Review discipline token: guard_execution_token" == line for line in status_lines)
    assert any(expected == line for line in guidance_lines)


def test_desktop_shell_review_discipline_marker_helpers_surface_compact_marker() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_discipline_marker_helpers"),
    )
    controller.create_pre_trade_note(
        content="Declared fractal plan",
        setup_tag="BW_FRACTAL_LONG",
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Discipline marker helper review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    controller.create_behavioral_flag("premature_exit")
    controller.create_rule_violation("manual_plan_deviation")

    journal_view = controller.get_workspace_view()["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    latest_result_lines = build_latest_result_lines(journal_view)
    history_lines = build_latest_trade_result_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        controller.get_workspace_view()["replay"],
        controller.get_workspace_view()["trading"],
        journal_view,
    )

    expected = "Discipline marker: Guard execution path."
    assert any("Review discipline marker: guard_execution_marker" == line for line in summary_lines)
    assert any(f"Discipline marker text: {expected}" == line for line in summary_lines)
    assert any("Review discipline marker: guard_execution_marker" == line for line in latest_result_lines)
    assert any(f"Discipline marker text: {expected}" == line for line in latest_result_lines)
    assert any("Review discipline marker: guard_execution_marker" == line for line in history_lines)
    assert any(f"Discipline marker text: {expected}" == line for line in history_lines)
    assert any("Review discipline marker: guard_execution_marker" == line for line in status_lines)
    assert any(expected == line for line in guidance_lines)


def test_desktop_shell_review_discipline_glyph_helpers_surface_compact_glyph() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_discipline_glyph_helpers"),
    )
    controller.create_pre_trade_note(
        content="Declared fractal plan",
        setup_tag="BW_FRACTAL_LONG",
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Discipline glyph helper review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    controller.create_behavioral_flag("premature_exit")
    controller.create_rule_violation("manual_plan_deviation")

    journal_view = controller.get_workspace_view()["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    latest_result_lines = build_latest_result_lines(journal_view)
    history_lines = build_latest_trade_result_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        controller.get_workspace_view()["replay"],
        controller.get_workspace_view()["trading"],
        journal_view,
    )

    expected = "Discipline glyph: Guard execution line."
    assert any("Review discipline glyph: guard_execution_glyph" == line for line in summary_lines)
    assert any(f"Discipline glyph text: {expected}" == line for line in summary_lines)
    assert any("Review discipline glyph: guard_execution_glyph" == line for line in latest_result_lines)
    assert any(f"Discipline glyph text: {expected}" == line for line in latest_result_lines)
    assert any("Review discipline glyph: guard_execution_glyph" == line for line in history_lines)
    assert any(f"Discipline glyph text: {expected}" == line for line in history_lines)
    assert any("Review discipline glyph: guard_execution_glyph" == line for line in status_lines)
    assert any(expected == line for line in guidance_lines)


def test_desktop_shell_review_discipline_sigil_helpers_surface_compact_sigil() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_discipline_sigil_helpers"),
    )
    controller.create_pre_trade_note(
        content="Declared fractal plan",
        setup_tag="BW_FRACTAL_LONG",
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Discipline sigil helper review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    controller.create_behavioral_flag("premature_exit")
    controller.create_rule_violation("manual_plan_deviation")

    journal_view = controller.get_workspace_view()["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    latest_result_lines = build_latest_result_lines(journal_view)
    history_lines = build_latest_trade_result_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        controller.get_workspace_view()["replay"],
        controller.get_workspace_view()["trading"],
        journal_view,
    )

    expected = "Discipline sigil: Guard execution signal."
    assert any("Review discipline sigil: guard_execution_sigil" == line for line in summary_lines)
    assert any(f"Discipline sigil text: {expected}" == line for line in summary_lines)
    assert any("Review discipline sigil: guard_execution_sigil" == line for line in latest_result_lines)
    assert any(f"Discipline sigil text: {expected}" == line for line in latest_result_lines)
    assert any("Review discipline sigil: guard_execution_sigil" == line for line in history_lines)
    assert any(f"Discipline sigil text: {expected}" == line for line in history_lines)
    assert any("Review discipline sigil: guard_execution_sigil" == line for line in status_lines)
    assert any(expected == line for line in guidance_lines)


def test_desktop_shell_review_discipline_seal_helpers_surface_compact_seal() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_discipline_seal_helpers"),
    )
    controller.create_pre_trade_note(
        content="Declared fractal plan",
        setup_tag="BW_FRACTAL_LONG",
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Discipline seal helper review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    controller.create_behavioral_flag("premature_exit")
    controller.create_rule_violation("manual_plan_deviation")

    journal_view = controller.get_workspace_view()["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    latest_result_lines = build_latest_result_lines(journal_view)
    history_lines = build_latest_trade_result_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        controller.get_workspace_view()["replay"],
        controller.get_workspace_view()["trading"],
        journal_view,
    )

    expected = "Discipline seal: Guard execution lock."
    assert any("Review discipline seal: guard_execution_seal" == line for line in summary_lines)
    assert any(f"Discipline seal text: {expected}" == line for line in summary_lines)
    assert any("Review discipline seal: guard_execution_seal" == line for line in latest_result_lines)
    assert any(f"Discipline seal text: {expected}" == line for line in latest_result_lines)
    assert any("Review discipline seal: guard_execution_seal" == line for line in history_lines)
    assert any(f"Discipline seal text: {expected}" == line for line in history_lines)
    assert any("Review discipline seal: guard_execution_seal" == line for line in status_lines)
    assert any(expected == line for line in guidance_lines)


def test_desktop_shell_review_discipline_crest_helpers_surface_compact_crest() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_discipline_crest_helpers"),
    )
    controller.create_pre_trade_note(
        content="Declared fractal plan",
        setup_tag="BW_FRACTAL_LONG",
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Discipline crest helper review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    controller.create_behavioral_flag("premature_exit")
    controller.create_rule_violation("manual_plan_deviation")

    journal_view = controller.get_workspace_view()["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    latest_result_lines = build_latest_result_lines(journal_view)
    history_lines = build_latest_trade_result_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        controller.get_workspace_view()["replay"],
        controller.get_workspace_view()["trading"],
        journal_view,
    )

    expected = "Discipline crest: Guard execution frame."
    assert any("Review discipline crest: guard_execution_crest" == line for line in summary_lines)
    assert any(f"Discipline crest text: {expected}" == line for line in summary_lines)
    assert any("Review discipline crest: guard_execution_crest" == line for line in latest_result_lines)
    assert any(f"Discipline crest text: {expected}" == line for line in latest_result_lines)
    assert any("Review discipline crest: guard_execution_crest" == line for line in history_lines)
    assert any(f"Discipline crest text: {expected}" == line for line in history_lines)
    assert any("Review discipline crest: guard_execution_crest" == line for line in status_lines)
    assert any(expected == line for line in guidance_lines)


def test_desktop_shell_review_discipline_emblem_helpers_surface_compact_emblem() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_discipline_emblem_helpers"),
    )
    controller.create_pre_trade_note(
        content="Declared fractal plan",
        setup_tag="BW_FRACTAL_LONG",
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Discipline emblem helper review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    controller.create_behavioral_flag("premature_exit")
    controller.create_rule_violation("manual_plan_deviation")

    journal_view = controller.get_workspace_view()["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    latest_result_lines = build_latest_result_lines(journal_view)
    history_lines = build_latest_trade_result_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        controller.get_workspace_view()["replay"],
        controller.get_workspace_view()["trading"],
        journal_view,
    )

    expected = "Discipline emblem: Guard execution badge."
    assert any("Review discipline emblem: guard_execution_emblem" == line for line in summary_lines)
    assert any(f"Discipline emblem text: {expected}" == line for line in summary_lines)
    assert any("Review discipline emblem: guard_execution_emblem" == line for line in latest_result_lines)
    assert any(f"Discipline emblem text: {expected}" == line for line in latest_result_lines)
    assert any("Review discipline emblem: guard_execution_emblem" == line for line in history_lines)
    assert any(f"Discipline emblem text: {expected}" == line for line in history_lines)
    assert any("Review discipline emblem: guard_execution_emblem" == line for line in status_lines)
    assert any(expected == line for line in guidance_lines)


def test_desktop_shell_review_sequence_helpers_surface_next_field_and_order() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_sequence_helpers"),
    )
    controller.create_pre_trade_note(
        content="Declared fractal plan",
        setup_tag="BW_FRACTAL_LONG",
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Sequence helper review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
        entry_timing_label="timely_entry",
    )

    journal_view = controller.get_workspace_view()["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    latest_result_lines = build_latest_result_lines(journal_view)
    history_lines = build_latest_trade_result_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        controller.get_workspace_view()["replay"],
        controller.get_workspace_view()["trading"],
        journal_view,
    )

    assert any("Latest next review field: market_context_label" == line for line in summary_lines)
    assert any("Next review field: market_context_label" == line for line in latest_result_lines)
    assert any("Recommended order: market_context_label -> exit_quality_label -> review_clarity_label" == line for line in latest_result_lines)
    assert any("Next review field: market_context_label" == line for line in history_lines)
    assert any("Recommended review order: market_context_label -> exit_quality_label -> review_clarity_label" == line for line in guidance_lines)


def test_desktop_shell_review_weak_spots_helpers_surface_session_underfilled_fields() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_weak_spots_helpers"),
    )

    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Complete review one",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
        entry_timing_label="timely_entry",
        market_context_label="clean_context",
        exit_quality_label="disciplined_exit",
        review_clarity_label="high_clarity",
    )

    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Partial review two",
        setup_tag="BW_1WM_LONG",
        compliance_label="valid_setup",
        entry_timing_label="timely_entry",
    )

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review weak spots: exit_quality_label, market_context_label, review_clarity_label" == line for line in summary_lines)
    assert any("Review weak spots: exit_quality_label, market_context_label, review_clarity_label" == line for line in status_lines)
    assert any("Session weak spots: exit_quality_label, market_context_label, review_clarity_label" == line for line in guidance_lines)


def test_desktop_shell_review_progress_helpers_surface_improved_vs_missing_weak_spots() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_progress_helpers"),
    )

    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Sparse review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
        entry_timing_label="timely_entry",
    )

    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Improving review",
        setup_tag="BW_1WM_LONG",
        compliance_label="valid_setup",
        entry_timing_label="timely_entry",
        market_context_label="clean_context",
        exit_quality_label="disciplined_exit",
        review_clarity_label="high_clarity",
    )

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review progress: weak_spots_improved" == line for line in summary_lines)
    assert any("Weak spots improved/still missing: exit_quality_label, market_context_label, review_clarity_label / none" == line for line in summary_lines)
    assert any("Review progress: weak_spots_improved" == line for line in status_lines)
    assert any("Latest review improved all current weak spots: exit_quality_label, market_context_label, review_clarity_label." == line for line in guidance_lines)


def test_desktop_shell_review_momentum_helpers_surface_recent_trend() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_momentum_helpers"),
    )

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Partial", setup_tag="BW_1WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    assert any("Review momentum: improving" == line for line in summary_lines)
    assert any("Momentum score sequence: 1, 3" == line for line in summary_lines)
    assert any("Review momentum: improving" == line for line in status_lines)


def test_desktop_shell_review_stability_helpers_surface_recent_evenness() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_stability_helpers"),
    )

    for kwargs in [
        dict(content="Partial one", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
        dict(content="Partial two", setup_tag="BW_1WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)

    assert any("Review stability: stable" == line for line in summary_lines)
    assert any("Stability spread: 0" == line for line in summary_lines)
    assert any("Review stability: stable" == line for line in status_lines)


def test_desktop_shell_review_swings_helpers_surface_sharp_swings() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_swings_helpers"),
    )

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review swings: sharp_swings_detected" == line for line in summary_lines)
    assert any("Max adjacent jump: 2" == line for line in summary_lines)
    assert any("Review swings: sharp_swings_detected" == line for line in status_lines)
    assert any("Recent Bill Williams review quality shows sharp swings between neighboring reviewed trades." == line for line in guidance_lines)


def test_desktop_shell_review_floor_helpers_surface_min_recent_quality() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_floor_helpers"),
    )

    for kwargs in [
        dict(content="Partial one", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
        dict(content="Partial two", setup_tag="BW_1WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review floor: moderate_floor" == line for line in summary_lines)
    assert any("Min recent score: 2" == line for line in summary_lines)
    assert any("Review floor: moderate_floor" == line for line in status_lines)
    assert any("Recent Bill Williams review quality is holding a moderate floor." == line for line in guidance_lines)


def test_desktop_shell_review_ceiling_helpers_surface_max_recent_quality() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_ceiling_helpers"),
    )

    for kwargs in [
        dict(content="Partial", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review ceiling: high_ceiling" == line for line in summary_lines)
    assert any("Max recent score: 3" == line for line in summary_lines)
    assert any("Review ceiling: high_ceiling" == line for line in status_lines)
    assert any("Recent Bill Williams review quality is reaching a high ceiling." == line for line in guidance_lines)


def test_desktop_shell_review_band_helpers_surface_recent_quality_corridor() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_band_helpers"),
    )

    for kwargs in [
        dict(content="Partial", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review band: controlled_band" == line for line in summary_lines)
    assert any("Recent quality corridor: 2-3" == line for line in summary_lines)
    assert any("Band width: 1" == line for line in summary_lines)
    assert any("Review band: controlled_band" == line for line in status_lines)
    assert any("Recent Bill Williams review quality is moving inside a controlled band of 2-3." == line for line in guidance_lines)


def test_desktop_shell_review_headroom_helpers_surface_remaining_quality_room() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_headroom_helpers"),
    )

    for kwargs in [
        dict(content="Partial one", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
        dict(content="Partial two", setup_tag="BW_1WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review headroom: narrow_headroom" == line for line in summary_lines)
    assert any("Remaining headroom: 1" == line for line in summary_lines)
    assert any("Review headroom: narrow_headroom" == line for line in status_lines)
    assert any("Recent Bill Williams review quality still has a narrow step of headroom above the current ceiling." == line for line in guidance_lines)


def test_desktop_shell_review_pressure_helpers_surface_current_quality_target() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_pressure_helpers"),
    )

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review pressure: tighten_band_pressure" == line for line in summary_lines)
    assert any("Pressure target: tighten_band" == line for line in summary_lines)
    assert any("Review pressure: tighten_band_pressure" == line for line in status_lines)
    assert any("Current Bill Williams review pressure is on tightening the recent quality band before pushing higher." == line for line in guidance_lines)


def test_desktop_shell_review_target_helpers_surface_next_quality_focus() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_target_helpers"),
    )

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review target: tighten_band_target" == line for line in summary_lines)
    assert any("Target field: entry_timing_label" == line for line in summary_lines)
    assert any("Review target: tighten_band_target" == line for line in status_lines)
    assert any("Tighten the recent quality band by reducing drift in: entry_timing_label." == line for line in guidance_lines)


def test_desktop_shell_review_focus_helpers_surface_compact_attention_cue() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_focus_helpers"),
    )

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review focus: tighten_focus" == line for line in summary_lines)
    assert any("Focus label: Tighten around entry_timing_label" == line for line in summary_lines)
    assert any("Review focus: tighten_focus" == line for line in status_lines)
    assert any("Keep today's review focus tight around entry_timing_label before broadening to other fields." == line for line in guidance_lines)


def test_desktop_shell_review_cue_helpers_surface_short_operating_hint() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_cue_helpers"),
    )

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review cue: tighten_cue" == line for line in summary_lines)
    assert any("Cue text: Tighten around entry_timing_label" == line for line in summary_lines)
    assert any("Review cue: tighten_cue" == line for line in status_lines)
    assert any("Tighten around entry_timing_label" == line for line in guidance_lines)


def test_desktop_shell_review_badge_helpers_surface_compact_status_carrier() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_badge_helpers"),
    )

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review badge: tighten_badge" == line for line in summary_lines)
    assert any("Badge text: Tighten around entry_timing_label" == line for line in summary_lines)
    assert any("Review badge: tighten_badge" == line for line in status_lines)
    assert any("Tighten around entry_timing_label" == line for line in guidance_lines)


def test_desktop_shell_review_pill_helpers_surface_compact_presentation_carrier() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_pill_helpers"),
    )

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review pill: tighten_pill" == line for line in summary_lines)
    assert any("Pill text: Tighten around entry_timing_label" == line for line in summary_lines)
    assert any("Review pill: tighten_pill" == line for line in status_lines)
    assert any("Tighten around entry_timing_label" == line for line in guidance_lines)


def test_desktop_shell_review_chip_helpers_surface_small_status_carrier() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_chip_helpers"),
    )

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review chip: tighten_chip" == line for line in summary_lines)
    assert any("Chip text: Tighten around entry_timing_label" == line for line in summary_lines)
    assert any("Review chip: tighten_chip" == line for line in status_lines)
    assert any("Tighten around entry_timing_label" == line for line in guidance_lines)


def test_desktop_shell_review_tag_helpers_surface_small_display_token() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_tag_helpers"),
    )

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review tag: tighten_tag" == line for line in summary_lines)
    assert any("Tag text: Tighten around entry_timing_label" == line for line in summary_lines)
    assert any("Review tag: tighten_tag" == line for line in status_lines)
    assert any("Tighten around entry_timing_label" == line for line in guidance_lines)


def test_desktop_shell_review_token_helpers_surface_small_display_carrier() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_token_helpers"),
    )

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review token: tighten_token" == line for line in summary_lines)
    assert any("Token text: Tighten around entry_timing_label" == line for line in summary_lines)
    assert any("Review token: tighten_token" == line for line in status_lines)
    assert any("Tighten around entry_timing_label" == line for line in guidance_lines)


def test_desktop_shell_review_marker_helpers_surface_small_status_carrier() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_marker_helpers"),
    )

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review marker: tighten_marker" == line for line in summary_lines)
    assert any("Marker text: Tighten around entry_timing_label" == line for line in summary_lines)
    assert any("Review marker: tighten_marker" == line for line in status_lines)
    assert any("Tighten around entry_timing_label" == line for line in guidance_lines)


def test_desktop_shell_review_glyph_helpers_surface_small_display_carrier() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_glyph_helpers"),
    )

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review glyph: tighten_glyph" == line for line in summary_lines)
    assert any("Glyph text: Tighten around entry_timing_label" == line for line in summary_lines)
    assert any("Review glyph: tighten_glyph" == line for line in status_lines)
    assert any("Tighten around entry_timing_label" == line for line in guidance_lines)


def test_desktop_shell_review_sigil_helpers_surface_small_display_carrier() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_sigil_helpers"),
    )

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review sigil: tighten_sigil" == line for line in summary_lines)
    assert any("Sigil text: Tighten around entry_timing_label" == line for line in summary_lines)
    assert any("Review sigil: tighten_sigil" == line for line in status_lines)
    assert any("Tighten around entry_timing_label" == line for line in guidance_lines)


def test_desktop_shell_review_seal_helpers_surface_small_display_carrier() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_seal_helpers"),
    )

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review seal: tighten_seal" == line for line in summary_lines)
    assert any("Seal text: Tighten around entry_timing_label" == line for line in summary_lines)
    assert any("Review seal: tighten_seal" == line for line in status_lines)
    assert any("Tighten around entry_timing_label" == line for line in guidance_lines)


def test_desktop_shell_review_crest_helpers_surface_small_display_carrier() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_crest_helpers"),
    )

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review crest: tighten_crest" == line for line in summary_lines)
    assert any("Crest text: Tighten around entry_timing_label" == line for line in summary_lines)
    assert any("Review crest: tighten_crest" == line for line in status_lines)
    assert any("Tighten around entry_timing_label" == line for line in guidance_lines)


def test_desktop_shell_review_emblem_helpers_surface_small_display_carrier() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_emblem_helpers"),
    )

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review emblem: tighten_emblem" == line for line in summary_lines)
    assert any("Emblem text: Tighten around entry_timing_label" == line for line in summary_lines)
    assert any("Review emblem: tighten_emblem" == line for line in status_lines)
    assert any("Tighten around entry_timing_label" == line for line in guidance_lines)


def test_desktop_shell_review_insignia_helpers_surface_small_display_carrier() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_insignia_helpers"),
    )

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review insignia: tighten_insignia" == line for line in summary_lines)
    assert any("Insignia text: Tighten around entry_timing_label" == line for line in summary_lines)
    assert any("Review insignia: tighten_insignia" == line for line in status_lines)
    assert any("Tighten around entry_timing_label" == line for line in guidance_lines)


def test_desktop_shell_review_standard_helpers_surface_small_display_carrier() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_standard_helpers"),
    )

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review standard: tighten_standard" == line for line in summary_lines)
    assert any("Standard text: Tighten around entry_timing_label" == line for line in summary_lines)
    assert any("Review standard: tighten_standard" == line for line in status_lines)
    assert any("Tighten around entry_timing_label" == line for line in guidance_lines)


def test_desktop_shell_review_banner_helpers_surface_small_display_carrier() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_banner_helpers"),
    )

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review banner: tighten_banner" == line for line in summary_lines)
    assert any("Banner text: Tighten around entry_timing_label" == line for line in summary_lines)
    assert any("Review banner: tighten_banner" == line for line in status_lines)
    assert any("Tighten around entry_timing_label" == line for line in guidance_lines)


def test_desktop_shell_review_pennant_helpers_surface_small_display_carrier() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_pennant_helpers"),
    )

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review pennant: tighten_pennant" == line for line in summary_lines)
    assert any("Pennant text: Tighten around entry_timing_label" == line for line in summary_lines)
    assert any("Review pennant: tighten_pennant" == line for line in status_lines)
    assert any("Tighten around entry_timing_label" == line for line in guidance_lines)


def test_desktop_shell_review_streamer_helpers_surface_small_display_carrier() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_streamer_helpers"),
    )

    for kwargs in [
        dict(content="Sparse", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup"),
        dict(content="Complete", setup_tag="BW_2WM_LONG", compliance_label="valid_setup", entry_timing_label="timely_entry", market_context_label="clean_context", exit_quality_label="disciplined_exit", review_clarity_label="high_clarity"),
    ]:
        controller.buy_market()
        controller.play()
        controller.advance_frame()
        controller.manual_close()
        controller.advance_frame()
        controller.pause()
        controller.create_post_trade_review(**kwargs)

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    summary_lines = build_review_summary_lines(journal_view)
    status_lines = build_history_status_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review streamer: tighten_streamer" == line for line in summary_lines)
    assert any("Streamer text: Tighten around entry_timing_label" == line for line in summary_lines)
    assert any("Review streamer: tighten_streamer" == line for line in status_lines)
    assert any("Tighten around entry_timing_label" == line for line in guidance_lines)



def test_desktop_shell_launch_helpers_auto_import_raw_dataset_file() -> None:
    from desktop_shell.launch import resolve_dataset_handle

    raw_dir = _reset_dir(TMP_ROOT / "launch_raw_import")
    raw_path = raw_dir / "eurusd_raw.csv"
    raw_path.write_text(
        "timestamp,bid,ask\n"
        "2025-01-02T10:00:00Z,1.10345,1.10357\n"
        "2025-01-02T10:00:01Z,1.10348,1.10360\n",
        encoding="utf-8",
    )
    config = DesktopLaunchConfig(
        dataset_handle=str(raw_path),
        storage_dir=raw_dir / "storage",
        replay_mode="training",
        instrument_id="EURUSD",
    )

    resolved = resolve_dataset_handle(config)
    controller = build_controller_from_launch_config(config)
    workspace = controller.get_workspace_view()

    assert Path(resolved).is_dir()
    assert workspace["replay"]["dataset_id"].endswith("-v1")
    assert workspace["replay"]["instrument_id"] == "EURUSD"


def test_desktop_shell_replay_and_readiness_surface_import_warnings_from_raw_launch_path() -> None:
    raw_dir = _reset_dir(TMP_ROOT / "readiness_raw_import")
    raw_path = raw_dir / "eurusd_raw.csv"
    raw_path.write_text(
        "timestamp,bid,ask\n"
        "2025-01-02T10:00:01Z,1.10348,1.10360\n"
        "2025-01-02T10:00:00Z,1.10345,1.10357\n"
        "2025-01-02T10:02:30Z,1.10356,1.10368\n",
        encoding="utf-8",
    )
    config = DesktopLaunchConfig(
        dataset_handle=str(raw_path),
        storage_dir=raw_dir / "storage",
        replay_mode="training",
        instrument_id="EURUSD",
    )

    snapshot = build_readiness_snapshot(config)
    report = format_readiness_report(snapshot)
    controller = build_controller_from_launch_config(config)
    replay_view = controller.get_workspace_view()["replay"]
    header_lines = build_replay_header_lines(replay_view)

    assert snapshot.dataset_quality_status == "accepted_with_warnings"
    assert snapshot.import_warning_count == 2
    assert "repaired_out_of_order_ticks:1" in snapshot.import_warning_preview
    assert "Import warnings: 2 (repaired_out_of_order_ticks:1, unexpected_gaps:1)" in report
    assert replay_view["dataset_quality"]["warning_count"] == 2
    assert any(line == "Import warnings: accepted_with_warnings (2)" for line in header_lines)
    assert any(line == "Warning preview: repaired_out_of_order_ticks:1, unexpected_gaps:1" for line in header_lines)


def test_desktop_shell_launch_returns_friendly_message_when_tk_environment_is_missing(monkeypatch) -> None:
    import desktop_shell.launch as launch_module

    monkeypatch.setattr(launch_module, "_try_relaunch_with_ascii_tk_python", lambda argv=None: False)
    monkeypatch.setattr(launch_module, "prompt_start_selection", lambda config: launch_module.DesktopStartSelection(key="start_new_session", label="Start new session", detail="test"))
    monkeypatch.setattr(launch_module, "launch_desktop_app", lambda controller: (_ for _ in ()).throw(RuntimeError("Can't find a usable init.tcl")))

    with pytest.raises(SystemExit) as exc_info:
        launch_module.run_desktop_shell([])

    message = str(exc_info.value)
    assert "Desktop shell could not start a Tk GUI" in message
    assert "Desktop readiness" in message
    assert "python -m desktop_shell" in message


def test_desktop_shell_launch_relaunches_with_ascii_tk_python_before_friendly_fallback(monkeypatch) -> None:
    import desktop_shell.launch as launch_module

    relaunched = {"value": False}

    def _mark_relaunch(argv=None) -> bool:
        relaunched["value"] = True
        return True

    monkeypatch.setattr(launch_module, "_try_relaunch_with_ascii_tk_python", _mark_relaunch)
    monkeypatch.setattr(launch_module, "prompt_start_selection", lambda config: launch_module.DesktopStartSelection(key="start_new_session", label="Start new session", detail="test"))
    monkeypatch.setattr(launch_module, "launch_desktop_app", lambda controller: (_ for _ in ()).throw(RuntimeError("Can't find a usable init.tcl")))

    launch_module.run_desktop_shell([])

    assert relaunched["value"] is True


def test_desktop_shell_surfaces_dataset_quality_context_after_warned_trade_flow() -> None:
    raw_dir = _reset_dir(TMP_ROOT / "dataset_quality_context_surfaces")
    raw_path = raw_dir / "eurusd_raw.csv"
    raw_path.write_text(
        "timestamp,bid,ask\n"
        "2025-01-02T10:00:01Z,1.10348,1.10360\n"
        "2025-01-02T10:00:00Z,1.10345,1.10357\n"
        "2025-01-02T10:02:30Z,1.10356,1.10368\n",
        encoding="utf-8",
    )
    controller = DesktopShellController(
        dataset_handle=build_controller_from_launch_config(
            DesktopLaunchConfig(
                dataset_handle=str(raw_path),
                storage_dir=raw_dir / "bootstrap_storage",
                replay_mode="training",
                instrument_id="EURUSD",
            )
        ).dataset_handle,
        storage_dir=_reset_dir(TMP_ROOT / "dataset_quality_context_surfaces_state"),
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Warned dataset review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )

    workspace = controller.get_workspace_view()
    trade_lines = build_trade_context_lines(workspace["trading"])
    latest_result_lines = build_latest_result_lines(workspace["journal"])
    summary_lines = build_review_summary_lines(workspace["journal"])
    guidance_lines = build_workflow_guidance_lines(workspace["replay"], workspace["trading"], workspace["journal"])

    assert any(line == "Dataset quality context: execution_warning_context" for line in trade_lines)
    assert any("Latest execution context flags: repaired_out_of_order_ticks, unexpected_gap." in line for line in trade_lines)
    assert any(line == "Dataset quality context: execution_warning_context" for line in latest_result_lines)
    assert any(line == "Dataset quality context: execution_warning_context" for line in summary_lines)
    assert any(line == "Dataset quality context: execution_warning_context" for line in guidance_lines)
    assert any("Dataset warnings remain active: repaired_out_of_order_ticks:1, unexpected_gaps:1." in line for line in guidance_lines)


def test_desktop_shell_surfaces_dataset_quality_finalization_link_in_readiness_pause_and_finalization() -> None:
    raw_dir = _reset_dir(TMP_ROOT / "dataset_quality_finalization_surfaces")
    raw_path = raw_dir / "eurusd_raw.csv"
    raw_path.write_text(
        "timestamp,bid,ask\n"
        "2025-01-02T10:00:01Z,1.10348,1.10360\n"
        "2025-01-02T10:00:00Z,1.10345,1.10357\n"
        "2025-01-02T10:02:30Z,1.10356,1.10368\n",
        encoding="utf-8",
    )
    boot = build_controller_from_launch_config(
        DesktopLaunchConfig(
            dataset_handle=str(raw_path),
            storage_dir=raw_dir / "bootstrap_storage",
            replay_mode="training",
            instrument_id="EURUSD",
        )
    )
    controller = DesktopShellController(
        dataset_handle=boot.dataset_handle,
        storage_dir=_reset_dir(TMP_ROOT / "dataset_quality_finalization_surfaces_state"),
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(content="Warned dataset review", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup")
    workspace = controller.finalize_session(reason="user_completed")

    config = DesktopLaunchConfig(dataset_handle=boot.dataset_handle, storage_dir=controller.storage_dir, replay_mode="training")
    readiness = build_readiness_snapshot(config)
    readiness_report = format_readiness_report(readiness)
    pause_point = build_mvp_pause_point_snapshot(config)
    pause_report = format_mvp_pause_point_report(pause_point)
    finalization_lines = build_finalization_lines(workspace["journal"], workspace["trading"])
    blocker_lines = build_finalization_blocker_lines(workspace["journal"], workspace["trading"])

    assert readiness.finalization_link_status == "finalized_warned_link"
    assert "Finalization link: finalized_warned_link" in readiness_report
    assert "warned dataset context" in readiness_report
    assert pause_point.finalization_link_status == "finalized_warned_link"
    assert "Finalization link: finalized_warned_link" in pause_report
    assert any(line == "Finalization dataset link: finalized_warned_link" for line in finalization_lines)
    assert any("session closed with warned dataset context" in line for line in finalization_lines)
    assert any(line == "Finalization dataset link: finalized_warned_link" for line in blocker_lines)


def test_desktop_shell_surfaces_clean_finalization_state_stays_clean_across_reports() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "clean_finalization_state_surfaces"),
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(content="Clean dataset review", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup")
    workspace = controller.finalize_session(reason="user_completed")

    config = DesktopLaunchConfig(dataset_handle=FIXTURE, storage_dir=controller.storage_dir, replay_mode="training")
    readiness = build_readiness_snapshot(config)
    readiness_report = format_readiness_report(readiness)
    pause_point = build_mvp_pause_point_snapshot(config)
    pause_report = format_mvp_pause_point_report(pause_point)
    finalization_lines = build_finalization_lines(workspace["journal"], workspace["trading"])
    blocker_lines = build_finalization_blocker_lines(workspace["journal"], workspace["trading"])

    assert readiness.finalization_link_status == "finalized_clean_context"
    assert "Finalization link: finalized_clean_context" in readiness_report
    assert "warned dataset context" not in readiness_report
    assert pause_point.finalization_link_status == "finalized_clean_context"
    assert "Finalization link: finalized_clean_context" in pause_report
    assert "warned dataset context" not in pause_report
    assert any(line == "Finalization dataset link: finalized_clean_context" for line in finalization_lines)
    assert any("session closed with clean dataset context" in line for line in finalization_lines)
    assert any(line == "Finalization dataset link: finalized_clean_context" for line in blocker_lines)


def test_desktop_shell_surfaces_review_dataset_quality_link_for_warned_review_flow() -> None:
    raw_dir = _reset_dir(TMP_ROOT / "review_dataset_quality_link_surfaces")
    raw_path = raw_dir / "eurusd_raw.csv"
    raw_path.write_text(
        "timestamp,bid,ask\n"
        "2025-01-02T10:00:01Z,1.10348,1.10360\n"
        "2025-01-02T10:00:00Z,1.10345,1.10357\n"
        "2025-01-02T10:02:30Z,1.10356,1.10368\n",
        encoding="utf-8",
    )
    boot = build_controller_from_launch_config(
        DesktopLaunchConfig(
            dataset_handle=str(raw_path),
            storage_dir=raw_dir / "bootstrap_storage",
            replay_mode="training",
            instrument_id="EURUSD",
        )
    )
    controller = DesktopShellController(
        dataset_handle=boot.dataset_handle,
        storage_dir=_reset_dir(TMP_ROOT / "review_dataset_quality_link_surfaces_state"),
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(content="Warned dataset review", setup_tag="BW_FRACTAL_LONG", compliance_label="valid_setup")

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    latest_result_lines = build_latest_result_lines(journal_view)
    history_lines = build_latest_trade_result_lines(journal_view)
    summary_lines = build_review_summary_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(workspace["replay"], workspace["trading"], journal_view)

    assert any(line == "Review dataset link: warned_execution_review_link" for line in latest_result_lines)
    assert any(line == "Review dataset link: warned_execution_review_link" for line in history_lines)
    assert any(line == "Review dataset link: warned_execution_review_link" for line in summary_lines)
    assert any(line == "Review dataset link text: Review link: warned dataset context touched this trade through repaired_out_of_order_ticks, unexpected_gap." for line in latest_result_lines)
    assert any(line == "Review link: warned dataset context touched this trade through repaired_out_of_order_ticks, unexpected_gap." for line in guidance_lines)


def test_desktop_shell_review_discipline_reason_helpers_surface_compact_reason() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "review_discipline_reason_helpers"),
    )
    controller.create_pre_trade_note(content="Declared fractal long", setup_tag="BW_FRACTAL_LONG")
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    controller.create_post_trade_review(
        content="Valid setup, weak discipline",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    controller.create_behavioral_flag("premature_exit")
    controller.create_rule_violation("manual_plan_deviation")

    workspace = controller.get_workspace_view()
    journal_view = workspace["journal"]
    latest_result_lines = build_latest_result_lines(journal_view)
    history_lines = build_latest_trade_result_lines(journal_view)
    summary_lines = build_review_summary_lines(journal_view)
    guidance_lines = build_workflow_guidance_lines(
        workspace["replay"],
        workspace["trading"],
        journal_view,
    )

    assert any("Review discipline reason: guard_execution_reason" == line for line in latest_result_lines)
    assert any("Review discipline reason: guard_execution_reason" == line for line in history_lines)
    assert any("Review discipline reason: guard_execution_reason" == line for line in summary_lines)
    assert any(
        "Discipline reason text: Discipline reason: setup BW_FRACTAL_LONG stayed valid, but execution discipline slipped through premature_exit, manual_plan_deviation." == line
        for line in latest_result_lines
    )
    assert any(
        "Discipline reason: setup BW_FRACTAL_LONG stayed valid, but execution discipline slipped through premature_exit, manual_plan_deviation." == line
        for line in guidance_lines
    )



def test_desktop_shell_history_helpers_handle_no_latest_trade_result() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "history_no_latest_trade"),
    )
    journal_view = controller.get_workspace_view()["journal"]
    lines = build_history_status_lines(journal_view)
    assert any("Latest next review field: -" == line for line in lines)

def test_desktop_shell_surfaces_dataset_quality_recovery_note_after_reopen() -> None:
    raw_dir = _reset_dir(TMP_ROOT / "dataset_quality_recovery_note_surfaces")
    raw_path = raw_dir / "eurusd_raw.csv"
    raw_path.write_text(
        "timestamp,bid,ask\n"
        "2025-01-02T10:00:01Z,1.10348,1.10360\n"
        "2025-01-02T10:00:00Z,1.10345,1.10357\n"
        "2025-01-02T10:02:30Z,1.10356,1.10368\n",
        encoding="utf-8",
    )
    boot = build_controller_from_launch_config(
        DesktopLaunchConfig(
            dataset_handle=str(raw_path),
            storage_dir=raw_dir / "bootstrap_storage",
            replay_mode="training",
            instrument_id="EURUSD",
        )
    )
    storage_dir = _reset_dir(TMP_ROOT / "dataset_quality_recovery_note_surfaces_state")
    controller_1 = DesktopShellController(
        dataset_handle=boot.dataset_handle,
        storage_dir=storage_dir,
    )
    controller_1.buy_market()
    controller_1.play()
    controller_1.advance_frame()
    controller_1.manual_close()
    controller_1.advance_frame()
    controller_1.pause()
    controller_1.create_post_trade_review(
        content="Warned dataset review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    controller_1.finalize_session(reason="user_completed")

    controller_2 = DesktopShellController(
        dataset_handle=boot.dataset_handle,
        storage_dir=storage_dir,
    )
    recovered_workspace = controller_2.get_workspace_view()
    recovered_guidance = build_workflow_guidance_lines(
        recovered_workspace["replay"],
        recovered_workspace["trading"],
        recovered_workspace["journal"],
    )
    readiness = build_readiness_snapshot(
        DesktopLaunchConfig(dataset_handle=boot.dataset_handle, storage_dir=storage_dir, replay_mode="training")
    )
    readiness_report = format_readiness_report(readiness)

    assert recovered_workspace["journal"]["recovered"] is True
    assert recovered_workspace["journal"]["dataset_quality_recovery_note"]["note_status"] == "recovered_warned_close_context"
    assert any("reopened finalized session still carries warned dataset close context" in line for line in recovered_guidance)
    assert readiness.recovery_note_status == "recovered_warned_close_context"
    assert "Recovery note: recovered_warned_close_context" in readiness_report
    assert "reopened finalized session still carries warned dataset close context" in readiness_report

def test_desktop_shell_surfaces_clean_recovery_state_stays_warning_free() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "clean_recovery_state_surfaces")
    controller_1 = DesktopShellController(dataset_handle=FIXTURE, storage_dir=storage_dir)
    controller_1.buy_market()
    controller_1.play()
    controller_1.advance_frame()
    controller_1.manual_close()
    controller_1.advance_frame()
    controller_1.pause()
    controller_1.create_post_trade_review(
        content="Clean dataset review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    controller_1.finalize_session(reason="user_completed")

    controller_2 = DesktopShellController(dataset_handle=FIXTURE, storage_dir=storage_dir)
    recovered_workspace = controller_2.get_workspace_view()
    recovered_guidance = build_workflow_guidance_lines(
        recovered_workspace["replay"],
        recovered_workspace["trading"],
        recovered_workspace["journal"],
    )
    feedback_lines = build_action_feedback_lines(None, recovered_workspace["journal"])
    button_map = build_button_state_map(recovered_workspace["replay"], recovered_workspace["trading"], recovered_workspace["journal"])
    readiness = build_readiness_snapshot(
        DesktopLaunchConfig(dataset_handle=FIXTURE, storage_dir=storage_dir, replay_mode="training")
    )

    assert recovered_workspace["journal"]["recovered"] is True
    assert readiness.recovery_note_status == "recovered_clean_context"
    assert readiness.recovery_acknowledgment_status == "not_applicable"
    assert any("reopened finalized session returns with clean dataset context" in line for line in recovered_guidance)
    assert feedback_lines[1] == "No action yet in this desktop session."
    assert button_map["acknowledge_recovery"] is False


def test_desktop_shell_surfaces_recovery_feedback_cue_after_reopen() -> None:
    raw_dir = _reset_dir(TMP_ROOT / "dataset_quality_recovery_feedback_surfaces")
    raw_path = raw_dir / "eurusd_raw.csv"
    raw_path.write_text(
        "timestamp,bid,ask\n"
        "2025-01-02T10:00:01Z,1.10348,1.10360\n"
        "2025-01-02T10:00:00Z,1.10345,1.10357\n"
        "2025-01-02T10:02:30Z,1.10356,1.10368\n",
        encoding="utf-8",
    )
    boot = build_controller_from_launch_config(
        DesktopLaunchConfig(
            dataset_handle=str(raw_path),
            storage_dir=raw_dir / "bootstrap_storage",
            replay_mode="training",
            instrument_id="EURUSD",
        )
    )
    storage_dir = _reset_dir(TMP_ROOT / "dataset_quality_recovery_feedback_surfaces_state")
    controller_1 = DesktopShellController(dataset_handle=boot.dataset_handle, storage_dir=storage_dir)
    controller_1.buy_market()
    controller_1.play()
    controller_1.advance_frame()
    controller_1.manual_close()
    controller_1.advance_frame()
    controller_1.pause()
    controller_1.create_post_trade_review(
        content="Warned dataset review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    controller_1.finalize_session(reason="user_completed")

    controller_2 = DesktopShellController(dataset_handle=boot.dataset_handle, storage_dir=storage_dir)
    recovered_workspace = controller_2.get_workspace_view()
    feedback_lines = build_action_feedback_lines(None, recovered_workspace["journal"])

    assert feedback_lines[0] == "Recent action:"
    assert feedback_lines[1] == "INFO: Review reopened warning"
    assert any("reopened finalized session still carries warned dataset close context" in line for line in feedback_lines)


def test_desktop_shell_recovery_acknowledgment_action_persists_and_subdues_feedback() -> None:
    raw_dir = _reset_dir(TMP_ROOT / "dataset_quality_recovery_acknowledgment_surfaces")
    raw_path = raw_dir / "eurusd_raw.csv"
    raw_path.write_text(
        "timestamp,bid,ask\n"
        "2025-01-02T10:00:01Z,1.10348,1.10360\n"
        "2025-01-02T10:00:00Z,1.10345,1.10357\n"
        "2025-01-02T10:02:30Z,1.10356,1.10368\n",
        encoding="utf-8",
    )
    boot = build_controller_from_launch_config(
        DesktopLaunchConfig(
            dataset_handle=str(raw_path),
            storage_dir=raw_dir / "bootstrap_storage",
            replay_mode="training",
            instrument_id="EURUSD",
        )
    )
    storage_dir = _reset_dir(TMP_ROOT / "dataset_quality_recovery_acknowledgment_surfaces_state")
    controller_1 = DesktopShellController(dataset_handle=boot.dataset_handle, storage_dir=storage_dir)
    controller_1.buy_market()
    controller_1.play()
    controller_1.advance_frame()
    controller_1.manual_close()
    controller_1.advance_frame()
    controller_1.pause()
    controller_1.create_post_trade_review(
        content="Warned dataset review",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )
    controller_1.finalize_session(reason="user_completed")

    controller_2 = DesktopShellController(dataset_handle=boot.dataset_handle, storage_dir=storage_dir)
    recovered_workspace = controller_2.get_workspace_view()
    recovery_ack = recovered_workspace["journal"]["dataset_quality_recovery_acknowledgment"]
    button_map_before = build_button_state_map(recovered_workspace["replay"], recovered_workspace["trading"], recovered_workspace["journal"])
    guidance_before = build_workflow_guidance_lines(recovered_workspace["replay"], recovered_workspace["trading"], recovered_workspace["journal"])
    feedback_before = build_action_feedback_lines(None, recovered_workspace["journal"])

    assert recovery_ack["acknowledgment_status"] == "acknowledgment_needed"
    assert button_map_before["acknowledge_recovery"] is True
    assert any("Review the reopened warning before starting a new local session." == line for line in guidance_before)
    assert feedback_before[1] == "INFO: Review reopened warning"

    updated_workspace = controller_2.acknowledge_recovery_context()
    updated_ack = updated_workspace["journal"]["dataset_quality_recovery_acknowledgment"]
    button_map_after = build_button_state_map(updated_workspace["replay"], updated_workspace["trading"], updated_workspace["journal"])
    guidance_after = build_workflow_guidance_lines(updated_workspace["replay"], updated_workspace["trading"], updated_workspace["journal"])
    feedback_after = build_action_feedback_lines(None, updated_workspace["journal"])
    readiness = build_readiness_snapshot(
        DesktopLaunchConfig(dataset_handle=boot.dataset_handle, storage_dir=storage_dir, replay_mode="training")
    )

    assert updated_ack["acknowledgment_status"] == "acknowledged"
    assert updated_ack["acknowledged_at"] is not None
    assert button_map_after["acknowledge_recovery"] is False
    assert any("Reopened warning already reviewed for this session." == line for line in guidance_after)
    assert feedback_after[1] == "INFO: Reopened warning reviewed"
    assert readiness.recovery_acknowledgment_status == "acknowledged"
    assert readiness.recovery_acknowledged_at != "none"

    controller_3 = DesktopShellController(dataset_handle=boot.dataset_handle, storage_dir=storage_dir)
    recovered_again = controller_3.get_workspace_view()
    assert recovered_again["journal"]["dataset_quality_recovery_acknowledgment"]["acknowledgment_status"] == "acknowledged"


def test_desktop_shell_recovery_acknowledgment_stays_hidden_without_warned_context() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "recovery_ack_hidden_clean"),
    )
    workspace = controller.get_workspace_view()
    button_map = build_button_state_map(workspace["replay"], workspace["trading"], workspace["journal"])
    feedback_lines = build_action_feedback_lines(None, workspace["journal"])

    assert workspace["journal"]["dataset_quality_recovery_acknowledgment"]["acknowledgment_status"] == "not_applicable"
    assert button_map["acknowledge_recovery"] is False
    assert feedback_lines[1] == "No action yet in this desktop session."

def test_desktop_shell_controller_exposes_chart_snapshot_authoring_flow() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "desktop_snapshot_authoring_flow"),
    )
    pre_workspace = controller.create_chart_snapshot(
        artifact_ref="snapshots/desktop/pre-entry.png",
        snapshot_role="pre_entry_context",
    )
    pre_snapshot_id = pre_workspace["journal"]["last_chart_snapshot"]["snapshot_id"]
    controller.create_pre_trade_note(
        content="Desktop note with snapshot",
        setup_tag="BW_FRACTAL_LONG",
        chart_snapshot_ref=pre_snapshot_id,
    )
    controller.buy_market()
    controller.play()
    controller.advance_frame()
    controller.manual_close()
    controller.advance_frame()
    controller.pause()
    review_workspace = controller.create_chart_snapshot(
        artifact_ref="snapshots/desktop/review.png",
        snapshot_role="review_context",
    )
    review_snapshot_id = review_workspace["journal"]["last_chart_snapshot"]["snapshot_id"]
    final_workspace = controller.create_post_trade_review(
        content="Desktop review with snapshot",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
        chart_snapshot_refs=(review_snapshot_id,),
    )

    journal_view = final_workspace["journal"]
    authoring_lines = build_authoring_status_lines(journal_view)
    note_lines = build_note_section_lines(journal_view)
    review_lines = build_review_section_lines(journal_view)

    assert journal_view["chart_snapshot_count"] == 2
    assert any(line == "Chart snapshots: 2" for line in authoring_lines)
    assert any(line.endswith("/ snapshots/desktop/review.png") for line in authoring_lines)
    assert any(line == f"Last note snapshot: {pre_snapshot_id}" for line in note_lines)
    assert any(line == f"Last review snapshots: {review_snapshot_id}" for line in review_lines)
    latest_result = journal_view["derived_review_output"]["latest_trade_result"]
    assert latest_result["linked_chart_snapshot_count"] == 2
    assert latest_result["linked_chart_snapshot_ids"] == [pre_snapshot_id, review_snapshot_id]

def test_desktop_shell_surfaces_initial_trade_protection_and_restart_recovery() -> None:
    active_storage_dir = _reset_dir(TMP_ROOT / "desktop_initial_protection_active")
    controller_1 = DesktopShellController(dataset_handle=FIXTURE, storage_dir=active_storage_dir)
    controller_1.buy_market(stop_loss=1.10340, take_profit=1.10370)
    controller_1.play()
    controller_1.advance_frame()

    active_workspace = controller_1.get_workspace_view()
    active_trade_lines = build_trade_context_lines(active_workspace["trading"])
    assert any(line == "Protection present: yes" for line in active_trade_lines)
    assert any(line == "Stop loss / take profit: 1.1034 / 1.1037" for line in active_trade_lines)

    controller_2 = DesktopShellController(dataset_handle=FIXTURE, storage_dir=active_storage_dir)
    recovered_active_workspace = controller_2.get_workspace_view()
    recovered_active_trade_lines = build_trade_context_lines(recovered_active_workspace["trading"])
    assert recovered_active_workspace["journal"]["recovered"] is True
    assert any(line == "Protection present: yes" for line in recovered_active_trade_lines)
    assert any(line == "Stop loss / take profit: 1.1034 / 1.1037" for line in recovered_active_trade_lines)

    closed_storage_dir = _reset_dir(TMP_ROOT / "desktop_initial_protection_closed")
    controller_3 = DesktopShellController(dataset_handle=FIXTURE, storage_dir=closed_storage_dir)
    controller_3.buy_market(stop_loss=1.10340, take_profit=1.10360)
    controller_3.play()
    controller_3.advance_frame()
    while controller_3.get_workspace_view()["trading"]["active_trade_present"]:
        controller_3.advance_frame()

    closed_workspace = controller_3.get_workspace_view()
    latest_result_lines = build_latest_result_lines(closed_workspace["journal"])
    history_lines = build_latest_trade_result_lines(closed_workspace["journal"])
    assert any(line == "Close reason: take_profit_hit" for line in latest_result_lines)
    assert any(line == "Protection present: yes" for line in latest_result_lines)
    assert any(line == "Stop loss / take profit: 1.1034 / 1.1036" for line in latest_result_lines)
    assert any(line == "Close reason: take_profit_hit" for line in history_lines)
    assert any(line == "Protection present: yes" for line in history_lines)
    assert any(line == "Stop loss / take profit: 1.1034 / 1.1036" for line in history_lines)

    controller_4 = DesktopShellController(dataset_handle=FIXTURE, storage_dir=closed_storage_dir)
    recovered_closed_workspace = controller_4.get_workspace_view()
    recovered_latest_result_lines = build_latest_result_lines(recovered_closed_workspace["journal"])
    recovered_history_lines = build_latest_trade_result_lines(recovered_closed_workspace["journal"])
    recovered_trade_lines = build_trade_context_lines(recovered_closed_workspace["trading"])

    assert recovered_closed_workspace["journal"]["recovered"] is True
    assert any(line == "Active trade: no" for line in recovered_trade_lines)
    assert any(line == "Last close reason: take_profit_hit" for line in recovered_trade_lines)
    assert any(line == "Close reason: take_profit_hit" for line in recovered_latest_result_lines)
    assert any(line == "Protection present: yes" for line in recovered_latest_result_lines)
    assert any(line == "Stop loss / take profit: 1.1034 / 1.1036" for line in recovered_latest_result_lines)
    assert any(line == "Close reason: take_profit_hit" for line in recovered_history_lines)
    assert any(line == "Protection present: yes" for line in recovered_history_lines)
    assert any(line == "Stop loss / take profit: 1.1034 / 1.1036" for line in recovered_history_lines)


def test_desktop_shell_surfaces_bill_williams_review_evidence_status_after_reopen() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "review_evidence_status_surfaces_state")

    controller_1 = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=storage_dir,
    )
    controller_1.buy_market()
    controller_1.play()
    controller_1.advance_frame()
    controller_1.manual_close()
    controller_1.advance_frame()
    controller_1.pause()
    controller_1.create_post_trade_review(
        content="Reviewed method without chart evidence",
        setup_tag="BW_FRACTAL_LONG",
        compliance_label="valid_setup",
    )

    controller_2 = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=storage_dir,
    )
    reopened_workspace = controller_2.get_workspace_view()
    journal_view = reopened_workspace["journal"]
    latest_result_lines = build_latest_result_lines(journal_view)
    history_lines = build_latest_trade_result_lines(journal_view)
    summary_lines = build_review_summary_lines(journal_view)
    workflow_lines = build_workflow_guidance_lines(
        reopened_workspace["replay"],
        reopened_workspace["trading"],
        journal_view,
    )

    assert reopened_workspace["journal"]["recovered"] is True
    assert any(line == "Review digest: reviewed_gap_open" for line in latest_result_lines)
    assert any(line == "Digest headline: Reviewed trade still needs linked chart evidence." for line in latest_result_lines)
    assert any(line == "Digest primary gap: Bill Williams review is filled, but no linked chart evidence is attached yet." for line in latest_result_lines)
    assert any(line == "Digest next step: Link a pre-trade or review chart snapshot to back this Bill Williams review." for line in latest_result_lines)
    assert any(line == "Review evidence: linked_evidence_missing" for line in latest_result_lines)
    assert any(
        line == "Review evidence text: Bill Williams review is filled, but no linked chart evidence is attached yet."
        for line in latest_result_lines
    )
    assert any(line == "Review evidence follow-up: link_any_chart_evidence" for line in latest_result_lines)
    assert any(
        line == "Review evidence next step: Link a pre-trade or review chart snapshot to back this Bill Williams review."
        for line in latest_result_lines
    )
    assert any(line == "Review digest: reviewed_gap_open" for line in history_lines)
    assert any(line == "Digest headline: Reviewed trade still needs linked chart evidence." for line in history_lines)
    assert any(line == "Digest primary gap: Bill Williams review is filled, but no linked chart evidence is attached yet." for line in history_lines)
    assert any(line == "Digest next step: Link a pre-trade or review chart snapshot to back this Bill Williams review." for line in history_lines)
    assert any(line == "Review evidence: linked_evidence_missing" for line in history_lines)
    assert any(
        line == "Review evidence text: Bill Williams review is filled, but no linked chart evidence is attached yet."
        for line in history_lines
    )
    assert any(line == "Review evidence follow-up: link_any_chart_evidence" for line in history_lines)
    assert any(
        line == "Review evidence next step: Link a pre-trade or review chart snapshot to back this Bill Williams review."
        for line in history_lines
    )
    assert any(line == "Latest trade digest: reviewed_gap_open" for line in summary_lines)
    assert any(line == "Digest headline: Reviewed trade still needs linked chart evidence." for line in summary_lines)
    assert any(line == "Digest primary gap: Bill Williams review is filled, but no linked chart evidence is attached yet." for line in summary_lines)
    assert any(line == "Digest next step: Link a pre-trade or review chart snapshot to back this Bill Williams review." for line in summary_lines)
    assert any(line == "Reviewed trades with BW evidence: 0" for line in summary_lines)
    assert any(line == "Reviewed trades missing BW evidence: 1" for line in summary_lines)
    assert any(line == "Reviewed trades needing BW evidence follow-up: 1" for line in summary_lines)
    assert any(line == "Latest BW evidence: linked_evidence_missing" for line in summary_lines)
    assert any(
        line == "Latest BW evidence text: Bill Williams review is filled, but no linked chart evidence is attached yet."
        for line in summary_lines
    )
    assert any(line == "Latest BW evidence follow-up: link_any_chart_evidence" for line in summary_lines)
    assert any(
        line == "Latest BW evidence next step: Link a pre-trade or review chart snapshot to back this Bill Williams review."
        for line in summary_lines
    )
    assert not any(line == "Review detail is sufficient. Standard Finalize is available when you are ready." for line in workflow_lines)
    assert any(line == "Reviewed trade still needs linked chart evidence." for line in workflow_lines)
    assert any(
        line == "Bill Williams review is filled, but no linked chart evidence is attached yet."
        for line in workflow_lines
    )
    assert any(
        line == "Link a pre-trade or review chart snapshot to back this Bill Williams review."
        for line in workflow_lines
    )



def test_desktop_shell_surfaces_current_trade_plan_context_and_restart_recovery() -> None:
    absent_storage = _reset_dir(TMP_ROOT / "plan_context_surfaces_absent")
    controller_absent = DesktopShellController(dataset_handle=FIXTURE, storage_dir=absent_storage)
    controller_absent.buy_market()
    controller_absent.play()
    controller_absent.advance_frame()

    absent_active_workspace = controller_absent.get_workspace_view()
    absent_trade_lines = build_trade_context_lines(absent_active_workspace["trading"], absent_active_workspace["journal"])
    absent_workflow_lines = build_workflow_guidance_lines(
        absent_active_workspace["replay"],
        absent_active_workspace["trading"],
        absent_active_workspace["journal"],
    )
    assert any(line == "Declared plan: absent" for line in absent_trade_lines)
    assert any(line == "Declared plan: absent" for line in absent_workflow_lines)

    controller_absent.manual_close()
    controller_absent.advance_frame()
    absent_closed_workspace = controller_absent.get_workspace_view()
    absent_result_lines = build_latest_result_lines(absent_closed_workspace["journal"])
    assert any(line == "Declared plan: absent" for line in absent_result_lines)

    full_storage = _reset_dir(TMP_ROOT / "plan_context_surfaces_full")
    controller_1 = DesktopShellController(dataset_handle=FIXTURE, storage_dir=full_storage)
    controller_1.create_pre_trade_note(
        content="Full plan note",
        setup_tag="BW_2WM_LONG",
        thesis_summary="expect second wise man continuation",
        risk_plan="protect below local pullback",
    )
    controller_1.buy_market()
    controller_1.play()
    controller_1.advance_frame()

    active_workspace_1 = controller_1.get_workspace_view()
    active_trade_lines_1 = build_trade_context_lines(active_workspace_1["trading"], active_workspace_1["journal"])
    active_workflow_lines_1 = build_workflow_guidance_lines(
        active_workspace_1["replay"],
        active_workspace_1["trading"],
        active_workspace_1["journal"],
    )
    assert any(line == "Declared plan: present" for line in active_trade_lines_1)
    assert any(line == "Declared setup: BW_2WM_LONG" for line in active_trade_lines_1)
    assert any(line == "Thesis summary: expect second wise man continuation" for line in active_trade_lines_1)
    assert any(line == "Risk plan: protect below local pullback" for line in active_trade_lines_1)
    assert any(line == "Declared plan: present" for line in active_workflow_lines_1)
    assert any(line == "Declared setup: BW_2WM_LONG" for line in active_workflow_lines_1)

    controller_2 = DesktopShellController(dataset_handle=FIXTURE, storage_dir=full_storage)
    active_workspace_2 = controller_2.get_workspace_view()
    recovered_active_trade_lines = build_trade_context_lines(active_workspace_2["trading"], active_workspace_2["journal"])
    recovered_active_workflow_lines = build_workflow_guidance_lines(
        active_workspace_2["replay"],
        active_workspace_2["trading"],
        active_workspace_2["journal"],
    )
    assert active_workspace_2["journal"]["recovered"] is True
    assert any(line == "Declared plan: present" for line in recovered_active_trade_lines)
    assert any(line == "Declared setup: BW_2WM_LONG" for line in recovered_active_trade_lines)
    assert any(line == "Declared plan: present" for line in recovered_active_workflow_lines)

    controller_2.manual_close()
    controller_2.advance_frame()
    closed_workspace = controller_2.get_workspace_view()
    closed_result_lines = build_latest_result_lines(closed_workspace["journal"])
    closed_workflow_lines = build_workflow_guidance_lines(
        closed_workspace["replay"],
        closed_workspace["trading"],
        closed_workspace["journal"],
    )
    assert any(line == "Declared plan: present" for line in closed_result_lines)
    assert any(line == "Declared setup: BW_2WM_LONG" for line in closed_result_lines)
    assert any(line == "Thesis summary: expect second wise man continuation" for line in closed_result_lines)
    assert any(line == "Risk plan: protect below local pullback" for line in closed_result_lines)
    assert any(line == "Declared plan: present" for line in closed_workflow_lines)
    assert any(line == "Declared setup: BW_2WM_LONG" for line in closed_workflow_lines)

    controller_3 = DesktopShellController(dataset_handle=FIXTURE, storage_dir=full_storage)
    recovered_closed_workspace = controller_3.get_workspace_view()
    recovered_closed_trade_lines = build_trade_context_lines(recovered_closed_workspace["trading"], recovered_closed_workspace["journal"])
    recovered_closed_result_lines = build_latest_result_lines(recovered_closed_workspace["journal"])
    recovered_closed_workflow_lines = build_workflow_guidance_lines(
        recovered_closed_workspace["replay"],
        recovered_closed_workspace["trading"],
        recovered_closed_workspace["journal"],
    )
    assert recovered_closed_workspace["journal"]["recovered"] is True
    assert any(line == "Declared plan: present" for line in recovered_closed_trade_lines)
    assert any(line == "Declared setup: BW_2WM_LONG" for line in recovered_closed_trade_lines)
    assert any(line == "Declared plan: present" for line in recovered_closed_result_lines)
    assert any(line == "Declared setup: BW_2WM_LONG" for line in recovered_closed_result_lines)
    assert any(line == "Thesis summary: expect second wise man continuation" for line in recovered_closed_result_lines)
    assert any(line == "Risk plan: protect below local pullback" for line in recovered_closed_result_lines)
    assert any(line == "Declared plan: present" for line in recovered_closed_workflow_lines)



def test_desktop_shell_surfaces_pending_stop_entry_and_restart_recovery() -> None:
    pending_storage = _reset_dir(TMP_ROOT / "desktop_pending_stop_pending")
    controller_pending_1 = DesktopShellController(dataset_handle=FIXTURE, storage_dir=pending_storage)
    controller_pending_1.sell_stop(trigger_price=1.10344, stop_loss=1.10360, take_profit=1.10330)

    pending_workspace_1 = controller_pending_1.get_workspace_view()
    pending_trade_lines_1 = build_trade_context_lines(pending_workspace_1["trading"], pending_workspace_1["journal"])
    pending_workflow_lines_1 = build_workflow_guidance_lines(
        pending_workspace_1["replay"],
        pending_workspace_1["trading"],
        pending_workspace_1["journal"],
    )
    pending_button_map_1 = build_button_state_map(
        pending_workspace_1["replay"],
        pending_workspace_1["trading"],
        pending_workspace_1["journal"],
    )
    assert any(line == "Pending stop: yes" for line in pending_trade_lines_1)
    assert any(line == "Pending stop side: sell" for line in pending_trade_lines_1)
    assert any(line == "Pending stop trigger: 1.10344" for line in pending_trade_lines_1)
    assert any(line == "Pending stop status: placed" for line in pending_trade_lines_1)
    assert any(line == "Pending stop SL / TP: 1.1036 / 1.1033" for line in pending_trade_lines_1)
    pending_finalization_lines_1 = build_finalization_lines(pending_workspace_1["journal"], pending_workspace_1["trading"])
    pending_blocker_lines_1 = build_finalization_blocker_lines(pending_workspace_1["journal"], pending_workspace_1["trading"])
    assert any(line == "Pending stop entry is staged for the current one-trade replay loop." for line in pending_workflow_lines_1)
    assert any(line == "Trade lifecycle focus: pending_entry_staged" for line in pending_trade_lines_1)
    assert any(line == "Trade lifecycle text: Pending entry is staged; no active trade is open yet." for line in pending_trade_lines_1)
    assert any(line == "Trade lifecycle in progress: pending_entry_staged" for line in pending_finalization_lines_1)
    assert any(line == "A pending entry is still staged." for line in pending_blocker_lines_1)
    assert pending_button_map_1["cancel_entry"] is True
    assert pending_button_map_1["buy_stop"] is False
    assert pending_button_map_1["sell_stop"] is False

    controller_pending_2 = DesktopShellController(dataset_handle=FIXTURE, storage_dir=pending_storage)
    pending_workspace_2 = controller_pending_2.get_workspace_view()
    pending_trade_lines_2 = build_trade_context_lines(pending_workspace_2["trading"], pending_workspace_2["journal"])
    assert pending_workspace_2["journal"]["recovered"] is True
    assert any(line == "Pending stop: yes" for line in pending_trade_lines_2)
    assert any(line == "Pending stop side: sell" for line in pending_trade_lines_2)
    assert any(line == "Pending stop trigger: 1.10344" for line in pending_trade_lines_2)

    controller_pending_2.cancel_pending_entry()
    cancelled_workspace = controller_pending_2.get_workspace_view()
    cancelled_trade_lines = build_trade_context_lines(cancelled_workspace["trading"], cancelled_workspace["journal"])
    cancelled_button_map = build_button_state_map(
        cancelled_workspace["replay"],
        cancelled_workspace["trading"],
        cancelled_workspace["journal"],
    )
    assert any(line == "Pending stop: no" for line in cancelled_trade_lines)
    assert any(line == "Pending stop result: cancelled" for line in cancelled_trade_lines)
    assert cancelled_button_map["cancel_entry"] is False
    assert cancelled_button_map["buy_stop"] is True

    triggered_storage = _reset_dir(TMP_ROOT / "desktop_pending_stop_triggered")
    controller_trigger_1 = DesktopShellController(dataset_handle=FIXTURE, storage_dir=triggered_storage)
    controller_trigger_1.buy_stop(trigger_price=1.10364, stop_loss=1.10340, take_profit=1.10370)
    controller_trigger_1.play()
    controller_trigger_1.advance_frame()
    waiting_workspace = controller_trigger_1.get_workspace_view()
    waiting_trade_lines = build_trade_context_lines(waiting_workspace["trading"], waiting_workspace["journal"])
    assert any(line == "Pending stop: yes" for line in waiting_trade_lines)
    assert any(line == "Pending stop status: placed" for line in waiting_trade_lines)

    controller_trigger_1.advance_frame()
    triggered_workspace_1 = controller_trigger_1.get_workspace_view()
    triggered_trade_lines_1 = build_trade_context_lines(triggered_workspace_1["trading"], triggered_workspace_1["journal"])
    triggered_workflow_lines_1 = build_workflow_guidance_lines(
        triggered_workspace_1["replay"],
        triggered_workspace_1["trading"],
        triggered_workspace_1["journal"],
    )
    assert any(line == "Active trade: yes" for line in triggered_trade_lines_1)
    assert any(line == "Pending stop: no" for line in triggered_trade_lines_1)
    assert any(line == "Pending stop result: triggered" for line in triggered_trade_lines_1)
    assert any(line == "Last execution reason: pending_stop_trigger" for line in triggered_trade_lines_1)
    assert any(line == "Protection present: yes" for line in triggered_trade_lines_1)
    assert any(line == "Active trade is open while replay is running." for line in triggered_workflow_lines_1)

    controller_trigger_2 = DesktopShellController(dataset_handle=FIXTURE, storage_dir=triggered_storage)
    triggered_workspace_2 = controller_trigger_2.get_workspace_view()
    recovered_triggered_trade_lines = build_trade_context_lines(triggered_workspace_2["trading"], triggered_workspace_2["journal"])
    assert triggered_workspace_2["journal"]["recovered"] is True
    assert any(line == "Active trade: yes" for line in recovered_triggered_trade_lines)
    assert any(line == "Pending stop result: triggered" for line in recovered_triggered_trade_lines)
    assert any(line == "Last execution reason: pending_stop_trigger" for line in recovered_triggered_trade_lines)


def _install_desktop_memory_storage(monkeypatch: pytest.MonkeyPatch, storage_dir: Path) -> Path:
    storage_path = storage_dir / "local_runtime_state.json"
    payloads: dict[str, str] = {}
    real_exists = Path.exists
    real_mkdir = Path.mkdir
    real_write_text = Path.write_text
    real_read_text = Path.read_text

    def patched_exists(self: Path) -> bool:
        if self == storage_dir:
            return True
        if self == storage_path:
            return storage_path.as_posix() in payloads
        return real_exists(self)

    def patched_mkdir(self: Path, mode: int = 0o777, parents: bool = False, exist_ok: bool = False) -> None:
        if self == storage_dir:
            return None
        return real_mkdir(self, mode=mode, parents=parents, exist_ok=exist_ok)

    def patched_write_text(self: Path, data: str, encoding: str | None = None, errors: str | None = None, newline: str | None = None) -> int:
        if self == storage_path:
            payloads[storage_path.as_posix()] = data
            return len(data)
        return real_write_text(self, data, encoding=encoding, errors=errors, newline=newline)

    def patched_read_text(self: Path, encoding: str | None = None, errors: str | None = None) -> str:
        if self == storage_path:
            return payloads[storage_path.as_posix()]
        return real_read_text(self, encoding=encoding, errors=errors)

    monkeypatch.setattr(Path, "exists", patched_exists)
    monkeypatch.setattr(Path, "mkdir", patched_mkdir)
    monkeypatch.setattr(Path, "write_text", patched_write_text)
    monkeypatch.setattr(Path, "read_text", patched_read_text)
    return storage_dir


def test_desktop_shell_surfaces_partial_close_and_restart_recovery(monkeypatch: pytest.MonkeyPatch) -> None:
    storage_dir = _install_desktop_memory_storage(monkeypatch, Path("memory/desktop-partial-close"))
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=storage_dir,
    )

    controller.buy_market(stop_loss=1.10351)
    controller.play()
    controller.advance_frame()
    controller.partial_close(0.5)
    workspace = controller.advance_frame()

    trading_view = workspace["trading"]
    journal_view = workspace["journal"]
    trade_lines = build_trade_context_lines(trading_view, journal_view)
    latest_result_lines = build_latest_result_lines(journal_view, trading_view)
    workflow_lines = build_workflow_guidance_lines(workspace["replay"], trading_view, journal_view)
    button_map = build_button_state_map(workspace["replay"], trading_view, journal_view)

    assert trading_view["trade_status"] == "partially_closed"
    assert trading_view["trade_partially_closed"] is True
    assert trading_view["current_open_volume"] == pytest.approx(0.5)
    assert any(line == "Trade partially closed: yes" for line in trade_lines)
    assert any(line == "Trade lifecycle focus: active_trade_partially_closed" for line in trade_lines)
    assert any(line == "Trade lifecycle text: Active trade remains open after a partial close." for line in trade_lines)
    assert any(line == "Partial close available: yes" for line in trade_lines)
    assert latest_result_lines[0] == "Latest result: active trade is partially closed"
    assert any(line == "Remaining open volume: 0.5" for line in latest_result_lines)
    assert any("partial close" in line.lower() for line in workflow_lines)
    assert button_map["partial_close"] is True

    recovered = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=storage_dir,
    )
    recovered_workspace = recovered.get_workspace_view()
    recovered_trading = recovered_workspace["trading"]
    recovered_journal = recovered_workspace["journal"]

    assert recovered_journal["recovered"] is True
    assert recovered_trading["trade_status"] == "partially_closed"
    assert recovered_trading["current_open_volume"] == pytest.approx(0.5)

    recovered.play()
    recovered.advance_frame()
    final_workspace = recovered.get_workspace_view()
    assert final_workspace["trading"]["trade_status"] == "closed"
    assert final_workspace["trading"]["last_close_reason"] == "stop_loss_hit"


def test_desktop_shell_surfaces_recovered_market_entry_pending_startup_state() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "market_entry_pending_startup")
    controller_1 = DesktopShellController(dataset_handle=FIXTURE, storage_dir=storage_dir)
    controller_1.buy_market()
    controller_1.play()

    controller_2 = DesktopShellController(dataset_handle=FIXTURE, storage_dir=storage_dir)
    workspace = controller_2.get_workspace_view()
    trade_lines = build_trade_context_lines(workspace["trading"], workspace["journal"])
    workflow_lines = build_workflow_guidance_lines(workspace["replay"], workspace["trading"], workspace["journal"])
    finalization_lines = build_finalization_lines(workspace["journal"], workspace["trading"])
    blocker_lines = build_finalization_blocker_lines(workspace["journal"], workspace["trading"])
    button_map = build_button_state_map(workspace["replay"], workspace["trading"], workspace["journal"])

    assert workspace["journal"]["recovered"] is True
    assert workspace["trading"]["lifecycle_state"] == "EntryRequested"
    assert workspace["trading"]["entry_pending_present"] is True
    assert any(line == "Pending entry: yes" for line in trade_lines)
    assert any(line == "Trade lifecycle focus: market_entry_pending" for line in trade_lines)
    assert any(line == "Trade lifecycle text: Market entry is already staged and awaiting the next replay fill; no active trade is open yet." for line in trade_lines)
    assert any(line == "A market entry is already staged for the current one-trade replay loop." for line in workflow_lines)
    assert any(line == "Trade lifecycle in progress: market_entry_pending" for line in finalization_lines)
    assert any(line == "A staged entry is still in progress." for line in blocker_lines)
    assert button_map["buy"] is False
    assert button_map["sell"] is False


def test_desktop_shell_readiness_and_pause_reports_surface_recovered_market_entry_pending_state() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "market_entry_pending_readiness")
    controller = DesktopShellController(dataset_handle=FIXTURE, storage_dir=storage_dir)
    controller.buy_market()
    controller.play()

    config = DesktopLaunchConfig(dataset_handle=str(FIXTURE), storage_dir=storage_dir, replay_mode="training")
    readiness = build_readiness_snapshot(config)
    readiness_report = format_readiness_report(readiness)
    pause_point = build_mvp_pause_point_snapshot(config)
    pause_report = format_mvp_pause_point_report(pause_point)

    assert readiness.recovered is True
    assert readiness.lifecycle_label == "market_entry_pending"
    assert readiness.lifecycle_text == "Market entry is already staged and awaiting the next replay fill; no active trade is open yet."
    assert "Trade lifecycle: market_entry_pending" in readiness_report
    assert "Lifecycle text: Market entry is already staged and awaiting the next replay fill; no active trade is open yet." in readiness_report
    assert "Trade lifecycle: market_entry_pending" in pause_report
    assert "Lifecycle text: Market entry is already staged and awaiting the next replay fill; no active trade is open yet." in pause_report


def test_desktop_main_screen_layout_spec_makes_chart_primary_and_debug_secondary() -> None:
    layout = build_main_screen_layout_spec()

    assert layout["screen_reading_order"] == [
        "chart_area",
        "replay_and_trading_actions",
        "compact_context",
        "review_entry",
        "secondary_debug",
    ]
    assert layout["zones"]["chart_area"]["dominance"] == "largest"
    assert layout["zones"]["chart_area"]["weight"] > layout["zones"]["right_workspace_rail"]["weight"]
    assert layout["zones"]["secondary_debug"]["placement"] == "below_primary_workspace"
    assert "compact_action_snapshot" in layout["primary_surface_allows"]
    assert "long_readiness_prose" in layout["primary_surface_excludes"]
    assert "raw_chart_bar_dump" in layout["primary_surface_excludes"]
    assert "debug_chart_detail" in layout["zones"]["secondary_debug"]["includes"]
    assert layout["zones"]["chart_area"]["primary_footer"] == "compact_chart_summary_only"


def test_desktop_primary_chart_footer_stays_compact_while_debug_keeps_recent_bars() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "primary_chart_footer"),
    )

    controller.play()
    for _ in range(12):
        controller.advance_frame()
    chart_context = controller.get_workspace_view()["replay"]["chart_context"]

    primary_footer = build_primary_chart_footer_lines(chart_context)
    debug_lines = build_tick_table_lines(chart_context, limit=4)

    assert any(line.startswith("Bars:") for line in primary_footer)
    assert any(line.startswith("AO pane:") for line in primary_footer)
    assert all("Recent bars:" not in line for line in primary_footer)
    assert debug_lines[0] == "Recent bars:"


def test_desktop_workspace_bar_lines_surface_compact_replay_and_trade_state() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "workspace_bar_lines"),
    )

    workspace = controller.get_workspace_view()
    bar_lines = build_workspace_bar_lines(workspace["replay"], workspace["trading"])

    assert len(bar_lines) == 2
    assert "Instrument:" in bar_lines[0]
    assert "Dataset:" in bar_lines[0]
    assert "Mode:" in bar_lines[0]
    assert "Time:" in bar_lines[1]
    assert "Replay:" in bar_lines[1]
    assert "Speed:" in bar_lines[1]
    assert "Trade:" in bar_lines[1]


def test_desktop_primary_workflow_snapshot_stays_short_and_actionable() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "primary_workflow_snapshot"),
    )

    snapshot_lines = build_primary_workflow_snapshot_lines(
        controller.get_workspace_view()["replay"],
        controller.get_workspace_view()["trading"],
        controller.get_workspace_view()["journal"],
        {"level": "info", "summary": "Workspace ready", "detail": "Verbose details stay secondary."},
    )

    assert snapshot_lines[0] == "Action snapshot:"
    assert len(snapshot_lines) <= 4
    assert any(line.startswith("Ready:") or line.startswith("Recent action:") for line in snapshot_lines[1:])
    assert all("Workflow guidance:" not in line for line in snapshot_lines)
    assert all("Dataset quality context:" not in line for line in snapshot_lines)
    assert all("Verbose details stay secondary." not in line for line in snapshot_lines)


def test_desktop_compact_context_and_review_entry_stay_factual() -> None:
    controller = DesktopShellController(
        dataset_handle=FIXTURE,
        storage_dir=_reset_dir(TMP_ROOT / "workspace_compact_context"),
    )

    controller.buy_stop(trigger_price=1.10364, stop_loss=1.10340, take_profit=1.10370)
    workspace = controller.get_workspace_view()
    compact_lines = build_compact_context_lines(workspace["trading"], workspace["journal"])
    review_lines = build_review_entry_lines(workspace["journal"])

    assert any(line == "Active trade: no" for line in compact_lines)
    assert any(line == "Pending entry: yes (buy stop @ 1.10364)" for line in compact_lines)
    assert any(line.startswith("SL / TP: 1.1034 / 1.1037") for line in compact_lines)
    assert all("Trade lifecycle text:" not in line for line in compact_lines)
    assert all("Recovery follow-up:" not in line for line in compact_lines)
    assert any(line.startswith("PreTradeNotes:") for line in review_lines)
    assert any(line.startswith("Review pending trade:") for line in review_lines)
    assert any(line.startswith("Next review action:") for line in review_lines)


def test_desktop_shell_start_flow_new_session_and_resume_split_recovery_honestly() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "startup_recovery_split")
    config = DesktopLaunchConfig(dataset_handle=str(FIXTURE), storage_dir=storage_dir, replay_mode="training")

    controller_1 = DesktopShellController(dataset_handle=FIXTURE, storage_dir=storage_dir)
    controller_1.buy_market()
    assert has_local_session_state(storage_dir) is True

    resumed_controller, resumed_selection = build_controller_from_start_selection(config, "resume_last_local_session")
    resumed_workspace = resumed_controller.get_workspace_view()
    assert resumed_selection.label == "Resume last local session"
    assert resumed_workspace["journal"]["recovered"] is True

    new_session_controller, new_session_selection = build_controller_from_start_selection(config, "start_new_session")
    new_session_workspace = new_session_controller.get_workspace_view()
    assert new_session_selection.label == "Start new session"
    assert new_session_workspace["journal"]["recovered"] is False


def test_desktop_shell_start_flow_prepared_and_raw_paths_route_into_workspace() -> None:
    storage_dir = _reset_dir(TMP_ROOT / "startup_paths_to_workspace")
    config = DesktopLaunchConfig(dataset_handle=str(FIXTURE), storage_dir=storage_dir, replay_mode="training", instrument_id="EURUSD")

    prepared_controller, prepared_selection = build_controller_from_start_selection(
        config,
        "open_prepared_dataset",
        selected_path=FIXTURE,
    )
    prepared_workspace = prepared_controller.get_workspace_view()
    assert prepared_selection.label == "Open prepared dataset"
    assert prepared_workspace["replay"]["dataset_id"] == "eurusd-sample-v1"
    assert prepared_workspace["journal"]["recovered"] is False

    raw_dir = _reset_dir(TMP_ROOT / "startup_raw_import")
    raw_path = raw_dir / "eurusd_raw.csv"
    raw_path.write_text(
        "timestamp,bid,ask\n"
        "2024-01-01T00:00:00Z,1.10000,1.10020\n"
        "2024-01-01T00:00:01Z,1.10010,1.10030\n",
        encoding="utf-8",
    )
    raw_config = DesktopLaunchConfig(
        dataset_handle=str(FIXTURE),
        storage_dir=raw_dir / "storage",
        replay_mode="training",
        instrument_id="EURUSD",
    )
    raw_controller, raw_selection = build_controller_from_start_selection(
        raw_config,
        "import_raw_historical_data",
        selected_path=raw_path,
    )
    raw_workspace = raw_controller.get_workspace_view()
    assert raw_selection.label == "Import raw historical data"
    assert raw_selection.selected_path == str(raw_path)
    assert raw_workspace["replay"]["dataset_id"].startswith("eurusd-raw-")
    assert raw_workspace["journal"]["recovered"] is False


def test_desktop_shell_start_flow_resolution_requires_explicit_external_paths() -> None:
    config = DesktopLaunchConfig(dataset_handle=str(FIXTURE), storage_dir=TMP_ROOT / "startup_resolution_validation", replay_mode="training")

    with pytest.raises(ValueError):
        resolve_start_selection(config, "open_prepared_dataset")
    with pytest.raises(ValueError):
        resolve_start_selection(config, "import_raw_historical_data")
