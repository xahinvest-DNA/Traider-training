# Minimal Executable Trading Loop

Дата фиксации: 2026-03-16
Статус: scope source for next coding slice
Приоритет: highest

## 1. Purpose and Scope

`MINIMAL_EXECUTABLE_TRADING_LOOP.md` фиксирует source-of-scope для следующего vertical slice поверх уже принятого replay bootstrap.

Документ не пересобирает архитектуру replay/trading заново. Его задача - ограничить следующий coding slice до минимального исполнимого торгового контура:

`market open -> active position -> manual close -> trade trace`

Этот документ должен удержать реализацию в рамках уже принятых contracts и не дать следующему шагу расползтись в stop orders, journal, analytics, Bill Williams review или UI-polish beyond MVP order.

## 2. Why This Slice Is Next

Replay bootstrap уже доказал первый working slice:

- normalized dataset выбирается и читается как internal artifact;
- replay session создается;
- simulation time и time cursor инициализируются;
- tick-driven playback работает;
- desktop получает usable replay state;
- mode-aware replay controls уже существуют.

Следующий шаг должен доказать, что этот replay-контур действительно способен поддержать одну реальную ручную сделку end-to-end.

Отдельная большая фаза `ExecutionSnapshot integration` не нужна. `ExecutionSnapshot` остается обязательным внутренним контрактом между replay и trading engine внутри этого slice.

## 3. Preconditions / Dependencies

Этот slice можно начинать только при наличии уже зафиксированных и принятых оснований:

- `01_MASTER/CURRENT_STATE.md`
- `01_MASTER/ROADMAP.md`
- `01_MASTER/PRODUCT_SCOPE.md`
- `01_MASTER/MVP_vs_FULL.md`
- `05_CODEX/DATASET_REPLAY_BOOTSTRAP.md`
- `03_MODULES/TRADING_ENGINE.md`
- `03_MODULES/REPLAY_ENGINE.md`
- `04_TECH/DATA_SCHEMA.md`
- `03_MODULES/DESKTOP_WORKSPACE.md`

Обязательные предпосылки:

- already working replay bootstrap;
- normalized dataset loading already available;
- replay session already creates usable replay state;
- desktop replay surface already получает usable chart/replay context;
- single-cursor and post-tick model уже зафиксированы и не обсуждаются заново.

## 4. In-Scope Behavior

Следующий trading slice включает только минимально необходимое поведение:

- `BuyMarket`
- `SellMarket`
- один активный `TradeLifecycle`
- одна активная агрегированная `Position`
- `ExecutionSnapshot` как единственный вход рынка в trading engine
- исполнение только `post-tick`
- только `manual close`
- минимальный `RiskGuard` для инвариантов v1
- создание и согласование domain / persisted entities:
  - `Order`
  - `Position`
  - `TradeRecord`
  - `ExecutionRecord`
- минимальная desktop projection для активной позиции и terminal trade result

Acceptance path этого slice должен оставаться строго таким:

`market open -> active position -> manual close -> trade trace`

## 5. Explicit Out-of-Scope

Из этого slice явно исключается:

- pending stop orders;
- add-on;
- partial close;
- SL/TP automation beyond minimum, если это не strictly required for compilation/runtime consistency;
- SL/TP modification history;
- journal / review flow;
- analytics calculations;
- Bill Williams classification;
- mentor flows;
- mobile flows;
- sync;
- multi-trade logic;
- multi-instrument logic;
- portfolio behavior;
- persistence hardening beyond minimum needed for this slice;
- replay recovery as separate dedicated scope;
- advanced desktop controls or polished desktop UX.

## 6. Runtime Contract with Replay / Bootstrap

Этот slice обязан использовать уже работающий replay bootstrap как единственный runtime source для времени и рынка.

Trading side получает:

- current replay mode;
- current replay state;
- current simulation time;
- current dataset position;
- current market snapshot only через `ExecutionSnapshot` contract;
- replay finished / paused / running status.

Trading side не должен:

- читать raw dataset напрямую;
- читать normalized tick stream в обход replay session;
- создавать собственное независимое время;
- пересобирать cursor model;
- исполнять действия intratick;
- обходить mode restrictions, already enforced by replay layer.

## 7. Minimal Order / Trade Lifecycle

Минимальный lifecycle этого slice:

1. `Idle`
2. `EntryRequested`
3. `PositionOpened`
4. `CloseRequested`
5. `PositionClosed`
6. `Terminal`

Смысл состояний:

- `Idle`: активной сделки нет.
- `EntryRequested`: пользователь дал `BuyMarket` или `SellMarket`, команда прошла первичную валидацию, но fill еще не произошел.
- `PositionOpened`: первый допустимый post-tick snapshot дал fill, сделка открыта.
- `CloseRequested`: пользователь дал manual close, но close fill еще не произошел.
- `PositionClosed`: на первом допустимом post-tick snapshot после close request позиция закрыта.
- `Terminal`: lifecycle завершен, активной сделки больше нет.

Допустимые переходы:

- `Idle -> EntryRequested`
- `EntryRequested -> PositionOpened`
- `PositionOpened -> CloseRequested`
- `CloseRequested -> PositionClosed`
- `PositionClosed -> Terminal`

Недопустимые переходы в этом slice:

- second independent entry while active lifecycle exists;
- add-on transitions;
- partial close transitions;
- pending order activation transitions;
- automatic SL/TP close transitions as mandatory product behavior.

## 8. ExecutionSnapshot Contract Usage

`ExecutionSnapshot` является обязательным внутренним контрактом между replay и trading.

В этом slice он используется для двух вещей:

- fill market entry;
- fill manual close.

Обязательные свойства usage contract:

- trading engine не читает рынок напрямую из dataset artifacts;
- market command не исполняется немедленно вне snapshot cycle;
- entry fill происходит только на первом допустимом `post-tick` snapshot после команды;
- close fill происходит только на первом допустимом `post-tick` snapshot после manual close command;
- execution reason и snapshot context должны быть пригодны для будущего trade trace.

В этом slice `ExecutionSnapshot` не расширяется до:

- pending stop trigger engine;
- advanced liquidity heuristics;
- SL/TP auto-exit orchestration;
- add-on / partial close semantics.

## 9. RiskGuard Minimum Responsibilities

`RiskGuard` в этом slice остается минимальным и защищает только v1 invariants.

Минимальные обязанности:

- не допускать вторую независимую сделку при active lifecycle;
- валидировать, что `BuyMarket` / `SellMarket` разрешены только из `Idle`;
- валидировать, что manual close разрешен только при active open position;
- валидировать, что replay session пригодна для trading action;
- валидировать, что replay не находится в terminal `finished` state for new entry;
- предотвращать команды, противоречащие mode/session invariants этого slice.

`RiskGuard` в этом slice не обязан:

- делать full broker-style margin checks;
- считать advanced risk sizing;
- валидировать pending order logic;
- обеспечивать behavioral discipline rules;
- становиться substitute for future journal analytics or BW compliance.

## 10. Required Entities

Для этого slice обязательны следующие сущности:

### Order

Нужен как record пользовательской команды на entry и close-related action within accepted trading contract.

### Position

Нужна как одна активная агрегированная позиция в рамках одного active lifecycle.

### TradeRecord

Нужен как единый trade-level aggregate, пригодный для последующего journal/analytics layer.

### ExecutionRecord

Нужен как атомарный trace исполнения entry и close.

### Runtime note

`TradeLifecycle` в этом slice остается runtime concept, но acceptance завязана на появление и согласованность четырех перечисленных сущностей выше.

## 11. State Transitions

Минимальные state transitions для slice:

### Entry path

- user command `BuyMarket` or `SellMarket`
- `RiskGuard` validates command
- system creates entry intent / order state
- next valid post-tick `ExecutionSnapshot` produces fill
- active `Position` opens
- `TradeRecord` moves into open state
- entry `ExecutionRecord` is recorded

