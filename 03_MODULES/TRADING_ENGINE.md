# Trading Engine

Дата фиксации: 2026-03-15
Статус: spec v1
Приоритет: highest

## 1. Назначение модуля

Trading engine отвечает за жизненный цикл ручной сделки внутри replay-среды: от момента постановки ордера до полного закрытия позиции и фиксации всех execution records.

### Роль в общей архитектуре

- `replay engine` поставляет рыночное состояние и время;
- `market model` поставляет правила инструмента, объема, издержек и session constraints;
- `trading engine` принимает торговые команды, валидирует их, исполняет их post-tick и ведет trade lifecycle;
- `journal/analytics` получает события и записи, созданные trading engine, но не управляет исполнением.

### Что входит в trading engine

- order model и валидация команд;
- trade lifecycle state machine;
- исполнение market и stop orders;
- логика partial close и add-on entry;
- управление stop loss / take profit;
- расчет execution price, gross/net PnL и trade cost components;
- публикация trading events;
- сборка `TradeRecord` и `ExecutionRecord`;
- `RiskGuard` для v1 ограничений.

### Что не входит в trading engine

- хранение и проигрывание исторических данных;
- агрегация баров и управление time cursor;
- импорт dataset и quality normalization;
- UI формы и desktop interaction flows;
- mobile layer;
- mentor/review system;
- portfolio engine;
- broker margin engine;
- multi-instrument netting/hedging logic beyond one active lifecycle.

## 2. Основные сущности

### Order

Назначение:

- пользовательская или системная инструкция на открытие, изменение или закрытие части позиции.

Обязательные поля:

- `orderId`
- `tradeId optional`
- `sessionId`
- `instrumentId`
- `orderType`
- `side`
- `requestedVolume`
- `requestedPrice optional`
- `stopLoss optional`
- `takeProfit optional`
- `createdAt`
- `createdBy`
- `status`
- `rejectionReason optional`

Жизненный цикл:

- создается как `draft -> placed -> active -> filled/cancelled/rejected`

Где хранится:

- in-memory trading session state
- serialized into journal/trade history after transition

Кто создает/обновляет:

- создается trading engine по user command
- обновляется trading engine на основе risk checks и execution outcomes

### Position

Назначение:

- текущее агрегированное рыночное состояние активной сделки.

Обязательные поля:

- `tradeId`
- `instrumentId`
- `side`
- `status`
- `totalOpenedVolume`
- `currentOpenVolume`
- `averageEntryPrice`
- `stopLoss optional`
- `takeProfit optional`
- `openedAt`
- `updatedAt`

Жизненный цикл:

- отсутствует -> open -> partially_closed optional -> closed

Где хранится:

- in-memory active trade state
- closed snapshot goes to `TradeRecord`

Кто создает/обновляет:

- создается trading engine при первом fill
- обновляется на add-on, SL/TP changes, partial close, close

### TradeLifecycle

Назначение:

- формальная оболочка вокруг одной активной сделки от первого order intent до финального закрытия.

Обязательные поля:

- `tradeId`
- `sessionId`
- `instrumentId`
- `state`
- `openedByOrderId optional`
- `activeOrderIds`
- `positionRef optional`
- `startedAt`
- `completedAt optional`

Жизненный цикл:

- `Idle -> ... -> Completed`

Где хранится:

- in-memory during session
- summarized into `TradeRecord`

Кто создает/обновляет:

- trading engine

### ExecutionEvent

Назначение:

- доменное событие исполнения или изменения lifecycle.

Обязательные поля:

- `eventId`
- `tradeId`
- `eventType`
- `timestamp`
- `snapshotRef`
- `payload`

Жизненный цикл:

- immutable append-only event

Где хранится:

- event stream in memory
- journal export

Кто создает/обновляет:

- публикуется trading engine

### TradeRecord

Назначение:

- итоговая агрегированная запись по одной сделке.

Обязательные поля:

- `tradeId`
- `sessionId`
- `symbol`
- `side`
- `status`
- `openedAt`
- `closedAt optional`
- `averageEntryPrice`
- `averageExitPrice optional`
- `realisedPnL`
- `closeReason optional`

Жизненный цикл:

- создается при открытии trade lifecycle
- обновляется по мере исполнения
- становится immutable после lifecycle completion

Где хранится:

- local storage/journal layer

Кто создает/обновляет:

- trading engine

### ExecutionRecord

Назначение:

- атомарная запись о каждом fill или execution-related action.

Обязательные поля:

- `executionId`
- `tradeId`
- `timestamp`
- `executionType`
- `requestedPrice optional`
- `triggerPrice optional`
- `fillPrice`
- `volume`
- `reason`
- `snapshotTickIndex`

Жизненный цикл:

- immutable append-only

Где хранится:

- local storage/journal layer

Кто создает/обновляет:

- trading engine

### RiskGuard

Назначение:

- минимальный слой защитных правил v1 перед постановкой/исполнением ордера.

Обязательные поля:

- `sessionRulesRef`
- `instrumentRulesRef`
- `v1ConstraintsRef`

Жизненный цикл:

- stateless service or lightweight rules component

Где хранится:

- runtime only

Кто создает/обновляет:

- owned by trading engine

### PositionLeg

Рекомендуемое решение v1:

- `PositionLeg` поддерживается как техническая сущность execution aggregation, но не как отдельная независимая позиция.

Назначение:

- хранить каждый входной fill, включая add-on, чтобы корректно считать average entry и историю исполнения.

Обязательные поля:

- `legId`
- `tradeId`
- `openedAt`
- `entryPrice`
- `openedVolume`
- `remainingVolume`
- `sourceExecutionId`

Жизненный цикл:

- open -> partially_consumed optional -> fully_consumed

Где хранится:

- in-memory as part of active position
- serialized for journal if needed

Кто создает/обновляет:

- создается trading engine при каждом entry/add-on fill
- обновляется trading engine на partial close / final close

## 3. Order Model

### Общие правила

Поддерживаемые типы v1:

- `BuyMarket`
- `SellMarket`
- `BuyStop`
- `SellStop`

### BuyMarket

Создается:

- по прямой команде пользователя.

Обязательные параметры:

- `instrumentId`
- `volume`
- `side = buy`
- `stopLoss optional`
- `takeProfit optional`

Когда становится активным:

- сразу после `OrderPlaced`.

Как отменяется:

- до исполнения не живет отдельной длительной жизнью; либо исполняется на ближайшем post-tick check, либо отклоняется.

Условия исполнения:

- на первом доступном post-tick `ExecutionSnapshot` при допустимом session state и успешном RiskGuard.

Причины отказа:

- invalid volume;
- second independent trade attempt;
- market session closed;
- instrument unavailable;
- invalid SL/TP configuration;
- replay mode restriction.

### SellMarket

Та же модель, что у `BuyMarket`, но `side = sell` и исполнение идет по sell-side semantics.

### BuyStop

Создается:

- по команде пользователя как pending order.

Обязательные параметры:

- `instrumentId`
- `volume`
- `triggerPrice`
- `side = buy`
- `stopLoss optional`
- `takeProfit optional`

Когда становится активным:

- после прохождения RiskGuard и перехода в `PendingOrderActive`.

Как отменяется:

- пользователем до trigger;
- системой при lifecycle cancellation or rejection.

Условия исполнения:

- когда `ask >= triggerPrice` на post-tick snapshot.

Причины отказа:

- invalid trigger placement;
- invalid volume;
- second independent trade attempt;
- market/session restriction;
- lifecycle state does not allow pending order.

### SellStop

Создается:

- по команде пользователя как pending order.

Обязательные параметры:

- `instrumentId`
- `volume`
- `triggerPrice`
- `side = sell`
- `stopLoss optional`
- `takeProfit optional`

Когда становится активным:

- после перехода в `PendingOrderActive`.

Как отменяется:

- пользователем до trigger;
- системой при lifecycle cancellation or rejection.

Условия исполнения:

- когда `bid <= triggerPrice` на post-tick snapshot.

Причины отказа:

- invalid trigger placement;
- invalid volume;
- session/instrument restriction;
- lifecycle state does not allow pending order.

## 4. Position Model

### Что такое позиция в v1

Позиция в v1 - это агрегированное состояние одной активной сделки по одному инструменту и одному направлению.

### Связь позиции со сделкой

- один `TradeLifecycle` может иметь только одну активную `Position`;
- `TradeLifecycle` может накапливать несколько entry executions через add-on;
- position живет внутри trade lifecycle until close.

### Как учитывать partial close

- partial close уменьшает `currentOpenVolume`;
- не создает новую сделку;
- создает новый `ExecutionRecord` закрывающего типа;
- может оставить trade lifecycle в `PositionPartiallyClosed`.

### Как учитывать add-on entry

Рекомендуемый вариант v1:

- add-on разрешен как увеличение той же позиции в рамках того же `TradeLifecycle`;
- каждый add-on создает новый `PositionLeg` и `ExecutionRecord`;
- `averageEntryPrice` пересчитывается как weighted average по оставшемуся открытому объему legs.

### Альтернатива

- отдельные независимые legs как mini-trades внутри одного инструмента.

Почему не берем в v1:

- это резко усложняет journal, analytics и lifecycle state machine;
- конфликтует с ограничением “одна активная сделка”.

## 5. Trade Lifecycle State Machine

### Состояния

#### Idle

Смысл:

- активной сделки нет.

Переходы:

- `OrderPlaced` -> `PendingOrderPlaced` или сразу `PositionOpened`
- `OrderRejected` -> `Rejected`

Журналируется:

- user intent to open trade

#### PendingOrderPlaced

Смысл:

- pending order создан и проходит initial validation/registration.

Переходы:

- valid pending -> `PendingOrderActive`
- invalid pending -> `Rejected`
- user cancel -> `Cancelled`

