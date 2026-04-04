# Data Schema

Дата фиксации: 2026-03-15
Статус: spec v1
Приоритет: highest

## 1. Назначение документа

`DATA_SCHEMA.md` переводит уже принятую storage-модель trading layer в явный persistence contract уровня технической схемы.

Документ не меняет доменную логику `TRADING_ENGINE.md`, а фиксирует:

- какие trade-сущности persistятся в v1;
- какие из них append-only, а какие mutable;
- как они связаны между собой;
- какие поля обязательны для journal/analytics;
- какие требования накладывает local-first recovery model.

## 2. Границы документа

### Что входит

- persistence-сущности торгового слоя v1;
- ключи, связи и cardinality;
- schema conventions для required/optional/immutable/mutable полей;
- audit и schema version conventions;
- persistence contract между trade storage и journal/analytics;
- recovery/local-first требования.

### Что не входит

- выбор конкретной БД;
- выбор ORM;
- cloud sync implementation;
- новая доменная логика исполнения;
- replay/data import internals beyond already agreed execution context fields;
- UI и mobile-specific модели.

## 3. Schema Principles v1

### Базовые принципы

- persistence contract остается `DB-agnostic`;
- replay остается `tick-driven`, а execution остается `post-tick`;
- storage не является вторым движком доменной логики, а только закрепляет уже принятые инварианты;
- `ExecutionRecord` и `PositionLeg` остаются append-only trace сущностями;
- `Position` и `TradeRecord` остаются mutable active snapshots до завершения сделки;
- `Order` хранится как audit trail пользовательского намерения и состояния ордера;
- active trade lifecycle в v1 ровно один;
- add-on не становится отдельной сделкой;
- partial close и add-on обязаны оставлять trace через `ExecutionRecord` и `PositionLeg`.

### Source of Truth vs Derived

Domain source of truth:

- `Order`
- `Position`
- `PositionLeg`
- `TradeRecord`
- `ExecutionRecord`

Derived / analytics data:

- expectancy
- drawdown
- total cost aggregates
- holding time aggregates
- behavioral flags
- session-level ratios и streak metrics

Derived data может persistиться later phase, но в v1 не должно подменять trade storage как первичный источник.

## 4. Persistence Entity Set v1

Persisted сущности v1:

- `Order`
- `Position`
- `PositionLeg`
- `TradeRecord`
- `ExecutionRecord`

Runtime-only сущности v1:

- `TradeLifecycle`
- `ExecutionSnapshot`
- `RiskGuard`
- ephemeral validation results
- transient execution candidate checks

Future persisted references, которые этот документ учитывает как внешние связи:

- `TrainingSession`
- `JournalSession`
- `PreTradeNote`
- `PostTradeReview`
- `BehavioralFlag`
- `RuleViolation`

## 5. Entity Categories

### Append-only trace entities

- `ExecutionRecord`
- `PositionLeg` as entry facts

Свойства:

- после записи не переписываются как исторический факт;
- используются для reconstructable timeline;
- являются обязательной базой для add-on и partial close trace.

### Mutable active snapshot entities

- `Order`
- `Position`
- `TradeRecord`

Свойства:

- обновляются по мере trade lifecycle;
- должны переживать локальный restart;
- после terminal state часть полей фактически стабилизируется, но сущность не становится append-only историей.

### Runtime-only entities

- `TradeLifecycle`
- `ExecutionSnapshot`
- `RiskGuard`

Свойства:

- не обязаны напрямую persistиться как самостоятельные schema entities;
- их факты должны быть проецируемы в persisted records, если они значимы для audit trail.

## 6. Identifier Rules for Local-First

### Общие правила идентификаторов

- каждый persisted entity получает стабильный локальный доменный ID;
- ID генерируется локально без зависимости от облака;
- ID должен быть уникален в рамках локального хранилища;
- ID не должен зависеть от автоинкремента конкретной БД;
- внешний sync later phase не должен требовать замены локальных ID.

