# Journal Review Loop

Дата фиксации: 2026-03-19
Статус: implementation boundary
Приоритет: highest

## 1. Purpose and Scope

`JOURNAL_REVIEW_LOOP.md` фиксирует следующий implementation slice после working replay+trading runtime: local-first session/journal integration.

Документ нужен, чтобы:

- замкнуть минимальный `session -> trade -> review` loop поверх уже работающего replay+trading runtime;
- перевести `TrainingSession`, `PreTradeNote` и `PostTradeReview` из schema/contracts в узкий implementation-facing scope;
- определить bounded review flow без premature расширения в analytics, mentor, mobile или sync;
- сохранить уже принятые source-of-truth boundaries между trade storage, journal schema, analytics и desktop workspace.

Документ не меняет принятые схемы `DATA_SCHEMA.md` и `JOURNAL_SCHEMA.md`, не расширяет trading logic и не является новым analytics-модулем.

## 2. Why this Slice is Next

Следующий slice логично идет сейчас, потому что:

- replay bootstrap уже реализован;
- minimal executable trading loop уже реализован;
- working runtime уже умеет пройти путь `normalized dataset -> replay session -> tick-driven playback -> BuyMarket/SellMarket -> post-tick fill -> active Position -> manual close -> trade trace`;
- roadmap уже фиксирует, что после trade persistence следующим phase-level шагом должен идти journal and review loop;
- без session/journal binding текущий runtime уже умеет торговать, но еще не замыкает обучающий контур MVP.

Этот slice нужен не для углубления аналитики, а для завершения первого локального учебного цикла: пользователь открыл/закрыл сделку, оставил note/review, перезапустил приложение и не потерял session/journal facts.

## 3. Preconditions / Dependencies

Этот slice опирается на уже принятые и не пересматриваемые зависимости:

- `04_TECH/DATA_SCHEMA.md` остается source of truth для `TradeRecord`, `ExecutionRecord`, `Position`, `PositionLeg`, `Order`;
- `04_TECH/JOURNAL_SCHEMA.md` остается source of truth для `TrainingSession`, `PreTradeNote`, `PostTradeReview` и related journal entities;
- `03_MODULES/JOURNAL_ANALYTICS.md` остается derive-on-read analytics contract и не становится обязательным write-layer для этого slice;
- `03_MODULES/DESKTOP_WORKSPACE.md` остается bounded operating surface, через который note/review loop становится usable, но не owner source facts;
- current runtime already emits enough trade facts to link session/journal entities by stable local IDs.

Минимальные фактические preconditions:

- есть stable `sessionId` boundary для training runtime;
- trade loop уже создает stable `tradeId` и execution trace;
- local persistence уже существует хотя бы на уровне текущего runtime bootstrap;
- runtime способен определить terminal trade state, после которого bounded review flow может открыться.

## 4. In-Scope Behavior

В этот slice входят только следующие поведения:

- local-first binding active runtime к persisted `TrainingSession`;
- создание `TrainingSession` при старте/инициализации session loop либо восстановление уже существующей local session;
- создание `PreTradeNote` в границах active `TrainingSession`;
- optional linking `PreTradeNote -> tradeId` после появления конкретной сделки;
- создание `PostTradeReview` после завершения сделки в bounded review flow;
- linking `PostTradeReview -> sessionId` и `PostTradeReview -> tradeId`;
- bounded desktop-facing projection для отображения current session context, existing pre-trade note state и post-trade review availability/status;
- local persistence и local recovery для session/journal facts этого slice;
- минимально достаточная связь journal entities с existing trade storage facts без дублирования trade truth.

## 5. Explicit Out-of-Scope

В этот slice сознательно не входят:

- advanced analytics;
- dashboards;
- advanced session summaries;
- mentor workflow;
- Bill Williams auto-classification;
- mobile flows;
- cloud sync;
- media management beyond strictly needed minimum;
- heavy `ChartSnapshot` workflow as implementation blocker;
- `BehavioralFlag` / `RuleViolation` как обязательная часть первого coding step этого slice;
- new trading logic;
- replay redesign;
- pending-order expansion, add-on, partial close polish;
- превращение desktop surface в full UI system.

Если что-то не требуется для local-first `session/journal/review` loop, это не должно затягиваться в текущий implementation step.

## 6. Runtime Contract with Working Replay+Trading Slice

Этот slice работает поверх уже принятого runtime contract:

- replay остается owner `simulation_time`, tick progression и playback state;
- trading layer остается owner trade lifecycle и execution trace;
- journal slice читает trade/session context и пишет только session/journal entities своего слоя;
- review flow не меняет `TradeRecord` / `ExecutionRecord` как source facts;
- terminal trade outcome определяется trading runtime, а не review form.

Минимальный runtime handoff:

1. runtime создает или восстанавливает active `TrainingSession`;
2. replay/trading loop выполняется как раньше, без новой торговой логики;
3. при pre-trade action пользователь может создать `PreTradeNote`, связанный минимум с `sessionId`;
4. когда появляется `tradeId`, runtime может привязать note к trade context, если это применимо;
5. после manual close и terminal `TradeRecord.status = closed` runtime открывает bounded возможность создать `PostTradeReview`;
6. journal persistence сохраняет review как отдельный source fact;
7. desktop surface читает combined state через links, а не через дублирование trade data.

## 7. TrainingSession Minimum Integration

Минимальная интеграция `TrainingSession` для этого slice:

- runtime должен иметь одну primary session identity на рабочую replay/trading session;
- `TrainingSession` создается локально при старте нового session loop;
- `TrainingSession` содержит минимум:
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
- в процессе runtime допускается обновление `status`, `endedAt`, `activeTimeframe`, `startSimulationTime`, `endSimulationTime`, `updatedAt`;
- все `TradeRecord`, `ExecutionRecord`, `PreTradeNote` и `PostTradeReview` этого slice обязаны быть связаны через `sessionId`;
- после локального restart runtime должен уметь восстановить active or recent `TrainingSession` и связанный контекст notes/reviews.

Минимальная цель не в богатой session analytics, а в том, чтобы session стала реальным persisted контейнером текущего рабочего loop.

## 8. PreTradeNote Minimum Contract

Минимальный контракт `PreTradeNote` в этом slice:

- note создается локально внутри active `TrainingSession`;
- minimum required linkage: `noteId`, `sessionId`;
- note может существовать до конкретной сделки и не обязан иметь `tradeId` в момент создания;
- если note относится к конкретной сделке, допускается поздняя привязка к `tradeId`;
- note не должен становиться owner trade facts.

Минимально полезные поля для first implementation:

- `noteId`
- `sessionId`
- `noteType`
- `content`
- `noteTimestamp`
- `createdAt`
- `schemaVersion`

Допустимые, но не обязательные в first slice поля:

- `tradeId`
- `instrumentId`
- `timeframeContext`
- `setupTag`
- `thesisSummary`
- `riskPlan`
- `updatedAt`

Поведенческая граница:

- note создается как bounded pre-trade thinking artifact;
- note не блокирует вход в сделку hard-rule'ом, если такой hard-rule отдельно не принят;
- note может быть пустым на уровне продукта only if desktop/runtime flow допускает отсутствие pre-trade authoring, но если note создан, он должен persistиться локально.

## 9. PostTradeReview Minimum Contract

Минимальный контракт `PostTradeReview` в этом slice:

- review создается после terminal close сделки либо в явном post-trade review step;
- minimum required linkage: `reviewId`, `sessionId`;
- для trade-level review в этом slice ожидается `tradeId`;
- review может ссылаться на trade outcome и execution context, но не переписывает их;
- review остается bounded manual reflection artifact, а не analytics summary owner.

Минимально полезные поля для first implementation:

- `reviewId`
- `sessionId`
- `reviewType`
- `content`
- `reviewTimestamp`
- `createdAt`
- `schemaVersion`

Минимально рекомендуемые optional fields для trade-level loop:

- `tradeId`
- `outcomeAssessment`
- `disciplineAssessment`
- `improvementActions`
- `reviewTags`
- `updatedAt`

Не является обязательным для first slice:

- rich media bundle;
- multiple snapshot attachments as blocker;
- mandatory `BehavioralFlag` and `RuleViolation` capture;
- advanced structured scoring.

## 10. Bounded Review Flow

Минимальный bounded review flow для этого slice:

1. пользователь запускает или восстанавливает local `TrainingSession`;
2. управляет replay и trading runtime как в working slice;
3. до entry может создать `PreTradeNote`;
4. выполняет сделку и закрывает ее;
5. после terminal close runtime открывает post-trade review affordance;
6. пользователь создает `PostTradeReview`, связанный с `sessionId` и `tradeId`;
7. desktop surface показывает, что review существует и привязан к trade/session context;
8. после restart session/note/review links восстанавливаются локально.

Граница bounded review:

- один trade-level post-close review step;
- без mentor dialogue;
- без large review workflow tree;
- без превращения review в отдельную review platform.