Журналируется:

- order payload, intent, validation result

#### PendingOrderActive

Смысл:

- stop order ждет trigger condition.

Переходы:

- trigger fill -> `PositionOpened`
- cancel -> `Cancelled`
- invalidated by session/end -> `Expired` or `Cancelled`

Журналируется:

- activation timestamp, trigger conditions

#### PositionOpened

Смысл:

- позиция открыта и имеет ненулевой open volume.

Переходы:

- add-on -> remains `PositionOpened`
- partial close -> `PositionPartiallyClosed`
- full close -> `PositionClosed`

Журналируется:

- first fill, entry costs, initial SL/TP

#### PositionPartiallyClosed

Смысл:

- часть позиции закрыта, но lifecycle еще активен.

Переходы:

- next partial close -> remains `PositionPartiallyClosed`
- add-on -> remains active and may return semantically to open state, но в v1 state оставляем `PositionPartiallyClosed` до полного закрытия
- full close -> `PositionClosed`

Журналируется:

- partial execution details, remaining volume, realized PnL

#### PositionClosed

Смысл:

- весь объем позиции закрыт.

Переходы:

- `TradeLifecycleCompleted`

Журналируется:

- final exit, total costs, close reason

#### Cancelled

Смысл:

- lifecycle завершен без открытия позиции.

Переходы:

- terminal

Журналируется:

- cancellation reason

#### Rejected

Смысл:

- order/lifecycle отклонен до открытия позиции.

Переходы:

- terminal

Журналируется:

- rejection reason and violated rule

#### Expired

Смысл:

- pending order истек без исполнения.

Релевантность v1:

- optional, но сохраняем как допустимое terminal state для pending orders, если later phase добавит explicit expiry policy.

Журналируется:

- expiry reason and timestamp

## 6. Execution Policy v1

### Когда исполняются market orders

- market orders исполняются на первом post-tick `ExecutionSnapshot`, доступном после команды пользователя;
- момент исполнения всегда привязан к уже примененному рынку, а не к hypothetical intrabar state.

### Когда проверяются stop orders

- после каждого нового примененного тика;
- `BuyStop` проверяется по `ask`;
- `SellStop` проверяется по `bid`.

### По какой стороне идет исполнение

- buy entry -> `ask`
- sell entry -> `bid`
- close long -> `bid`
- close short -> `ask`

### Как применяются bid/ask

- `trigger_price` проверяется по корректной стороне рынка;
- `execution_price` берется с той же стороны плюс slippage policy;
- spread фиксируется как `ask - bid` snapshot.

### Как учитываются издержки

- `spread` = implicit cost through bid/ask
- `slippage` = explicit execution adjustment
- `commission` = per instrument commission rule
- `swap` = рассчитывается при удержании через rollover logic

### Что считается execution price

- цена стороны рынка в snapshot после применения slippage rule.

### Что считается trigger price

- цена, по которой условие ордера/SL/TP считается достигнутым;
- для stop orders это `bid` или `ask` depending on side;
- для SL/TP это соответствующая close-side price.

### Как фиксируется execution reason

Минимальные значения:

- `market_entry`
- `pending_order_trigger`
- `manual_partial_close`
- `manual_full_close`
- `stop_loss_hit`
- `take_profit_hit`
- `add_on_entry`
- `system_reject`
- `user_cancel`

## 7. Slippage Policy

### Вариант 1: Fixed

Описание:

- фиксированное значение slippage in points/ticks per execution.

Плюсы:

- просто реализуется;
- легко воспроизводится;
- не добавляет скрытый stochastic behavior.

Минусы:

- менее реалистичен для разных условий ликвидности.

### Вариант 2: Deterministic Band

Описание:

- slippage вычисляется по детерминированной функции внутри заранее заданного диапазона, например от spread или timestamp parity.

Плюсы:

- чуть реалистичнее;
- все еще воспроизводим.

Минусы:

- труднее объяснить пользователю;
- создает больше скрытой логики в v1.

### Вариант 3: Liquidity-flag-based

Описание:

- slippage зависит от `liquidityFlags` и `dataQualityFlags` snapshot.

Плюсы:

- ближе к рыночной реальности;
- использует уже существующие quality signals.

Минусы:

- требует более зрелой quality taxonomy;
- повышает связанность import/replay/execution.

### Рекомендуемая policy v1

Рекомендуемый вариант:

- `Fixed slippage`

Почему этого достаточно:

- дает воспроизводимое и прозрачное поведение для первого прототипа;
- не перегружает lifecycle-логику;
- не мешает later phase перейти к более умной policy.

Что откладываем:

- adaptive slippage by liquidity regime;
- stochastic slippage models;
- broker-specific execution latency models.

## 8. Partial Close

### Как инициируется

- по прямой команде пользователя на активной позиции.

### Как рассчитывается объем закрытия

- requested close volume должен быть `> 0`;
- не должен превышать `currentOpenVolume`;
- remaining volume после close должен быть либо `0`, либо `>= minLot` и кратен `lotStep`.

