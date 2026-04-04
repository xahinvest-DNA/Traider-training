# Journal Analytics

Дата фиксации: 2026-03-15
Статус: spec v1.1
Приоритет: highest

## 1. Назначение

Journal and analytics превращает торговую сессию в учебный материал и слой диагностики. Его задача - не заменить trade storage, а использовать уже зафиксированные source-of-truth сущности для расчета метрик, behavioral assessment и review summaries.

Модуль должен отвечать на 4 вопроса:

- что произошло в сделке и сессии;
- сколько это стоило и к чему привело;
- где была поведенческая или дисциплинарная ошибка;
- какие метрики являются фактами хранения, а какие только derived analytics.

## 2. Scope v1.1

### Что входит

- ownership model для ключевых метрик первого контура;
- write/read contract между trade storage, journal schema и analytics layer;
- разделение на source of truth, derived analytics и read models;
- boundaries между execution-, trade-, session- и series-level metrics;
- behavioral analytics contract;
- derived summary policy;
- minimal analytics persistence policy v1.

### Что не входит

- UI/UX экраны статистики;
- конкретная БД, ORM или sync stack;
- пересмотр replay core;
- пересмотр trade persistence schema;
- превращение analytics cache в primary entities.

## 3. Почему это критично

Исследовательский материал проекта показывает, что одного win rate недостаточно. Для обучения нужны метрики, которые ловят:

- стоимость торговли;
- хвостовой риск;
- drawdown;
- частоту сделок и овертрейдинг;
- асимметрию выигрышей и проигрышей;
- поведенческие ошибки и нарушение правил.

Ключевой вывод research base:

- издержки и частота торговли системно ухудшают результат;
- высокая доля прибыльных сделок не гарантирует положительное expectancy;
- контроль поведения и риска важнее, чем простая фиксация PnL;
- series/session-level metrics нужны для отделения удачи от повторяемого процесса.

## 4. Four-Layer Model

### 4.1. Trade source of truth

Определен в `04_TECH/DATA_SCHEMA.md`:

- `Order`
- `Position`
- `PositionLeg`
- `TradeRecord`
- `ExecutionRecord`

Назначение:

- хранить execution facts, costs, fill prices, position changes и trade lifecycle.

### 4.2. Session / journal source of truth

Определен в `04_TECH/JOURNAL_SCHEMA.md`:

- `TrainingSession`
- `PreTradeNote`
- `PostTradeReview`
- `ChartSnapshot`
- `BehavioralFlag`
- `RuleViolation`

Назначение:

- хранить session identity, user reflection, review artifacts, persisted behavioral history и rule history.

### 4.3. Derived analytics

Derived analytics не являются primary storage facts.

Примеры:

- expectancy
- payoff ratio
- win rate
- max drawdown
- trade frequency
- losing streak
- behavioral error count
- session performance aggregates
- series persistence metrics later

### 4.4. Optional read models / cache

Разрешены только как derived-only artifacts:

- `SessionSummary`
- session cards
- dashboard counters
- heatmaps
- cached timeline projections
- trade review digests later

Ограничение:

- ни один read model или cache не становится source of truth.

## 5. Source of Truth vs Derived Analytics

### Primary sources of truth

Trade storage:

- `TradeRecord`
- `ExecutionRecord`
- `PositionLeg` where leg-aware reconstruction is needed

Session/journal storage:

- `TrainingSession`
- `BehavioralFlag`
- `RuleViolation`
- `PreTradeNote`
- `PostTradeReview`
- `ChartSnapshot`

### Что считается derived analytics

- trade-level ratios
- session-level aggregates
- series-level aggregates
- performance persistence windows
- drawdown curves
- streaks
- behavioral counters
- risk and cost summaries

### Что нельзя делать source of truth

- `SessionSummary`
- analytics cache
- dashboard aggregates
- heatmaps
- KPI counters
- denormalized trade cards

## 6. Metrics Ownership Model

### Общий принцип

Каждая метрика должна иметь:

- уровень расчета;
- source inputs;
- calculation owner;
- persist policy;
- cache policy;
- required fields;
- source entities.

### Calculation owner v1

