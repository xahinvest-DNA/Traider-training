from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .dataset_loader import load_normalized_dataset
from .errors import ModeRestrictionError, OutOfBoundsSeekError, ReplayFinishedError
from .types import (
    ExecutionSnapshot,
    NormalizedDataset,
    ReplayEvent,
    ReplayState,
    SUPPORTED_REPLAY_MODES,
)

Subscriber = Callable[[ReplayEvent], None]


class ReplaySession:
    def __init__(
        self,
        dataset: NormalizedDataset,
        replay_mode: str,
        active_timeframe: str | None = None,
        synchronized_timeframes: tuple[str, ...] | None = None,
    ) -> None:
        if replay_mode not in SUPPORTED_REPLAY_MODES:
            raise ValueError(f"Unsupported replay mode: {replay_mode}")

        current_tick = dataset.ticks[0]
        self.dataset = dataset
        self.subscribers: list[Subscriber] = []
        self.events: list[ReplayEvent] = []
        self.state = ReplayState(
            dataset_id=dataset.dataset_id,
            instrument_id=dataset.instrument_id,
            market_profile=dataset.market_profile,
            replay_mode=replay_mode,
            active_timeframe=active_timeframe or dataset.active_timeframe,
            synchronized_timeframes=(
                synchronized_timeframes or dataset.synchronized_timeframes
            ),
            dataset_start_time=dataset.dataset_start_time,
            dataset_end_time=dataset.dataset_end_time,
            time_cursor=0,
            simulation_time=current_tick.timestamp,
            speed_multiplier=1.0,
            is_paused=True,
            is_finished=False,
            current_tick=current_tick,
            recent_ticks=[current_tick],
        )
        self._publish(
            "TimeframeSynced",
            {
                "active_timeframe": self.state.active_timeframe,
                "synchronized_timeframes": list(self.state.synchronized_timeframes),
            },
        )

    def subscribe(self, handler: Subscriber) -> None:
        self.subscribers.append(handler)

    def play(self) -> ReplayState:
        if self.state.is_finished:
            raise ReplayFinishedError("Replay already finished")
        if self.state.is_paused:
            self.state.is_paused = False
            self._publish(
                "ReplayResumed",
                {"speed_multiplier": self.state.speed_multiplier},
            )
        return self.state

    def pause(self) -> ReplayState:
        if not self.state.is_paused:
            self.state.is_paused = True
            self._publish("ReplayPaused", {})
        return self.state

    def set_speed(self, speed_multiplier: float) -> ReplayState:
        if speed_multiplier <= 0:
            raise ValueError("speed_multiplier must be positive")
        previous = self.state.speed_multiplier
        self.state.speed_multiplier = float(speed_multiplier)
        self._publish(
            "ReplaySpeedChanged",
            {
                "previous_speed_multiplier": previous,
                "new_speed_multiplier": self.state.speed_multiplier,
            },
        )
        return self.state

    def seek_to(self, target_timestamp: str) -> ReplayState:
        if self.state.replay_mode == "exam":
            raise ModeRestrictionError("Seek/jump is not allowed in exam mode")
        if target_timestamp < self.state.dataset_start_time or target_timestamp > self.state.dataset_end_time:
            raise OutOfBoundsSeekError(
                f"Target timestamp {target_timestamp} is outside dataset boundaries"
            )

        target_index = None
        for index, tick in enumerate(self.dataset.ticks):
            if tick.timestamp >= target_timestamp:
                target_index = index
                break
        if target_index is None:
            raise OutOfBoundsSeekError(
                f"No normalized tick available at or after {target_timestamp}"
            )

        previous_time = self.state.simulation_time
        self._set_cursor(target_index)
        self._publish(
            "ReplayJumped",
            {
                "previous_simulation_time": previous_time,
                "new_simulation_time": self.state.simulation_time,
                "time_cursor": self.state.time_cursor,
            },
        )
        self._publish(
            "TimeframeSynced",
            {
                "active_timeframe": self.state.active_timeframe,
                "synchronized_timeframes": list(self.state.synchronized_timeframes),
            },
        )
        return self.state

    def advance_frame(self) -> ReplayState:
        if self.state.is_paused or self.state.is_finished:
            return self.state

        ticks_to_consume = max(1, int(self.state.speed_multiplier))
        for _ in range(ticks_to_consume):
            if self.state.is_finished:
                break
            next_index = self.state.time_cursor + 1
            if next_index >= len(self.dataset.ticks):
                self.state.is_finished = True
                self.state.is_paused = True
                self._publish(
                    "ReplayFinished",
                    {
                        "dataset_end_time": self.state.dataset_end_time,
                        "final_time_cursor": self.state.time_cursor,
                    },
                )
                break
            self._set_cursor(next_index)
            self._publish(
                "TickArrived",
                {
                    "time_cursor": self.state.time_cursor,
                    "bid": self.state.current_tick.bid,
                    "ask": self.state.current_tick.ask,
                },
            )
        return self.state

    def get_allowed_controls(self) -> dict[str, bool]:
        can_seek = self.state.replay_mode != "exam" and not self.state.is_finished
        return {
            "can_play": not self.state.is_finished,
            "can_pause": not self.state.is_paused and not self.state.is_finished,
            "can_change_speed": not self.state.is_finished,
            "can_seek": can_seek,
            "can_seek_backward": can_seek,
            "can_seek_forward": can_seek,
        }

    def get_chart_context(self) -> dict[str, Any]:
        recent_points = [
            {
                "timestamp": tick.timestamp,
                "bid": tick.bid,
                "ask": tick.ask,
                "mid": tick.mid,
            }
            for tick in self.state.recent_ticks[-120:]
        ]
        return {
            "instrument_id": self.state.instrument_id,
            "active_timeframe": self.state.active_timeframe,
            "synchronized_timeframes": list(self.state.synchronized_timeframes),
            "simulation_time": self.state.simulation_time,
            "current_tick": {
                "timestamp": self.state.current_tick.timestamp,
                "bid": self.state.current_tick.bid,
                "ask": self.state.current_tick.ask,
                "mid": self.state.current_tick.mid,
            },
            "recent_points": recent_points,
        }

    def get_execution_snapshot(self) -> ExecutionSnapshot:
        quality_flags = tuple(
            str(flag) for flag in self.dataset.quality_report.get("data_quality_flags", [])
        )
        liquidity_flags = tuple(
            str(flag) for flag in self.dataset.quality_report.get("liquidity_flags", [])
        )
        return ExecutionSnapshot(
            timestamp=self.state.current_tick.timestamp,
            symbol=self.state.instrument_id,
            bid=self.state.current_tick.bid,
            ask=self.state.current_tick.ask,
            mid=self.state.current_tick.mid,
            active_timeframe=self.state.active_timeframe,
            synchronized_timeframes=self.state.synchronized_timeframes,
            replay_mode=self.state.replay_mode,
            market_session_state="open" if not self.state.is_finished else "finished",
            data_quality_flags=quality_flags,
            liquidity_flags=liquidity_flags,
            dataset_position=self.state.time_cursor,
        )

    def _set_cursor(self, index: int) -> None:
        tick = self.dataset.ticks[index]
        self.state.time_cursor = index
        self.state.simulation_time = tick.timestamp
        self.state.current_tick = tick
        self.state.recent_ticks.append(tick)
        self.state.recent_ticks = self.state.recent_ticks[-100:]

    def _publish(self, event_type: str, payload: dict[str, Any]) -> None:
        event = ReplayEvent(
            event_type=event_type,
            simulation_time=self.state.simulation_time,
            payload=payload,
        )
        self.events.append(event)
        for subscriber in self.subscribers:
            subscriber(event)


def create_replay_session(
    dataset_handle: str,
    replay_mode: str,
    active_timeframe: str | None = None,
    synchronized_timeframes: tuple[str, ...] | None = None,
) -> ReplaySession:
    dataset = load_normalized_dataset(dataset_handle)
    return ReplaySession(
        dataset=dataset,
        replay_mode=replay_mode,
        active_timeframe=active_timeframe,
        synchronized_timeframes=synchronized_timeframes,
    )