### Как пересчитывается remaining position

- `currentOpenVolume = currentOpenVolume - closedVolume`
- legs are consumed in deterministic order for auditability; в v1 рекомендуется FIFO.

### Как фиксируется realised/unrealised PnL

- на partial close создается realized PnL по закрытому объему;
- remaining open volume сохраняет unrealized PnL по текущему snapshot;
- unrealized snapshots не пишутся на каждый тик в `TradeRecord`, а считаются journal/analytics layer from execution + replay history.

### Какие execution records создаются

- один `ExecutionRecord` типа `partial_close`;
- один `ExecutionRecorded` event;
- optional `PositionPartiallyClosed`.

### Как это отражается в journal

- как отдельное закрывающее исполнение;
- с объемом, ценой, cost breakdown, remaining volume и причиной.

## 9. Add-on Entry

### Когда разрешен

- только если уже существует активный `TradeLifecycle`;
- только в том же инструменте и в том же направлении;
- только если после add-on суммарный объем остается валидным.

### Проверка ограничения “одна активная сделка”

- add-on не считается второй независимой сделкой;
- он допустим только как увеличение существующей позиции;
- попытка открыть противоположную или независимую сделку отклоняется `RiskGuard`.

### Как пересчитывается средняя цена

`newAverageEntry = (oldAverageEntry * oldOpenVolume + addOnFillPrice * addOnVolume) / newOpenVolume`

### Как это попадает в trade record

- `TradeRecord.volume_opened` увеличивается;
- `TradeRecord.averageEntryPrice` обновляется;
- создается `ExecutionRecord` типа `add_on_entry`;
- создается `PositionLeg`.

### Как это отображается в lifecycle

- состояние остается активным `PositionOpened` или `PositionPartiallyClosed`, если раньше уже был partial close;
- отдельного state only for add-on не вводим.

## 10. Stop Loss / Take Profit

### Где они живут

Рекомендуемое решение v1:

- `stopLoss` и `takeProfit` живут в `Position` как текущие активные защитные уровни;
- в `Order` они могут быть заданы как initial parameters, которые при открытии позиции копируются в position state.

### Как обновляются

- пользователь может изменить активные SL/TP только для открытой позиции;
- изменение проходит через RiskGuard validation;
- фиксируется отдельным lifecycle/update event later phase if needed.

### Как проверяются post-tick

- после каждого нового snapshot;
- для long position:
  - `stopLoss` проверяется по `bid <= stopLoss`
  - `takeProfit` проверяется по `bid >= takeProfit`
- для short position:
  - `stopLoss` проверяется по `ask >= stopLoss`
  - `takeProfit` проверяется по `ask <= takeProfit`

### Приоритет, если в одном тике затронуты несколько условий

В модели tick-only ambiguity v1 правило такое:

- приоритет имеет первое логически достижимое условие в направлении риска:
  - для long: если snapshot уже ниже SL, считаем `StopLossHit`
  - для short: если snapshot уже выше SL, считаем `StopLossHit`
- если и SL, и TP формально пересечены из-за gap without intratick path, выбирается худший для пользователя защитный вариант:
  - long -> `StopLossHit`
  - short -> `StopLossHit`

Причина:

- это консервативно;
- не вводит ложной оптимистичности при отсутствии intratick path.

### Как фиксируется причина закрытия

- `closeReason`
- `execution_reason`
- `trigger_price`
- `fill_price`
- `snapshotRef`

## 11. Risk Guard / Rules

Минимальные защитные правила v1:

- запрет на вторую независимую сделку;
- валидация объема against `minLot`, `maxLot`, `lotStep`;
- валидация stop loss against side and current market;
- валидация session state;
- валидация instrument availability;
- запрет исполнения вне v1 rules;
- корректная и понятная классификация user errors.

Минимальные error classes:

- `validation_error`
- `session_error`
- `state_error`
- `constraint_violation`
- `execution_reject`

## 12. Execution Events

### OrderPlaced

Обязательные поля:

- `eventId`
- `orderId`
- `tradeId optional`
- `timestamp`
- `orderType`
- `requestedVolume`

Публикует:

- trading engine

Подписываются:

- journal layer
- desktop workspace

### OrderActivated

Обязательные поля:

- `eventId`
- `orderId`
- `timestamp`
- `activationState`

Публикует:

- trading engine

Подписываются:

- journal layer

### OrderCancelled

Обязательные поля:

- `eventId`
- `orderId`
- `timestamp`
- `reason`

Публикует:

- trading engine

Подписываются:

- journal layer

### OrderRejected

Обязательные поля:

- `eventId`
- `orderId`
- `timestamp`
- `reason`
- `violatedRule`

Публикует:

- trading engine

Подписываются:

- journal layer
- desktop workspace

### PositionOpened

Обязательные поля:

- `eventId`
- `tradeId`
- `timestamp`
- `fillPrice`
- `volume`
- `side`

