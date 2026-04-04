# MVP vs Full

Дата фиксации: 2026-03-15
Статус: master document
Приоритет: highest

## 1. Purpose of Boundary Document

`MVP_vs_FULL.md` фиксирует границу между:

- обязательным MVP / first working prototype;
- возможностями, которые допустимы позже, но не блокируют первый рабочий контур;
- возможностями, которые явно относятся только к later phases.

Документ нужен, чтобы:

- не тащить в MVP все, что уже architecture-ready;
- остановить scope creep после завершения основных contracts;
- дать проверяемую границу принятия первого рабочего прототипа.

## 2. MVP Definition

MVP проекта Trader Trainer - это минимально замкнутый desktop-first контур, в котором один пользователь может:

- загрузить или выбрать normalized historical dataset;
- запустить replay без доступа к будущему;
- вручную провести одну сделку по Bill Williams;
- сохранить execution trace, journal facts и базовую review/analytics информацию;
- восстановить эти данные локально без облака.

MVP не обязан включать все уже описанные later-ready contracts.

## 3. First Working Prototype Definition

`First Working Prototype` в этом проекте означает практический, проверяемый продуктовый контур, а не только архитектурную готовность.

Для принятия первого рабочего прототипа достаточно, чтобы продукт:

- работал по одному инструменту за сессию;
- поддерживал один активный trade lifecycle;
- позволял честно провести replay-driven manual trade;
- фиксировал trade/journal facts как source-of-truth;
- давал базовый review output после сделки и сессии.

## 4. Boundary Zones

### A. Обязательно для MVP / First Working Prototype

- desktop-first workflow;
- один инструмент на сессию;
- tick-driven replay engine;
- minimal usable `Training Mode`;
- minimal usable `Exam Mode`;
- minimal usable `Review Replay Mode`;
- скрытие будущего и единый replay time cursor;
- manual order placement;
- market orders и stop orders в рамках принятой trading model;
- single active trade lifecycle;
- базовый open -> manage -> close trade flow;
- `TradeRecord` и `ExecutionRecord` trace;
- `TrainingSession` и базовые journal entities;
- `PreTradeNote` и `PostTradeReview`;
- базовые `BehavioralFlag` и `RuleViolation`;
- базовые метрики:
  - realised PnL
  - total trade cost
  - holding time
  - win/loss outcome
  - basic behavioral/rule tracking
- Bill Williams structured review support;
- normalized internal dataset flow;
- local persistence and recovery.

### B. Допустимо позже, но не блокирует первый рабочий контур

- `add-on entry` как продуктово обязательный сценарий;
- `partial close` как продуктово обязательный сценарий;
- richer trade review digests;
- advanced multi-session analytics;
- mentor review overlays;
- mobile review beyond minimal read-only access;
- richer read models, dashboard aggregates and caches;
- advanced Bill Williams rule-assisted classification;
- severity-weighted scoring;
- cloud sync;
- advanced chart/media artifact management.

Примечание:

`add-on` и `partial close` уже приняты на уровне архитектурной и storage-модели, но не фиксируются здесь как блокеры первого рабочего прототипа до отдельного продуктового подтверждения.

### C. Явно вне MVP / Later Phase Only

- multi-instrument portfolio logic;
- multi-position / hedging / netting complexity;
- full broker margin engine;
- universal support всех методов торговли;
- full Bill Williams signal engine;
- probabilistic setup scoring engine;
- full mentor platform;
- production-grade cloud collaboration;
- broad market coverage beyond selected v1 profile;
- mobile as equal trading terminal.

## 5. MVP Required Modules

Для MVP обязательны следующие слои и документы решений:

- `Replay Core` в минимально рабочем виде;
- `Trading Engine` в минимально рабочем виде;
- `Market/Data Layer` в объеме, необходимом для normalized dataset replay;
- `Journal & Analytics` в объеме базовой trace/review/metrics диагностики;
- `Bill Williams Layer` как reference vocabulary + limited rule-assisted support;
- `Desktop Workspace` как основной operating surface;
- local persistence для trade/session/journal facts.

## 6. MVP Optional-but-Non-Blocking Items

Вещи, которые полезны, но не блокируют MVP:

- add-on user flow as polished feature;
- partial close user flow as polished feature;
- optional analytics read models;
- optional `SessionSummary` cache;
- mentor annotations;
- richer snapshot/media management;
- optional read-only mobile review surface.

## 7. Full Version / Later Phase Items

К later phases относятся:

- review layer for mentor workflows;
- mobile companion as полноценный слой разбора;
- cloud sync and cross-device continuity;
- richer dashboards and progress tracking;
- more complete Bill Williams semantic assistance;
- broader market profiles and import coverage;
- commercial layer;
- roles and permissions;
- schools / groups / mentor cabinet.

## 8. Explicitly Deferred Items

Сознательно откладываются:

- full auto-detection of Bill Williams setups;
- deep canonical coverage of all Wise Man variants;
- mentor scoring framework;
- series-level advanced statistics and progression scoring;
- cloud-first collaboration;
- portfolio and account abstraction;
- broker-style margin and exposure logic;
- universal multi-market execution model.

## 9. Hard Exclusions from MVP

Строго не входят в MVP:

- несколько независимых активных сделок одновременно;
- multi-instrument portfolio mode;
- hedging / netting engine;
- automated strategy execution;
- MT5 as architectural core;
- mobile execution;
- cloud dependency as prerequisite;
- analytics cache as source of truth;
- taxonomy labels as substitute for raw trade facts.

## 10. Why These Items Are Deferred

Эти возможности отложены, потому что:

- они не нужны для замкнутого первого пользовательского цикла;
- они резко увеличивают complexity без пропорционального роста обучающей ценности на первом шаге;
- часть из них уже architecture-ready, но еще не product-required;
- premature inclusion увеличит риск scope creep и затормозит появление первого реально работающего контура.

## 11. MVP Boundary by Layer

### Replay Core

Minimum required for MVP:

- tick-driven replay;
- global time cursor;
- hidden future;
- minimal `Training`, `Exam`, `Review Replay`.

Explicitly deferred:

- advanced checkpoints;
- complex scenario branching;
- rich timeline tooling.

Architecture-ready but not product-required yet:

- deeper replay workflow features beyond minimal session usability.

### Trading Engine

Minimum required for MVP:

- manual market and stop orders;
- one active trade lifecycle;
- deterministic execution trace;
- open/manage/close flow.

Explicitly deferred:

- product-critical dependence on add-on and partial close;
- broader execution sophistication.

Architecture-ready but not product-required yet:

- persisted `PositionLeg` support for add-on/partial close trace.

### Market/Data Layer

Minimum required for MVP:

- normalized internal dataset;
- first market profile `FX/CFD`;
- basic quality validation;
- replay-ready bars derived from ticks.

Explicitly deferred:

- wide market coverage;
- complex provider support;
- advanced anomaly handling.

Architecture-ready but not product-required yet:

- richer market profiles and extended import policies.

### Journal & Analytics

Minimum required for MVP:

- `TrainingSession`;
- `PreTradeNote`;
- `PostTradeReview`;
- `BehavioralFlag`;
- `RuleViolation`;
- basic trade/session metrics.

Explicitly deferred:

- advanced multi-session analytics;
- rich derived summaries and caches;
- advanced scoring.

Architecture-ready but not product-required yet:

- optional summaries and richer read models.

### Bill Williams Layer

Minimum required for MVP:

- structured taxonomy;
- compliance labels;
- review tags;
- review-assisted labeling as primary mode;
- limited deterministic runtime assistance.

Explicitly deferred:

- full signal engine;
- advanced auto-detection;
- mentor-grade taxonomy.

Architecture-ready but not product-required yet:

- future auto-detection boundary already defined in contracts.

### Desktop Workspace

Minimum required for MVP:

- chart + replay controls;
- manual trading controls;
- note/review entry points;
- access to basic journal and review output.

Explicitly deferred:

- elaborate layout system;
- polished power-user workspace features.

Architecture-ready but not product-required yet:

- richer desktop UX layers.

### Mobile Review

Minimum required for MVP:

- none.

Explicitly deferred:

- read-only review companion;
- session browsing on mobile;
- mobile review artifacts.

Architecture-ready but not product-required yet:

- mobile as later review layer.

### Sync Layer

Minimum required for MVP:

- none beyond local persistence and recovery semantics.

Explicitly deferred:

- cloud sync;
- conflict resolution;
- collaborative continuity.

Architecture-ready but not product-required yet:

- sync contracts as later extension path.

## 12. Architecture-Ready vs Product-Required

В проекте уже описано больше, чем обязано войти в MVP.

Нужно жестко различать:

- `architecture-ready`: функция или слой уже имеют spec/contract и могут быть реализованы later без переизобретения модели;
- `product-required`: функция нужна, чтобы первый рабочий прототип считался завершенным.

Следствия:

- наличие storage support для add-on/partial close не делает их обязательным MVP feature;
- наличие mobile review architecture не делает mobile частью MVP;
- наличие extended analytics contracts не делает advanced dashboards обязательными;
- наличие future auto-detection boundary не означает наличие signal engine в MVP.

## 13. MVP Acceptance Scenario

Минимальный проверяемый пользовательский сценарий первого рабочего прототипа:

1. Пользователь импортирует или выбирает готовый normalized dataset.
2. Выбирает один инструмент и стартовое время сессии.
3. Запускает replay в desktop workspace и видит рынок без будущих данных.
4. Добавляет `PreTradeNote` с краткой идеей сделки.
5. Вручную открывает сделку по Bill Williams context.
6. Сопровождает сделку в пределах минимального open/manage/close flow.
7. Закрывает сделку.
8. Система сохраняет `TradeRecord` и `ExecutionRecord`.
9. Пользователь добавляет `PostTradeReview` и Bill Williams review tags.
10. Система показывает базовый review session output:
    - outcome
    - realised PnL
    - total trade cost
    - holding time
    - basic rule / behavioral markers

Если этот сценарий проходит end-to-end без потери данных и без обращения к облаку, MVP product boundary считается достигнутой.

## 14. MVP Readiness Criteria

MVP считается готовым, если:

- есть end-to-end desktop flow replay -> trade -> journal -> review;
- replay работает по normalized historical data;
- trade facts сохраняются локально и восстанавливаются;
- journal/session facts сохраняются локально и восстанавливаются;
- базовые Bill Williams labels доступны для review;
- базовые metrics считаются без подмены source-of-truth слоев;
- пользователь может завершить хотя бы одну полную training session.

## 15. Boundary Protection Rules

Чтобы не размыть границу MVP, действуют правила:

- нельзя включать feature в MVP только потому, что она уже описана в spec;
- нельзя превращать architecture-ready later features в блокеры первого релиза;
- любые новые MVP claims требуют явной проверки против `PRODUCT_SCOPE.md`, `CONSTRAINTS.md`, `DECISIONS.md` и `CURRENT_STATE.md`;
- если функция не нужна для acceptance scenario, она не должна считаться обязательной;
- mobile, mentor, sync, advanced analytics и deep Bill Williams automation не могут тихо протечь в MVP через соседние задачи.
