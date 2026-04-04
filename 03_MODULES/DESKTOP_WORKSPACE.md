# Desktop Workspace

Дата фиксации: 2026-03-16
Статус: module contract v1
Приоритет: highest

## 1. Purpose and Scope

`DESKTOP_WORKSPACE.md` фиксирует MVP-level operating contract desktop-контура первого рабочего прототипа.

Документ нужен, чтобы:

- свести replay, one-trade loop, notes/review и basic analytics в один desktop operating surface;
- определить, что именно desktop обязан показывать и инициировать в MVP;
- не превратить desktop contract в полный UI system design;
- сохранить границы source-of-truth слоев и не перенести доменную логику в UI.

Документ не проектирует весь UI/UX продукт целиком и не меняет принятые contracts replay/trading/storage/journal layers.

## 2. Architectural Role

Desktop Workspace v1 - это основной operating surface first working prototype.

Desktop Workspace:

- является главным пользовательским контуром MVP;
- не является source of truth для trade facts или session facts;
- не является местом новой доменной логики replay/trading;
- не является mentor layer;
- не является mobile companion;
- не является BI/dashboard platform.

Роль desktop workspace - давать пользователю единое рабочее пространство, в котором уже принятые source-of-truth слои становятся usable end-to-end workflow.

## 3. Workspace Responsibilities

Desktop Workspace v1 отвечает за:

- запуск и удержание desktop training session surface;
- отображение chart/replay context;
- предоставление replay controls в рамках replay contracts;
- предоставление trading controls в рамках trading contracts;
- показ активной session/trade context;
- создание и редактирование `PreTradeNote` / `PostTradeReview` в границах journal schema;
- показ basic result and analytics surface на derived basis;
- отражение mode/state boundaries для `Training`, `Exam`, `Review Replay`.

Desktop Workspace v1 не отвечает за:

- расчеты рынка или времени;
- исполнение ордеров;
- хранение trade/session source facts как primary owner;
- вычисление analytics как отдельный source of truth;
- full Bill Williams signal assistance;
- mentor collaboration or cloud-first review.

## 4. MVP User Workflow

Минимальный пользовательский цикл MVP desktop workspace:

1. пользователь выбирает или загружает normalized dataset;
2. открывает desktop session по одному инструменту;
3. управляет replay без доступа к будущему;
4. создает `PreTradeNote` при необходимости до сделки;
5. вручную открывает одну сделку;
6. сопровождает и закрывает ее;
7. фиксирует `PostTradeReview`;
8. видит basic review/analytics result по сделке и сессии.

Этот workflow является основным acceptance path для desktop MVP.

## 5. Primary Desktop Surfaces

Desktop MVP ограничен следующими основными поверхностями:

- `Chart / Replay Surface`
- `Trading Control Surface`
- `Session / Trade Context Surface`
- `Notes / Review Surface`
- `Basic Result Surface`

### 5.1. Chart / Replay Surface

Назначение:

- показать рынок и текущее состояние replay session.

Что показывает:

- active instrument;
- active timeframe;
- synchronized timeframe context where available;
- current market bars/ticks as delivered by replay layer;
- current simulation time;
- replay mode and replay state.

Что может инициировать:

- play;
- pause;
- speed change;
- allowed seek/jump actions according to mode;
- timeframe switch inside accepted replay contract.

Какими source-of-truth слоями питается:

- `REPLAY_ENGINE.md`
- normalized dataset derived state via replay only

Что сознательно не входит в MVP:

- advanced chart studies as separate product layer;
- complex layout presets;
- custom workspace docking system;
- independent market calculations inside UI.

### 5.2. Trading Control Surface

Назначение:

- дать минимальный manual trade control inside replay session.

Что показывает:

- active trade status;
- active order status;
- side, volume, stop/take protection if present;
- execution outcomes and close result.

Что может инициировать:

- manual market order;
- manual stop order;
- close active trade;
- minimal manage actions allowed by trading contract.

Какими source-of-truth слоями питается:

- `TRADING_ENGINE.md`
- trade persistence through `TradeRecord` / `ExecutionRecord`

