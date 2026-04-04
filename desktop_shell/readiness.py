from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Sequence

from .launch import DesktopLaunchConfig, build_controller_from_launch_config, parse_launch_args, resolve_dataset_handle


@dataclass(frozen=True)
class DesktopReadinessSnapshot:
    dataset_handle: str
    storage_dir: str
    replay_mode: str
    replay_status: str
    simulation_time: str
    dataset_quality_status: str
    import_warning_count: int
    import_warning_preview: str
    finalization_link_status: str
    finalization_link_text: str
    recovery_note_status: str
    recovery_note_text: str
    recovery_acknowledgment_status: str
    recovery_acknowledgment_text: str
    recovery_acknowledged_at: str
    session_status: str
    summary_status: str
    review_pending_trade_id: str | None
    is_session_finalized: bool
    recovered: bool
    launch_commands: tuple[str, ...]


def build_readiness_snapshot(config: DesktopLaunchConfig) -> DesktopReadinessSnapshot:
    resolved_dataset_handle = resolve_dataset_handle(config)
    controller = build_controller_from_launch_config(
        DesktopLaunchConfig(
            dataset_handle=resolved_dataset_handle,
            storage_dir=config.storage_dir,
            replay_mode=config.replay_mode,
            instrument_id=config.instrument_id,
            market_profile=config.market_profile,
            price_precision=config.price_precision,
            timezone_canonical=config.timezone_canonical,
            import_output_root=config.import_output_root,
        )
    )
    workspace = controller.get_workspace_view()
    dataset_quality = workspace["replay"].get("dataset_quality") or {}
    finalization_link = workspace["journal"]["session_finalization"].get("dataset_quality_finalization_link") or {}
    recovery_note = workspace["journal"].get("dataset_quality_recovery_note") or {}
    recovery_ack = workspace["journal"].get("dataset_quality_recovery_acknowledgment") or {}
    return DesktopReadinessSnapshot(
        dataset_handle=resolved_dataset_handle,
        storage_dir=str(config.storage_dir),
        replay_mode=config.replay_mode,
        replay_status=workspace["replay"]["status"],
        simulation_time=workspace["replay"]["simulation_time"],
        dataset_quality_status=str(dataset_quality.get("status") or "unknown"),
        import_warning_count=int(dataset_quality.get("warning_count") or 0),
        import_warning_preview=str(dataset_quality.get("warning_preview") or "none"),
        finalization_link_status=str(finalization_link.get("link_status") or "no_finalization_link"),
        finalization_link_text=str(finalization_link.get("link_text") or "none"),
        recovery_note_status=str(recovery_note.get("note_status") or "no_recovery_note"),
        recovery_note_text=str(recovery_note.get("note_text") or "none"),
        recovery_acknowledgment_status=str(recovery_ack.get("acknowledgment_status") or "not_applicable"),
        recovery_acknowledgment_text=str(recovery_ack.get("status_text") or recovery_ack.get("prompt_text") or "none"),
        recovery_acknowledged_at=str(recovery_ack.get("acknowledged_at") or "none"),
        session_status=workspace["journal"]["session_status"],
        summary_status=workspace["journal"]["session_review_summary"]["summary_status"],
        review_pending_trade_id=workspace["journal"]["review_pending_trade_id"],
        is_session_finalized=workspace["journal"]["session_finalization"]["is_session_finalized"],
        recovered=workspace["journal"]["recovered"],
        launch_commands=(
            "python run_desktop_shell_gui.py",
            "python -m desktop_shell",
            "python run_desktop_shell.py",
        ),
    )


def format_readiness_report(snapshot: DesktopReadinessSnapshot) -> str:
    pending_trade = snapshot.review_pending_trade_id or "none"
    finalized = "yes" if snapshot.is_session_finalized else "no"
    recovered = "yes" if snapshot.recovered else "no"
    recovery_followup = _format_recovery_followup(snapshot.recovery_acknowledgment_status, snapshot.recovery_acknowledgment_text)
    launch_lines = "\n".join(f"- {command}" for command in snapshot.launch_commands)
    return (
        "Desktop readiness\n"
        f"Dataset: {snapshot.dataset_handle}\n"
        f"Storage: {snapshot.storage_dir}\n"
        f"Replay mode: {snapshot.replay_mode}\n"
        f"Replay status: {snapshot.replay_status} @ {snapshot.simulation_time}\n"
        f"Dataset quality: {snapshot.dataset_quality_status}\n"
        f"Import warnings: {snapshot.import_warning_count} ({snapshot.import_warning_preview})\n"
        f"Finalization link: {snapshot.finalization_link_status}\n"
        f"Finalization text: {snapshot.finalization_link_text}\n"
        f"Recovery note: {snapshot.recovery_note_status}\n"
        f"Recovery text: {snapshot.recovery_note_text}\n"
        f"Recovery follow-up: {recovery_followup}\n"
        f"Recovery acknowledged at: {snapshot.recovery_acknowledged_at}\n"
        f"Session status: {snapshot.session_status}\n"
        f"Summary status: {snapshot.summary_status}\n"
        f"Pending review trade: {pending_trade}\n"
        f"Session finalized: {finalized}\n"
        f"Recovered state: {recovered}\n"
        "Launch commands:\n"
        f"{launch_lines}"
    )


def readiness_snapshot_to_json(snapshot: DesktopReadinessSnapshot) -> str:
    payload = asdict(snapshot)
    payload["launch_commands"] = list(snapshot.launch_commands)
    return json.dumps(payload, indent=2)


def run_readiness_report(argv: Sequence[str] | None = None) -> str:
    json_mode = False
    args_list = list(argv) if argv is not None else None
    if args_list is not None and "--json" in args_list:
        json_mode = True
        args_list = [arg for arg in args_list if arg != "--json"]
    config = parse_launch_args(argv=args_list)
    snapshot = build_readiness_snapshot(config)
    return readiness_snapshot_to_json(snapshot) if json_mode else format_readiness_report(snapshot)


def main(argv: Sequence[str] | None = None) -> None:
    print(run_readiness_report(argv=argv))


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])


def _format_recovery_followup(status: str, text_value: str) -> str:
    if status in {"acknowledgment_needed", "acknowledged"}:
        return text_value
    return "none"