Публикует:

- trading engine

Подписываются:

- journal layer
- desktop workspace

### PositionIncreased

Обязательные поля:

- `eventId`
- `tradeId`
- `timestamp`
- `addedVolume`
- `fillPrice`
- `newAverageEntryPrice`

Публикует:

- trading engine

Подписываются:

- journal layer

### PositionPartiallyClosed

Обязательные поля:

- `eventId`
- `tradeId`
- `timestamp`
- `closedVolume`
- `remainingVolume`
- `realisedPnL`

Публикует:

- trading engine

Подписываются:

- journal layer
- analytics layer

### PositionClosed

Обязательные поля:

- `eventId`
- `tradeId`
- `timestamp`
- `finalVolumeClosed`
- `realisedPnL`
- `closeReason`

Публикует:

- trading engine

Подписываются:

- journal layer
- analytics layer

### StopLossHit

Обязательные поля:

- `eventId`
- `tradeId`
- `timestamp`
- `triggerPrice`
- `fillPrice`

Публикует:

- trading engine

Подписываются:

- journal layer
- analytics layer

### TakeProfitHit

Обязательные поля:

- `eventId`
- `tradeId`
- `timestamp`
- `triggerPrice`
- `fillPrice`

Публикует:

- trading engine

Подписываются:

- journal layer
- analytics layer

### ExecutionRecorded

Обязательные поля:

- `eventId`
- `executionId`
- `tradeId`
- `timestamp`
- `executionType`
- `reason`

Публикует:

- trading engine

Подписываются:

- journal layer
- analytics layer

### TradeLifecycleCompleted

Обязательные поля:

- `eventId`
- `tradeId`
- `timestamp`
- `finalState`

Публикует:

- trading engine

Подписываются:

- journal layer
- analytics layer

Что уходит в journal:

- все перечисленные events;
- links to corresponding `TradeRecord` and `ExecutionRecord`;
- user note references.

## 13. TradeRecord и ExecutionRecord

### TradeRecord

Минимальные поля:

- `tradeId`
- `sessionId`
- `symbol`
- `timeframeContext`
- `side`
- `openedAt`
- `closedAt optional`
- `entryPrice`
- `exitPrice optional`
- `averageEntryPrice`
- `averageExitPrice optional`
- `stopLoss optional`
- `takeProfit optional`
- `volumeOpened`
- `volumeClosed`
- `realisedPnL`
- `unrealisedPnLSnapshotsPolicy`
- `closeReason optional`
- `userNotesRefs`
- `replayMode`
- `marketQualityFlagsRefs`

Рекомендуемая `unrealisedPnLSnapshotsPolicy` v1:

- unrealized PnL не хранится как полный tick-by-tick stream внутри `TradeRecord`;
- record хранит policy ref, а detailed reconstruction делается analytics layer from replay + execution data.

### ExecutionRecord

Минимальные поля:

- `executionId`
- `tradeId`
- `timestamp`
- `executionType`
- `requestedPrice optional`
- `triggerPrice optional`
- `fillPrice`
- `bid`
- `ask`
- `spread`
- `slippage`
- `commissionComponent`
- `swapComponent optional`
- `reason`
- `datasetPositionReference`
- `volume`

## 14. Contract with Journal/Analytics

Trading engine обязан отдавать journal layer:

- все execution events;
- все `TradeRecord` updates;
- все `ExecutionRecord` entries;
- rejection/cancellation reasons;
- cost components;
- lifecycle state transitions.

Для analytics обязательны:

- open/close timestamps;
- fill prices;
- volume changes;
- partial close details;
- add-on details;
- reasons for close;
- quality/session flags at execution.

Связь с text notes:

- user notes хранятся вне trading engine;
- trading engine сохраняет `userNotesRefs` on trade level and optional event-level refs.

Partial close / add-on в аналитике:

- partial close влияет на realized PnL segments;
- add-on влияет на average entry, opened volume and execution count;
- analytics layer должен видеть их как distinct execution events внутри одной сделки.

## 15. Edge Cases

### Stop order trigger on gap

- если trigger condition впервые выполняется на gap tick, order исполняется по snapshot-side price с slippage policy;
- optimistic fill at trigger price не допускается.

### Market order during extreme spread spike

- order исполняется по фактическому snapshot;
- `data_quality_flags` and `spread_at_execution` must be logged;
- no synthetic spread smoothing in v1.

### Position close on last available tick

- допускается;
- если последний tick существует, close can execute;
- после этого trade closes and session may continue to `end_of_data`.

### Partial close below min lot step

- rejected by RiskGuard.

### Add-on, приводящий к невалидному объёму

- rejected by RiskGuard;
- trade lifecycle remains active without modification.

### Session closed / symbol unavailable

- new execution rejected;
- pending orders remain inactive until valid market reopen unless explicitly cancelled.

### Simultaneous SL/TP ambiguity within one tick model

- conservative rule: choose `StopLossHit`.

