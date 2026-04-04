# Decisions

Дата начала реестра: 2026-03-14
Статус: active

## D-001

- Дата: 2026-03-14
- Тема: Операционная модель проекта
- Решение: Проект ведется как единая система документов Project Brain, а не как цепочка чатов.
- Альтернативы: держать контекст в переписках; хранить контекст только в памяти модели; дробить проект на несвязанные файлы без общего центра.
- Причина выбора: проект архитектурно сложный, длинный по времени и чувствителен к потере решений и повторным обсуждениям.
- Последствия: основными артефактами проекта становятся master-документы, модульные документы, журнал решений и файл текущего состояния.

## D-002

- Дата: 2026-03-14
- Тема: Ядро продукта
- Решение: Ядром продукта являются replay исторического рынка и ручное исполнение сделок.
- Альтернативы: начать с аналитики; начать с мобильного приложения; строить продукт как журнал без симуляции.
- Причина выбора: без replay и ручного исполнения продукт теряет свою учебную ценность и перестает быть тренажером.
- Последствия: replay core и trading engine считаются приоритетом Phase 1.

## D-003

- Дата: 2026-03-14
- Тема: Основная платформа использования
- Решение: desktop - основной рабочий контур; mobile - слой просмотра и разбора, а не полная торговая среда.
- Альтернативы: равный функционал на всех устройствах; mobile-first; только desktop без mobile.
- Причина выбора: полноценная ручная симуляция и торговое рабочее место требуют пространства, точности и плотного UX, тогда как мобильный формат лучше подходит для review.
- Последствия: проектирование desktop и mobile идет разными треками; торговый терминал не обязан целиком переноситься на телефон.

## D-004

- Дата: 2026-03-14
- Тема: Зависимость от MT5
- Решение: продукт не строится на MT5 как на архитектурном ядре, даже если MT5 может использоваться как источник вдохновения, данных или промежуточной интеграции.
- Альтернативы: полностью встроить тренажер в MT5; завязать хранение и исполнение на сущности MT5.
- Причина выбора: такая зависимость ограничивает продукт, ухудшает контроль над replay, журналом, синхронизацией и будущим развитием.
- Последствия: внутренняя модель рынка, сделки и хранения проектируются как собственные сущности проекта.

## D-005

- Дата: 2026-03-14
- Тема: Методологическая основа
- Решение: система Bill Williams обязательна для MVP как встроенный обучающий и аналитический слой.
- Альтернативы: сделать универсальный тренажер без конкретной методики; отложить Bill Williams на потом.
- Причина выбора: это исходная цель продукта и главный критерий его отличия от обычного тестера.
- Последствия: индикаторы, сигналы, ограничения и обучающие сценарии по Bill Williams должны быть формализованы отдельным модулем и исследованиями.

## D-006

- Дата: 2026-03-14
- Тема: Ограничение позиции
- Решение: базовое правило первого контура - одна активная сделка одновременно.
- Альтернативы: несколько одновременных позиций; портфельная торговля с первого этапа.
- Причина выбора: это упрощает учебный сценарий, контроль ошибок и логику журнала на старте.
- Последствия: trading engine и UX первого контура строятся вокруг одного активного trade context.

## D-007

- Дата: 2026-03-14
- Тема: Хранение истории
- Решение: история сделок и сессий должна храниться локально с перспективой синхронизации в облако.
- Альтернативы: только локально; только облако.
- Причина выбора: локальная устойчивость нужна для ежедневной работы, а облако важно для review, бэкапа и будущей коммерческой версии.
- Последствия: архитектура сразу предусматривает local-first модель.

## D-008