- `trading layer` пишет raw trade facts и costs, но не является owner большинства derived analytics;
- `journal layer` пишет review/history entities и persisted behavioral classifications;
- `analytics layer` является owner расчета derived metrics;
- `analytics layer` mostly derives-on-read in v1;
- optional caches may be written later by analytics layer, but remain derived-only.

## 7. Write/Read Contracts

### Что пишет trading layer

Trading layer пишет только trade source-of-truth entities:

- `Order`
- `Position`
- `PositionLeg`
- `TradeRecord`
- `ExecutionRecord`

Trading layer также публикует lifecycle and execution events.

### Что пишет journal layer

Journal layer пишет только session/journal source-of-truth entities:

- `TrainingSession`
- `PreTradeNote`
- `PostTradeReview`
- `ChartSnapshot`
- `BehavioralFlag`
- `RuleViolation`

### Что пишет analytics layer

В v1:

- analytics layer не обязан писать primary entities;
- analytics layer по умолчанию считает derived metrics on read;
- analytics layer может later писать only derived caches like `SessionSummary`, metric snapshots or dashboard read models.

### Кто только читает

- analytics layer читает trade and journal storage;
- review/reporting layer читает trade, session and derived outputs;
- dashboard/read-model builders читают trade and journal storage.

### Какие поля analytics обязана читать из DATA_SCHEMA, а не копировать

Из `TradeRecord`:

- `tradeId`
- `sessionId`
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
- `side`
- `timeframeContext`
- `replayMode`

Из `ExecutionRecord`:

- `executionId`
- `tradeId`
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

Из `PositionLeg` when needed:

- `legId`
- `tradeId`
- `openedAt`
- `entryPrice`
- `openedVolume`
- `remainingVolume`

Из `TrainingSession`:

- `sessionId`
- `mode`
- `startedAt`
- `endedAt`
- `instrumentId`
- `symbol`
- `datasetId`

Из `BehavioralFlag` and `RuleViolation`:

- `flagCode` / `ruleCode`
- `scope`
- `severity`
- `source`
- `flagTimestamp` / `violationTimestamp`
- `tradeId`
- `executionId`
- `sessionId`

### Stable ID contract

Analytics, summaries and read models обязаны ссылаться только на stable local IDs:

- `sessionId`
- `tradeId`
- `executionId`
- `legId`
- `flagId`
- `violationId`
- `noteId`
- `reviewId`
- `snapshotId`

## 8. Metric Input Requirements

### Базовые input categories

#### Execution inputs

Берутся из `ExecutionRecord`:

- execution timestamp;
- volume;
- fill price;
- spread;
- slippage;
- commission;
- swap;
- execution reason;
- market and data quality context.

#### Trade inputs

Берутся из `TradeRecord`:

- open/close timestamps;
- trade-level realised PnL;
- volumes;
- average entry/exit;
- total trade cost;
- close reason.

#### Session inputs
n
Берутся из `TrainingSession`:

- session start/end;
- mode;
- instrument/session context.

#### Behavioral inputs

Берутся из:

- `BehavioralFlag`
- `RuleViolation`
- optional references to `PreTradeNote` / `PostTradeReview`

### Notes and reviews

`PreTradeNote` и `PostTradeReview` не являются source inputs для базовых PnL metrics.

Они используются только там, где реально нужны:

- pre-trade vs outcome comparison;
- manual review scoring;
- evidence for behavioral/rule interpretation.

## 9. Metric Boundaries

### Метрики только trade level

- net PnL
- total trade cost
- average holding time at single-trade granularity
- average win at per-trade input level
- average loss at per-trade input level
- payoff ratio at per-trade input level

### Метрики только session level

- trade frequency for one session
- session max drawdown
- session drawdown duration
- losing streak in one session
- behavioral error count in one session
- win rate and loss rate for one session
- session expectancy

### Метрики series level only

- multi-session expectancy
- multi-session persistence measures
- rolling drawdown statistics
- 3/6/12 month profitability persistence later
- long-run behavioral regime metrics later

### Метрики, которые не должны считаться на execution level

- expectancy
- payoff ratio
- win rate
- loss rate
- losing streak
- max drawdown
- drawdown duration

Execution level может давать только raw inputs for these metrics.

### Behavioral indicators: event-derived vs review-derived

Event-derived:

- overtrading indicators
- cost-blind behavior
- revenge-like post-loss escalation
- missing stop behavior if derived from order/trade facts
- risk escalation signals

