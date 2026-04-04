# Replay Engine

Дата фиксации: 2026-03-14
Статус: spec v1
Приоритет: highest

## 1. Назначение модуля

### Роль в общей архитектуре

Replay engine - это временное ядро симуляции. Он отвечает за управляемое воспроизведение исторического рынка как последовательности рыночных событий, синхронизированных по одному источнику времени. Через него проходят:

- текущий момент симуляции;
- видимая часть рынка;
- доступность данных по таймфреймам;
- переход между режимами training, exam и review replay;
- публикация событий, на которые опираются trading engine, journal layer и desktop UI.

### Что входит в replay engine

- загрузка и валидация replay dataset для одного инструмента;
- управление time cursor;
- проигрывание tick stream;
- сборка и обновление bar state по поддерживаемым таймфреймам;
- публикация replay events;
- управление режимом, паузой, скоростью, jump/seek и завершением симуляции;
- предоставление snapshot state для UI и других слоев.

### Что не входит в replay engine

- логика ордеров и исполнения сделок;
- расчет PnL, издержек и trade lifecycle;
- journal schema и аналитические метрики;
- визуальный рендеринг графиков;
- импорт сырой истории из внешних провайдеров;
- mobile execution;
- multi-instrument portfolio coordination.

## 2. Формальная модель времени

### Текущий момент симуляции

Текущий момент симуляции - это `simulation_time`, равный timestamp последнего примененного к состоянию рынка tick event.

Правило v1:

- рынок считается продвинутым вперед только после применения нового тика;
- бары пересчитываются как производные сущности от tick stream;
- UI может быть bar-based, но источник истины по времени остается tick-driven.

### Time cursor

`time_cursor` - это объект, определяющий позицию replay внутри загруженного датасета.

Минимальные поля:

- `current_tick_index`
- `simulation_time`
- `start_time`
- `end_time`
- `is_paused`
- `speed_multiplier`
- `mode`

### Как курсор двигается по историческим данным

Курсор всегда движется монотонно вперед по упорядоченному набору тиков.

Базовые правила:

- один примененный тик = одно продвижение курсора;
- переход на новый бар не двигает курсор отдельно, а является следствием поступления тика;
- seek/jump меняет позицию курсора только на допустимый target timestamp внутри границ датасета;
- в exam mode курсор не может быть перемещен назад после начала сессии.

### Tick-time и bar-time

`tick-time`:

- время фактического рыночного события;
- определяет истинную последовательность симуляции;
- используется для исполнения ордеров, синхронизации и журналирования.

`bar-time`:

- время открытия или закрытия агрегированного бара конкретного таймфрейма;
- вычисляется на основе уже примененных тиков;
- используется для UI, индикаторов и пошаговой навигации `stepBar()`.

Принцип v1:

- tick-time первичен;
- bar-time вторичен и всегда выводится из tick-time.

### Pause

`pause` переводит replay engine в состояние, при котором:

- курсор не движется автоматически;
- новые тики не применяются;
- state snapshot остается доступным на чтение;
- trading engine и UI могут запрашивать текущее состояние;
- публикается `ReplayPaused`.

### Play

`play` переводит replay engine в автоматическое продвижение вперед.

При этом:

- engine начинает последовательно применять тики;
- после каждого примененного тика обновляет bar state;
- публикует связанные рыночные и системные события;
- останавливается на `pause`, `end_of_data` или критической ошибке dataset.

### Ускорение

Ускорение задает `speed_multiplier`, который определяет, с какой скоростью engine потребляет тики относительно базового playback rate UI.

В v1 скорость влияет на темп проигрывания, но не меняет порядок событий и не пропускает тики.

Примеры допустимых значений:

- `0.25x`
- `1x`
- `2x`
- `4x`
- `8x`
- `16x`

### Jump / Seek

`seek` - управляемый перенос курсора к целевому timestamp.

Правила v1:

- target должен лежать внутри dataset boundaries;
- seek позиционирует engine на первый тик `>= target`;
- после seek engine пересобирает bar state для всех синхронизированных таймфреймов;
- публикуется `ReplayJumped` и затем `TimeframeSynced`.

Ограничения по режимам:

- training mode: seek вперед и назад разрешен;
- exam mode: seek назад запрещен, seek вперед запрещен как средство подсматривания;
- review replay mode: seek вперед и назад разрешен.

