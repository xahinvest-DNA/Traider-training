# Dataset and Replay Bootstrap

Дата фиксации: 2026-03-16
Статус: implementation-facing boundary
Приоритет: highest

## 1. Purpose and Scope

`DATASET_REPLAY_BOOTSTRAP.md` переводит уже принятые contracts replay/data/desktop layers в первый реально кодируемый bootstrap-срез.

Документ нужен, чтобы:

- ограничить первый implementation slice границей `normalized dataset -> replay session -> chart/replay controls`;
- сделать понятным, что именно кодировать первым;
- не тянуть в стартовую реализацию trading, journal, analytics и Bill Williams review beyond boundary;
- сохранить source-of-truth и MVP boundaries без перепроектирования архитектуры.

## 2. Bootstrap Goal

Goal bootstrap-среза:

- загрузить already normalized dataset;
- создать replay session по одному инструменту;
- инициализировать `simulation_time` и `time_cursor`;
- воспроизводить рынок tick-driven без доступа к будущему;
- дать desktop surface usable chart/replay state and controls.

Это первый implementation slice before one-trade lifecycle.

## 3. Vertical Slice Boundary

### В slice входят

- dataset selection/loading;
- dataset metadata and manifest read;
- replay session creation;
- one-instrument replay context;
- tick-driven playback;
- chart/replay controls;
- mode-aware replay behavior in minimal usable form.

### В slice не входят как обязательные

- trade execution loop;
- order placement;
- trade persistence;
- notes/review flow;
- analytics surfaces;
- Bill Williams review assistance;
- mobile;
- sync.

## 4. Source-of-Truth Documents

Bootstrap обязан опираться на:

- `03_MODULES/REPLAY_ENGINE.md` для time/event model;
- `03_MODULES/DATA_IMPORT.md` для normalized dataset contract;
- `03_MODULES/MARKET_MODEL.md` для instrument/profile assumptions;
- `03_MODULES/DESKTOP_WORKSPACE.md` для replay surface contract;
- `01_MASTER/ROADMAP.md` для phase sequencing;
- `01_MASTER/PRODUCT_SCOPE.md` и `01_MASTER/MVP_vs_FULL.md` для product boundary;
- `01_MASTER/CONSTRAINTS.md` для hard constraints.

## 5. Required Inputs

Минимальные required inputs bootstrap slice:

- selected dataset handle or dataset id;
- selected instrument id;
- accepted market profile;
- replay mode (`Training`, `Exam`, `Review Replay`);
- initial active timeframe;
- synchronized timeframe set;
- dataset manifest;
- dataset quality report.

## 6. Required Runtime Outputs

Минимальные runtime outputs bootstrap slice:

- created replay session;
- initialized replay state;
- visible current `simulation_time`;
- visible current instrument/timeframe/mode context;
- visible market playback state for chart surface;
- working controls for play/pause/speed/allowed seek;
- correct transition to finished state;
- explicit failure state on invalid bootstrap prerequisites.

## 7. Minimal End-to-End Flow

Минимальный end-to-end flow:

1. пользователь выбирает dataset;
2. система валидирует bootstrap prerequisites;
3. создается replay session;
4. chart surface показывает initial market context;
5. пользователь жмет play/pause;
6. replay двигается по тикам;
7. пользователь видит `simulation_time` и market movement;
8. при конце датасета replay переходит в finished state.

## 8. Replay Session Bootstrap Contract

### 8.1. Session creation steps

Для создания replay session нужны шаги:

1. принять dataset handle;
2. проверить manifest and quality prerequisites;
3. проверить instrument/profile compatibility;
4. инициализировать replay mode;
5. инициализировать active timeframe and synchronized timeframes;
6. позиционировать `time_cursor` на начальный допустимый tick;
7. вычислить initial replay state;
8. опубликовать initial replay-ready state for desktop surface.

### 8.2. Minimal initialized state fields

Минимальные state fields, которые должны быть initialized:

- `dataset_id` or handle;
- `instrument_id`;
- `market_profile`;
- `replay_mode`;
- `active_timeframe`;
- `synchronized_timeframes`;
- `dataset_start_time`;
- `dataset_end_time`;
- `time_cursor` position;
- `simulation_time`;
- `speed_multiplier`;
- `is_paused`;
- `is_finished`;
- current chart/replay projection state.

