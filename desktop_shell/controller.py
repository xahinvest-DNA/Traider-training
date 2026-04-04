from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime_bootstrap import (
    LocalJournalRuntime,
    MinimalTradingLoop,
    build_desktop_journal_view,
    build_desktop_replay_view,
    build_desktop_trading_view,
    create_replay_session,
)


class DesktopShellController:
    def __init__(
        self,
        dataset_handle: str | Path,
        storage_dir: str | Path,
        replay_mode: str = "training",
    ) -> None:
        self.dataset_handle = str(dataset_handle)
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.replay_session = create_replay_session(self.dataset_handle, replay_mode=replay_mode)
        self.trading_loop = MinimalTradingLoop(self.replay_session)
        self.journal_runtime = LocalJournalRuntime(
            self.replay_session,
            self.trading_loop,
            self.storage_dir,
        )

    def get_workspace_view(self) -> dict[str, Any]:
        return {
            "replay": build_desktop_replay_view(self.replay_session),
            "trading": build_desktop_trading_view(self.trading_loop),
            "journal": build_desktop_journal_view(self.journal_runtime),
        }

    def play(self) -> dict[str, Any]:
        self.replay_session.play()
        return self.get_workspace_view()

    def pause(self) -> dict[str, Any]:
        self.replay_session.pause()
        return self.get_workspace_view()

    def advance_frame(self) -> dict[str, Any]:
        self.replay_session.advance_frame()
        return self.get_workspace_view()

    def set_speed(self, speed_multiplier: float) -> dict[str, Any]:
        self.replay_session.set_speed(speed_multiplier)
        return self.get_workspace_view()

    def seek_to(self, target_timestamp: str) -> dict[str, Any]:
        self.replay_session.seek_to(target_timestamp)
        return self.get_workspace_view()

    def buy_market(self, volume: float = 1.0) -> dict[str, Any]:
        self.trading_loop.buy_market(volume=volume)
        return self.get_workspace_view()

    def sell_market(self, volume: float = 1.0) -> dict[str, Any]:
        self.trading_loop.sell_market(volume=volume)
        return self.get_workspace_view()

    def manual_close(self) -> dict[str, Any]:
        self.trading_loop.manual_close()
        return self.get_workspace_view()

    def create_chart_snapshot(
        self,
        artifact_ref: str,
        artifact_type: str = "image_path",
        snapshot_role: str = "review_context",
    ) -> dict[str, Any]:
        self.journal_runtime.create_chart_snapshot(
            artifact_ref=artifact_ref,
            artifact_type=artifact_type,
            snapshot_role=snapshot_role,
        )
        return self.get_workspace_view()

    def create_pre_trade_note(
        self,
        content: str,
        setup_tag: str | None = None,
        thesis_summary: str | None = None,
        risk_plan: str | None = None,
        chart_snapshot_ref: str | None = None,
    ) -> dict[str, Any]:
        self.journal_runtime.create_pre_trade_note(
            content=content,
            setup_tag=setup_tag,
            thesis_summary=thesis_summary,
            risk_plan=risk_plan,
            chart_snapshot_ref=chart_snapshot_ref,
        )
        return self.get_workspace_view()

    def create_post_trade_review(
        self,
        content: str,
        setup_tag: str | None = None,
        compliance_label: str | None = None,
        review_tags: tuple[str, ...] | list[str] = (),
        discipline_assessment: str | None = None,
        improvement_actions: str | None = None,
        setup_variant: str | None = None,
        entry_timing_label: str | None = None,
        market_context_label: str | None = None,
        exit_quality_label: str | None = None,
        review_clarity_label: str | None = None,
        chart_snapshot_refs: tuple[str, ...] | list[str] = (),
    ) -> dict[str, Any]:
        self.journal_runtime.create_post_trade_review(
            content=content,
            setup_tag=setup_tag,
            compliance_label=compliance_label,
            review_tags=review_tags,
            discipline_assessment=discipline_assessment,
            improvement_actions=improvement_actions,
            setup_variant=setup_variant,
            entry_timing_label=entry_timing_label,
            market_context_label=market_context_label,
            exit_quality_label=exit_quality_label,
            review_clarity_label=review_clarity_label,
            chart_snapshot_refs=chart_snapshot_refs,
        )
        return self.get_workspace_view()

    def create_behavioral_flag(
        self,
        flag_code: str,
        description: str | None = None,
    ) -> dict[str, Any]:
        self.journal_runtime.create_behavioral_flag(
            flag_code=flag_code,
            description=description,
        )
        return self.get_workspace_view()

    def create_rule_violation(
        self,
        rule_code: str,
        description: str | None = None,
    ) -> dict[str, Any]:
        self.journal_runtime.create_rule_violation(
            rule_code=rule_code,
            description=description,
        )
        return self.get_workspace_view()

    def finalize_session(self, force: bool = False, reason: str = "user_completed") -> dict[str, Any]:
        self.journal_runtime.finalize_session(force=force, reason=reason)
        return self.get_workspace_view()

    def acknowledge_recovery_context(self) -> dict[str, Any]:
        self.journal_runtime.acknowledge_recovery_context()
        return self.get_workspace_view()