### Fast-forward

`fast-forward` - это ускоренное продвижение курсора вперед без изменения порядка событий.

В v1 fast-forward реализуется как частный случай play с высоким `speed_multiplier`.

Отдельный режим "проскочить без событий" не вводится, потому что:

- это ломает честную event sequence для trading engine и journal;
- может скрыть момент исполнения ордера;
- приводит к разрыву между replay time и observed state.

### Возврат в training mode

В training mode разрешены:

- restart сценария от стартовой точки;
- seek назад;
- повтор того же участка истории;
- jump к контрольным checkpoint внутри сессии, если checkpoint был зафиксирован в рамках training session.

### Почему в exam mode возврат назад запрещен

В exam mode возврат назад запрещен или ограничен, потому что:

- решение должно быть необратимым как в реальной торговой среде;
- возможность отката уничтожает учебную ценность оценки;
- журнал должен фиксировать конечную последовательность действий без повторной попытки внутри той же экзаменационной сессии.

В v1 правило жесткое:

- после `exam_session_started` любые seek назад и restart сценария внутри той же сессии запрещены;
- новый проход возможен только как новая exam session.

## 3. Event Model

### Принципы event model

- replay engine публикует доменные события рынка и системные события управления replay;
- события публикуются строго в причинном порядке;
- каждый event содержит `session_id`, `instrument` и `simulation_time`;
- subscribers не меняют replay state напрямую, а только реагируют на события.

### TickArrived

Назначение:

- зафиксировать поступление следующего тика и продвижение рынка вперед.

Обязательные поля:

- `event_type`
- `session_id`
- `instrument`
- `tick_index`
- `simulation_time`
- `bid`
- `ask`
- `mid`
- `volume` или `tick_volume`
- `is_gap_after_previous_tick`

Публикует:

- replay engine

Подписываются:

- trading engine
- journal layer
- desktop workspace
- indicator layer later phase

### BarOpened

Назначение:

- сообщить, что для конкретного таймфрейма открылся новый бар.

Обязательные поля:

- `event_type`
- `session_id`
- `instrument`
- `timeframe`
- `bar_open_time`
- `trigger_tick_time`
- `open`

Публикует:

- replay engine

Подписываются:

- desktop workspace
- journal layer
- indicator layer later phase

### BarUpdated

Назначение:

- сообщить, что активный бар конкретного таймфрейма изменился после нового тика.

Обязательные поля:

- `event_type`
- `session_id`
- `instrument`
- `timeframe`
- `bar_open_time`
- `trigger_tick_time`
- `open`
- `high`
- `low`
- `close`
- `tick_count_in_bar`

Публикует:

- replay engine

Подписываются:

- desktop workspace
- indicator layer later phase
- journal layer при необходимости делать snapshots по бару

### BarClosed

Назначение:

- зафиксировать завершение бара и финальные OHLC значения.

Обязательные поля:

- `event_type`
- `session_id`
- `instrument`
- `timeframe`
- `bar_open_time`
- `bar_close_time`
- `open`
- `high`
- `low`
- `close`
- `tick_count_in_bar`

Публикует:

- replay engine

Подписываются:

- desktop workspace
- trading engine для bar-based rules if needed
- journal layer
- indicator layer later phase

### TimeframeSynced

Назначение:

- сообщить, что after seek/load/restart все активные таймфреймы согласованы с одним `simulation_time`.

Обязательные поля:

- `event_type`
- `session_id`
- `instrument`
- `simulation_time`
- `active_timeframe`
- `synchronized_timeframes`
- `current_bar_open_times`

Публикует:

- replay engine

Подписываются:

- desktop workspace
- trading engine
- journal layer

### ReplayPaused

Назначение:

- зафиксировать остановку автоматического проигрывания.

Обязательные поля:

- `event_type`
- `session_id`
- `instrument`
- `simulation_time`
- `reason`

Публикует:

- replay engine

Подписываются:

- desktop workspace
- journal layer

### ReplayResumed

Назначение:

- зафиксировать переход из paused в running.

Обязательные поля:

- `event_type`
- `session_id`
- `instrument`
- `simulation_time`
- `speed_multiplier`

Публикует:

- replay engine

Подписываются:

- desktop workspace
- journal layer

### ReplaySpeedChanged

Назначение:

- сообщить о смене скорости playback.