### Dataset anomaly flags during execution

- execution still allowed unless anomaly is hard market/session restriction;
- flags must be attached to execution record and journal.

## 16. Ограничения v1

- одна активная сделка;
- один инструмент за сессию;
- desktop-first;
- manual trading only;
- no portfolio engine;
- no hedging/netting complexity beyond single lifecycle;
- no broker margin engine v1;
- no opposite-side reversal inside same tick without explicit close/open sequence;
- no autonomous strategy logic.

## 17. Архитектурные решения и компромиссы

### Рассмотренные варианты

#### Полностью агрегированная позиция без legs

Плюсы:

- проще реализация.

Минусы:

- хуже аудит execution history;
- слабее основа для partial close and add-on analytics.

Статус:

- не выбран как основной вариант.

#### Полноценная multi-leg independent trade model

Плюсы:

- гибче;
- лучше для будущего portfolio/hedging.

Минусы:

- слишком тяжело для v1;
- конфликтует с ограничением одной активной сделки.

Статус:

- отложено.

### Почему выбран текущий lifecycle

- он держит одну активную сделку как главный инвариант;
- позволяет partial close и add-on без распада на несколько сделок;
- оставляет точку расширения через `PositionLeg`.

### Что сознательно отложено

- buy/sell limit and stop limit orders;
- trailing stop automation;
- OCO groups;
- hedging/netting modes;
- multi-trade portfolio state;
- broker latency and partial fill simulation;
- advanced slippage models.

### Точка расширения для v2

- richer order types;
- leg-aware analytics;
- adaptive slippage;
- margin and leverage model;
- multi-instrument portfolio engine.

## 18. Артефакты на выходе

В рамках этой спецификации должны быть согласованы и при необходимости обновлены:

- `03_MODULES/TRADING_ENGINE.md`
- `01_MASTER/DECISIONS.md`
- `01_MASTER/CURRENT_STATE.md`

## 19. Data Schema / Storage Contract v1

### Принципы storage-модели v1

Storage contract v1 должен быть совместим с local-first архитектурой, но не привязываться к конкретной БД или ORM.

Базовые принципы:

- runtime-state и persisted-state разделяются явно;
- `ExecutionRecord` и `PositionLeg` являются append-only trace сущностями;
- `Position` является mutable active snapshot сущностью;
- `TradeRecord` является агрегированной persisted записью по одной сделке;
- `Order` хранится не только как runtime intent, но и как audit trail пользовательского действия;
- все persisted сущности должны быть сериализуемы и пригодны для последующей синхронизации;
- любое исполнение обязано ссылаться на `snapshotTimestamp`, `snapshotTickIndex`, `marketSessionState` и `quality/session flags`.

### Общие storage-конвенции

Для persisted сущностей v1 рекомендуются общие поля:

- `entityId` или доменный ID сущности
- `sessionId`
- `instrumentId`
- `createdAt`
- `updatedAt optional`
- `schemaVersion optional`
- `syncState optional later`

Для local-first совместимости:

- все доменные ID должны быть стабильными и уникальными в рамках локального хранилища;
- persisted модель не должна требовать cloud-generated keys;
- mutable active entities должны быть безопасны для восстановления после локального restart.

### Order storage contract

#### Назначение

`Order` хранит пользовательское или системное намерение на открытие, активацию, отмену или отклонение торгового действия.

#### Persisted или runtime-only

- runtime: да
- persisted: да

Причина:

- даже market order должен сохраняться для audit trail и journal trace.

#### Обязательные поля

- `orderId`
- `sessionId`
- `instrumentId`
- `orderType`
- `side`
- `requestedVolume`
- `createdAt`
- `createdBy`
- `status`
- `replayMode`

#### Optional поля

- `tradeId`
- `requestedPrice`
- `triggerPrice`
- `stopLoss`
- `takeProfit`
- `activatedAt`
- `cancelledAt`
- `rejectedAt`
- `filledAt`
- `rejectionReason`
- `expiresAt`
- `sourceNoteRef`

#### Идентификаторы и связи

- PK: `orderId`
- FK optional: `tradeId -> TradeRecord.tradeId`
- FK: `sessionId -> training session`
- FK: `instrumentId -> InstrumentSpec.instrumentId`

#### Lifecycle / status поля

Рекомендуемые значения `status`:

- `draft`
- `placed`
- `active`
- `filled`
- `cancelled`
- `rejected`
- `expired optional`

#### Immutable поля

- `orderId`
- `sessionId`
- `instrumentId`
- `orderType`
- `side`
- `createdAt`
- `createdBy`

#### Mutable поля

- `status`
- `tradeId`
- `activatedAt`
- `cancelledAt`
- `rejectedAt`
- `filledAt`
- `rejectionReason`

#### Поля, обязательные для journal/analytics

- `orderId`
- `tradeId if assigned`
- `orderType`
- `side`
- `requestedVolume`
- `requestedPrice/triggerPrice if present`
- `status`
- `createdAt`
- `rejectionReason if rejected`

