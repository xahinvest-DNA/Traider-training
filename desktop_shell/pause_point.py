from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Sequence

from .launch import DesktopLaunchConfig, parse_launch_args
from .readiness import DesktopReadinessSnapshot, build_readiness_snapshot


@dataclass(frozen=True)
class MVPPausePointSnapshot:
    mvp_status: str
    desktop_status: str
    acceptance_status: str
    launch_status: str
    readiness_status: str
    replay_status: str
    session_status: str
    summary_status: str
    finalization_link_status: str
    finalization_link_text: str
    recovery_note_status: str
    recovery_note_text: str
    recovery_acknowledgment_status: str
    recovery_acknowledgment_text: str
    recovery_acknowledged_at: str
    lifecycle_label: str
    lifecycle_text: str
    is_session_finalized: bool
    next_expansion_gate: str
    preserved_boundaries: tuple[str, ...]
    deferred_areas: tuple[str, ...]
    launch_commands: tuple[str, ...]


def build_mvp_pause_point_snapshot(config: DesktopLaunchConfig) -> MVPPausePointSnapshot:
    readiness = build_readiness_snapshot(config)
    return MVPPausePointSnapshot(
        mvp_status="accepted",
        desktop_status="usable",
        acceptance_status="desktop_smoke_passed",
        launch_status="predictable_local_launch",
        readiness_status="handoff_ready",
        replay_status=readiness.replay_status,
        session_status=readiness.session_status,
        summary_status=readiness.summary_status,
        finalization_link_status=readiness.finalization_link_status,
        finalization_link_text=readiness.finalization_link_text,
        recovery_note_status=readiness.recovery_note_status,
        recovery_note_text=readiness.recovery_note_text,
        recovery_acknowledgment_status=readiness.recovery_acknowledgment_status,
        recovery_acknowledgment_text=readiness.recovery_acknowledgment_text,
        recovery_acknowledged_at=readiness.recovery_acknowledged_at,
        lifecycle_label=readiness.lifecycle_label,
        lifecycle_text=readiness.lifecycle_text,
        is_session_finalized=readiness.is_session_finalized,
        next_expansion_gate="requires new bounded slice after MVP freeze",
        preserved_boundaries=(
            "desktop remains thin projection consumer",
            "trade facts stay in DATA_SCHEMA source of truth",
            "session/journal facts stay in JOURNAL_SCHEMA source of truth",
            "analytics stays derive-on-read",
        ),
        deferred_areas=(
            "dashboards",
            "mentor workflow",
            "mobile",
            "sync",
            "packaging/platform engineering",
            "multi-session shell",
        ),
        launch_commands=readiness.launch_commands,
    )


def format_mvp_pause_point_report(snapshot: MVPPausePointSnapshot) -> str:
    finalized = "yes" if snapshot.is_session_finalized else "no"
    recovery_followup = _format_recovery_followup(snapshot.recovery_acknowledgment_status, snapshot.recovery_acknowledgment_text)
    boundaries = "\n".join(f"- {item}" for item in snapshot.preserved_boundaries)
    deferred = "\n".join(f"- {item}" for item in snapshot.deferred_areas)
    commands = "\n".join(f"- {item}" for item in snapshot.launch_commands)
    return (
        "MVP pause point\n"
        f"MVP status: {snapshot.mvp_status}\n"
        f"Desktop status: {snapshot.desktop_status}\n"
        f"Acceptance: {snapshot.acceptance_status}\n"
        f"Launch: {snapshot.launch_status}\n"
        f"Readiness: {snapshot.readiness_status}\n"
        f"Replay status: {snapshot.replay_status}\n"
        f"Session status: {snapshot.session_status}\n"
        f"Summary status: {snapshot.summary_status}\n"
        f"Finalization link: {snapshot.finalization_link_status}\n"
        f"Finalization text: {snapshot.finalization_link_text}\n"
        f"Recovery note: {snapshot.recovery_note_status}\n"
        f"Recovery text: {snapshot.recovery_note_text}\n"
        f"Recovery follow-up: {recovery_followup}\n"
        f"Recovery acknowledged at: {snapshot.recovery_acknowledged_at}\n"
        f"Trade lifecycle: {snapshot.lifecycle_label}\n"
        f"Lifecycle text: {snapshot.lifecycle_text}\n"
        f"Session finalized: {finalized}\n"
        f"Expansion gate: {snapshot.next_expansion_gate}\n"
        "Preserved boundaries:\n"
        f"{boundaries}\n"
        "Deferred areas:\n"
        f"{deferred}\n"
        "Launch commands:\n"
        f"{commands}"
    )


def mvp_pause_point_to_json(snapshot: MVPPausePointSnapshot) -> str:
    payload = asdict(snapshot)
    payload["preserved_boundaries"] = list(snapshot.preserved_boundaries)
    payload["deferred_areas"] = list(snapshot.deferred_areas)
    payload["launch_commands"] = list(snapshot.launch_commands)
    return json.dumps(payload, indent=2)


def run_mvp_pause_point_report(argv: Sequence[str] | None = None) -> str:
    json_mode = False
    args_list = list(argv) if argv is not None else None
    if args_list is not None and "--json" in args_list:
        json_mode = True
        args_list = [arg for arg in args_list if arg != "--json"]
    config = parse_launch_args(argv=args_list)
    snapshot = build_mvp_pause_point_snapshot(config)
    return mvp_pause_point_to_json(snapshot) if json_mode else format_mvp_pause_point_report(snapshot)


def main(argv: Sequence[str] | None = None) -> None:
    print(run_mvp_pause_point_report(argv=argv))


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])


def _format_recovery_followup(status: str, text_value: str) -> str:
    if status in {"acknowledgment_needed", "acknowledged"}:
        return text_value
    return "none"
