# Session Report - 2026-03-15 - Trading Engine Spec

## Тема сессии

Формализация Trading Engine v1: lifecycle, order model, execution policy, trade records и execution records.

## Что было сделано

- полностью переработан `03_MODULES/TRADING_ENGINE.md` до уровня инженерной спецификации;
- зафиксирована state machine trade lifecycle;
- описаны `Order`, `Position`, `TradeLifecycle`, `ExecutionEvent`, `TradeRecord`, `ExecutionRecord`, `RiskGuard`, `PositionLeg`;
- формализованы `partial close` и `add-on entry`;
- выбрана рекомендуемая `fixed slippage` policy для v1;
- зафиксировано консервативное правило для SL/TP ambiguity в tick-only модели;
- обновлены `01_MASTER/DECISIONS.md` и `01_MASTER/CURRENT_STATE.md`.

## Ключевые принятые решения

- одна активная сделка = один `TradeLifecycle`;
- активная позиция агрегированная, но execution history хранится через `PositionLeg`;
- все исполнения работают только post-tick через `ExecutionSnapshot`;
- add-on entry не считается второй независимой сделкой;
- partial close создает отдельные execution records и уменьшает remaining volume;
- slippage v1 фиксированный и воспроизводимый.

## Что осталось открытым

- делать ли stop loss обязательным hard-rule в v1;
- нужна ли explicit expiry policy для pending stop orders;
- нужна ли event-level история изменения SL/TP уже в первом прототипе;
- достаточно ли FIFO для consumption of legs на partial close.

## Следующий шаг

Перейти к проектированию data schema и storage contracts для `Order`, `Position`, `TradeRecord`, `ExecutionRecord`, `PositionLeg` и связей с journal/analytics.
