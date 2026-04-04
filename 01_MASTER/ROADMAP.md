# Roadmap

Дата фиксации: 2026-03-16
Статус: master document
Приоритет: highest

## 1. Purpose of Roadmap

`ROADMAP.md` переводит уже принятые master- и module-contracts в реалистичную последовательность движения к first working prototype.

Документ нужен, чтобы:

- разложить реализацию по фазам без пересборки архитектуры;
- сохранить MVP boundary из `PRODUCT_SCOPE.md` и `MVP_vs_FULL.md`;
- зафиксировать dependency order между слоями;
- определить, какой vertical slice должен появиться раньше всего;
- уменьшить риск параллельного хаотичного кодинга.

Roadmap не является новым архитектурным документом и не меняет уже принятые constraints.

## 2. Roadmap Principles

Рабочие принципы roadmap:

- сначала строится минимальный вертикальный контур, а не все слои сразу;
- coding начинается только после фиксации active module contract;
- architecture-ready не равно implementation-now;
- replay-centered ядро идет раньше review polish и later layers;
- source-of-truth слои должны появляться раньше derived summaries и read models;
- desktop-first остается главным execution path;
- mobile, mentor, cloud sync и advanced analytics не блокируют first working prototype;
- каждая фаза должна завершаться проверяемым пользовательским результатом, а не только кодом без сценария.

## 3. First Working Prototype Target

Целевой first working prototype - это минимальный end-to-end продуктовый контур, в котором пользователь может:

1. выбрать или импортировать normalized dataset;
2. запустить replay по одному инструменту;
3. видеть рынок без будущего;
4. вручную открыть одну сделку;
5. сопровождать и закрыть ее;
6. получить `TradeRecord` и `ExecutionRecord`;
7. оставить `PreTradeNote` и `PostTradeReview`;
8. увидеть базовый review result по сделке и сессии;
9. восстановить session/trade/journal facts после локального restart.

## 4. Phase Structure

Рекомендуемая структура roadmap:

- `Phase 0` - Project Brain / contracts frozen
- `Phase 1` - Replay-ready market/data foundation
- `Phase 2` - Minimal executable trading loop
- `Phase 3` - Journal and review loop
- `Phase 4` - Bill Williams review integration
- `Phase 5` - MVP hardening / acceptance pass

## 5. Phase Goals

### Phase 0 - Project Brain / contracts frozen

Цель фазы:

- зафиксировать master- и module-contracts так, чтобы implementation не стартовал в тумане.

Source-of-truth документы:

- `01_MASTER/CURRENT_STATE.md`
- `01_MASTER/DECISIONS.md`
- `01_MASTER/CONSTRAINTS.md`
- `01_MASTER/PRODUCT_SCOPE.md`
- `01_MASTER/MVP_vs_FULL.md`
- `01_MASTER/ROADMAP.md`

Что должно быть реализовано:

- файловое ядро Project Brain;
- ключевые архитектурные contracts;
- product boundary и roadmap.

Что сознательно не входит:

- активная реализация приложения beyond exploratory bootstrap.

Критерии входа:

- есть исходный vision и базовые constraints.

Критерии выхода:

- MVP boundary заморожен;
- implementation order понятен;
- следующий implementation module выбран без двусмысленности.

Проверяемый результат для пользователя:

- команда понимает, что именно строить первым и что не тащить в MVP.

### Phase 1 - Replay-ready market/data foundation

Цель фазы:

- сделать dataset pipeline и replay core достаточно рабочими для честного одиночного playback по одному инструменту.

Source-of-truth документы:

- `03_MODULES/DATA_IMPORT.md`
- `03_MODULES/MARKET_MODEL.md`
- `03_MODULES/REPLAY_ENGINE.md`
- `01_MASTER/CONSTRAINTS.md`
- `01_MASTER/PRODUCT_SCOPE.md`

Что должно быть реализовано:

- ingest/normalization path до internal dataset;
- dataset boundaries and metadata;
- базовая quality validation;
- first market profile `FX/CFD`;
- tick-driven replay bootstrap;
- one-instrument replay session;
- minimal `Training`, `Exam`, `Review Replay` mode mechanics на уровне usable core.

