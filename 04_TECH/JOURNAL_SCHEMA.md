# Journal Schema

Дата фиксации: 2026-03-15
Статус: spec v1
Приоритет: highest

## 1. Назначение документа

`JOURNAL_SCHEMA.md` формализует persistence schema v1 для session/journal/review слоя Trader Trainer.

Документ описывает:

- какие session/journal сущности persistятся в v1;
- как они ссылаются на trade storage из `DATA_SCHEMA.md`;
- какие из них являются source of truth, а какие derived/read-model;
- как хранить review, behavioral markers и rule violations без дублирования trade facts;
- какие local-first и recovery требования действуют для journal/session слоя.

Документ не меняет доменную логику replay или trading engine и не переопределяет trade storage source of truth.

## 2. Границы документа

### Что входит

- persistence schema для `TrainingSession`, `PreTradeNote`, `PostTradeReview`, `ChartSnapshot`, `BehavioralFlag`, `RuleViolation`;
- решение по `JournalSession`;
- optional derived artifact policy для `SessionSummary`;
- ключи, связи, cardinality и field policy;
- behavioral and review taxonomy v1;
- persistence contract with trade storage;
- session timeline reconstruction;
- recovery / local-first requirements.

### Что не входит

- UI/UX flows journal screens;
- конкретная БД, ORM или sync stack;
- пересмотр trade storage schema;
- расчет полного набора аналитических агрегатов как source of truth;
- mentor layer и roles/permissions beyond references;
- cloud media storage implementation.

## 3. Schema Principles v1

### Базовые принципы

- trade storage source of truth закреплен в `04_TECH/DATA_SCHEMA.md`;
- journal/session layer не переопределяет `Order`, `Position`, `PositionLeg`, `TradeRecord`, `ExecutionRecord`;
- все journal-сущности используют stable IDs trade/session layer;
- replay остается центром времени, поэтому journal timestamps должны быть совместимы с `simulation_time`, `snapshotTimestamp` и session context;
- analytics измеряет не только PnL, но поведение, риск, издержки и дисциплину;
- denormalization допустима только как read model и не становится первичным источником истины;
- local-first обязателен: review и история сессий должны оставаться доступны без облака.

### Source of Truth vs Derived

Primary source of truth for journal/session layer:

- `TrainingSession`
- `PreTradeNote`
- `PostTradeReview`
- `ChartSnapshot`
- `BehavioralFlag`
- `RuleViolation`

Trade source of truth, external to this document:

- `Order`
- `Position`
- `PositionLeg`
- `TradeRecord`
- `ExecutionRecord`

Derived / read-model / cache:

- `SessionSummary optional`
- denormalized timeline rows
- aggregated dashboards
- leaderboard / progress views later

## 4. Entity Set v1

Persisted entities v1:

- `TrainingSession`
- `PreTradeNote`
- `PostTradeReview`
- `ChartSnapshot`
- `BehavioralFlag`
- `RuleViolation`

Optional persisted derived entity:

- `SessionSummary`

Not recommended as separate source-of-truth entity in v1:

- `JournalSession`

Runtime-only or primarily runtime:

- transient review filters
- session timeline projections
- analytics caches
- UI selection state

## 5. Decision on JournalSession

### Рекомендуемое решение v1

Отдельная persisted сущность `JournalSession` в v1 не нужна.

В v1 достаточно одной primary сущности:

- `TrainingSession`

Причина:

- replay, trading и journal already converge on one session identity;
- введение второй session source-of-truth создаст лишнюю двусмысленность;
- потребности review и analytics можно закрыть через `TrainingSession` + linked trade/journal entities + optional derived `SessionSummary`.

### Что допускается later phase

`JournalSession` может появиться later как:

- read-model alias;
- cross-device review projection;
- mentor-facing presentation aggregate.

Но не как отдельный source of truth для session facts v1.

## 6. Identifier Rules for Local-First

### Общие правила

- каждая persisted entity получает локально стабильный ID;
- IDs генерируются offline и не зависят от облака;
- IDs immutable после создания;
- IDs пригодны для cross-entity references;
- session/journal entities должны быть sync-compatible без cloud-generated IDs.

### Рекомендуемые ID

- `sessionId`
- `noteId`
- `reviewId`
- `snapshotId`
- `flagId`
- `violationId`
- `summaryId optional`

## 7. Schema Conventions

### Required fields

Поля, без которых сущность не считается валидной persisted записью.

### Optional fields