Review-derived:

- impulsive entry confirmed by manual review
- discipline broken
- good process / bad outcome
- bad process / good outcome
- setup-quality tags

## 10. Metric Ownership Table v1

### net PnL

- Level: trade, session, series
- Source entities: `TradeRecord`
- Source fields: `realisedPnL`
- Calculation owner: analytics layer for session/series aggregation; trading layer provides trade-level fact
- Persist policy: trade-level persisted in `TradeRecord`; session/series derived
- Cache allowed: yes, derived-only session summary later
- Required fields: `tradeId`, `sessionId`, `realisedPnL`, `closedAt`
- No new source of truth allowed outside `TradeRecord`

### expectancy

- Level: session, series
- Source entities: `TradeRecord`
- Source fields: `realisedPnL`, `tradeId`, `sessionId`
- Calculation owner: analytics layer
- Persist policy: derive-on-read in v1
- Cache allowed: yes, later session/series cache
- Required fields: `sessionId`, `tradeId`, `realisedPnL`
- Not valid as primary persisted fact

### average win

- Level: session, series
- Source entities: `TradeRecord`
- Source fields: `realisedPnL`
- Calculation owner: analytics layer
- Persist policy: derive-on-read
- Cache allowed: yes
- Required fields: `tradeId`, `sessionId`, `realisedPnL`
- Uses only trades with positive `realisedPnL`

### average loss

- Level: session, series
- Source entities: `TradeRecord`
- Source fields: `realisedPnL`
- Calculation owner: analytics layer
- Persist policy: derive-on-read
- Cache allowed: yes
- Required fields: `tradeId`, `sessionId`, `realisedPnL`
- Uses only trades with negative `realisedPnL`

### payoff ratio

- Level: session, series
- Source entities: `TradeRecord`
- Source fields: `realisedPnL`
- Calculation owner: analytics layer
- Persist policy: derive-on-read
- Cache allowed: yes
- Required fields: positive and negative trade outcomes by `sessionId` or series scope
- Must not be stored as primary trade fact

### win rate

- Level: session, series
- Source entities: `TradeRecord`
- Source fields: `realisedPnL`, `tradeId`
- Calculation owner: analytics layer
- Persist policy: derive-on-read
- Cache allowed: yes
- Required fields: closed trades in target scope
- Does not live at execution level

### loss rate

- Level: session, series
- Source entities: `TradeRecord`
- Source fields: `realisedPnL`, `tradeId`
- Calculation owner: analytics layer
- Persist policy: derive-on-read
- Cache allowed: yes
- Required fields: closed trades in target scope
- Complementary to win rate, not separate source fact

### max drawdown

- Level: session, series
- Source entities: `TradeRecord`
- Source fields: ordered `realisedPnL`, `closedAt`
- Calculation owner: analytics layer
- Persist policy: derive-on-read in v1
- Cache allowed: yes, later summary cache
- Required fields: `sessionId`, `tradeId`, `closedAt`, `realisedPnL`
- No execution-level max drawdown metric in v1

### drawdown duration

- Level: session, series
- Source entities: `TradeRecord`
- Source fields: `closedAt`, ordered cumulative PnL derived from `realisedPnL`
- Calculation owner: analytics layer
- Persist policy: derive-on-read
- Cache allowed: yes
- Required fields: ordered closed trades by scope
- Not source-of-truth persisted field

### trade frequency

- Level: session, series
- Source entities: `TradeRecord`, `TrainingSession`
- Source fields: `tradeId`, `sessionId`, `openedAt`, `closedAt`, `startedAt`, `endedAt`
- Calculation owner: analytics layer
- Persist policy: derive-on-read
- Cache allowed: yes
- Required fields: trade count and target time window
- May be reported as trades per session/day/week depending on scope

### turnover proxy

- Level: trade, session, series
- Source entities: `TradeRecord`, `ExecutionRecord`
- Source fields: `volumeOpened`, `volumeClosed`, `executionType`, `volume`
- Calculation owner: analytics layer
- Persist policy: derive-on-read
- Cache allowed: yes
- Required fields: trade volumes and/or execution volumes in scope
- Must remain derived proxy, not broker ledger source-of-truth

### total trade cost