Что сознательно не входит в MVP:

- polished add-on workflow;
- polished partial close workflow;
- complex order editing surface;
- multi-position controls.

### 5.3. Session / Trade Context Surface

Назначение:

- держать пользователя в контексте текущей session и текущей сделки.

Что показывает:

- `TrainingSession` identity;
- replay mode;
- active instrument;
- current session status;
- one active trade context;
- session state such as running / paused / finished / recovered.

Что может инициировать:

- session start;
- session continue after recovery;
- transition into review actions after trade/session completion.

Какими source-of-truth слоями питается:

- replay state;
- trading state;
- `TrainingSession`

Что сознательно не входит в MVP:

- portfolio overview;
- multi-session navigation shell;
- complex session dashboards.

### 5.4. Notes / Review Surface

Назначение:

- дать bounded place for pre-trade thinking и post-trade review.

Что показывает:

- `PreTradeNote` fields;
- `PostTradeReview` fields;
- Bill Williams structured review hooks;
- linked `BehavioralFlag` / `RuleViolation` context where present.

Что может инициировать:

- create/update `PreTradeNote`;
- create/update `PostTradeReview`;
- attach structured BW tags allowed in v1;
- create or link persisted review-related markers where supported by journal contract.

Какими source-of-truth слоями питается:

- `JOURNAL_SCHEMA.md`
- `BILL_WILLIAMS_LAYER.md`

Что сознательно не входит в MVP:

- heavy mentor workflow;
- threaded collaboration;
- advanced media management;
- large review authoring system.

### 5.5. Basic Result Surface

Назначение:

- показать базовый outcome after trade/session completion.

Что показывает:

- realised PnL;
- total trade cost;
- holding time;
- win/loss outcome;
- basic behavioral/rule tracking;
- basic review status.

Что может инициировать:

- open trade/session review context;
- revisit review replay mode where allowed.

Какими source-of-truth слоями питается:

- derived reads from `JOURNAL_ANALYTICS.md`
- source facts from trade and journal storage indirectly

Что сознательно не входит в MVP:

- advanced dashboards;
- heavy summaries;
- deep series analytics;
- BI-like drill-down system.

## 6. Replay Surface Contract

### 6.1. MVP replay controls

В MVP desktop workspace нужны следующие replay controls:

- play;
- pause;
- speed change;
- allowed seek/jump according to replay mode;
- timeframe switch in accepted synchronized context;
- visible replay finished state.

### 6.2. Use of simulation time

Desktop использует `simulation_time` только как delivered state from replay engine.

Desktop:

- отображает current simulation time;
- связывает UI state with replay mode/state;
- не создает собственный независимый clock.

### 6.3. Required reactions to replay events

Desktop должен реагировать на:

- `ReplayPaused` -> update controls and session state;
- `ReplayResumed` -> switch interaction surface to running state;
- `ReplayJumped` -> refresh chart/trade context against new replay position;
- `ReplayFinished` -> show terminal replay state and allow review transition;
- `TimeframeSynced` -> update visible timeframe context and synchronized labels.

### 6.4. What desktop must not do

Desktop не должен:

- становиться вторым источником времени;
- пересобирать replay state сам;
- читать raw dataset напрямую;
- вычислять свой собственный market truth вне replay contract.

## 7. Trading Surface Contract

### 7.1. Required user actions in MVP

MVP desktop trading surface must support:

- manual market order;
- manual stop order;
- close active trade;
- basic manage flow within accepted one-trade model.

### 7.2. Single active trade display

Desktop должен явно показывать:

- есть ли активная сделка;
- side and volume active trade;
- current status active trade lifecycle;
- basic protection context if present;
- execution outcomes for the current trade.

Desktop interaction layer must enforce visible single-trade constraint and not encourage parallel independent trade flows.

### 7.3. ExecutionSnapshot usage boundary

Desktop использует `ExecutionSnapshot` only indirectly:

- via replay state delivered to chart/replay surface;
- via trading outcomes delivered by trading engine;
- not as a standalone source for independent execution decisions in UI.

### 7.4. Outcome display

Desktop должен показывать:

- order accepted/rejected/cancelled states;
- trade opened/closed state;
- key execution outcomes;
- close result for active trade.

### 7.5. What is not required polished MVP UX

Не является обязательным polished MVP UX:

- advanced add-on flow;
- advanced partial close flow;
- complex order editing surface;
- multi-step power-user trade ticket.

## 8. Note and Review Surface Contract

### 8.1. Pre-trade note in MVP

`PreTradeNote` создается в рамках active `TrainingSession` и может быть used before entry or before a concrete planned action.

Desktop должен позволять:

- создать note with session link;
- optionally attach trade link where applicable;
- show structured Bill Williams intent fields allowed in journal contract.

### 8.2. Post-trade review in MVP

`PostTradeReview` создается после trade completion or after session completion in bounded MVP flow.

Desktop должен позволять:

- связать review with `sessionId`;
- связать review with `tradeId` where applicable;
- optionally reference related `executionId` where the journal contract allows it;
- add Bill Williams structured review hooks.

### 8.3. Bill Williams structured review hooks

В MVP notes/review surface может использовать:

- `setupTag`;
- `complianceLabel`;
- `reviewTags[]`;
- links to relevant `RuleViolation` / `BehavioralFlag` where appropriate.

Эти hooks являются bounded review assistance and not a substitute for trade facts.

### 8.4. BehavioralFlag and RuleViolation in desktop flow

Desktop MVP может:

- отображать существующие `BehavioralFlag` / `RuleViolation` markers;
- позволять их bounded capture or linking if already supported by journal flow;
- не превращать review flow в heavy audit console.

### 8.5. Review boundary

Review в desktop MVP остается bounded:

- no mentor workflow;
- no threaded feedback system;
- no rich collaborative review;
- no heavy media review management.

## 9. Basic Analytics Surface Contract

### 9.1. Required basic metrics in MVP

Desktop basic result surface must expose at minimum:

- realised PnL;
- total trade cost;
- holding time;
- win/loss outcome;
- basic behavioral/rule tracking.

### 9.2. Analytics read boundary

Desktop читает analytics как derived layer.

Это означает:

- trade and journal source entities remain owners of facts;
- analytics values are read projections over those facts;
- desktop must not persist analytics summaries as new source of truth.

### 9.3. Explicit exclusions

Не входят в MVP desktop analytics contract:

- advanced dashboards;
- heavy summaries;
- cross-session performance lab;
- deep scoring/ranking systems.

## 10. Contracts with Replay Engine

Desktop читает из replay layer:

- current simulation time;
- current replay mode;
- running / paused / finished state;
- timeframe synchronization state;
- visible market context for chart surface;
- allowed control affordances based on mode.

Desktop инициирует через replay contract:

- play/pause;
- speed change;
- allowed seek/jump actions;
- timeframe changes in accepted bounds.

Desktop не меняет:

- replay event model;
- replay state calculation;
- raw market data ownership.

## 11. Contracts with Trading Engine

Desktop использует trading layer для:

- manual order submission;
- close active trade;
- basic trade management actions allowed in MVP;
- reading order/trade/execution outcomes.

Desktop читает из trading layer:

- active trade state;
- order status;
- execution outcomes;
- single active trade constraint state.

Desktop не является:

- execution authority;
- position ledger;
- alternative lifecycle engine.

## 12. Contracts with Journal Schema

Desktop создает или обновляет в рамках journal contract:

- `TrainingSession` context where required by workflow;
- `PreTradeNote`;
- `PostTradeReview`;
- bounded links to `BehavioralFlag` / `RuleViolation` where supported.

Desktop читает из journal schema:

- existing notes;
- existing reviews;
- persisted behavioral markers;
- persisted rule violations;
- session identity and context.

Desktop не должен:

- переписывать trade source facts через journal forms;
- дублировать `TradeRecord` / `ExecutionRecord` fields as new primary facts.

## 13. Contracts with Journal Analytics

Desktop читает from analytics layer only derived outputs needed for MVP surface:

- realised PnL view;
- total cost view;
- holding time view;
- basic win/loss outcome;
- basic behavioral/rule counters or markers.