### 8.3. Required links

Replay session must be linked with:

- dataset;
- instrument;
- replay mode;
- active timeframe;
- synchronized timeframes.

### 8.4. Failure states

Bootstrap must explicitly handle:

- dataset not found;
- invalid or unsupported manifest;
- empty tick stream;
- out-of-bound seek target;
- replay already finished;
- corrupted metadata;
- incompatible schema version.

## 9. Dataset Loading Contract

Bootstrap dataset loading contract:

- bootstrap reads only already normalized internal dataset artifacts;
- bootstrap may read dataset handle, manifest, quality report, metadata and normalized tick stream;
- bootstrap does not read raw provider file directly;
- bootstrap does not perform import-layer normalization inside replay session startup;
- bootstrap fails early if normalized dataset prerequisites are not satisfied.

## 10. Normalized Dataset Requirements

Bootstrap считает already available следующие minimum artifacts:

- dataset id or handle;
- instrument id;
- market profile;
- dataset start time;
- dataset end time;
- normalized tick stream;
- derived bars availability or deterministic replay-side bar state support if accepted by replay contract;
- manifest;
- quality report;
- canonical timezone / precision info.

Отдельное правило:

- replay bootstrap не читает raw provider format напрямую.

## 11. Chart / Replay Controls MVP Contract

### 11.1. Required controls

MVP bootstrap must support:

- play;
- pause;
- speed change;
- allowed seek/jump according to replay mode;
- visible current simulation time;
- visible replay finished state;
- visible instrument/timeframe/session mode context.

### 11.2. Control boundary

Chart/replay surface:

- не является source of truth;
- не читает raw dataset напрямую;
- не пересобирает replay state;
- не создает собственное время.

### 11.3. Mode-aware behavior

Bootstrap implementation must respect minimal mode-aware rules:

- `Training` allows play/pause/speed and allowed seek behavior;
- `Exam` restricts forbidden seek-back or future-aware navigation;
- `Review Replay` allows broader replay navigation according to replay contract.

## 12. Phase-1 Acceptance Scenario

Проверяемый acceptance scenario для bootstrap phase:

1. пользователь выбирает готовый normalized dataset;
2. система читает manifest and quality report;
3. создает replay session по одному инструменту;
4. chart surface показывает initial state;
5. пользователь запускает play;
6. рынок движется вперед tick-driven;
7. пользователь может pause and change speed;
8. allowed seek works only within current mode restrictions;
9. при конце датасета visible state becomes finished.

## 13. Implementation Sequence

Рекомендуемый coding order внутри bootstrap:

1. dataset handle + bootstrap input contract;
2. replay session creation;
3. cursor initialization;
4. tick feed stepping;
5. replay event publication for desktop;
6. chart/replay state projection;
7. mode-aware control validation;
8. finished and error states;
9. minimal recovery-safe local session state only if truly needed already in bootstrap.

## 14. Non-Goals

Из этого implementation task explicitly excluded:

- trading engine integration beyond interfaces needed not to block later;
- order placement;
- position state;
- journal persistence;
- analytics calculations;
- Bill Williams structured review;
- mobile or mentor flows;
- advanced chart tooling;
- tech-stack debates beyond what is necessary to express implementation boundary.

## 15. Risks and Failure Modes

### Risks

- scope creep from bootstrap into trade execution;
- mixing replay bootstrap with full desktop UI design;
- attempting to normalize raw provider data inside replay startup;
- under-specifying manifest and metadata validation;
- overbuilding chart layer before replay state is stable.

### Failure modes

- dataset selected but manifest incompatible;
- replay session created without valid tick stream;
- UI shows time different from replay `simulation_time`;
- seek allowed in forbidden mode branch;
- finished state not visible or not terminal;
- replay bootstrap accidentally depends on raw provider format.

## 16. Acceptance Criteria

Задача считается принятой, если:

- можно выбрать готовый normalized dataset;
- создается replay session по одному инструменту;
- рынок воспроизводится tick-driven без доступа к будущему;
- play/pause/speed/allowed seek работают согласно mode restrictions;
- desktop chart/replay surface получает usable state;
- replay корректно доходит до finished state;
- нет прямого чтения raw provider format из replay bootstrap.
