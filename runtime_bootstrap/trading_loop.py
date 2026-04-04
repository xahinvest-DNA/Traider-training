from __future__ import annotations

from dataclasses import asdict
from itertools import count
from typing import Any, Callable

from .errors import (
    ActiveTradeExistsError,
    InvalidTradeCommandError,
    NoActivePositionError,
    TradingModeRestrictionError,
)
from .replay_session import ReplaySession
from .types import (
    ExecutionRecord,
    ExecutionSnapshot,
    OrderRecord,
    PositionRecord,
    ReplayEvent,
    TradeRecord,
    TradingState,
)

TradingSubscriber = Callable[[dict[str, Any]], None]


class MinimalTradingLoop:
    def __init__(self, replay_session: ReplaySession) -> None:
        self.replay_session = replay_session
        self.state = TradingState()
        self.events: list[dict[str, Any]] = []
        self.subscribers: list[TradingSubscriber] = []
        self.session_id = "session-unbound"
        self._id_counter = count(1)
        self.replay_session.subscribe(self._on_replay_event)

    def subscribe(self, handler: TradingSubscriber) -> None:
        self.subscribers.append(handler)

    def set_session_id(self, session_id: str) -> None:
        self.session_id = session_id

    def restore_state(self, state: TradingState) -> None:
        self.state = state
        session_ids = [record.session_id for record in [*state.orders, *state.trades, *state.executions]]
        if state.position is not None:
            session_ids.append(state.position.session_id)
        if session_ids:
            self.session_id = session_ids[-1]
        self._sync_id_counter()

    def buy_market(
        self,
        volume: float = 1.0,
        stop_loss: float | None = None,
        take_profit: float | None = None,
    ) -> OrderRecord:
        return self._request_market_entry(
            side="buy",
            volume=volume,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

    def sell_market(
        self,
        volume: float = 1.0,
        stop_loss: float | None = None,
        take_profit: float | None = None,
    ) -> OrderRecord:
        return self._request_market_entry(
            side="sell",
            volume=volume,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

    def manual_close(self) -> OrderRecord:
        self._validate_close_allowed()
        assert self.state.position is not None
        order = OrderRecord(
            order_id=self._next_id("order"),
            session_id=self.session_id,
            trade_id=self.state.active_trade_id,
            instrument_id=self.replay_session.state.instrument_id,
            order_type="ManualClose",
            side=self.state.position.side,
            status="placed",
            requested_volume=self.state.position.current_open_volume,
            created_at=self.replay_session.state.simulation_time,
            replay_mode=self.replay_session.state.replay_mode,
        )
        self.state.orders.append(order)
        self.state.pending_close_order_id = order.order_id
        self.state.lifecycle_state = "CloseRequested"
        self._publish("OrderPlaced", {"order_id": order.order_id, "order_type": order.order_type})
        return order

    def get_active_trade_count(self) -> int:
        return 1 if self.state.position and self.state.position.status == "open" else 0

    def build_desktop_projection(self) -> dict[str, Any]:
        position = self.state.position
        latest_trade = self.state.trades[-1] if self.state.trades else None
        trade_status = latest_trade.status if latest_trade else "idle"
        protection_present = bool(
            position
            and position.status == "open"
            and (position.stop_loss is not None or position.take_profit is not None)
        )
        return {
            "lifecycle_state": self.state.lifecycle_state,
            "active_trade_present": position is not None and position.status == "open",
            "active_trade_id": self.state.active_trade_id,
            "trade_side": position.side if position else None,
            "current_open_volume": position.current_open_volume if position else 0.0,
            "average_entry_price": position.average_entry_price if position else None,
            "current_stop_loss": position.stop_loss if position and position.status == "open" else None,
            "current_take_profit": position.take_profit if position and position.status == "open" else None,
            "protection_present": protection_present,
            "trade_status": trade_status,
            "last_execution_outcome": asdict(self.state.last_execution) if self.state.last_execution else None,
            "last_close_reason": latest_trade.close_reason if latest_trade else None,
            "manual_close_available": position is not None and position.status == "open",
            "replay_mode": self.replay_session.state.replay_mode,
            "session_context": {
                "session_id": self.session_id,
                "instrument_id": self.replay_session.state.instrument_id,
                "active_timeframe": self.replay_session.state.active_timeframe,
                "simulation_time": self.replay_session.state.simulation_time,
            },
            "closed_trade_count": len(self._closed_trades()),
            "unrealized_pnl": self._calculate_unrealized_pnl(),
        }

    def _request_market_entry(
        self,
        side: str,
        volume: float,
        stop_loss: float | None = None,
        take_profit: float | None = None,
    ) -> OrderRecord:
        self._validate_entry_allowed()
        if volume <= 0:
            raise InvalidTradeCommandError("Volume must be positive")
        self._validate_initial_protection(side, stop_loss, take_profit)

        order_type = "BuyMarket" if side == "buy" else "SellMarket"
        order = OrderRecord(
            order_id=self._next_id("order"),
            session_id=self.session_id,
            trade_id=None,
            instrument_id=self.replay_session.state.instrument_id,
            order_type=order_type,
            side=side,
            status="placed",
            requested_volume=float(volume),
            created_at=self.replay_session.state.simulation_time,
            replay_mode=self.replay_session.state.replay_mode,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )
        self.state.orders.append(order)
        self.state.pending_order_id = order.order_id
        self.state.lifecycle_state = "EntryRequested"
        self._publish("OrderPlaced", {"order_id": order.order_id, "order_type": order.order_type})
        return order

    def _validate_entry_allowed(self) -> None:
        if self.replay_session.state.replay_mode == "review_replay":
            raise TradingModeRestrictionError("Trading actions are not allowed in review replay mode")
        if self.replay_session.state.is_finished:
            raise InvalidTradeCommandError("Cannot open a trade on finished replay state")
        if self.state.lifecycle_state not in {"Idle", "Terminal", "Recovered"}:
            raise ActiveTradeExistsError("Only one active trade lifecycle is allowed")
        if self.state.position and self.state.position.status == "open":
            raise ActiveTradeExistsError("Only one active position is allowed")

    def _validate_close_allowed(self) -> None:
        if self.replay_session.state.replay_mode == "review_replay":
            raise TradingModeRestrictionError("Trading actions are not allowed in review replay mode")
        if self.replay_session.state.is_finished:
            raise InvalidTradeCommandError("Cannot close a trade after replay finished")
        if self.state.lifecycle_state != "PositionOpened" or not self.state.position:
            raise NoActivePositionError("Manual close requires an open position")

    def _validate_initial_protection(
        self,
        side: str,
        stop_loss: float | None,
        take_profit: float | None,
    ) -> None:
        snapshot = self.replay_session.get_execution_snapshot()
        if stop_loss is None and take_profit is None:
            return
        if side == "buy":
            if stop_loss is not None and stop_loss >= snapshot.ask:
                raise InvalidTradeCommandError("BuyMarket stop loss must stay below the current ask")
            if take_profit is not None and take_profit <= snapshot.ask:
                raise InvalidTradeCommandError("BuyMarket take profit must stay above the current ask")
            return
        if stop_loss is not None and stop_loss <= snapshot.bid:
            raise InvalidTradeCommandError("SellMarket stop loss must stay above the current bid")
        if take_profit is not None and take_profit >= snapshot.bid:
            raise InvalidTradeCommandError("SellMarket take profit must stay below the current bid")

    def _on_replay_event(self, event: ReplayEvent) -> None:
        if event.event_type != "TickArrived":
            return
        snapshot = self.replay_session.get_execution_snapshot()
        if self.state.pending_order_id:
            self._fill_entry(snapshot)
        elif self.state.pending_close_order_id:
            self._fill_close(snapshot)
        elif self.state.position and self.state.position.status == "open":
            protective_reason = self._protective_reason(self.state.position, snapshot)
            if protective_reason is not None:
                self._fill_protective_close(snapshot, protective_reason)
            else:
                self.state.position.last_snapshot_timestamp = snapshot.timestamp
                self.state.position.last_snapshot_tick_index = snapshot.dataset_position

    def _fill_entry(self, snapshot: ExecutionSnapshot) -> None:
        assert self.state.pending_order_id is not None
        order = self._find_order(self.state.pending_order_id)
        fill_price = snapshot.ask if order.side == "buy" else snapshot.bid
        trade_id = self._next_id("trade")
        position_id = self._next_id("position")
        order.status = "filled"
        order.filled_at = snapshot.timestamp
        order.trade_id = trade_id

        trade = TradeRecord(
            trade_id=trade_id,
            session_id=self.session_id,
            instrument_id=self.replay_session.state.instrument_id,
            symbol=self.replay_session.state.instrument_id,
            replay_mode=self.replay_session.state.replay_mode,
            timeframe_context=self.replay_session.state.active_timeframe,
            side=order.side,
            status="open",
            opened_at=snapshot.timestamp,
            average_entry_price=fill_price,
            volume_opened=order.requested_volume,
            volume_closed=0.0,
            realised_pnl=0.0,
            total_trade_cost=self._spread(snapshot),
            entry_price=fill_price,
            stop_loss=order.stop_loss,
            take_profit=order.take_profit,
        )
        position = PositionRecord(
            position_id=position_id,
            session_id=self.session_id,
            trade_id=trade_id,
            instrument_id=self.replay_session.state.instrument_id,
            side=order.side,
            status="open",
            total_opened_volume=order.requested_volume,
            current_open_volume=order.requested_volume,
            average_entry_price=fill_price,
            opened_at=snapshot.timestamp,
            stop_loss=order.stop_loss,
            take_profit=order.take_profit,
            last_snapshot_timestamp=snapshot.timestamp,
            last_snapshot_tick_index=snapshot.dataset_position,
        )
        execution = self._build_execution(
            trade_id=trade_id,
            order_id=order.order_id,
            side=order.side,
            volume=order.requested_volume,
            fill_price=fill_price,
            snapshot=snapshot,
            execution_type="entry_fill",
            reason="market_entry",
        )

        self.state.trades.append(trade)
        self.state.position = position
        self.state.executions.append(execution)
        self.state.last_execution = execution
        self.state.active_trade_id = trade_id
        self.state.active_position_id = position_id
        self.state.pending_order_id = None
        self.state.lifecycle_state = "PositionOpened"
        self._publish("PositionOpened", {"trade_id": trade_id, "position_id": position_id})

    def _fill_close(self, snapshot: ExecutionSnapshot) -> None:
        assert self.state.pending_close_order_id is not None
        order = self._find_order(self.state.pending_close_order_id)
        self._close_position(
            snapshot=snapshot,
            order=order,
            execution_type="manual_close_fill",
            reason="manual_close",
            close_reason="manual_close",
            clear_pending_close=True,
        )

    def _fill_protective_close(self, snapshot: ExecutionSnapshot, protective_reason: str) -> None:
        assert self.state.position is not None
        assert self.state.active_trade_id is not None
        order = OrderRecord(
            order_id=self._next_id("order"),
            session_id=self.session_id,
            trade_id=self.state.active_trade_id,
            instrument_id=self.replay_session.state.instrument_id,
            order_type="ProtectiveClose",
            side=self.state.position.side,
            status="filled",
            requested_volume=self.state.position.current_open_volume,
            created_at=snapshot.timestamp,
            replay_mode=self.replay_session.state.replay_mode,
            filled_at=snapshot.timestamp,
        )
        self.state.orders.append(order)
        self._close_position(
            snapshot=snapshot,
            order=order,
            execution_type="protective_close_fill",
            reason=protective_reason,
            close_reason=protective_reason,
            clear_pending_close=False,
        )

    def _close_position(
        self,
        snapshot: ExecutionSnapshot,
        order: OrderRecord,
        execution_type: str,
        reason: str,
        close_reason: str,
        clear_pending_close: bool,
    ) -> None:
        assert self.state.position is not None
        position = self.state.position
        trade = self.state.trades[-1]
        volume_to_close = position.current_open_volume
        fill_price = snapshot.bid if position.side == "buy" else snapshot.ask

        order.status = "filled"
        order.filled_at = snapshot.timestamp
        execution = self._build_execution(
            trade_id=trade.trade_id,
            order_id=order.order_id,
            side=position.side,
            volume=volume_to_close,
            fill_price=fill_price,
            snapshot=snapshot,
            execution_type=execution_type,
            reason=reason,
        )
        realised_pnl = self._calculate_realised_pnl(position.side, position.average_entry_price, fill_price, volume_to_close)
        trade.status = "closed"
        trade.volume_closed = volume_to_close
        trade.realised_pnl = realised_pnl
        trade.total_trade_cost += self._spread(snapshot)
        trade.exit_price = fill_price
        trade.average_exit_price = fill_price
        trade.close_reason = close_reason
        trade.closed_at = snapshot.timestamp

        position.status = "closed"
        position.average_exit_price = fill_price
        position.close_reason = close_reason
        position.closed_at = snapshot.timestamp
        position.last_snapshot_timestamp = snapshot.timestamp
        position.last_snapshot_tick_index = snapshot.dataset_position
        position.current_open_volume = 0.0

        self.state.executions.append(execution)
        self.state.last_execution = execution
        if clear_pending_close:
            self.state.pending_close_order_id = None
        self.state.lifecycle_state = "PositionClosed"
        self._publish("PositionClosed", {"trade_id": trade.trade_id, "order_id": order.order_id})
        self.state.lifecycle_state = "Terminal"
        self.state.active_trade_id = None
        self.state.active_position_id = None

    def _protective_reason(self, position: PositionRecord, snapshot: ExecutionSnapshot) -> str | None:
        stop_loss = position.stop_loss
        take_profit = position.take_profit
        if position.side == "buy":
            if stop_loss is not None and snapshot.bid <= stop_loss:
                return "stop_loss_hit"
            if take_profit is not None and snapshot.bid >= take_profit:
                return "take_profit_hit"
            return None
        if stop_loss is not None and snapshot.ask >= stop_loss:
            return "stop_loss_hit"
        if take_profit is not None and snapshot.ask <= take_profit:
            return "take_profit_hit"
        return None

    def _build_execution(
        self,
        trade_id: str,
        order_id: str,
        side: str,
        volume: float,
        fill_price: float,
        snapshot: ExecutionSnapshot,
        execution_type: str,
        reason: str,
    ) -> ExecutionRecord:
        return ExecutionRecord(
            execution_id=self._next_id("execution"),
            session_id=self.session_id,
            trade_id=trade_id,
            order_id=order_id,
            instrument_id=self.replay_session.state.instrument_id,
            timestamp=snapshot.timestamp,
            execution_type=execution_type,
            reason=reason,
            side=side,
            volume=volume,
            fill_price=fill_price,
            bid=snapshot.bid,
            ask=snapshot.ask,
            spread=self._spread(snapshot),
            slippage=0.0,
            commission_component=0.0,
            swap_component=0.0,
            snapshot_timestamp=snapshot.timestamp,
            snapshot_tick_index=snapshot.dataset_position,
            market_session_state=snapshot.market_session_state,
            data_quality_flags=snapshot.data_quality_flags,
            liquidity_flags=snapshot.liquidity_flags,
            dataset_position_reference=snapshot.dataset_position,
        )

    def _find_order(self, order_id: str | None) -> OrderRecord:
        for order in self.state.orders:
            if order.order_id == order_id:
                return order
        raise InvalidTradeCommandError(f"Order not found: {order_id}")

    def _calculate_unrealized_pnl(self) -> float | None:
        position = self.state.position
        if not position or position.status != "open":
            return None
        snapshot = self.replay_session.get_execution_snapshot()
        close_price = snapshot.bid if position.side == "buy" else snapshot.ask
        return self._calculate_realised_pnl(
            position.side,
            position.average_entry_price,
            close_price,
            position.current_open_volume,
        )

    def _closed_trades(self) -> list[TradeRecord]:
        return [trade for trade in self.state.trades if trade.status == "closed"]

    @staticmethod
    def _calculate_realised_pnl(side: str, entry_price: float, exit_price: float, volume: float) -> float:
        if side == "buy":
            return (exit_price - entry_price) * volume
        return (entry_price - exit_price) * volume

    @staticmethod
    def _spread(snapshot: ExecutionSnapshot) -> float:
        return snapshot.ask - snapshot.bid

    def _next_id(self, prefix: str) -> str:
        return f"{prefix}-{next(self._id_counter):04d}"

    def _sync_id_counter(self) -> None:
        seen_ids = [
            *[order.order_id for order in self.state.orders],
            *[trade.trade_id for trade in self.state.trades],
            *[execution.execution_id for execution in self.state.executions],
        ]
        if self.state.position:
            seen_ids.append(self.state.position.position_id)
        max_value = 0
        for raw_id in seen_ids:
            try:
                max_value = max(max_value, int(raw_id.rsplit("-", 1)[1]))
            except (IndexError, ValueError):
                continue
        self._id_counter = count(max_value + 1)

    def _publish(self, event_type: str, payload: dict[str, Any]) -> None:
        event = {
            "event_type": event_type,
            "simulation_time": self.replay_session.state.simulation_time,
            "payload": payload,
        }
        self.events.append(event)
        for subscriber in self.subscribers:
            subscriber(event)