Поля, зависящие от режима, completeness review или future extensions.

### Immutable fields

Поля, которые не изменяются после создания сущности.

### Mutable fields

Поля, которые могут обновляться по мере течения сессии или review workflow.

### Audit fields

Минимум для persisted journal entities:

- `createdAt`
- `updatedAt optional for mutable entities`
- `createdBy optional`
- `schemaVersion`

### Time fields

В journal/session layer используются разные time categories:

- `sessionStartedAt` / `sessionEndedAt`
- `noteTimestamp`
- `reviewTimestamp`
- `capturedAt`
- `simulationTime optional`
- `snapshotTimestampRef optional`

Правило:

- если сущность привязана к replay/trade context, она должна уметь ссылаться на simulation-aligned time.

## 8. Entity Specification

### 8.1. TrainingSession

#### Назначение

`TrainingSession` является primary persisted сущностью одной учебной или экзаменационной сессии и контейнером для связанных сделок, заметок, review и behavioral markers.

#### Persisted / runtime

- runtime: yes
- persisted: yes

#### Required fields

- `sessionId`
- `mode`
- `sessionType`
- `instrumentId`
- `symbol`
- `marketProfile`
- `datasetId`
- `startedAt`
- `status`
- `createdAt`
- `schemaVersion`

#### Optional fields

- `endedAt`
- `activeTimeframe`
- `synchronizedTimeframes`
- `datasetStartTime`
- `datasetEndTime`
- `startSimulationTime`
- `endSimulationTime`
- `replaySpeedPolicy`
- `sessionGoal`
- `userContextRef`
- `summaryRef`
- `updatedAt`
- `recoveryContextAcknowledgedAt` for reopened finalized warned-session recovery acknowledgment state

#### Immutable fields

- `sessionId`
- `mode`
- `sessionType`
- `instrumentId`
- `symbol`
- `marketProfile`
- `datasetId`
- `startedAt`
- `createdAt`
- `schemaVersion`

#### Mutable fields

- `status`
- `endedAt`
- `activeTimeframe`
- `synchronizedTimeframes`
- `startSimulationTime`
- `endSimulationTime`
- `replaySpeedPolicy`
- `sessionGoal`
- `summaryRef`
- `updatedAt`
- `recoveryContextAcknowledgedAt`

#### Lifecycle / status fields

Рекомендуемые `status`:

- `created`
- `running`
- `paused`
- `completed`
- `abandoned`
- `recovered`

#### Keys and relations

- PK: `sessionId`
- FK: `instrumentId -> InstrumentSpec.instrumentId`
- FK: `datasetId -> DatasetHandle.datasetId`
- relation: one `TrainingSession` to many `TradeRecord`
- relation: one `TrainingSession` to many `ExecutionRecord`
- relation: one `TrainingSession` to many `PreTradeNote`
- relation: one `TrainingSession` to many `PostTradeReview`
- relation: one `TrainingSession` to many `ChartSnapshot`
- relation: one `TrainingSession` to many `BehavioralFlag`
- relation: one `TrainingSession` to many `RuleViolation`
- relation optional: one `TrainingSession` to zero-or-one `SessionSummary`

#### Source-of-truth role

- source of truth for session identity and session-level metadata;
- source of truth for compact local recovery acknowledgment state tied to the current `TrainingSession`;
- not source of truth for trade facts or execution facts.

### 8.2. PreTradeNote

#### Назначение

`PreTradeNote` хранит размышления пользователя до входа в сделку или до конкретного торгового действия.

#### Persisted / runtime

- runtime: yes
- persisted: yes

#### Required fields

- `noteId`
- `sessionId`
- `noteType`
- `content`
- `noteTimestamp`
- `createdAt`
- `schemaVersion`

#### Optional fields

- `tradeId`
- `executionId`
- `instrumentId`
- `timeframeContext`
- `setupTag`
- `confidenceScore optional`
- `thesisSummary`
- `riskPlan`
- `chartSnapshotRef`
- `updatedAt`

#### Immutable fields

- `noteId`
- `sessionId`
- `noteTimestamp`
- `createdAt`
- `schemaVersion`

#### Mutable fields

- `content`
- `tradeId`
- `executionId`
- `instrumentId`
- `timeframeContext`
- `setupTag`
- `confidenceScore`
- `thesisSummary`
- `riskPlan`
- `chartSnapshotRef`
- `updatedAt`

#### Lifecycle / status fields