- Дата: 2026-03-14
- Тема: Модель времени Replay Engine v1
- Решение: replay engine v1 строится как tick-driven simulation с одним global time cursor; бары и таймфреймы являются производным состоянием от потока тиков.
- Альтернативы: bar-driven replay; отдельное время для каждого таймфрейма; независимые графические курсоры.
- Причина выбора: это устраняет двусмысленность по текущему моменту рынка, дает честную основу для исполнения ордеров и сохраняет возможность роста к более точной симуляции.
- Последствия: trading engine, journal layer и desktop workspace обязаны опираться на единый simulation_time; UI может оставаться bar-based, но не становится источником истины по времени.

## D-009

- Дата: 2026-03-14
- Тема: Режимы Replay Engine v1
- Решение: v1 поддерживает три режима replay - Training Mode, Exam Mode и Review Replay Mode; seek назад и restart разрешены только вне exam mode.
- Альтернативы: один универсальный режим; exam mode с частичным откатом; review как отдельный модуль без replay controls.
- Причина выбора: режимы имеют разные учебные цели и разные требования к честности и обратимости решения.
- Последствия: replay engine должен хранить mode в state, валидировать команды управления в зависимости от режима и логировать нарушения exam constraints.

## D-010

- Дата: 2026-03-14
- Тема: Fast-forward и gaps в Replay Engine v1
- Решение: fast-forward в v1 не пропускает рыночные события, а только ускоряет их consumption; gaps в данных не заполняются синтетическими тиками или барами.
- Альтернативы: fast-forward с пропуском промежуточных событий; synthetic tick fillers; synthetic empty bars без реальных тиков.
- Причина выбора: пропуск событий ломает честность исполнения и журналирования, а синтетическое заполнение данных создает ложную картину рынка.
- Последствия: low-liquidity участки и market gaps отображаются как реальные особенности исторического датасета; последний незавершенный бар может остаться incomplete.

## D-011

- Дата: 2026-03-14
- Тема: Market Model v1
- Решение: для v1 вводится универсальная рыночная модель с первым боевым профилем `FX/CFD`, в которой свойства инструмента, pricing rules, volume mode и cost rules разделены между отдельными сущностями.
- Альтернативы: жестко зашитая FX-only модель; полная broker-specific market model с первого этапа.
- Причина выбора: это дает достаточную универсальность для первого прототипа, но не перегружает v1 margin engine, portfolio logic и broker-specific деталями.
- Последствия: replay engine и trading engine обязаны использовать `InstrumentSpec` и связанный market profile, а выбор объема хранится отдельно от свойств инструмента.

## D-012

- Дата: 2026-03-14
- Тема: Data Import и качество dataset v1
- Решение: replay engine работает только с нормализованным internal dataset; raw provider format никогда не читается напрямую replay core. Минимальный dataset v1 должен содержать monotonic bid/ask tick stream, metadata, quality report и dataset manifest.
- Альтернативы: direct replay from raw CSV; нормализация на лету внутри replay engine; хранение только баров без ticks.
- Причина выбора: это отделяет import concerns от playback concerns, упрощает repeatability и делает quality policy явной.
- Последствия: import layer становится обязательной частью архитектуры; incomplete last bar, gaps, duplicates и anomalies фиксируются до старта replay session.

## D-013

- Дата: 2026-03-14
- Тема: Контракт Trading Engine ↔ Replay Engine v1
- Решение: trading engine получает рынок только через `ExecutionSnapshot`, сформированный replay engine после применения каждого тика; проверки исполнения выполняются только на таком snapshot.
- Альтернативы: bar-based execution; прямой доступ trading engine к tick dataset; самостоятельная агрегация баров в trading engine.
- Причина выбора: это сохраняет единый источник времени и состояния рынка и устраняет дублирование логики между слоями.
- Последствия: любое исполнение сделки обязано ссылаться на snapshot timestamp, tick index, session state и quality flags.

## D-014