Обязательные поля:

- `event_type`
- `session_id`
- `instrument`
- `simulation_time`
- `previous_speed_multiplier`
- `new_speed_multiplier`

Публикует:

- replay engine

Подписываются:

- desktop workspace
- journal layer

### ReplayJumped

Назначение:

- зафиксировать программный перенос курсора.

Обязательные поля:

- `event_type`
- `session_id`
- `instrument`
- `previous_simulation_time`
- `new_simulation_time`
- `direction`
- `reason`

Публикует:

- replay engine

Подписываются:

- trading engine
- journal layer
- desktop workspace

### ReplayFinished

Назначение:

- сообщить о достижении конца симуляции.

Обязательные поля:

- `event_type`
- `session_id`
- `instrument`
- `simulation_time`
- `dataset_end_time`
- `reason`

Публикует:

- replay engine

Подписываются:

- desktop workspace
- trading engine
- journal layer

## 4. Рыночные данные и входной формат

### Минимальный входной формат v1

Replay core v1 должен поддерживать один инструмент и один поток упорядоченных тиков.

Минимальная структура tick dataset:

- `instrument`
- `timezone`
- `price_precision`
- `ticks[]`

Структура `tick`:

- `timestamp`
- `bid`
- `ask`
- `mid` optional if не хранится, то вычисляется
- `tick_volume` optional

Обязательные требования:

- timestamps строго неубывающие;
- дубликаты по timestamp допустимы только как отдельные последовательные тики;
- bid/ask не должны быть пустыми;
- dataset должен иметь явные `dataset_start_time` и `dataset_end_time`.

### Как хранятся тики

Внутри replay engine тики должны быть доступны как indexable sequence:

- массив или поток с индексом доступа;
- возможность быстро найти первый tick `>= target_timestamp`;
- возможность прочитать previous tick для gap detection.

### Как из тиков строятся бары

Бары строятся детерминированной агрегацией по таймфрейму.

Правила:

- новый бар открывается при попадании тика в новый timeframe bucket;
- `open` = цена первого тика bucket;
- `high` = максимум по всем тикам bucket;
- `low` = минимум по всем тикам bucket;
- `close` = цена последнего примененного тика bucket;
- если в bucket нет ни одного тика, бар не создается синтетически в v1.

### Как синхронизируются M5, M15, H1, H4, D1

Поддерживаемые таймфреймы v1:

- M5
- M15
- H1
- H4
- D1

Синхронизация строится от одного `simulation_time`.

Для каждого примененного тика engine:

1. определяет timeframe bucket для каждого активного TF;
2. проверяет, открыт ли бар для этого bucket;
3. если bucket новый - закрывает предыдущий бар и открывает новый;
4. если bucket текущий - обновляет активный бар;
5. после обновления всех TF публикует `TimeframeSynced`, если произошло structural change after load/seek/restart, либо держит синхронизацию как часть current state.

### Как обеспечивается единый момент рынка при переключении ТФ

Переключение активного таймфрейма не двигает время и не создает новый источник истины.

Правило:

- все отображаемые TF показывают состояние, вычисленное на одном `simulation_time`;
- активный TF влияет только на UI, step-bar navigation и user focus;
- если пользователь переключается с M15 на H1, он видит H1 bar state, актуальный на тот же момент времени.

### Требования к историческим данным для v1

- один инструмент на одну replay session;
- tick-level bid/ask data;
- согласованная таймзона внутри dataset;
- данные должны покрывать start time и участок после него, достаточный для построения хотя бы одного активного бара на каждом включенном TF;
- допустимы gaps рынка, но они должны быть честно представлены;
- источник данных должен быть уже нормализован import layer, replay engine не очищает сырые провайдерские ошибки beyond basic validation.

## 5. Режимы работы

### Training Mode

Разрешено:

- play/pause;
- изменение скорости;
- step tick;
- step bar;
- seek вперед и назад;
- restart сценария;
- fast-forward;
- просмотр последствий решения.

Запрещено:

- скрытая модификация истории;
- сохранение "идеального" результата поверх исходной последовательности событий.

Откат:

- разрешен.

### Exam Mode

Разрешено:

- play/pause;
- ограниченное изменение скорости;
- step tick;
- step bar вперед;
- просмотр только уже наступивших событий.

Запрещено:

- seek назад;
- restart внутри той же exam session;
- jump вперед как средство подсматривания;
- fast-forward, который пропускает момент принятия решения.

Откат:

- запрещен внутри текущей сессии.

### Review Replay Mode

Назначение:

- разбор уже завершенной сессии или сделки.

Разрешено:

- play/pause;
- свободный seek вперед и назад;
- высокая скорость;
- jump к trade markers;
- быстрый просмотр последствий решения.

Запрещено:

- торговое исполнение как часть review workflow в v1.

Откат:

- разрешен.

## 6. Контракты с другими слоями

### Контракт с TRADING_ENGINE

Replay engine предоставляет trading engine:

- текущую цену `bid/ask/mid`;
- текущее `simulation_time`;
- состояние активного бара по каждому синхронизированному TF;
- сигналы о поступлении нового тика и закрытии бара;
- признак конца данных.

Trading engine обязан:

- не использовать собственное независимое рыночное время;
- проверять исполнение ордеров только на replay events;
- не продвигать replay cursor самостоятельно.

#### Как trading engine получает текущую цену и состояние бара

- через `getCurrentState()`;
- через подписку на `TickArrived`, `BarOpened`, `BarUpdated`, `BarClosed`, `TimeframeSynced`.

#### В какой момент ордер проверяется на исполнение

В v1:

- pending order и stop/take conditions проверяются после применения каждого нового тика;
- если tick изменил бар, сначала обновляется replay market state, затем вызывается логика исполнения trading engine;
- replay engine не решает, исполнился ли ордер, но гарантирует, что trading engine видит полный market snapshot после тика.

### Контракт с JOURNAL_ANALYTICS

Replay engine публикует для journal layer:

- все системные replay events;
- ключевые рыночные события;
- факты jump, pause, resume, finish;
- режим replay и параметры скорости.

Journal layer использует это для:

- таймлайна сессии;
- фиксации режима работы;
- привязки trade events к рыночному времени;
- разбора поведенческих паттернов вроде частых jump или нарушений exam mode.

### Контракт с DESKTOP_WORKSPACE

Replay engine предоставляет desktop UI:

- snapshot текущего состояния;
- статус paused/running;
- speed multiplier;
- active timeframe;
- synchronized timeframe states;
- dataset boundaries;
- end-of-data flag.

Desktop workspace:

- не рассчитывает бары самостоятельно;
- не хранит альтернативный курсор времени;
- может инициировать команды `play`, `pause`, `seek`, `stepBar`, `stepTick`, `setActiveTimeframe`.

#### Как UI узнает, какие ТФ синхронизированы

- через `getCurrentState().synchronized_timeframes`;
- через `TimeframeSynced`.

## 7. Ограничения v1

- одна активная сделка;
- desktop-first;
- первый market profile - FX/CFD;
- UI bar-based, но simulation tick-driven;
- без portfolio mode;
- без multi-position portfolio coordination;
- без mobile execution;
- одна replay session = один инструмент;
- replay engine не содержит индикаторную логику Bill Williams, только поставляет временной и рыночный контекст.

## 8. Минимальный API прототипа

### Lifecycle

- `loadDataset(dataset)`
- `setInstrument(instrumentId)`
- `setMode(mode)`
- `setStartTime(timestamp)`
- `startSession()`
- `restartSession()`
- `disposeSession()`

### Playback control

- `play()`
- `pause()`
- `setSpeed(multiplier)`
- `seekTo(timestamp)`
- `fastForward(multiplier)`
- `stepTick()`
- `stepBar(timeframe = activeTimeframe)`

### State and data access

- `getCurrentState()`
- `getCurrentTick()`
- `getCurrentBar(timeframe)`
- `getSynchronizedBars()`
- `getDatasetBoundaries()`

### UI context

- `setActiveTimeframe(timeframe)`
- `getActiveTimeframe()`

### Event subscription

- `subscribe(eventType, handler)`
- `unsubscribe(subscriptionId)`

## 9. Состояние replay engine

Минимальный `ReplayState` object:

- `session_id`
- `instrument`
- `mode`
- `active_timeframe`
- `synchronized_timeframes`
- `simulation_time`
- `current_tick_index`
- `current_tick_timestamp`
- `current_prices`
- `current_bar_timestamps_by_timeframe`
- `current_bars_by_timeframe`
- `speed_multiplier`
- `is_paused`
- `is_running`
- `dataset_start_time`
- `dataset_end_time`
- `end_of_data`
- `last_event_type`