Desktop не должен:

- превращать analytics cache в source of truth;
- требовать advanced dashboards as blocker for MVP;
- дублировать analytics-derived summaries as owned UI facts.

## 14. Contracts with Bill Williams Layer

Desktop использует Bill Williams layer only as vocabulary and classification assistance.

Desktop may use:

- `setupTag` vocabulary;
- `complianceLabel` vocabulary;
- `reviewTags` vocabulary;
- bounded links to related `RuleViolation` / `BehavioralFlag` context.

Desktop does not:

- run a full Bill Williams signal engine;
- redefine method boundaries;
- persist method labels outside accepted journal entities.

## 15. State and Mode Boundaries

### 15.1. Replay modes

Desktop must distinguish:

- `Training`;
- `Exam`;
- `Review Replay`.

### 15.2. Exam mode restrictions

В `Exam Mode` desktop must disable or restrict controls that violate replay contract, including:

- forbidden seek-back actions;
- forbidden restart behavior within active exam session;
- any control that pretends future-aware navigation is allowed.

### 15.3. Session state visibility

Desktop должен явно отражать:

- running state;
- paused state;
- finished state;
- recovered state after restart;
- active trade vs no-active-trade state.

### 15.4. One active trade simultaneously

Desktop interaction surface must respect:

- one active trade at a time;
- no second independent trade entry while one lifecycle remains active;
- no portfolio-like visual flow.

## 16. Contracts with Source-of-Truth Layers

### What desktop reads from Replay Engine

- replay state;
- simulation time;
- market display context;
- replay mode and allowed actions.

### What desktop reads or initiates through Trading Engine

- order submission;
- active trade state;
- execution outcomes;
- close action;
- basic manage flow.

### What desktop reads or creates in Journal Schema

- `TrainingSession`;
- `PreTradeNote`;
- `PostTradeReview`;
- `BehavioralFlag`;
- `RuleViolation`;
- related chart/review references if later allowed.

### What desktop reads from Journal Analytics

- derived basic metrics;
- derived basic result summaries;
- no source-of-truth ownership.

### What desktop uses from Bill Williams Layer

- vocabulary;
- review classification assistance;
- bounded method labels only where journal contract allows them.

## 17. Desktop MVP Boundary

В MVP desktop workspace не входят:

- complex multi-window layout system;
- professional multi-monitor terminal behavior;
- mobile-like secondary flows;
- mentor collaboration overlays;
- advanced dashboards;
- cloud-dependent workspace state;
- full Bill Williams signal assistance;
- portfolio / multi-instrument mode.

Также не входят как обязательный polished workflow:

- advanced add-on flow;
- advanced partial close flow;
- rich order editing surface.

## 18. Explicit Non-Goals

Desktop Workspace v1 не должен:

- становиться новым доменным слоем;
- хранить trade or session truth as primary owner;
- заменять mobile review app;
- подменять mentor system;
- превращаться в BI/reporting product;
- требовать full UX system before MVP slice works.

## 19. Acceptance Criteria

Desktop workspace contract считается принятым, если:

- desktop clearly defined as primary operating surface for MVP;
- replay, one-trade loop, notes/review and basic analytics сведены в один bounded contract;
- source-of-truth boundaries не нарушены;
- mode/state boundaries определены явно;
- MVP desktop scope отделен от later-phase UI expansion;
- acceptance scenario описывает end-to-end desktop workflow.

## 20. Acceptance Scenario

Проверяемый desktop MVP scenario:

1. пользователь запускает desktop session;
2. видит chart and replay controls;
3. выбирает или загружает normalized dataset по одному инструменту;
4. запускает replay без доступа к будущему;
5. при необходимости создает `PreTradeNote`;
6. вручную открывает одну сделку;
7. сопровождает и закрывает trade loop;
8. получает `TradeRecord` / `ExecutionRecord` result;
9. оставляет `PostTradeReview` с bounded Bill Williams review hooks;
10. видит basic result surface;
11. закрывает приложение;
12. после повторного запуска может восстановить session/trade/journal facts локально.