### Position storage contract

#### Назначение

`Position` хранит текущее агрегированное состояние активной сделки по одному инструменту и одному направлению.

#### Persisted или runtime-only

- runtime: да
- persisted: да

Причина:

- active position должна восстанавливаться в local-first сценарии и оставаться источником агрегированного состояния сделки.

#### Обязательные поля

- `positionId`
- `tradeId`
- `sessionId`
- `instrumentId`
- `side`
- `status`
- `totalOpenedVolume`
- `currentOpenVolume`
- `averageEntryPrice`
- `openedAt`
- `updatedAt`

#### Optional поля

- `stopLoss`
- `takeProfit`
- `closedAt`
- `closeReason`
- `averageExitPrice`
- `lastSnapshotTimestamp`
- `lastSnapshotTickIndex`
- `marketSessionStateAtLastUpdate`
- `qualityFlagsAtLastUpdate`

#### Идентификаторы и связи

- PK: `positionId`
- Unique FK: `tradeId -> TradeRecord.tradeId`
- FK: `sessionId`
- FK: `instrumentId`

#### Lifecycle / status поля

Рекомендуемые значения `status`:

- `open`
- `partially_closed`
- `closed`

#### Immutable поля

- `positionId`
- `tradeId`
- `sessionId`
- `instrumentId`
- `side`
- `openedAt`

#### Mutable поля

- `status`
- `totalOpenedVolume`
- `currentOpenVolume`
- `averageEntryPrice`
- `stopLoss`
- `takeProfit`
- `updatedAt`
- `closedAt`
- `closeReason`
- `averageExitPrice`
- `lastSnapshotTimestamp`
- `lastSnapshotTickIndex`
- `marketSessionStateAtLastUpdate`
- `qualityFlagsAtLastUpdate`

#### Поля, обязательные для journal/analytics

- `tradeId`
- `side`
- `averageEntryPrice`
- `currentOpenVolume`
- `stopLoss`
- `takeProfit`
- `openedAt`
- `closedAt`
- `closeReason`

### PositionLeg storage contract

#### Назначение

`PositionLeg` хранит каждое входное исполнение, которое увеличивает позицию внутри того же `TradeLifecycle`.

#### Persisted или runtime-only

- runtime: да
- persisted: да

Причина:

- без persisted legs невозможно корректно восстановить add-on history, weighted average entry и partial close trace.

#### Обязательные поля

- `legId`
- `tradeId`
- `positionId`
- `sourceExecutionId`
- `openedAt`
- `entryPrice`
- `openedVolume`
- `remainingVolume`

#### Optional поля

- `fullyConsumedAt`
- `consumptionRule`
- `noteRef optional`

#### Идентификаторы и связи

- PK: `legId`
- FK: `tradeId -> TradeRecord.tradeId`
- FK: `positionId -> Position.positionId`
- FK: `sourceExecutionId -> ExecutionRecord.executionId`

#### Lifecycle / status поля

Рекомендуется не отдельный `status`, а вычисление по объему:

- `remainingVolume == openedVolume` -> open
- `0 < remainingVolume < openedVolume` -> partially_consumed
- `remainingVolume == 0` -> fully_consumed

#### Immutable поля

- `legId`
- `tradeId`
- `positionId`
- `sourceExecutionId`
- `openedAt`
- `entryPrice`
- `openedVolume`

#### Mutable поля

- `remainingVolume`
- `fullyConsumedAt`

#### Поля, обязательные для journal/analytics

- `legId`
- `tradeId`
- `sourceExecutionId`
- `openedAt`
- `entryPrice`
- `openedVolume`
- `remainingVolume`

### TradeRecord storage contract

#### Назначение

`TradeRecord` является единой persisted записью по одной сделке и главным агрегатом для journal/analytics.

#### Persisted или runtime-only

- runtime: да, как mutable aggregate during lifecycle
- persisted: да

#### Обязательные поля

- `tradeId`
- `sessionId`
- `instrumentId`
- `symbol`
- `marketProfile`
- `replayMode`
- `timeframeContext`
- `side`
- `status`
- `openedAt`
- `averageEntryPrice`
- `volumeOpened`
- `volumeClosed`
- `realisedPnL`
- `totalTradeCost`
- `createdAt`
- `updatedAt`

#### Optional поля

- `closedAt`
- `entryPrice`
- `exitPrice`
- `averageExitPrice`
- `stopLoss`
- `takeProfit`
- `closeReason`
- `userNotesRefs`
- `marketQualityFlagsRefs`
- `holdingDuration`
- `lastUnrealisedPnLSnapshot optional`

#### Идентификаторы и связи

- PK: `tradeId`
- FK: `sessionId`
- FK: `instrumentId`
- reverse relation to `Order`, `Position`, `PositionLeg`, `ExecutionRecord`

#### Lifecycle / status поля

Рекомендуемые значения `status`:

- `idle_placeholder optional`
- `pending`
- `open`
- `partially_closed`
- `closed`
- `cancelled`
- `rejected`
- `expired optional`

#### Immutable поля

- `tradeId`
- `sessionId`
- `instrumentId`
- `symbol`
- `marketProfile`
- `replayMode`
- `side`
- `openedAt`

#### Mutable поля

- `status`
- `averageEntryPrice`
- `entryPrice`
- `exitPrice`
- `averageExitPrice`
- `stopLoss`
- `takeProfit`
- `volumeOpened`
- `volumeClosed`
- `realisedPnL`
- `totalTradeCost`
- `closeReason`
- `closedAt`
- `updatedAt`
- `userNotesRefs`
- `marketQualityFlagsRefs`
- `lastUnrealisedPnLSnapshot optional`

#### Поля, обязательные для journal/analytics

- `tradeId`
- `sessionId`
- `symbol`
- `timeframeContext`
- `side`
- `openedAt`
- `closedAt`
- `entryPrice`
- `exitPrice`
- `averageEntryPrice`
- `averageExitPrice`
- `volumeOpened`
- `volumeClosed`
- `realisedPnL`
- `closeReason`
- `replayMode`
- `marketQualityFlagsRefs`
- `userNotesRefs`

### ExecutionRecord storage contract

#### Назначение

`ExecutionRecord` хранит каждое атомарное исполнение или закрывающее действие, образуя полную трассу сделки.

#### Persisted или runtime-only

- runtime: да
- persisted: обязательно

Причина:

- execution trace является обязательной базой для journal, analytics, audit trail, add-on и partial close.

#### Обязательные поля

- `executionId`
- `tradeId`
- `sessionId`
- `instrumentId`
- `timestamp`
- `executionType`
- `reason`
- `volume`
- `fillPrice`
- `bid`
- `ask`
- `spread`
- `slippage`
- `commissionComponent`
- `snapshotTimestamp`
- `snapshotTickIndex`
- `marketSessionState`
- `dataQualityFlags`
- `liquidityFlags`
- `datasetPositionReference`
- `createdAt`

#### Optional поля

- `orderId`
- `positionId`
- `positionLegId`
- `requestedPrice`
- `triggerPrice`
- `swapComponent`
- `noteRef`

#### Идентификаторы и связи

- PK: `executionId`
- FK: `tradeId -> TradeRecord.tradeId`
- FK optional: `orderId -> Order.orderId`
- FK optional: `positionId -> Position.positionId`
- FK optional: `positionLegId -> PositionLeg.legId`

#### Lifecycle / status поля

- отдельный `status` не нужен;
- `ExecutionRecord` append-only и immutable after write.

#### Immutable поля

- все поля immutable после записи

#### Mutable поля

- отсутствуют

#### Поля, обязательные для journal/analytics

- `executionId`
- `tradeId`
- `timestamp`
- `executionType`
- `reason`
- `volume`
- `fillPrice`
- `bid`
- `ask`
- `spread`
- `slippage`
- `commissionComponent`
- `swapComponent`
- `snapshotTimestamp`
- `snapshotTickIndex`
- `marketSessionState`
- `dataQualityFlags`
- `liquidityFlags`
- `datasetPositionReference`

### Runtime-only vs persisted summary

Runtime-only or primarily runtime:

- `RiskGuard`
- ephemeral validation results
- transient execution candidate checks

Persisted mandatory:

- `Order`
- `Position`
- `PositionLeg`
- `TradeRecord`
- `ExecutionRecord`

Persisted append-only:

- `ExecutionRecord`
- `PositionLeg` entry facts

Persisted mutable active snapshots:

- `Order`
- `Position`
- `TradeRecord`

### Минимальные storage-связи с journal/analytics

Journal/analytics должны иметь возможность:

- поднять один `TradeRecord` как агрегат сделки;
- развернуть все связанные `ExecutionRecord` в хронологическом порядке;
- увидеть add-on историю через `PositionLeg`;
- увидеть partial close volume changes;
- связать trade/execution timeline с user notes refs;
- восстановить execution context через snapshot timestamp, tick index, session state и quality flags.

### Совместимость с local-first

Storage contract v1 не детализирует sync-модель, но закладывает совместимость:

- IDs локально стабильны;
- append-only trace не зависит от серверной генерации;
- mutable active snapshot сущности могут быть безопасно синхронизированы позже;
- journal/analytics могут работать полностью локально без облака.

## Открытые вопросы, требующие отдельного обсуждения

1. Нужно ли требовать обязательный stop loss для каждой сделки на уровне v1 RiskGuard или оставить это как soft-rule analytics flag.
2. Хотим ли мы в v1 фиксировать explicit expiry policy для pending stop orders или пока ограничиться `cancel/reject`.
3. Нужна ли event-level возможность изменять SL/TP несколько раз внутри одной позиции уже в первом прототипе.
4. Достаточно ли `FIFO` для consumption of legs on partial close или нужен другой deterministic rule.