### Close path

- user command `manual close`
- `RiskGuard` validates that open position exists
- system creates close intent inside current lifecycle
- next valid post-tick `ExecutionSnapshot` produces close fill
- `Position` closes
- `TradeRecord` moves to closed / terminal-consistent state
- closing `ExecutionRecord` is recorded

### Invariant

После close path active trade count снова должен стать равен нулю.

## 12. Desktop-Facing Projection Needs

Desktop surface не является source of truth, но для usable MVP slice должен получать минимум:

- active trade presence or absence;
- trade side;
- current open volume;
- average entry price;
- current order/trade status;
- last execution outcome;
- manual close availability;
- replay mode and session context still visible;
- unrealized PnL optional, если получается almost free from already available state.

Desktop projection в этом slice не обязана включать:

- polished multi-panel trade terminal;
- advanced order ticket editing;
- add-on / partial close interaction model;
- advanced review surface;
- analytics dashboards.

## 13. Acceptance Scenario

Slice считается принятым, если проходит следующий сценарий:

1. Есть готовая replay session на normalized dataset.
2. Пользователь дает команду `BuyMarket` или `SellMarket`.
3. Команда проходит через минимальный `RiskGuard`.
4. На первом допустимом post-tick snapshot создается fill.
5. Открывается один `TradeLifecycle` и одна `Position`.
6. Во время replay desktop видит актуальное состояние позиции:
   - `side`
   - `volume`
   - `average entry`
   - `unrealized pnl optional`
7. Пользователь дает команду manual close.
8. На следующем допустимом post-tick snapshot позиция закрывается.
9. Формируются минимально согласованные records:
   - `Order`
   - `TradeRecord`
   - `ExecutionRecord`
   - `Position`
10. Lifecycle переходит в terminal state без нарушения инварианта `one active trade`.

## 14. Acceptance Criteria

Задача считается принятой, если:

- replay bootstrap уже работает и используется без обходных контуров;
- пользователь может дать `BuyMarket` / `SellMarket` command;
- команда проходит только через допустимый lifecycle path;
- fill происходит только `post-tick`;
- одновременно существует не более одного active lifecycle;
- одновременно существует не более одной active aggregated `Position`;
- manual close работает через тот же post-tick execution discipline;
- создаются минимально согласованные `Order`, `Position`, `TradeRecord`, `ExecutionRecord`;
- после закрытия trace пригоден для future journal / analytics integration;
- slice не затягивает pending orders, add-on, partial close, journal, analytics or BW review.

## 15. Non-Goals / Deferred Items

Сознательно отложено на later slices:

- pending stop orders;
- add-on;
- partial close;
- SL/TP automation as full exit path;
- stop/limit order management surface;
- persisted replay recovery;
- journal notes / post-trade review;
- analytics calculations and summaries;
- Bill Williams review or runtime classification;
- advanced desktop UX;
- cloud/sync/mobile/mentor concerns.

## 16. Risks / Boundary Protections

Главные риски этого slice:

### Scope creep into trading richness

Риск:

- незаметно протянуть pending orders, add-on, partial close и SL/TP logic.

Protection:

- любое расширение beyond `market open -> manual close` считается out-of-scope until separate accepted task.

### Scope creep into journal / analytics

Риск:

- пытаться сразу дописать notes, review, metrics и dashboards.

Protection:

- этот slice обязан завершаться trade trace, а не journal/reporting surface.

### Breaking replay ownership

Риск:

- дать trading layer доступ к dataset or independent time handling.

Protection:

- `ExecutionSnapshot` only, post-tick only, no direct dataset reads.

### Breaking one-active-trade invariant

Риск:

- неявно допустить multiple active trades or second entry.

Protection:

- minimal `RiskGuard` обязан блокировать second independent trade path.

### Over-hardening persistence too early

Риск:

- увязнуть в recovery and storage hardening до того, как заработает базовый one-trade loop.

Protection:

- minimum entity consistency yes; full persistence hardening no.