- Дата: 2026-03-15
- Тема: Trade Lifecycle v1
- Решение: v1 использует один `TradeLifecycle` с одной активной агрегированной `Position`, допускающей `partial close` и `add-on entry`; история входов хранится через `PositionLeg`, но legs не являются отдельными сделками.
- Альтернативы: полностью агрегированная позиция без legs; полноценная multi-leg independent trade model.
- Причина выбора: это сохраняет ограничение одной активной сделки, но не теряет инженерную точность для average entry, partial close и audit trail.
- Последствия: `TradeRecord` остается единым на сделку, а add-on и partial close отражаются как отдельные `ExecutionRecord`.

## D-015

- Дата: 2026-03-15
- Тема: Slippage Policy v1
- Решение: рекомендуемая slippage policy для v1 - `fixed slippage`.
- Альтернативы: deterministic band; liquidity-flag-based slippage.
- Причина выбора: fixed policy прозрачна, воспроизводима и не перегружает первый прототип скрытой execution-логикой.
- Последствия: trading engine v1 использует простой и объяснимый execution adjustment; adaptive slippage переносится в later phases.

## D-016

- Дата: 2026-03-15
- Тема: Разрешение SL/TP ambiguity в tick-only модели
- Решение: если в одном tick snapshot без intratick path теоретически затронуты и SL, и TP, v1 выбирает консервативный результат `StopLossHit`.
- Альтернативы: оптимистичный TP-first; случайный выбор; synthetic intratick reconstruction.
- Причина выбора: это не добавляет ложного оптимизма и не требует недостоверной реконструкции пути цены внутри тика.
- Последствия: backtest-like execution remains conservative by design; более детальная path modeling отложена.

## D-017

- Дата: 2026-03-15
- Тема: Storage Contract Trading Engine v1
- Решение: storage-level модель v1 сохраняет `Order`, `Position`, `PositionLeg`, `TradeRecord` и `ExecutionRecord`; при этом `ExecutionRecord` и входные факты `PositionLeg` считаются append-only trace сущностями, а `Position` и `TradeRecord` остаются mutable active snapshots до завершения сделки.
- Альтернативы: хранить только итог сделки; держать position и orders только runtime-only; не сохранять legs отдельно от execution trace.
- Причина выбора: проекту нужна восстановимая local-first модель и полная трасса исполнения для journal/analytics, partial close и add-on entry.
- Последствия: journal/analytics получают единый `TradeRecord` как агрегат и `ExecutionRecord`/`PositionLeg` как детальную трассу; storage contract не привязывается к конкретной БД, но уже фиксирует доменные инварианты хранения.

## D-018

- Дата: 2026-03-15
- Тема: Вынос trade storage contract в отдельную technical schema
- Решение: persistence/schema-спецификация trade-сущностей v1 выносится из доменного контекста `TRADING_ENGINE.md` в отдельный документ `04_TECH/DATA_SCHEMA.md`, который становится основным technical source of truth для keys, cardinality, immutable/mutable field policy, local-first recovery и связей с journal/analytics.
- Альтернативы: оставить storage contract только внутри `TRADING_ENGINE.md`; сразу перейти к конкретной БД и ORM; смешать schema и journal/session модель в одном модуле.
- Причина выбора: доменная спецификация trading engine и техническая схема хранения решают разные задачи; вынесение в отдельный документ уменьшает двусмысленность, упрощает дальнейшее проектирование storage/contracts и не привязывает проект к конкретному implementation stack.
- Последствия: следующий слой проектирования должен опираться на `DATA_SCHEMA.md`; journal/session schema и storage contracts должны ссылаться на этот документ, а не заново определять trade entity storage rules.



## D-019

- Дата: 2026-03-15
- Тема: Session and Journal Schema v1
- Решение: session/journal persistence layer v1 строится вокруг одной primary сущности `TrainingSession`; отдельная persisted сущность `JournalSession` в v1 не вводится как второй source of truth. `PreTradeNote`, `PostTradeReview`, `ChartSnapshot`, `BehavioralFlag` и `RuleViolation` хранятся как primary journal entities и ссылаются на stable IDs trade storage из `DATA_SCHEMA.md`.
- Альтернативы: вводить отдельный `JournalSession`; хранить review и behavioral markers как произвольные вложения без формальной схемы; дублировать trade facts внутри journal layer.
- Причина выбора: одна session identity уменьшает двусмысленность между replay, trading и journal; формальная schema journal layer нужна для local-first review, behavioral analytics и audit trail, но не должна переопределять trade source of truth.
- Последствия: `04_TECH/JOURNAL_SCHEMA.md` становится technical source of truth для session/journal persistence; derived session summaries и read models допускаются позже, но не становятся primary storage.