- Level: trade, session, series
- Source entities: `TradeRecord`, `ExecutionRecord`
- Source fields: `totalTradeCost`, `spread`, `slippage`, `commissionComponent`, `swapComponent`
- Calculation owner: trading layer provides trade-level aggregate; analytics aggregates upward
- Persist policy: trade-level persisted in `TradeRecord`; session/series derived
- Cache allowed: yes
- Required fields: `tradeId`, `sessionId`, `totalTradeCost` or execution cost components
- Cost breakdown uses `ExecutionRecord`; aggregate source fact remains `TradeRecord.totalTradeCost`

### average holding time

- Level: trade, session, series
- Source entities: `TradeRecord`
- Source fields: `openedAt`, `closedAt`
- Calculation owner: analytics layer for averages; trade-level raw duration derived from source timestamps
- Persist policy: derive-on-read; optional `holdingDuration` in `TradeRecord` may exist as convenience but not required as source
- Cache allowed: yes
- Required fields: `openedAt`, `closedAt`, `tradeId`, `sessionId`
- Partial close timestamps may be used later for segmented holding analytics

### losing streak

- Level: session, series
- Source entities: `TradeRecord`
- Source fields: ordered `realisedPnL`, `closedAt`
- Calculation owner: analytics layer
- Persist policy: derive-on-read
- Cache allowed: yes
- Required fields: ordered closed trades in target scope
- Not meaningful on execution level

### behavioral error count

- Level: trade, session, series
- Source entities: `BehavioralFlag`, `RuleViolation`
- Source fields: `flagId`, `flagCode`, `severity`, `sessionId`, `tradeId`, `source`; `violationId`, `ruleCode`, `severity`
- Calculation owner: analytics layer
- Persist policy: derive-on-read from persisted classifications
- Cache allowed: yes
- Required fields: flag/violation rows in scope
- Source of truth for behavioral history remains persisted `BehavioralFlag` and `RuleViolation`, not counter outputs

## 11. Session/Trade/Series Metric Boundaries

### Execution level

Execution level stores inputs, not final performance KPIs.

Allowed derived outputs:

- cost per execution
- execution quality diagnostics
- spread/slippage anomaly views
- event-derived behavioral triggers

### Trade level

Trade level is the first meaningful performance boundary.

Allowed metrics:

- trade net PnL
- trade total cost
- trade holding duration
- trade add-on / partial close trace summaries
- trade-level behavioral markers

### Session level

Session level is the primary analytics boundary for v1 dashboards.

Allowed metrics:

- expectancy
- win/loss rate
- average win/loss
- payoff ratio
- max drawdown
- drawdown duration
- trade frequency
- turnover proxy
- losing streak
- behavioral error count

### Multi-session / series level

Allowed later-phase metrics:

- rolling expectancy
- persistence probability
- long-run drawdown profile
- cross-session behavioral regime stats
- learning/progression markers

## 12. Behavioral Analytics Contract

### Как BehavioralFlag участвует в аналитике

`BehavioralFlag` является persisted source of truth for behavioral history once the flag record exists.

Analytics layer uses `BehavioralFlag` for:

- behavioral error count
- behavior heatmaps
- session discipline summaries
- trade-level behavioral overlays
- series-level behavior trends later

### Когда flag является persisted classification, а когда только derived detection

- raw detection logic may exist runtime-only;
- if detection is persisted as `BehavioralFlag`, that record becomes historical source of truth;
- if detection is not persisted, it remains ephemeral runtime signal and must not be counted as historical behavioral fact.

### Как RuleViolation участвует в score/reporting

`RuleViolation` is source of truth for persisted rule history.

Analytics may use it for:

- rule violation counts
- discipline scoring
- setup compliance reporting
- exam/training integrity summaries

### Manual review and derived detection coexistence

Они сосуществуют так:

- `source = manual` means user/reviewer created classification;
- `source = derived` means rule/detection engine created it;
- `source = hybrid` means derived detection was confirmed or enriched by review.

Конфликта нет, если history keeps source and evidence refs.

### Может ли один behavioral pattern существовать без persisted flag record

Да, как runtime-only detection.

Но в этом случае:

- он не считается частью historical behavioral record;
- он не должен участвовать в persisted counters or long-run analytics.