Отдельный `status` не обязателен.

Возможные `noteType`:

- `session_plan`
- `trade_intent`
- `pre_entry_observation`

#### Keys and relations

- PK: `noteId`
- FK: `sessionId -> TrainingSession.sessionId`
- FK optional: `tradeId -> TradeRecord.tradeId`
- FK optional: `executionId -> ExecutionRecord.executionId`
- FK optional: `chartSnapshotRef -> ChartSnapshot.snapshotId`

#### Source-of-truth role

- source of truth for user-authored pre-trade thinking;
- never source of truth for entry price, execution or trade state.

### 8.3. PostTradeReview

#### Назначение

`PostTradeReview` хранит review после сделки или после завершения сессии.

#### Persisted / runtime

- runtime: yes
- persisted: yes

#### Required fields

- `reviewId`
- `sessionId`
- `reviewType`
- `content`
- `reviewTimestamp`
- `createdAt`
- `schemaVersion`

#### Optional fields

- `tradeId`
- `relatedExecutionRefs`
- `chartSnapshotRefs`
- `outcomeAssessment`
- `disciplineAssessment`
- `improvementActions`
- `setupVariant`
- `entryTimingLabel`
- `marketContextLabel`
- `exitQualityLabel`
- `reviewClarityLabel`
- `reviewTags`
- `updatedAt`

#### Immutable fields

- `reviewId`
- `sessionId`
- `reviewType`
- `reviewTimestamp`
- `createdAt`
- `schemaVersion`

#### Mutable fields

- `content`
- `tradeId`
- `relatedExecutionRefs`
- `chartSnapshotRefs`
- `outcomeAssessment`
- `disciplineAssessment`
- `improvementActions`
- `setupVariant`
- `entryTimingLabel`
- `marketContextLabel`
- `exitQualityLabel`
- `reviewClarityLabel`
- `reviewTags`
- `updatedAt`

#### Lifecycle / status fields

Отдельный `status` не обязателен.

Возможные `reviewType`:

- `trade_review`
- `session_review`
- `exam_review`

#### Keys and relations

- PK: `reviewId`
- FK: `sessionId -> TrainingSession.sessionId`
- FK optional: `tradeId -> TradeRecord.tradeId`
- FK optional: `relatedExecutionRefs[] -> ExecutionRecord.executionId`
- FK optional: `chartSnapshotRefs[] -> ChartSnapshot.snapshotId`

#### Source-of-truth role

- source of truth for user or system-authored post-trade reflection;
- not source of truth for raw trade outcomes.

### 8.4. ChartSnapshot

#### Назначение

`ChartSnapshot` хранит reference на графический артефакт review without duplicating trade facts.

#### Persisted / runtime

- runtime: optional
- persisted: yes

#### Required fields

- `snapshotId`
- `sessionId`
- `capturedAt`
- `artifactType`
- `artifactRef`
- `schemaVersion`

#### Optional fields

- `tradeId`
- `executionId`
- `simulationTime`
- `timeframeContext`
- `instrumentId`
- `snapshotRole`
- `annotationRef`
- `createdAt`

#### Immutable fields

- `snapshotId`
- `sessionId`
- `capturedAt`
- `artifactType`
- `artifactRef`
- `schemaVersion`

#### Mutable fields

- `tradeId`
- `executionId`
- `simulationTime`
- `timeframeContext`
- `instrumentId`
- `snapshotRole`
- `annotationRef`

#### Lifecycle / status fields

Отдельный `status` не обязателен.

Возможные `snapshotRole`:

- `pre_entry_context`
- `entry_context`
- `management_context`
- `exit_context`
- `review_context`

#### Keys and relations

- PK: `snapshotId`
- FK: `sessionId -> TrainingSession.sessionId`
- FK optional: `tradeId -> TradeRecord.tradeId`
- FK optional: `executionId -> ExecutionRecord.executionId`
- FK optional: `instrumentId -> InstrumentSpec.instrumentId`

#### Source-of-truth role

- source of truth for review artifact reference and capture context;
- not source of truth for market, trade or execution facts visible on the image.

### 8.5. BehavioralFlag

#### Назначение

`BehavioralFlag` хранит manual или derived behavioral marker, связанный с сессией, сделкой или исполнением.

#### Persisted / runtime

- runtime: yes
- persisted: yes

#### Required fields

- `flagId`
- `sessionId`
- `flagCode`
- `source`
- `scope`
- `severity`
- `flagTimestamp`
- `createdAt`
- `schemaVersion`