### Рекомендуемые ID категории

- `sessionId`
- `orderId`
- `tradeId`
- `positionId`
- `legId`
- `executionId`
- `noteId later`
- `reviewId later`

### Требования к ID

- stable after creation;
- immutable;
- serializable;
- safe for offline creation;
- suitable for foreign-key style linking even without cloud-generated IDs.

## 7. Schema Conventions

### Required fields

Поля, без которых сущность не считается валидной для записи.

### Optional fields

Поля, которые разрешены, но могут отсутствовать в зависимости от lifecycle stage или режима.

### Immutable fields

Поля, которые после создания не должны изменяться.

### Mutable fields

Поля, которые могут обновляться в рамках active lifecycle.

### Audit fields

Рекомендуемый минимум для persisted entities:

- `createdAt`
- `updatedAt optional when entity mutable`
- `createdBy optional if user/system distinction важна`
- `schemaVersion`

### Schema version fields

Каждая persisted сущность должна быть совместима с versioned schema evolution.

Минимум:

- `schemaVersion`

Рекомендуется:

- entity-level `schemaVersion`
- dataset/session-level compatibility info в соседних техдокументах later phase

## 8. Common Field Conventions

Для persisted trade entities v1 рекомендуются общие поля, где они применимы:

- доменный ID сущности;
- `sessionId`;
- `instrumentId`;
- `createdAt`;
- `updatedAt` для mutable сущностей;
- `schemaVersion`.

Дополнительно для execution-aware сущностей обязательна возможность ссылаться на execution context:

- `snapshotTimestamp`
- `snapshotTickIndex`
- `marketSessionState`
- `dataQualityFlags`
- `liquidityFlags`
- `datasetPositionReference`

## 9. Entity Specification

### 9.1. Order

#### Назначение

`Order` хранит пользовательское или системное намерение на открытие, ожидание trigger, отмену или отклонение торгового действия.

#### Persisted / runtime

- runtime: yes
- persisted: yes

#### Required fields

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
- `schemaVersion`

#### Optional fields

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
- `updatedAt`

#### Lifecycle / status fields

Рекомендуемые `status`:

- `draft`
- `placed`
- `active`
- `filled`
- `cancelled`
- `rejected`
- `expired optional`

#### Immutable fields

- `orderId`
- `sessionId`
- `instrumentId`
- `orderType`
- `side`
- `createdAt`
- `createdBy`
- `replayMode`
- `schemaVersion`

#### Mutable fields

- `status`
- `tradeId`
- `requestedPrice` only if domain later allows pre-activation edits
- `triggerPrice` only if domain later allows pre-activation edits
- `stopLoss`
- `takeProfit`
- `activatedAt`
- `cancelledAt`
- `rejectedAt`
- `filledAt`
- `rejectionReason`
- `expiresAt`
- `updatedAt`

#### Keys and relations

- PK: `orderId`
- FK: `sessionId -> TrainingSession.sessionId later`
- FK: `instrumentId -> InstrumentSpec.instrumentId`
- FK optional: `tradeId -> TradeRecord.tradeId`
- relation: many `Order` to one `TradeRecord`

#### Journal / analytics required fields

- `orderId`
- `tradeId if assigned`
- `orderType`
- `side`
- `requestedVolume`
- `requestedPrice`
- `triggerPrice`
- `status`
- `createdAt`
- `filledAt`
- `rejectionReason`

### 9.2. Position

#### Назначение

`Position` хранит агрегированное текущее состояние одной активной сделки по одному инструменту и одному направлению.

#### Persisted / runtime

- runtime: yes
- persisted: yes

#### Required fields

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
- `schemaVersion`

#### Optional fields

- `stopLoss`
- `takeProfit`
- `closedAt`
- `closeReason`
- `averageExitPrice`
- `lastSnapshotTimestamp`
- `lastSnapshotTickIndex`
- `marketSessionStateAtLastUpdate`
- `qualityFlagsAtLastUpdate`