Требования к state:

- должен быть read-only для внешних consumers;
- должен отражать уже примененное состояние рынка;
- должен быть сериализуем для journal snapshot later phase.

## 10. Краевые случаи

### Гэпы в данных

- gap не заполняется искусственными тиками;
- следующий реальный тик продвигает рынок сразу на новую цену;
- `TickArrived.is_gap_after_previous_tick = true`.

### Отсутствие тиков

- если в выбранном участке после start time нет тиков, session не стартует и возвращает validation error;
- если в процессе рынка наступает низколиквидный участок без тиков, replay остается на последнем примененном состоянии до появления следующего тика.

### Неполный бар

- активный последний бар считается незакрытым, пока не пришел тик следующего bucket или не закончился dataset;
- при `ReplayFinished` последний активный бар маркируется как incomplete in state, но не форсируется в synthetic closed bar.

### Переход между днями

- переход дня - это обычное следствие новых timestamps;
- day boundary не создает особую паузу сам по себе;
- если активен D1, новый день открывает новый D1 bar.

### Выход за границы истории

- seek раньше `dataset_start_time` или позже `dataset_end_time` запрещен;
- engine возвращает bounded error и не меняет cursor.

### Переключение ТФ во время проигрывания

- разрешено;
- не двигает cursor;
- не меняет синхронизацию;
- влияет только на `active_timeframe` и target для `stepBar()`.

### Jump в участок с низкой ликвидностью

- seek ставит cursor на первый доступный tick `>= target`;
- если ближайший тик далеко по времени, это честное состояние данных;
- UI должен видеть фактический jump во времени через `ReplayJumped`.

### Конец симуляции

Концом симуляции считается состояние, когда:

- применен последний доступный tick dataset;
- больше нет следующего тика для продвижения cursor вперед.

После этого:

- `end_of_data = true`;
- публикуется `ReplayFinished`;
- `play()` без restart/seek больше не двигает рынок.

## 11. Решения и компромиссы

### Принятые решения

- replay v1 строится как tick-driven simulation;
- UI остается bar-based;
- один global time cursor является единственным источником рыночного времени;
- seek назад разрешен только вне exam mode;
- fast-forward не пропускает события, а только ускоряет их consumption;
- бары без тиков не создаются синтетически;
- v1 ограничен одним инструментом и одной активной сделкой.

### Рассмотренные альтернативы

#### Bar-driven replay

Плюсы:

- проще реализация;
- легче для UI.

Минусы:

- теряется честность исполнения внутри бара;
- сложнее корректно проверять pending orders;
- хуже база для дальнейшего роста к более точной симуляции.

Статус:

- отклонено для ядра v1.

#### Отдельное время для каждого TF

Плюсы:

- локально проще для каждого графика.

Минусы:

- ломает единый момент рынка;
- усложняет исполнение и журналирование;
- создает двусмысленность между окнами.

Статус:

- отклонено.

#### Fast-forward с пропуском событий

Плюсы:

- быстрее просмотр.

Минусы:

- не гарантирует честный момент исполнения;
- ломает журнал;
- создает скрытые скачки состояния.

Статус:

- отклонено для v1.

### Что сознательно отложено на later phases

- multi-instrument replay;
- portfolio mode;
- synthetic gap fillers;
- precomputed indicator streams Bill Williams внутри replay core;
- отдельный event bus outside process;
- mobile replay control;
- server-synced collaborative replay sessions.

## 12. Артефакты на выходе

В рамках этой спецификации должны быть согласованы и при необходимости обновлены:

- `03_MODULES/REPLAY_ENGINE.md`
- `01_MASTER/DECISIONS.md`
- `01_MASTER/CURRENT_STATE.md`

## Открытые вопросы, требующие отдельного обсуждения

1. Какая точность tick data обязательна для первого рабочего профиля FX/CFD: real tick provider или допустим нормализованный pseudo-tick source?
2. Нужен ли в v1 session checkpoint как пользовательская сущность или достаточно restart/seek?
3. Должен ли incomplete last bar участвовать в аналитике review layer как полноценный bar artifact?
4. Какие ограничения скорости нужны в exam mode: полный фикс `1x` или ограниченный набор ускорений?