## 11. Desktop-Facing Note/Review Projection Needs

Desktop для этого slice должен уметь показать только минимально необходимые projections:

- active `TrainingSession` identity and status;
- наличие или отсутствие `PreTradeNote` для текущей session/trade context;
- доступность post-trade review после close;
- наличие уже созданного `PostTradeReview`;
- базовый linked trade context рядом с note/review without duplicating source trade fields;
- recovered state after local restart.

Desktop не обязан в этом slice:

- строить advanced review dashboard;
- считать session summary как persisted artifact;
- управлять complex chart media gallery;
- превращать notes/review в full-screen authoring suite.

## 12. Persistence Expectations

Persistence expectations для этого slice:

- `TrainingSession`, `PreTradeNote`, `PostTradeReview` persistятся локально как primary journal entities;
- их IDs генерируются локально и stable offline;
- trade linkage идет только через stable IDs из `DATA_SCHEMA.md`;
- local restart не должен терять session identity, existing notes или existing reviews;
- session/journal layer не копирует open/close price, realised PnL, execution timestamps и другие trade facts как новый source of truth;
- analytics summaries не persistятся как обязательная часть этого slice;
- если later нужен derived session summary, он остается вне текущего шага.

Минимально ожидаемая local recovery semantics:

- system находит последнюю relevant `TrainingSession`;
- поднимает связанные `TradeRecord` по `sessionId`;
- поднимает связанные `PreTradeNote` и `PostTradeReview`;
- показывает, что session/journal loop продолжим или уже завершен;
- не требует облака для чтения этой истории.

## 13. Acceptance Scenario

Проверяемый acceptance scenario этого slice:

1. пользователь открывает local replay runtime на normalized dataset;
2. runtime создает `TrainingSession` и связывает с ней replay/trading context;
3. пользователь двигается по replay и до входа создает `PreTradeNote`;
4. note сохраняется локально и связан минимум с `sessionId`;
5. пользователь открывает и затем вручную закрывает одну сделку;
6. runtime сохраняет `TradeRecord` / `ExecutionRecord` как раньше;
7. после close пользователь создает `PostTradeReview`, связанный с `sessionId` и `tradeId`;
8. desktop/runtime показывает, что у trade есть note/review linkage;
9. пользователь закрывает приложение или runtime;
10. после повторного запуска локально восстанавливаются `TrainingSession`, trade linkage, `PreTradeNote` и `PostTradeReview`.

## 14. Acceptance Criteria

Slice считается принятым, если:

- `TrainingSession` реально интегрирован в working local runtime, а не только существует в схеме;
- `PreTradeNote` можно создать и локально сохранить в рамках active session;
- `PostTradeReview` можно создать и локально сохранить после закрытия сделки;
- note/review корректно связываются с `sessionId`, а review также с `tradeId`;
- trade storage boundaries не нарушены и trade facts не дублируются как journal truth;
- desktop/runtime может отразить bounded note/review state without advanced dashboards;
- после local restart session/journal facts доступны и читаемы;
- slice не тащит в себя advanced analytics, mentor, mobile, sync или replay/trading redesign.

## 15. Non-Goals / Deferred Items

Отложено на следующие шаги:

- `BehavioralFlag` / `RuleViolation` как полноценный implementation slice;
- Bill Williams structured review enrichment beyond minimum hooks already allowed elsewhere;
- advanced analytics and session summaries;
- mentor-facing review workflows;
- mobile review surfaces;
- sync and cloud reconciliation;
- richer `ChartSnapshot` / media manifest handling;
- dashboards and cross-session statistics;
- broader session orchestration beyond one bounded local training loop.

## 16. Risks / Boundary Protections

Основные риски:

- расползание slice в analytics/dashboard work раньше появления простого local journal loop;
- попытка переопределить trade facts внутри note/review storage;
- смешивание desktop projection с ownership source facts;
- затягивание slice в Bill Williams automation instead of simple persistence-backed review;
- расширение review flow до mentor/mobile/cloud workflows;
- переусложнение `TrainingSession` до тяжёлого session aggregate before MVP need.

Boundary protections:

- trade storage truth остается только в `DATA_SCHEMA.md`;
- session/journal truth остается только в `JOURNAL_SCHEMA.md`;
- analytics остается derive-on-read per `JOURNAL_ANALYTICS.md`;
- desktop остается bounded operating surface per `DESKTOP_WORKSPACE.md`;
- current slice добавляет только minimum local-first session/journal binding;
- любой новый structured classification or automation beyond this scope требует отдельного next-step boundary.