#### Optional fields

- `tradeId`
- `executionId`
- `noteRef`
- `reviewRef`
- `evidenceRefs`
- `description`
- `confidenceScore`
- `resolvedAt optional later`
- `updatedAt`

#### Immutable fields

- `flagId`
- `sessionId`
- `flagCode`
- `source`
- `scope`
- `flagTimestamp`
- `createdAt`
- `schemaVersion`

#### Mutable fields

- `severity`
- `tradeId`
- `executionId`
- `noteRef`
- `reviewRef`
- `evidenceRefs`
- `description`
- `confidenceScore`
- `resolvedAt`
- `updatedAt`

#### Lifecycle / status fields

`source`:

- `manual`
- `derived`
- `hybrid`

`scope`:

- `session`
- `trade`
- `execution`

`severity`:

- `info`
- `warning`
- `high`

#### Keys and relations

- PK: `flagId`
- FK: `sessionId -> TrainingSession.sessionId`
- FK optional: `tradeId -> TradeRecord.tradeId`
- FK optional: `executionId -> ExecutionRecord.executionId`
- FK optional: `noteRef -> PreTradeNote.noteId`
- FK optional: `reviewRef -> PostTradeReview.reviewId`
- FK optional: `evidenceRefs[] -> ChartSnapshot.snapshotId | ExecutionRecord.executionId | PreTradeNote.noteId | PostTradeReview.reviewId`

#### Source-of-truth role

- source of truth for persisted behavioral classification decisions;
- derived logic may produce flags, but the persisted flag record becomes the authoritative audit record of that classification in the session history.

### 8.6. RuleViolation

#### Назначение

`RuleViolation` хранит факт нарушения торгового, методологического или session rule with explicit scope and evidence.

#### Persisted / runtime

- runtime: yes
- persisted: yes

#### Required fields

- `violationId`
- `sessionId`
- `ruleCode`
- `scope`
- `severity`
- `source`
- `violationTimestamp`
- `createdAt`
- `schemaVersion`

#### Optional fields

- `tradeId`
- `executionId`
- `description`
- `evidenceRefs`
- `hardRule`
- `relatedNoteRef`
- `relatedReviewRef`
- `updatedAt`

#### Immutable fields

- `violationId`
- `sessionId`
- `ruleCode`
- `scope`
- `source`
- `violationTimestamp`
- `createdAt`
- `schemaVersion`

#### Mutable fields

- `severity`
- `tradeId`
- `executionId`
- `description`
- `evidenceRefs`
- `hardRule`
- `relatedNoteRef`
- `relatedReviewRef`
- `updatedAt`

#### Lifecycle / status fields

`scope`:

- `session`
- `trade`
- `execution`

`severity`:

- `soft`
- `hard`

`source`:

- `manual_review`
- `derived_rule_engine`
- `hybrid`

#### Keys and relations

- PK: `violationId`
- FK: `sessionId -> TrainingSession.sessionId`
- FK optional: `tradeId -> TradeRecord.tradeId`
- FK optional: `executionId -> ExecutionRecord.executionId`
- FK optional: `relatedNoteRef -> PreTradeNote.noteId`
- FK optional: `relatedReviewRef -> PostTradeReview.reviewId`

#### Source-of-truth role

- source of truth for persisted rule violation audit trail;
- not source of truth for the underlying trade fact that triggered the violation.

### 8.7. SessionSummary optional

#### Назначение

`SessionSummary` может использоваться later as derived persisted artifact for faster session list rendering and review dashboards.

#### Persisted / runtime

- runtime: optional
- persisted: optional

#### Required fields if persisted

- `summaryId`
- `sessionId`
- `generatedAt`
- `schemaVersion`

#### Optional fields

- `tradeCount`
- `winCount`
- `lossCount`
- `netPnL`
- `totalCost`
- `holdingTimeAggregate`
- `behavioralFlagCount`
- `ruleViolationCount`
- `summaryVersion`

#### Immutable fields

- `summaryId`
- `sessionId`
- `generatedAt`
- `schemaVersion`

#### Mutable fields

- none if generated as append-only snapshot

#### Source-of-truth role

- never source of truth;
- derived cache/read-model only.

## 9. Relationship Model and Cardinality

### Core relations