### Что считается source of truth для behavioral history

- `BehavioralFlag`
- `RuleViolation`

`PreTradeNote` and `PostTradeReview` могут быть evidence or context, but not behavioral history source-of-truth entities by themselves.

## 13. Derived Summaries and Read Models

### SessionSummary

`SessionSummary` - optional derived persisted artifact for faster session list rendering and compact review entry points.

It may contain:

- trade count
- win/loss count
- session net PnL
- total cost
- behavioral flag count
- rule violation count
- lightweight session status summary

It must not contain primary trade facts as new source of truth.

### Разрешенные read models / cache v1

- `SessionSummary optional`
- session list previews
- dashboard counters
- compact session timeline projections

### Разрешенные later read models

- trade review digest
- behavioral heatmap aggregates
- series analytics snapshots
- mentor-facing review digest

### Что категорически нельзя делать source of truth

- session dashboards
- KPI cards
- cached expectancy tables
- heatmaps
- precomputed win rate tables
- progress widgets

## 14. Derived Summary Policy

### Базовая политика v1

- analytics mostly derive-on-read;
- no mandatory analytics cache in v1;
- only optional lightweight summaries may persist later;
- every persisted summary must be marked as derived-only.

### Если cache допустим later

It must include at least:

- `sourceScopeId`
- `generatedAt`
- `summaryVersion`
- `derivedFromSchemaVersions optional`
- `derivedOnly = true`

### Why no primary analytics persistence in v1

- avoids duplication of trade facts;
- preserves local-first simplicity;
- reduces consistency risk;
- keeps recalculation possible after schema evolution.

## 15. Minimal Analytics Persistence Policy v1

### Минимально допустимая политика

- analytics mostly derive-on-read;
- primary persistence belongs to trade storage and journal storage only;
- optional analytics cache is not required for v1;
- if cache appears, it must be explicitly marked derived-only and regenerable.

### Нужен ли отдельный analytics cache already in v1

Рекомендуемое решение:

- нет, не нужен как обязательный слой.

Причина:

- v1 еще формирует source-of-truth storage;
- premature cache layer повышает риск дублирования и drift.

### Какие summaries можно persist later

- `SessionSummary`
- rolling series summary
- dashboard counter snapshots
- derived digest artifacts

## 16. Behavioral Error and Discipline Counting

### behavioral error count

Behavioral error count is derived from persisted behavioral history.

Recommended inputs:

- count of `BehavioralFlag` in scope;
- optional separate count of `RuleViolation`;
- optional weighted view by severity in later phase.

### discipline reporting

Discipline reporting should combine:

- `BehavioralFlag`
- `RuleViolation`
- optional `PostTradeReview.disciplineAssessment`

But only persisted flags/violations form the source-of-truth history.

## 17. Consistency Rules

- analytics never rewrites trade or journal source facts;
- analytics must read stable IDs, not generate alternative identities;
- metrics with trade scope must reconcile with `TradeRecord` source values;
- metrics with behavioral scope must reconcile with persisted `BehavioralFlag` / `RuleViolation`;
- derived summaries must be reproducible from source-of-truth entities;
- no dashboard number may become the only place where a metric exists historically.

## 18. Выходные артефакты модуля

- история сессий;
- список сделок;
- страница разбора сделки;
- агрегированная статистика;
- behavioral and discipline reports;
- база для mentor review later;
- explicit ownership contract for metrics and summaries.

## 19. Открытые вопросы

1. Нужно ли в v1 вводить отдельный severity-weighted scoring model для `BehavioralFlag` и `RuleViolation` или пока ограничиться counts.
2. Нужно ли later хранить explicit rolling series summaries как persisted derived snapshots.
3. Какой минимальный structured vocabulary нужен для `setupTag` и Bill Williams compliance labels.
4. Нужен ли отдельный analytics-specific schema document later, если блок series metrics существенно вырастет.

## 20. Критерии готовности модуля для следующей фазы

- Зафиксирована ownership model для ключевых метрик первого контура.
- Source-of-truth и derived analytics разделены явно.
- Понятен write/read contract между trade storage, journal schema и analytics layer.
- SessionSummary и другие summaries зафиксированы как derived-only.
- Behavioral analytics contract описан явно.
- Analytics cache не становится primary source of truth.