Что сознательно не входит:

- indicator engine Bill Williams;
- advanced auto-detection;
- broad market support;
- mobile and sync.

Критерии входа:

- contracts по replay/data уже зафиксированы;
- product boundary frozen.

Критерии выхода:

- replay может запуститься на normalized dataset;
- рынок воспроизводится без доступа к будущему;
- time cursor, speed, pause and finish semantics устойчивы.

Проверяемый результат для пользователя:

- пользователь может открыть одну replay session по одному инструменту и честно прокручивать рынок вперед.

### Phase 2 - Minimal executable trading loop

Цель фазы:

- поверх replay построить минимальный работающий loop одной ручной сделки.

Source-of-truth документы:

- `03_MODULES/TRADING_ENGINE.md`
- `03_MODULES/REPLAY_ENGINE.md`
- `04_TECH/DATA_SCHEMA.md`
- `03_MODULES/MARKET_MODEL.md`
- `01_MASTER/MVP_vs_FULL.md`

Что должно быть реализовано:

- `ExecutionSnapshot` loop;
- manual market and stop orders;
- single active trade lifecycle;
- базовый open -> manage -> close flow;
- persistence `TradeRecord` / `ExecutionRecord`;
- recovery активной trade/session state after restart at minimal acceptable level.

Что сознательно не входит:

- product-critical add-on and partial close UX;
- broad execution sophistication;
- advanced risk engine;
- broker-specific margin behavior.

Критерии входа:

- replay core уже выдает стабильный рынок и time context;
- normalized dataset flow уже работает.

Критерии выхода:

- одна ручная сделка может быть открыта и закрыта на replay;
- trade facts persistятся локально;
- после сделки trace доступен для последующих journal/review слоев.

Проверяемый результат для пользователя:

- пользователь может совершить одну ручную сделку на историческом рынке и не потерять execution trace.

### Phase 3 - Journal and review loop

Цель фазы:

- замкнуть session/journal контур вокруг уже работающей сделки.

Source-of-truth документы:

- `04_TECH/JOURNAL_SCHEMA.md`
- `03_MODULES/JOURNAL_ANALYTICS.md`
- `04_TECH/DATA_SCHEMA.md`
- `03_MODULES/TRADING_ENGINE.md`
- `01_MASTER/PRODUCT_SCOPE.md`

Что должно быть реализовано:

- `TrainingSession` as primary session entity;
- `PreTradeNote` and `PostTradeReview` persistence;
- `BehavioralFlag` and `RuleViolation` primary persistence;
- timeline linkage between trade facts and journal facts;
- базовые metrics по сделке и сессии;
- local recovery of session review state.

Что сознательно не входит:

- advanced dashboards;
- cached summaries as primary artifacts;
- mentor review workflows;
- complex media artifact management.

Критерии входа:

- одна manual trade loop уже работает end-to-end;
- trade persistence уже существует.

Критерии выхода:

- пользователь может оставить note/review;
- session and journal facts сохраняются и читаются локально;
- базовый review result собирается из source-of-truth слоев.

Проверяемый результат для пользователя:

- после сделки пользователь видит не только PnL, но и базовый учебный разбор сессии.

### Phase 4 - Bill Williams review integration

Цель фазы:

- встроить Bill Williams taxonomy в notes/review flow без ложной автоматизации.

Source-of-truth документы:

- `02_RESEARCH/BILL_WILLIAMS_RULES.md`
- `03_MODULES/BILL_WILLIAMS_LAYER.md`
- `04_TECH/JOURNAL_SCHEMA.md`
- `03_MODULES/JOURNAL_ANALYTICS.md`
- `01_MASTER/MVP_vs_FULL.md`

Что должно быть реализовано:

- structured `setupTag` / `complianceLabel` hooks in review flow;
- Bill Williams review tags;
- связь review labels с `RuleViolation` и `BehavioralFlag` boundary;
- limited deterministic runtime assistance only where explicitly allowed.

Что сознательно не входит:

- full signal engine;
- advanced auto-detection;
- mentor-grade semantic scoring;
- confidence/probability engine.

Критерии входа:

- journal/review loop уже существует;
- notes and review persistence already work.

Критерии выхода:

- пользователь может завершить review с Bill Williams structured vocabulary;
- taxonomy не подменяет trade facts;
- analytics ownership remains unchanged.

Проверяемый результат для пользователя:

- review становится методологически полезным, а не только текстовым комментарием.

### Phase 5 - MVP hardening / acceptance pass

Цель фазы:

- проверить, что все обязательные части first working prototype реально сходятся в один устойчивый сценарий.

Source-of-truth документы:

- `01_MASTER/PRODUCT_SCOPE.md`
- `01_MASTER/MVP_vs_FULL.md`
- `01_MASTER/ROADMAP.md`
- `01_MASTER/CURRENT_STATE.md`
- acceptance-related module contracts of replay/trading/journal/BW layers

Что должно быть реализовано:

- acceptance pass against MVP scenario;
- consistency pass across persistence and recovery;
- anti-scope pass to exclude later-phase creep;
- минимальная hardening работа вокруг core workflow.

Что сознательно не входит:

- feature expansion for mobile;
- mentor layer;
- cloud sync;
- advanced analytics or dashboards.

Критерии входа:

- phases 1-4 complete enough for end-to-end path.

Критерии выхода:

- first working prototype acceptance scenario проходит от начала до конца;
- MVP boundary выдержан;
- следующий шаг после MVP может уже идти в roadmap of later phases.

Проверяемый результат для пользователя:

- продукт можно использовать как первый реальный тренажерный контур, а не только как набор разрозненных subsystems.

## 6. Phase Entry / Exit Criteria

Общие правила по фазам:

- новая фаза не стартует, пока ее source-of-truth contracts не зафиксированы;
- coding phase не должна закрываться без пользовательского acceptance result;
- derived layers не могут стартовать раньше primary source-of-truth layers;
- UI-heavy work не должна обгонять replay/trading/journal core;
- later-phase features не могут быть протащены в текущую фазу как "раз уж уже рядом".

## 7. Vertical Slice Strategy

Roadmap строится вокруг одного минимального vertical slice:

- сначала появляется market playback;
- затем поверх него появляется one-trade execution;
- затем появляется persistence trace;
- затем notes/review;
- затем Bill Williams structured interpretation;
- затем acceptance hardening.

Это означает, что проект не должен сначала пытаться завершить все subsystem contracts на одинаковой глубине реализации.

## 8. Recommended Vertical Slice

Минимальный end-to-end slice first working prototype:

1. пользователь выбирает или импортирует normalized dataset;
2. запускает replay по одному инструменту;
3. видит рынок без будущего;
4. вручную открывает одну сделку;
5. сопровождает и закрывает ее;
6. получает `TradeRecord` и `ExecutionRecord`;
7. оставляет `PreTradeNote` и `PostTradeReview`;
8. видит базовый review result по сделке и сессии.

Если этот vertical slice не работает end-to-end, later features не должны становиться приоритетом.

## 9. Dependency Order by Module

### Что должно быть готово до Desktop Workspace

До полноценного MVP-level desktop interaction surface должны быть готовы:

- replay bootstrap and market playback;
- normalized dataset availability;
- execution snapshot loop;
- minimal trading lifecycle contract;
- persistence contract для trade facts.

### Что должно быть готово до Journal UI

До заметного journal/review surface должны быть готовы:

- trade persistence;
- session identity via `TrainingSession`;
- `PreTradeNote` / `PostTradeReview` schema;
- базовая analytics ownership model;
- stable links between trade and journal entities.

### Что должно быть готово до Bill Williams-assisted review

До методологически полезного Bill Williams review должны быть готовы:

- notes/review persistence;
- final trade timeline;
- taxonomy vocabulary;
- explicit boundaries between setup classification, behavior and rule violations.

### Что может быть architecture-ready, но не обязательно для первой реализации

- add-on / partial close as polished product flow;
- advanced analytics summaries and caches;
- mobile review;
- mentor layer;
- cloud sync;
- advanced Bill Williams auto-detection.

## 10. What Must Exist Before Coding Each Phase

### Before coding Phase 1

- replay/data contracts frozen;
- v1 market profile accepted;
- quality policy understood at least at MVP level.

### Before coding Phase 2