#### Lifecycle / status fields

Рекомендуемые `status`:

- `open`
- `partially_closed`
- `closed`

#### Immutable fields

- `positionId`
- `tradeId`
- `sessionId`
- `instrumentId`
- `side`
- `openedAt`
- `schemaVersion`

#### Mutable fields

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

#### Keys and relations

- PK: `positionId`
- FK unique: `tradeId -> TradeRecord.tradeId`
- FK: `sessionId -> TrainingSession.sessionId later`
- FK: `instrumentId -> InstrumentSpec.instrumentId`
- relation: one `TradeRecord` to zero-or-one `Position`
- relation: one `Position` to many `PositionLeg`
- relation: one `Position` to many `ExecutionRecord`

#### Journal / analytics required fields

- `tradeId`
- `side`
- `averageEntryPrice`
- `currentOpenVolume`
- `stopLoss`
- `takeProfit`
- `openedAt`
- `closedAt`
- `closeReason`

### 9.3. PositionLeg

#### Назначение

`PositionLeg` хранит каждый входной fill, который увеличивает позицию внутри того же `TradeLifecycle`.

#### Persisted / runtime

- runtime: yes
- persisted: yes

#### Required fields

- `legId`
- `tradeId`
- `positionId`
- `sourceExecutionId`
- `openedAt`
- `entryPrice`
- `openedVolume`
- `remainingVolume`
- `schemaVersion`

#### Optional fields

- `fullyConsumedAt`
- `consumptionRule`
- `noteRef`

#### Lifecycle / status fields

Отдельный persisted `status` не требуется.

Состояние legs вычисляется из объема:

- `remainingVolume == openedVolume` -> open
- `0 < remainingVolume < openedVolume` -> partially_consumed
- `remainingVolume == 0` -> fully_consumed

#### Immutable fields

- `legId`
- `tradeId`
- `positionId`
- `sourceExecutionId`
- `openedAt`
- `entryPrice`
- `openedVolume`
- `schemaVersion`

#### Mutable fields

- `remainingVolume`
- `fullyConsumedAt`
- `consumptionRule`

#### Keys and relations

- PK: `legId`
- FK: `tradeId -> TradeRecord.tradeId`
- FK: `positionId -> Position.positionId`
- FK: `sourceExecutionId -> ExecutionRecord.executionId`
- relation: one `TradeRecord` to many `PositionLeg`
- relation: one `Position` to many `PositionLeg`
- relation: one entry `ExecutionRecord` to one `PositionLeg`

#### Journal / analytics required fields

- `legId`
- `tradeId`
- `positionId`
- `sourceExecutionId`
- `openedAt`
- `entryPrice`
- `openedVolume`
- `remainingVolume`

### 9.4. TradeRecord

#### Назначение

`TradeRecord` является единым persisted агрегатом сделки и главным source-of-truth объектом для journal timeline и trade-level analytics.

#### Persisted / runtime

- runtime: yes, as mutable aggregate during lifecycle
- persisted: yes

#### Required fields

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
- `schemaVersion`

#### Optional fields

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
- `lastUnrealisedPnLSnapshot`

#### Lifecycle / status fields

Рекомендуемые `status`:

- `pending`
- `open`
- `partially_closed`
- `closed`
- `cancelled`
- `rejected`
- `expired optional`

#### Immutable fields

- `tradeId`
- `sessionId`
- `instrumentId`
- `symbol`
- `marketProfile`
- `replayMode`
- `side`
- `openedAt`
- `createdAt`
- `schemaVersion`

#### Mutable fields

- `status`
- `timeframeContext`
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
- `holdingDuration`
- `lastUnrealisedPnLSnapshot`

#### Keys and relations