## D-020

- Дата: 2026-03-15
- Тема: Journal Analytics Ownership Contract v1
- Решение: слой analytics в v1 работает поверх already defined trade storage и session/journal storage по модели `derive-on-read by default`; `SessionSummary`, dashboard aggregates и analytics cache допускаются только как derived-only read models и не становятся source of truth.
- Альтернативы: сохранять analytics aggregates как primary persistence; дублировать trade facts внутри analytics layer; строить analytics как отдельный независимый storage source.
- Причина выбора: это сохраняет local-first простоту, снижает риск drift между слоями и удерживает trade/session facts в уже зафиксированных source-of-truth документах.
- Последствия: `03_MODULES/JOURNAL_ANALYTICS.md` фиксирует ownership метрик, boundaries и write/read contracts; любой analytics cache later phase должен быть явно помечен как derived-only и регенерируемый.

## D-021

- Дата: 2026-03-15
- Тема: Bill Williams taxonomy contract v1
- Решение: Bill Williams слой v1 фиксируется через отдельный reference/spec `02_RESEARCH/BILL_WILLIAMS_RULES.md`, где `setup taxonomy`, `compliance labels` и `review tags` отделены от `BehavioralFlag` и `RuleViolation`. Методологическая классификация не становится новым source of truth для trade facts и не переопределяет contracts из `DATA_SCHEMA.md`, `JOURNAL_SCHEMA.md` и `JOURNAL_ANALYTICS.md`.
- Альтернативы: держать Bill Williams vocabulary только в свободном тексте review; смешать setup classification с behavioral flags; смешать compliance labels с rule violations; отложить taxonomy до UI или до полноценного signal engine.
- Причина выбора: проекту нужен единый методологический словарь уже на MVP-уровне, иначе setup quality, review и analytics drift быстро разойдутся между документами, review и будущей реализацией.
- Последствия: `PreTradeNote` и `PostTradeReview` могут ссылаться на structured `setupTag`/`complianceLabel`; `RuleViolation` продолжает фиксировать rule breaches, а `BehavioralFlag` - behavioral patterns; следующий слой проектирования должен формализовать `BILL_WILLIAMS_LAYER` как runtime/review contract, не ломая уже закрепленную persistence and analytics model.

## D-022

- Дата: 2026-03-15
- Тема: Bill Williams Layer v1 as methodological classification contract
- Решение: `03_MODULES/BILL_WILLIAMS_LAYER.md` фиксирует Bill Williams слой как отдельный модульный classification layer, который работает поверх replay/trading/journal facts, но не становится source of truth для trade facts, не становится analytics cache и не подменяет review полноценным signal engine. Runtime classification в v1 ограничивается deterministic rule-assisted cases; review-assisted classification остается primary для ambiguous method judgment.
- Альтернативы: трактовать Bill Williams layer как UI concern; сделать его скрытой частью analytics; пытаться already in v1 автоматизировать полный signal engine; смешать runtime method labels с `BehavioralFlag` и `RuleViolation`.
- Причина выбора: проекту нужен рабочий модульный контракт между reference taxonomy и будущей реализацией, но без ложной автоматизации и без размывания source-of-truth границ.
- Последствия: следующие implementation- and scope-level задачи должны опираться на явную границу между runtime/rule-assisted, review-assisted и future auto-detection logic; дальнейшее расширение Bill Williams detection возможно только как later phase поверх этого контракта.

## D-023

