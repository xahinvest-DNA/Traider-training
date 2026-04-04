# Bill Williams Layer

Дата фиксации: 2026-03-15
Статус: spec v1
Приоритет: high

## 1. Purpose and Scope

`BILL_WILLIAMS_LAYER.md` переводит reference taxonomy из `02_RESEARCH/BILL_WILLIAMS_RULES.md` в рабочий модульный контракт продукта.

Bill Williams Layer v1 - это методологический classification layer, который работает поверх already defined replay/trading/journal facts и использует зафиксированный vocabulary для:

- setup classification;
- compliance labeling;
- rule-violation mapping;
- review-tag contract;
- future auto-detection boundary.

### Что это такое

- не source of truth для trade facts;
- не analytics cache;
- не UI слой;
- не execution authority;
- не полный signal engine Profitunity;
- не замена review.

### Что входит

- runtime / rule-assisted classification boundary;
- review-assisted classification boundary;
- future auto-detection boundary;
- contracts with replay/trading/journal/analytics;
- границы между methodological setup classification, compliance labels, rule violations и behavioral markers.

### Что не входит

- управление replay cursor;
- исполнение ордеров;
- хранение trade facts как source of truth;
- пересчет аналитики как primary persistence;
- UI workflow screens;
- full machine-verifiable implementation всех setup variations Bill Williams.

## 2. Architectural Role

### Роль в общей архитектуре

Bill Williams Layer sits between:

- factual market/trade/session history;
- methodological interpretation;
- review and progress tracking.

Он использует:

- replay context от `REPLAY_ENGINE.md`;
- execution and lifecycle context от `TRADING_ENGINE.md`;
- persistence references от `DATA_SCHEMA.md` и `JOURNAL_SCHEMA.md`;
- analytics ownership boundaries от `JOURNAL_ANALYTICS.md`;
- vocabulary and method boundaries от `BILL_WILLIAMS_RULES.md`.

### Главная функция

Главная функция слоя - не решать, что рынок сделал, а интерпретировать зафиксированные факты в терминах Bill Williams настолько далеко, насколько это допустимо без подмены человеческого review или несуществующего signal engine.

## 3. Layer Responsibilities

Bill Williams Layer v1 отвечает за:

- применение structured vocabulary к trade/review context;
- выпуск `setup classification proposals` и `compliance label proposals`;
- определение, какие labels допустимы только как review-assisted;
- mapping method-rule classes к `RuleViolation.ruleCode`;
- явную границу между methodological и behavioral layers;
- подготовку future auto-detection candidates.

Bill Williams Layer v1 не отвечает за:

- создание или изменение `TradeRecord`, `ExecutionRecord`, `PositionLeg` как source of truth;
- execution decisions;
- PnL, costs, slippage, market data aggregation;
- analytics ownership;
- mentor scoring.

## 4. Inputs and Outputs

### 4.1. Inputs

Bill Williams Layer может читать следующие входы:

#### Replay inputs

- replay events;
- `simulation_time`;
- active timeframe;
- synchronized timeframes;
- replay mode;
- current bar state by timeframe;
- replay jump / pause / finish context.

#### Trading inputs

- trading events;
- `Order` refs;
- `TradeRecord` refs;
- `ExecutionRecord` refs;
- `PositionLeg` refs if leg-aware interpretation needed;
- trade lifecycle state;
- add-on / partial close / exit reasons.

#### Session / journal inputs

- `TrainingSession` context;
- `PreTradeNote.setupTag`;
- `PreTradeNote.timeframeContext`;
- `PreTradeNote.thesisSummary`;
- `PreTradeNote.riskPlan`;
- `PostTradeReview.reviewTags`;
- `PostTradeReview.outcomeAssessment`;
- `PostTradeReview.disciplineAssessment`;
- `RuleViolation` links;
- `BehavioralFlag` links;
- optional `ChartSnapshot` refs for review-assisted mode.

### 4.2. Outputs

Bill Williams Layer v1 выдает:

- setup classification proposals;
- compliance label proposals;
- review tag vocabulary contract;
- RuleViolation mapping rules;
- BehavioralFlag boundary guidance;
- later auto-detection candidates;
- explicit unresolved/unclear states where runtime facts insufficient.

### 4.3. Output semantics

По умолчанию outputs этого слоя в v1 делятся на:

- `deterministic rule-assisted outputs`;
- `review-assisted outputs`;
- `future-only auto-detection candidates`.

Bill Williams Layer v1 не обязан persistить эти outputs как новый source of truth. Если classification попадает в persistence, она должна жить через уже принятые journal entities и их поля/refs.

## 5. Runtime / Rule-Assisted Classification Boundary

### 5.1. Принцип

Runtime / rule-assisted classification в v1 допустим только там, где available facts already structured enough и не требуют полноценного chart-reading judgment.

### 5.2. Что runtime может знать уже сейчас

Runtime v1 или near-v1 может reliably знать:

- instrument and timeframe context availability;
- replay mode context;
- есть ли active trade lifecycle;
- является ли действие first entry, add-on, partial close или exit;
- привязано ли действие к существующему `TradeRecord` / `ExecutionRecord` / `PositionLeg`;
- заявлен ли user intent через `PreTradeNote.setupTag`;
- есть ли явное расхождение между declared method intent и factual lifecycle state.

### 5.3. Что может классифицироваться rule-assisted

Допустимые runtime / rule-assisted outputs v1:

- `unclear_setup` when runtime facts insufficient;
- `add_on_valid` only in narrow high-level sense;
- `add_on_invalid` when deterministic mismatch exists;
- `exit_by_rule` only where explicit deterministic mapping exists;
- `exit_outside_rule` only where explicit deterministic mapping exists;
- method-related `RuleViolation` candidates for obvious hard mismatches.

### 5.4. Deterministic add-on checks

Runtime v1 может rule-assist `add_on_valid` / `add_on_invalid` только на high level:

- add-on допустим только внутри уже активного `TradeLifecycle`;
- add-on должен ссылаться на существующую открытую `Position`;
- add-on не должен создавать second independent trade;
- add-on должен быть совместим с side existing trade;
- add-on должен быть связан с entry-increasing execution, а не с close execution.

Если эти условия не выполнены:

- допустим `add_on_invalid`;
- допустим `RuleViolation` candidate вроде `bw_invalid_add_on` или `bw_add_on_without_open_context`.

Если условия выполнены:

- допустим только `add_on_valid` в структурном high-level смысле;
- runtime все равно не должен притворяться, что он подтвердил полный AO / Alligator / Fractal context без отдельного signal engine.

### 5.5. Deterministic exit checks

Runtime v1 может rule-assist `exit_by_rule` только в узких случаях, когда:

- exit reason уже однозначно зафиксирован в trading facts;
- существует explicit mapping между reason и method-allowed protective exit;
- нет необходимости в subjective chart reading.

Примеры narrow deterministic cases:

- protective close linked to existing stop/protection plan;
- close because declared trade plan already required protective exit;
- close reason explicitly matches method-protection rule ref later phase.

Во всех остальных случаях:

- runtime должен выдавать `exit_outside_rule` only as candidate or leave classification to review.

### 5.6. Что runtime обязан не делать

Runtime v1 не должен:

- финально подтверждать `First Wise Man` в неоднозначных случаях;
- утверждать `valid_setup`, если нужны chart-context and method judgment;
- подменять review labels автоматическим verdict;
- считать Alligator/AO/Fractal semantics уже реализованными, если signal engine отсутствует;
- выводить methodology certainty из одних execution facts.

## 6. Review-Assisted Classification Boundary

### 6.1. Принцип

Review-assisted classification остается primary mode for Bill Williams method labeling в v1.

### 6.2. Что остается review-assisted

В review-assisted зоне остаются:

- `setupFamily` assignment in ambiguous cases;
- `setupCode` confirmation when chart/context reading needed;
- `weak_setup`;
- `unconfirmed_setup`;
- `late_entry`;
- `early_entry`;
- nuanced `First Wise Man` interpretation;
- `mixed_bw_setup` vs `unclear_bw_setup` distinction;
- context-quality tags requiring chart reading;
- nuanced `exit_by_rule` vs `exit_outside_rule` evaluation where method judgment needed.

### 6.3. Почему это review-assisted

Потому что эти classifications требуют одного или нескольких элементов:

- visual chart reading;
- method judgment over context;
- interpretation of incomplete facts;
- discrimination between weak and invalid setup;
- understanding of how much move was already gone by entry time.

### 6.4. Review actor responsibilities

Review-assisted layer в v1 может использовать:

- `PostTradeReview`;
- related `ChartSnapshot` refs;
- `PreTradeNote` intent;
- full trade timeline;
- optional manual confirmation of derived candidates.

## 7. Future Auto-Detection Boundary

### 7.1. Принцип

Future auto-detection boundary описывает, что later phase может стать partially or fully auto-detectable, но не должно считаться реализованным в v1 только потому, что taxonomy уже существует.

### 7.2. Future auto-detection candidates

Later phases may implement:

- fractal context detection;
- Alligator mouth / outside-mouth logic;
- AO-based continuation checks;
- balance line context detection;
- setup candidate engine;
- confidence scoring for method candidates;
- mentor-assist scoring later.

### 7.3. What remains future-only now

Не считается реализованным сейчас:

- full auto-confirmation of `setupFamily`;
- full machine-verifiable Wise Man canon;
- automatic setup grading;
- advanced multi-timeframe semantic grading;
- probability ranking / confidence engine;
- mentor-grade and progress score.

### 7.4. Safe wording for v1

Пока этот слой не реализован, корректные формулировки только такие:

- `candidate`;
- `proposal`;
- `review-needed`;
- `runtime-insufficient`.

## 8. Contracts with Replay Engine

### 8.1. Что доступно Bill Williams Layer

Из replay layer доступны:

- `simulation_time`;
- active timeframe and synchronized timeframes;
- current bar states;
- replay mode;
- replay lifecycle events;
- consistent temporal ordering of market context.

### 8.2. Что layer может использовать

Bill Williams Layer может использовать replay context для:

- timeframe-aware tagging;
- session/mode awareness;
- aligning review artifacts with simulation time;
- validating that classification references the same replay session context.

### 8.3. Что layer не должен делать

Bill Williams Layer не должен:

- двигать replay cursor;
- создавать собственное независимое время;
- переписывать market source facts;
- заново агрегировать рынок как competing source of truth.

## 9. Contracts with Trading Engine

### 9.1. Отношение к entry, add-on, partial close, exit

Bill Williams Layer может интерпретировать:

- entry;
- add-on;
- partial close;
- exit.

Но только как method classification layer.

### 9.2. Какие сущности может ссылочно использовать

Bill Williams Layer может ссылаться на:

- `Order` for intent and order-type context;
- `TradeRecord` for trade-level context;
- `ExecutionRecord` for event-level execution trace;
- `PositionLeg` for add-on history and leg-aware continuity.

### 9.3. Что layer не делает

Bill Williams Layer не:

- управляет исполнением;
- не подтверждает fill authority;
- не валидирует market price truth;
- не заменяет `RiskGuard`;
- не становится execution authority.

### 9.4. Contract semantics

Trading layer writes facts.
Bill Williams Layer reads facts and produces method interpretation boundaries.

## 10. Contracts with Journal Schema

### 10.1. PreTradeNote contract

`PreTradeNote` may carry structured BW references through existing fields:

- `setupTag`
- `timeframeContext`
- `thesisSummary`
- `riskPlan`

Допустимая semantics v1:

- `setupTag` = declared Bill Williams intent;
- it is not proof that setup was valid.

### 10.2. PostTradeReview contract

`PostTradeReview` may carry:

- final `setupTag`;
- final `complianceLabel`;
- `reviewTags[]`;
- links to `RuleViolation` and `BehavioralFlag` when relevant.

### 10.3. RuleViolation relationship

`RuleViolation.ruleCode` хранит method breach or session-rule breach.

Bill Williams Layer defines:

- which BW rule classes may map to violation candidates;
- where `RuleViolation` is allowed;
- where `unclear` should remain only classification ambiguity.

### 10.4. BehavioralFlag coexistence

`BehavioralFlag` may coexist with method labels when:

- the setup was methodologically valid but behavior poor;
- the setup was weak and behavior also poor;
- there is emotional or discipline context beyond method rule.

### 10.5. classificationSource / classificationMode later

Later phase may introduce explicit fields such as:

- `classificationSource`
- `classificationMode`

Potential values later:

- `runtime_rule_assisted`
- `review_assisted`
- `hybrid`

В v1 это не требуется как schema change, но допустимо как future contract point.

## 11. Contracts with Journal Analytics

### 11.1. Какие BW classifications являются persisted review facts

Если classification persisted in v1, primary persisted facts должны жить через journal entities, mainly:

- `PreTradeNote.setupTag`
- `PostTradeReview.setupTag`
- `PostTradeReview.reviewTags`
- linked `RuleViolation`
- linked `BehavioralFlag`

### 11.2. Какие classifications остаются optional metadata

Optional metadata by default:

- runtime proposals not confirmed by review;
- future setup candidate outputs;
- convenience labels in read models;
- mentor-only qualitative overlays later.

### 11.3. Какие counts later можно агрегировать

Later analytics may aggregate:

- count of setups by family;
- count of `valid_setup` / `weak_setup` / `unconfirmed_setup`;
- count of `late_entry` and `early_entry`;
- count of `add_on_valid` / `add_on_invalid`;
- count of `exit_by_rule` / `exit_outside_rule`;
- progress tracking by method compliance.

### 11.4. Что layer не меняет

Bill Williams Layer does not change:

- current analytics ownership model;
- derive-on-read default;
- source-of-truth boundaries.

## 12. RuleViolation and BehavioralFlag Boundary

### Methodological setup classification

Describes:

- what setup this is;
- what method family it belongs to;
- whether context supports method reading.

### Compliance labeling

Describes:

- how close the action was to Bill Williams method.

### Rule violation mapping

Describes:

- whether explicit declared method rule was broken.

### Behavioral markers

Describes:

- how the trader behaved.

### Boundary rule

These four layers must not be merged.

Allowed coexistence:

- one trade may have method label, compliance label, one rule violation and one behavioral flag.

Forbidden collapse:

- using behavioral code as setup code;
- using rule violation as setup quality label;
- using review tag as substitute for trade fact.

## 13. PreTradeNote / PostTradeReview Contract

### PreTradeNote role

`PreTradeNote` is the place for:

- declared intent;
- planned setup family;
- planned thesis;
- planned risk/protection idea.

It should not be treated as final proof of method compliance.

### PostTradeReview role

`PostTradeReview` is the place for:

- final reviewed setup assignment;
- final compliance label;
- quality tags;
- explicit links to rule/behavior findings.

### Contract rule

If pre-trade and post-trade classifications differ:

- both may coexist;
- post-trade review becomes the authoritative review interpretation;
- trade facts remain external in trade storage.

## 14. MVP Boundary

### Минимально допустимое поведение v1

MVP must support:

- reference vocabulary usable in notes and review;
- limited rule-assisted classification only for deterministic cases;
- review-assisted method labeling as primary path;
- no full signal engine;
- no full machine-verifiable Profitunity implementation.

### MVP outputs

- structured `setupTag` usage;
- limited `complianceLabel` support;
- deterministic rule-assisted add-on and obvious mismatch checks;
- clear `unclear_setup` fallback;
- consistent boundary with `RuleViolation` and `BehavioralFlag`.

## 15. Later Expansion Boundary

Consciously postponed:

- full auto-detection engine;
- deep canonical coverage of all Wise Man variants;
- mentor-grade taxonomy;
- probability/confidence engine;
- advanced multi-timeframe semantic grading;
- setup scoring model;
- full Bill Williams signal engine;
- automated chart-reading quality model.

## 16. Consistency Rules

- Bill Williams Layer does not redefine trade facts.
- Bill Williams Layer does not redefine journal source entities.
- Bill Williams Layer does not become analytics cache.
- Runtime certainty must stay below the level of available facts.
- `review-assisted` remains primary for ambiguous method judgment in v1.
- `unclear_setup` is preferable to false precision.

## 17. Open Questions

1. Should v1 keep `First Wise Man` only as review-level family, or partially formalize it into narrower candidate classes.
2. Whether later we need explicit `classificationSource` fields in journal schema.
3. How far near-v1 rule-assisted logic may go before it effectively becomes a signal engine.
4. Whether method-compliance progress tracking should appear before `PRODUCT_SCOPE.md` and `MVP_vs_FULL.md` are fixed.

## 18. Ready-State Criteria

- Runtime, review-assisted and future auto-detection boundaries are explicit.
- Contracts with Replay Engine, Trading Engine, Journal Schema and Journal Analytics are explicit.
- Methodological setup classification, compliance labels, rule violations and behavioral markers remain separated.
- MVP and later expansion boundaries are fixed.
- Source-of-truth and analytics ownership contracts remain untouched.