- PK: `tradeId`
- FK: `sessionId -> TrainingSession.sessionId later`
- FK: `instrumentId -> InstrumentSpec.instrumentId`
- relation: one `TradeRecord` to many `Order`
- relation: one `TradeRecord` to zero-or-one `Position`
- relation: one `TradeRecord` to many `PositionLeg`
- relation: one `TradeRecord` to many `ExecutionRecord`
- relation: one `TradeRecord` to many journal references

#### Journal / analytics required fields

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
- `totalTradeCost`
- `closeReason`
- `replayMode`
- `marketQualityFlagsRefs`
- `userNotesRefs`

### 9.5. ExecutionRecord

#### Назначение

`ExecutionRecord` хранит каждое атомарное исполнение или execution-related action и образует полную трассу сделки.

#### Persisted / runtime

- runtime: yes
- persisted: mandatory

#### Required fields

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
- `schemaVersion`

#### Optional fields

- `orderId`
- `positionId`
- `positionLegId`
- `requestedPrice`
- `triggerPrice`
- `swapComponent`
- `noteRef`

#### Lifecycle / status fields

- отдельный `status` не нужен;
- сущность append-only и immutable after write.

#### Immutable fields

- все поля immutable после записи

#### Mutable fields

- отсутствуют

#### Keys and relations

- PK: `executionId`
- FK: `tradeId -> TradeRecord.tradeId`
- FK: `sessionId -> TrainingSession.sessionId later`
- FK: `instrumentId -> InstrumentSpec.instrumentId`
- FK optional: `orderId -> Order.orderId`
- FK optional: `positionId -> Position.positionId`
- FK optional: `positionLegId -> PositionLeg.legId`
- relation: many `ExecutionRecord` to one `TradeRecord`
- relation: many `ExecutionRecord` to one `Position`

#### Journal / analytics required fields

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

## 10. Relationship Model and Cardinality

### Core relations

- one `TrainingSession` -> many `TradeRecord`
- one `TrainingSession` -> many `Order`
- one `TradeRecord` -> many `Order`
- one `TradeRecord` -> zero-or-one `Position`
- one `TradeRecord` -> many `ExecutionRecord`
- one `TradeRecord` -> many `PositionLeg`
- one `Position` -> many `ExecutionRecord`
- one `Position` -> many `PositionLeg`
- one entry `ExecutionRecord` -> zero-or-one `PositionLeg`

### Invariants

- в рамках одной активной сессии одновременно допускается только один active `TradeRecord` in non-terminal state;
- active `TradeRecord` соответствует не более чем одной active `Position`;
- `PositionLeg` никогда не существует без `TradeRecord` и `Position`;
- `ExecutionRecord` никогда не существует без `TradeRecord`;
- add-on и partial close обязаны попадать в отдельные `ExecutionRecord`;
- add-on entry обязан создавать новый `PositionLeg`;
- partial close обязан уменьшать `remainingVolume` у существующих `PositionLeg` по deterministic rule.

## 11. Persistence Contract Across Trade Entities

### TradeRecord <-> ExecutionRecord

- `TradeRecord` является агрегатом сделки;
- `ExecutionRecord` хранит атомарные факты исполнения внутри сделки;
- journal/analytics должны уметь поднять `TradeRecord` и развернуть все связанные `ExecutionRecord` в хронологическом порядке;
- итоговые trade-level поля (`averageEntryPrice`, `volumeOpened`, `volumeClosed`, `realisedPnL`, `totalTradeCost`) являются агрегированным состоянием, согласованным с execution trace.

### PositionLeg for Add-on Trace

- каждый entry fill или add-on создает отдельный `PositionLeg`;
- `PositionLeg.sourceExecutionId` связывает leg с конкретным entry execution;
- weighted average entry восстанавливается из совокупности активных legs;
- история add-on не хранится как отдельные сделки, а как legs внутри одного `TradeRecord`.

### PositionLeg for Partial Close Trace