- Дата: 2026-03-15
- Тема: Product Scope and MVP Boundary Freeze
- Решение: первый рабочий контур Trader Trainer фиксируется как `desktop-first` тренажер ручной торговли по Bill Williams на исторических данных. Обязательное продуктовое ядро MVP: replay, manual trading, local-first persistence, journal/review и базовая analytics-диагностика. Mobile, mentor layer, advanced analytics, cloud sync и deep Bill Williams automation не являются блокерами first working prototype.
- Альтернативы: считать все уже описанные architectural capabilities обязательными для MVP; расширить MVP до mobile, mentor and cloud-adjacent layers; включить add-on and partial close в обязательный first working prototype без отдельного product confirmation.
- Причина выбора: проекту нужна жесткая продуктовая граница после завершения базовых contracts; architecture-ready не равно product-required; первый рабочий контур должен быть замкнутым, проверяемым и ограниченным.
- Последствия: `01_MASTER/PRODUCT_SCOPE.md` и `01_MASTER/MVP_vs_FULL.md` становятся master-границей против scope creep; последующие задачи должны проверяться against MVP acceptance scenario; later-phase возможности больше не считаются implicit MVP по умолчанию.

## D-024

- Дата: 2026-03-16
- Тема: Roadmap and MVP Implementation Sequencing
- Решение: после freeze product boundary проект движется по фазам `Phase 1 - Replay-ready market/data foundation`, `Phase 2 - Minimal executable trading loop`, `Phase 3 - Journal and review loop`, `Phase 4 - Bill Williams review integration`, `Phase 5 - MVP hardening / acceptance pass`. Реализация строится вокруг одного vertical slice: dataset -> replay -> one manual trade -> trade persistence -> session/journal persistence -> basic review.
- Альтернативы: реализовывать слои параллельно без phase order; начинать с UI-heavy desktop shell; тянуть mobile/review/mentor/cloud features раньше рабочего core loop; считать architecture completeness достаточной без end-to-end acceptance.
- Причина выбора: проекту нужен реалистичный implementation order, который опирается на уже принятые contracts и не размывает MVP; vertical slice снижает риск хаотичного параллельного кодинга и premature feature expansion.
- Последствия: `01_MASTER/ROADMAP.md` становится master-ориентиром для phase sequencing; `T-010` считается закрытой; следующим implementation-facing модулем становится MVP-level contract для desktop workspace или другой явный модуль только если он не ломает roadmap order.

## D-025

- Дата: 2026-03-16
- Тема: Desktop Workspace v1 as bounded MVP operating surface
- Решение: `03_MODULES/DESKTOP_WORKSPACE.md` фиксирует desktop workspace как основной operating surface first working prototype. Desktop объединяет replay controls, one-trade interaction, notes/review и basic result surfaces, но не становится source of truth для trade/session facts, не создает новую доменную логику replay/trading и не расширяется до mentor/mobile/BI platform.
- Альтернативы: сначала проектировать full UI system; делать desktop shell раньше explicit workflow contracts; переносить часть replay/trading logic в UI; тянуть advanced dashboards, mobile-like flows или polished add-on/partial close UX в обязательный MVP scope.
- Причина выбора: после roadmap проекту нужен implementation-facing desktop contract, который связывает already frozen layers в usable MVP workflow и одновременно удерживает границы against premature UI expansion.
- Последствия: `T-011` считается закрытой; следующим логичным шагом становится первая implementation задача vertical slice, starting from dataset/replay bootstrap and not from secondary UI polish or later-phase features.

## D-026