- replay emits stable market context;
- execution snapshot contract fixed;
- trade persistence schema fixed.

### Before coding Phase 3

- one-trade lifecycle already works;
- trade facts persist and recover;
- journal schema fixed.

### Before coding Phase 4

- notes/review loop already exists;
- Bill Williams taxonomy and layer contract fixed;
- review-assisted path accepted as primary.

### Before coding Phase 5

- all MVP-required modules exist in working form;
- acceptance scenario documented;
- no unresolved scope disputes blocking validation.

## 11. Implementation Sequence for MVP

Рекомендуемая последовательность реализации:

1. dataset + replay bootstrap
2. execution snapshot loop
3. one-trade lifecycle
4. persistence of trade facts
5. persistence of session/journal facts
6. basic desktop interaction surface
7. notes/review flow
8. basic analytics/report
9. Bill Williams structured review hooks
10. MVP acceptance pass

## 12. Implementation Order Recommendation

Для Codex и разработки рекомендуется следующий практический порядок:

1. Сначала довести `dataset -> normalized internal dataset -> replay playback` до реально запускаемого состояния.
2. Затем подключить `ExecutionSnapshot` и минимальный trading loop одной сделки.
3. После этого зафиксировать локальное сохранение `TradeRecord` и `ExecutionRecord`.
4. Затем добавить `TrainingSession`, `PreTradeNote`, `PostTradeReview`, `BehavioralFlag`, `RuleViolation` как persistence-backed journal loop.
5. После появления source-of-truth слоев собрать минимальный desktop interaction surface, который не притворяется финальным UX.
6. Затем встроить базовый analytics/report layer без превращения summaries в source of truth.
7. Затем подвесить Bill Williams structured review hooks и limited rule-assisted help.
8. Только после этого проводить MVP acceptance pass и hardening.

## 13. Phase Exit Acceptance

### Phase 0 acceptance

- есть замороженные contracts, MVP boundary и roadmap.

### Phase 1 acceptance

- пользователь может запустить replay на normalized dataset и честно двигаться по рынку вперед.

### Phase 2 acceptance

- пользователь может вручную открыть и закрыть одну сделку на replay и получить execution trace.

### Phase 3 acceptance

- пользователь может завершить trade session с note/review и увидеть базовый session output.

### Phase 4 acceptance

- пользователь может размечать сделку через Bill Williams structured vocabulary без подмены trade facts.

### Phase 5 acceptance

- весь MVP scenario проходит end-to-end локально, устойчиво и без включения later-phase blockers.

## 14. Architecture-Ready vs Implementation-Now

Уже спроектировано, но не должно автоматически становиться immediate implementation scope:

- add-on / partial close как обязательный продуктовый workflow;
- advanced analytics summaries;
- mobile review;
- mentor layer;
- cloud sync;
- advanced Bill Williams auto-detection;
- richer dashboards and caches;
- broader market profile support.

Эти части могут оставаться architecture-ready until later phases without blocking first working prototype.

## 15. Risks and Anti-Patterns

### Roadmap Risks

- scope creep после freeze MVP boundary;
- premature UI polish до появления стабильного replay/trade loop;
- coding before active module contract is clear;
- mixing architecture work with implementation work;
- dragging later-phase features into MVP because they are already documented;
- overbuilding analytics before basic replay/trade loop works.

### Anti-Patterns

- делать mobile или mentor layer раньше basic desktop vertical slice;
- обсуждать новые later features до acceptance pass MVP;
- строить advanced dashboards без надежного trade/journal source of truth;
- реализовывать Bill Williams auto-detection раньше review-assisted foundation;
- считать architecture completeness эквивалентом product readiness.

## 16. What Is Explicitly Not in Roadmap Scope

Roadmap не определяет:

- конкретный tech stack shortlist;
- DB or ORM choice;
- UI wireframes;
- detailed sprint planning;
- later-phase commercial sequencing;
- новую архитектуру поверх уже принятых contracts.

## 17. Dependency Order by Module Summary

Короткая сводка dependency order:

- data/import and replay before trading;
- trading core before journal/review;
- trade persistence before analytics;
- journal persistence before Bill Williams structured review;
- MVP acceptance before later-phase expansion.