- partial close не создает новый `PositionLeg`;
- partial close уменьшает `remainingVolume` у существующих legs по deterministic rule;
- закрывающий факт фиксируется через отдельный `ExecutionRecord`;
- trace partial close восстанавливается через комбинацию:
  - closing `ExecutionRecord`
  - updated `Position.currentOpenVolume`
  - `PositionLeg.remainingVolume`

## 12. Required Execution Context for Analytics

Для любого execution-related analytics обязательны:

- `snapshotTimestamp`
- `snapshotTickIndex`
- `marketSessionState`
- `dataQualityFlags`
- `liquidityFlags`
- `datasetPositionReference`
- `spread`
- `slippage`
- `commissionComponent`
- `swapComponent if present`
- `reason`

Причина:

- без этих полей нельзя честно восстанавливать cost, holding context, anomaly-aware analysis и проверять спорные исполнения.

## 13. Timeline Reconstruction Rules

Journal/analytics должны восстанавливать timeline сделки так:

1. взять `TradeRecord` как агрегат сделки;
2. выбрать все связанные `ExecutionRecord`;
3. отсортировать `ExecutionRecord` по:
   - `timestamp`
   - затем `snapshotTickIndex`
   - затем stable `executionId` as deterministic tie-breaker;
4. подтянуть связанные `PositionLeg`;
5. связать timeline с `userNotesRefs`, `sourceNoteRef`, future `PreTradeNote` и `PostTradeReview`.

Результат reconstruction должен позволять:

- увидеть first entry;
- увидеть каждый add-on;
- увидеть каждый partial close;
- увидеть final close;
- увидеть execution context и cost per execution;
- проверить terminal close reason.

## 14. Persistence Contract with Journal/Analytics

### Что пишет trading layer

Trading layer является writer для:

- `Order`
- `Position`
- `PositionLeg`
- `TradeRecord`
- `ExecutionRecord`

Trading layer также публикует lifecycle and execution events, но source of truth для persistable trade facts остается в указанных сущностях.

### Что journal layer не должен дублировать как source of truth

Journal layer не должен становиться основным владельцем:

- open/close prices;
- volume transitions;
- execution timestamps;
- cost components;
- partial close trace;
- add-on trace.

Эти данные journal layer должен читать или ссылочно проецировать из trade storage.

### Какие journal-сущности только ссылаются на trade storage

В v1 и later phase ссылочными consumers считаются:

- `PreTradeNote`
- `PostTradeReview`
- `BehavioralFlag`
- `RuleViolation`
- `ChartSnapshot`
- session-level analytics records

Они должны ссылаться на:

- `tradeId`
- `executionId optional`
- `orderId optional`
- `sessionId`

### Какие поля обязательны для expectancy, drawdown, total cost, holding time, behavioral flags

#### Expectancy

- `tradeId`
- `realisedPnL`
- `volumeOpened`
- `volumeClosed`
- `side`
- `closeReason`

#### Drawdown

- `closedAt`
- `openedAt`
- `realisedPnL`
- session-level ordering by time

#### Total cost

- `spread`
- `slippage`
- `commissionComponent`
- `swapComponent`
- `totalTradeCost`

#### Holding time

- `openedAt`
- `closedAt`
- partial close timestamps if segmented holding analytics needed later

#### Behavioral flags

- `order timestamps`
- `execution timestamps`
- `closeReason`
- `stopLoss`
- `takeProfit`
- `userNotesRefs`
- `marketSessionState`
- quality/liquidity flags

### Source of truth vs derived analytics data

Source of truth:

- raw trade storage entities, listed above

Derived analytics:

- expectancy
- drawdown statistics
- total trade cost aggregates beyond raw components
- overtrading flags
- revenge trading flags
- no-stop entry flags
- streak metrics
- session summaries

Derived analytics may be recomputed from source-of-truth trade storage and journal references.

## 15. Future Contract with Session / Journal Entities

Этот документ не проектирует полностью `TrainingSession` и journal schema, но задает минимальные ожидания:

- каждая trade-сущность должна иметь `sessionId`;
- journal/session слой должен уметь строить session timeline на основе `TradeRecord` + `ExecutionRecord`;
- notes/reviews/flags должны ссылаться на trade storage через stable IDs;
- trade storage должно быть пригодно для локальной аналитики без обязательного облака.

Минимальные будущие reference points:

- `TrainingSession.sessionId`
- `PreTradeNote.tradeId`
- `PostTradeReview.tradeId`
- `BehavioralFlag.tradeId`
- `BehavioralFlag.executionId optional`
- `RuleViolation.tradeId`

## 16. Recovery / Local-First Requirements

### Какие сущности должны переживать локальный restart

Обязательно:

- `Order`
- `Position`
- `PositionLeg`
- `TradeRecord`
- `ExecutionRecord`

Причина:

- локальный restart не должен уничтожать активную сделку;
- execution trace не должен теряться;
- journal/analytics должны быть доступны локально без облака.

### Как восстанавливается активная сделка

После restart система должна уметь:

1. найти последний non-terminal `TradeRecord`;
2. восстановить связанную `Position`;
3. восстановить все `PositionLeg` с их `remainingVolume`;
4. восстановить связанные active/pending `Order`;
5. поднять execution history через `ExecutionRecord`;
6. продолжить lifecycle без ручного восстановления пользователем.

### Требования к sync-совместимости

- сущности должны иметь stable local IDs;
- append-only trace сущности не должны требовать server-side rewrite;
- mutable snapshot сущности должны быть сериализуемы в полную актуальную версию;
- восстановление active trade должно быть возможно из локального persisted state без server reconciliation;
- later sync не должен требовать cloud-generated IDs как precondition для локальной работы.

## 17. Consistency Rules

### Domain consistency

- `TradeRecord.volumeClosed <= TradeRecord.volumeOpened`
- `Position.currentOpenVolume >= 0`
- `PositionLeg.remainingVolume >= 0`
- sum of active `PositionLeg.remainingVolume` должен согласовываться с `Position.currentOpenVolume`
- terminal `TradeRecord.status` должен быть согласован с terminal `Position.status` if position existed
- `ExecutionRecord.tradeId` должен указывать на существующий `TradeRecord`
- closing `ExecutionRecord` не может существовать без prior open volume

### Audit consistency

- каждый persisted fill должен иметь `ExecutionRecord`
- каждый add-on entry должен иметь и `ExecutionRecord`, и `PositionLeg`
- каждый partial close должен иметь closing `ExecutionRecord`
- каждый execution обязан сохранять execution context fields

## 18. Что остается в TRADING_ENGINE, а что вынесено сюда

В `TRADING_ENGINE.md` остаются:

- lifecycle logic;
- order model;
- execution policy;
- risk rules;
- event model trading layer.

В `DATA_SCHEMA.md` вынесены:

- persistence entities;
- identifiers;
- cardinality;
- immutable/mutable field policy;
- source-of-truth separation;
- recovery/local-first persistence requirements;
- contract between trade storage and journal/analytics.

## 19. Ограничения v1

- одна активная сделка;
- один инструмент за сессию;
- replay tick-driven и post-tick execution не меняются;
- add-on не является отдельной сделкой;
- `ExecutionRecord` и `PositionLeg` обязательны как trace;
- нет portfolio schema;
- нет broker margin schema;
- нет привязки к конкретной БД, ORM или sync stack.

## 20. Открытые вопросы

1. Нужна ли в v1 отдельная persisted история изменения `stopLoss/takeProfit`, или достаточно финального состояния в snapshot entities и execution events.
2. Нужно ли вводить отдельную persisted сущность для session timeline до полной формализации `TrainingSession`.
3. Где пройдет граница между persisted analytics cache и fully derived-on-read analytics в later phases.
4. Нужно ли в v1 явно хранить leg consumption links для каждого partial close, или достаточно `remainingVolume` + FIFO rule.