- Дата: 2026-03-16
- Тема: First implementation slice is Dataset and Replay Bootstrap
- Решение: первый implementation slice first working prototype ограничивается контуром `normalized dataset -> replay session -> chart/replay controls`. Он включает загрузку already normalized dataset, создание replay session, инициализацию `simulation_time` / `time_cursor`, tick-driven playback и minimal replay controls. Он не включает trade execution, journal flow, analytics surfaces или Bill Williams review as acceptance blockers.
- Альтернативы: начинать с desktop shell without strict replay bootstrap boundary; подтянуть trading loop уже в первый implementation slice; смешать bootstrap with raw import concerns; начать с broader UI or analytics work.
- Причина выбора: проекту нужен самый узкий запускаемый vertical slice, который проверяет replay-centered ядро и не размывает roadmap. Это уменьшает риск scope creep и дает четкий first coding target.
- Последствия: `05_CODEX/DATASET_REPLAY_BOOTSTRAP.md` становится implementation-facing boundary document для первого coding step; последующие slices должны добавлять trading, persistence and review только после acceptance bootstrap stage.

## D-027

- Дата: 2026-03-16
- Тема: Replay bootstrap implementation uses headless normalized-dataset runtime
- Решение: первый working implementation slice реализован как минимальный headless runtime package `runtime_bootstrap/`, который работает только с already normalized dataset artifacts, создает replay session по одному инструменту, инициализирует `simulation_time` / `time_cursor`, публикует replay events, поддерживает mode-aware controls и строит desktop-facing replay state projection. Трейдинг, journal, analytics и Bill Williams review intentionally excluded from this implementation slice.
- Альтернативы: ждать полноценного desktop stack before coding; тянуть GUI framework в первый slice; смешать replay bootstrap with import/raw data concerns; сразу включить trading loop в тот же шаг.
- Причина выбора: проекту нужен самый узкий работающий кодовый срез, который подтверждает replay-centered ядро и acceptance boundary из `DATASET_REPLAY_BOOTSTRAP.md` без преждевременного расширения scope.
- Последствия: bootstrap slice теперь подтвержден кодом и тестами; следующим implementation step может идти `ExecutionSnapshot`-driven one-trade lifecycle поверх already working replay runtime.


## D-028

- Date: 2026-03-30
- Topic: First Post-MVP Direction
- Decision: after MVP freeze and explicit pause point, the first post-MVP direction is `Bill Williams Method Depth`, starting with a bounded review/methodology expansion track. Mentor workflow, mobile review layer, sync/cloud continuity, dashboard growth, and packaging/platform work are not selected as the first post-MVP track.
- Alternatives: go first into mentor workflow; go first into mobile review layer; go first into sync/cloud continuity; go first into dashboard/analytics expansion; go first into packaging/distribution.
- Reason: the core value of Trader Trainer is not only replay and manual trade execution, but also deeper method training in Bill Williams logic. Once the desktop MVP is already acceptance-backed, the strongest next product gain comes from deepening the method layer instead of broadening surfaces or platform concerns.
- Consequences: the next bounded step should be designed as a narrow Bill Williams method-depth slice, not as mentor/mobile/sync/dashboard/platform expansion; frozen MVP boundaries remain unchanged until a separate later-phase decision is made.


## D-029

- Date: 2026-03-30
- Topic: First Bill Williams Method-Depth Slice Boundary
- Decision: the first implementation slice inside the selected post-MVP direction `Bill Williams Method Depth` is a bounded `Bill Williams Review Depth` slice centered on richer structured review-authored `PostTradeReview` method facets. It deepens human review semantics for one finished trade before any auto-detection, mentor overlays, mobile/sync continuity, dashboard growth, or scoring expansion.
- Alternatives: start first with runtime setup-candidate detection; start first with mentor workflow; start first with dashboard/multi-session method analytics; start first with mobile/sync method continuity; start first with a scoring/confidence engine.
- Reason: the strongest next product gain comes from improving the quality and teachability of Bill Williams review inside the already accepted local-first desktop loop. This deepens the product core without reopening frozen MVP scope or pretending a signal engine already exists.
- Consequences: the next coding step should extend `PostTradeReview` and its bounded projections, validation, and desktop authoring support rather than broadening surfaces or runtime automation; review-authored method depth remains primary and vocabulary-backed.