- one `TrainingSession` -> many `TradeRecord`
- one `TrainingSession` -> many `ExecutionRecord`
- one `TrainingSession` -> many `PreTradeNote`
- one `TrainingSession` -> many `PostTradeReview`
- one `TrainingSession` -> many `ChartSnapshot`
- one `TrainingSession` -> many `BehavioralFlag`
- one `TrainingSession` -> many `RuleViolation`
- one `TradeRecord` -> many `PostTradeReview`
- one `TradeRecord` -> many `ChartSnapshot`
- one `TradeRecord` -> many `BehavioralFlag`
- one `TradeRecord` -> many `RuleViolation`
- one `ExecutionRecord` -> many `BehavioralFlag`
- one `ExecutionRecord` -> many `RuleViolation`
- one `ExecutionRecord` -> many `ChartSnapshot`

### Invariants

- каждая journal entity v1 обязана иметь `sessionId`;
- никакая journal entity не может создавать собственный trade source of truth;
- trade/execution references always use stable IDs from trade storage;
- `BehavioralFlag` и `RuleViolation` могут иметь session-only scope, но если они trade/execution scoped, то ссылка обязательна;
- `ChartSnapshot` не дублирует OHLC, fills и PnL как primary facts;
- `SessionSummary`, если persisted, не подменяет `TrainingSession` и trade storage.

## 10. Persistence Contract with Trade Storage

### Какие сущности журнала только ссылаются на trade storage

- `PreTradeNote`
- `PostTradeReview`
- `ChartSnapshot`
- `BehavioralFlag`
- `RuleViolation`
- `SessionSummary optional`

### Какие поля journal layer читает из trade storage, а не хранит как source of truth

Из `TradeRecord`:

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

Из `ExecutionRecord`:

- `executionId`
- `timestamp`
- `executionType`
- `reason`
- `volume`
- `fillPrice`
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

### Где разрешена денормализация

Разрешена только ради UX/read model:

- session list previews;
- review cards;
- compact timeline rows;
- cached aggregate counters.

Условие:

- денормализованные поля должны быть помечены как derived и пересчитываемые;
- source of truth остается в trade storage и primary journal entities.

### Какие derived entities можно позже кешировать

- `SessionSummary`
- session timeline cache
- trade review digest
- behavioral heatmap aggregates

В v1 они не становятся primary persistence layer.

## 11. Session and Review Link Semantics

### TrainingSession <-> TradeRecord / ExecutionRecord

- `TradeRecord.sessionId` связывает сделку с `TrainingSession`;
- `ExecutionRecord.sessionId` связывает execution trace с `TrainingSession`;
- `TrainingSession` не копирует trade facts, а контейнеризует их на уровне session identity.

### PreTradeNote link semantics

`PreTradeNote` обязательно связан:

- с `sessionId`

Опционально связан:

- с `tradeId`
- с `executionId` later

Смысл:

- note может существовать как session-level planning note до появления конкретной сделки;
- после появления сделки note может быть привязан к `tradeId` without becoming trade fact.

### PostTradeReview link semantics

`PostTradeReview` может быть:

- session-level review;
- trade-level review.

Обязательные links:

- `sessionId`

Опциональные links:

- `tradeId`
- `relatedExecutionRefs`

### ChartSnapshot link semantics

`ChartSnapshot` обязательно связан:

- с `sessionId`

Опционально связан:

- с `tradeId`
- с `executionId`
- с `simulationTime`

Правило:

- snapshot хранит artifact reference и context refs;
- trade prices, volumes и outcomes подтягиваются из trade storage.

## 12. Behavioral and Review Taxonomy v1

### BehavioralFlag codes

Минимальный словарь v1:

- `overtrading`
- `post_loss_revenge_trading`
- `averaging_down`
- `oversized_position`
- `impulsive_entry`
- `no_stop_entry`
- `premature_exit`
- `rule_violation_setup`
- `risk_escalation_after_win`
- `risk_escalation_after_loss`
- `holding_loser_too_long`
- `cost_blind_trading`

### RuleViolation codes

Минимальный словарь v1:

- `bw_setup_missing_confirmation`
- `bw_entry_without_fractal_context`
- `bw_entry_against_alligator_context`
- `session_second_independent_trade_attempt`
- `execution_outside_session_rule`
- `invalid_position_size`
- `missing_stop_loss`
- `manual_plan_deviation`
- `exam_mode_backseek_attempt`
- `exam_mode_restart_attempt`

### Manual review tags optional

Опциональный минимальный словарь:

- `good_process_bad_outcome`
- `bad_process_good_outcome`
- `discipline_kept`
- `discipline_broken`
- `costs_too_high`
- `good_exit`
- `poor_exit`
- `good_risk_control`
- `poor_risk_control`

### Taxonomy principles

- `BehavioralFlag` описывает observed pattern or risk behavior;
- `RuleViolation` описывает explicit violation of declared method/session rule;
- manual review tags служат lightweight qualitative labeling и не заменяют flags/violations.

## 13. Session Timeline Reconstruction

Session timeline восстанавливается из:

- `TrainingSession`
- linked `TradeRecord`
- linked `ExecutionRecord`
- `PreTradeNote`
- `PostTradeReview`
- `ChartSnapshot`
- `BehavioralFlag`
- `RuleViolation`

### Порядок reconstruction

1. взять `TrainingSession`;
2. выбрать все `TradeRecord` по `sessionId`;
3. для каждой сделки выбрать `ExecutionRecord` и отсортировать по:
   - `timestamp`
   - `snapshotTickIndex`
   - stable ID tie-breaker;
4. выбрать все `PreTradeNote` и `PostTradeReview`;
5. выбрать связанные `ChartSnapshot`, `BehavioralFlag`, `RuleViolation`;
6. выстроить unified timeline by:
   - `noteTimestamp`
   - `openedAt`
   - execution timestamps
   - `reviewTimestamp`
   - marker timestamps

### Что timeline должен восстанавливать

- ход сессии;
- последовательность сделок;
- pre-trade thinking;
- execution trace;
- post-trade review;
- behavioral markers;
- rule markers;
- связь между размышлением, действием и результатом.

## 14. Recovery / Local-First Requirements

### Какие сущности обязаны переживать локальный restart

Обязательно:

- `TrainingSession`
- `PreTradeNote`
- `PostTradeReview`
- `ChartSnapshot`
- `BehavioralFlag`
- `RuleViolation`

Причина:

- локальный restart не должен уничтожать историю сессии;
- review должен оставаться доступным offline;
- behavioral/rule audit trail нужен для последующей аналитики.

### Что можно потерять как cache/read-model

- `SessionSummary`
- timeline caches
- denormalized session cards
- temporary analytics projections

### Как session review остается доступным без облака

- все primary journal entities persistятся локально;
- media/artifact refs должны указывать на локально доступный или синхронизируемый later asset;
- review timeline должен собираться из локальных trade + journal entities.

### Sync-compatibility требования

- stable local IDs;
- references only via stable IDs;
- no cloud-generated identity dependency;
- local session history fully readable without reconciliation;
- derived caches can be regenerated after sync.

## 15. Analytics Support Contract

### Journal layer must support at least

- expectancy inputs;
- drawdown inputs;
- total cost analysis;
- holding time analysis;
- behavioral error counting;
- rule violation counting;
- pre-trade vs outcome comparison.

### Required analytics-support fields across journal layer

- `sessionId`
- `tradeId optional`
- `executionId optional`
- timestamps aligned with replay/trade context
- `flagCode` / `ruleCode`
- `severity`
- `source`
- `evidenceRefs`

## 16. Consistency Rules

### Domain consistency

- every journal entity must reference an existing `TrainingSession`;
- trade-scoped journal records must reference existing `tradeId`;
- execution-scoped journal records must reference existing `executionId`;
- `BehavioralFlag.scope` and `RuleViolation.scope` must match available references;
- `SessionSummary` must be reproducible from primary entities if persisted.

### Audit consistency

- pre-trade note must never overwrite trade source-of-truth fields;
- post-trade review must never overwrite realised PnL or execution facts;
- chart snapshot must not become sole storage for trade outcome data;
- derived behavioral flags should preserve `source = derived` or `hybrid`.

## 17. Ограничения v1

- journal layer не переопределяет trade storage;
- replay/trading architecture не меняется;
- analytics cache не становится primary source of truth;
- `JournalSession` не вводится как вторая session source-of-truth сущность;
- schema remains DB-agnostic and local-first.

## 18. Открытые вопросы

1. Нужен ли в v1 отдельный persisted словарь `setupTag` и `Bill Williams review tags`, или пока достаточно строковых/enum refs.
2. Нужна ли отдельная media manifest schema для `ChartSnapshot` artifacts.
3. Стоит ли в v1 хранить `confidenceScore` и `disciplineAssessment` как structured enums или пока как text fields.
4. Нужен ли в v1 session-level derived cache beyond optional `SessionSummary`.
