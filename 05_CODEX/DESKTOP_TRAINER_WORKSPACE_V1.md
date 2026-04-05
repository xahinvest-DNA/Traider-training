# Desktop Trainer Workspace v1

Last updated: 2026-04-05
Status: accepted boundary draft
Task ID: T-122
Task type: implementation-facing boundary document

## Instruction block

Работаем не как над очередным `desktop text/status refinement`, а как над переходом от engineering shell к первому usable trader workspace.

Контекст:

- текущее приложение технически рабочее, но продуктово непригодно для реальной тренировки торговли;
- главная проблема не в ядре `replay` / `trading` / `journal`, а в том, что пользовательская operating surface собрана как debug-shell;
- слишком много служебного текста;
- нет нормального chart-first сценария;
- неочевиден старт с данными;
- не собран ясный путь `загрузил данные -> увидел график -> запустил replay -> открыл сделку -> провел review`.

Текущую `desktop shell` форму нельзя принимать как продуктовую норму. Она считается инженерной промежуточной оболочкой.

Что нужно удержать:

- не переписывать архитектурное ядро;
- не ломать existing source-of-truth ownership;
- не уводить задачу в `mentor` / `mobile` / `sync` / `dashboard` / `platform` scope;
- не открывать broad rewrite.

Ключевая продуктовая фиксация:

- основной график - только бары, не свечи;
- на основном графике обязательны `Alligator` и `Fractals`;
- под основным графиком обязателен отдельный нижний блок `AO`.

Смысл этого документа:

- переопределить главный экран как рабочее место трейдера, а не как панель внутренних состояний;
- ответить на вопрос: как должен выглядеть и работать первый реально используемый desktop-тренажер, если ядро уже существует, а пользовательская форма еще нет.

## T-122 Desktop Trainer Workspace Boundary

### Purpose

Зафиксировать bounded product-facing границу первого usable chart-first desktop trainer workspace поверх уже существующего `replay` / `trading` / `journal` ядра.

Этот документ нужен, чтобы перевести проект от текущего debug-shell состояния к реальному пользовательскому торговому контуру без архитектурного rewrite.

## Product statement

`Desktop Trainer Workspace v1` - это первый реально используемый desktop-тренажер, в котором пользователь:

- выбирает или импортирует исторические данные;
- попадает сразу в chart-first рабочее пространство;
- запускает replay рынка без знания будущего;
- вручную открывает, сопровождает и закрывает сделку;
- фиксирует контекст решения;
- переходит в review по завершенной сделке;
- продолжает или завершает сессию.

Workspace v1 является:

- основным пользовательским рабочим местом;
- thin operating surface над уже существующим ядром;
- consumer существующих source-of-truth слоев;
- bounded product reset для desktop формы.

Workspace v1 не является:

- новым owner рыночного времени, trade facts или journal facts;
- новой архитектурой поверх `replay/trading/journal`;
- mentor/dashboard/mobile/sync platform;
- full broker terminal;
- broad charting platform.

## Current problem

Текущий desktop shell уже usable как инженерная оболочка, но продуктово непригоден как рабочее место трейдера, потому что:

- главный экран не собран вокруг графика;
- старт с датасетом остается двусмысленным;
- replay воспринимается как управление внутренним состоянием, а не как рынок;
- торговой работе мешают служебные тексты и derived explanations;
- review и notes еще не ощущаются как рабочая форма;
- полезные для инженера surfaces не отделены от primary user workspace.

Следствие: проект имеет working core, но еще не имеет первого product-credible trader workspace.

## Stage goal

Цель этапа - не полировать текущий shell, а переопределить bounded product-facing форму первого usable trainer workspace.

Результат этого этапа:

- главный экран становится chart-first;
- старт работы с данными становится однозначным;
- trade loop и review entry становятся понятными без чтения внутренних документов;
- debug/dev diagnostics уходят с основной поверхности;
- существующие ownership boundaries остаются без изменений.

## Existing ownership that must stay unchanged

- `03_MODULES/REPLAY_ENGINE.md` остается owner replay semantics, cursor/time behavior и replay commands.
- `03_MODULES/TRADING_ENGINE.md` остается owner order/position/trade lifecycle semantics.
- `04_TECH/DATA_SCHEMA.md` остается source of truth для `Order`, `Position`, `PositionLeg`, `TradeRecord`, `ExecutionRecord`.
- `04_TECH/JOURNAL_SCHEMA.md` остается source of truth для `TrainingSession`, `PreTradeNote`, `PostTradeReview`, `ChartSnapshot`, `BehavioralFlag`, `RuleViolation`.
- `03_MODULES/DESKTOP_WORKSPACE.md` остается module-level desktop contract для MVP operating surface.

Этот документ не меняет ownership. Он фиксирует product-facing boundary того, как эти already accepted layers должны собраться в первый usable trader workspace.

## Start flow

Старт v1 должен быть однозначным и коротким. Пользователь входит в workspace через один из четырех допустимых путей:

1. `Open prepared dataset`
2. `Import raw historical data`
3. `Create new session`
4. `Restore previous session`

### Start flow rules

- Если у пользователя уже есть prepared dataset, система должна позволять выбрать его без чтения служебной диагностики.
- Если у пользователя есть raw historical file, система должна дать явный `Import` path, после которого пользователь попадает в dataset-ready state.
- Если есть восстановимая незавершенная сессия, `Restore previous session` должен быть отдельным, ясно различимым action.
- Если подходящей сессии нет, основной path должен вести к созданию новой session на выбранном dataset.

### What the user must understand at start

До попадания на главный экран пользователю нужно понять только:

- с какими данными он работает;
- создает ли он новую сессию или восстанавливает прошлую;
- готов ли workspace к открытию графика.

### What must not dominate the start flow

На старте не должны доминировать:

- readiness prose;
- derived recovery explanations;
- long finalization text;
- quality dumps;
- internal lifecycle narration.

Dataset quality warnings допустимы только как компактные warnings, а не как основное содержание старта.

## Screen zones

Главный экран `Desktop Trainer Workspace v1` должен состоять из следующих зон.

### 1. Top replay/session bar

Назначение:

- показать текущую dataset/session/replay рамку;
- дать основные replay controls;
- удержать минимум необходимого статуса.

Обязательный состав:

- instrument / dataset label;
- replay mode;
- current simulation time;
- play/pause;
- step / advance;
- speed;
- session state;
- compact active trade indicator.

### 2. Main chart area

Назначение:

- быть центром рабочего пространства;
- показывать рынок как основную operating surface для торгового решения.

Это самая крупная и визуально доминирующая зона экрана.

### 3. Trading panel

Назначение:

- дать ясный и компактный вход в торговые действия;
- показать текущее состояние ордера/позиции без длинного текста.

### 4. Compact trade/session context

Назначение:

- держать на главной поверхности только краткий рабочий контекст;
- не превращать экран в status console.

### 5. Review / notes entry point

Назначение:

- давать явный вход в `PreTradeNote` и `PostTradeReview`;
- показывать, когда review нужен, доступен или уже существует.

### 6. Secondary panels

Назначение:

- хранить result/history/review-support surfaces, которые полезны, но не должны занимать центр экрана.

### 7. Optional debug/dev panel

Назначение:

- дать инженеру доступ к diagnostics без захвата primary workspace.

Эта зона по умолчанию скрыта или вторична.

## Chart-first rule

`Desktop Trainer Workspace v1` обязан быть chart-first.

Это означает:

- график является главным и центральным элементом интерфейса;
- пользователь должен попадать прежде всего на рынок, а не на текстовые статусы;
- replay, trade и review actions должны читаться как действия вокруг графика;
- текстовые блоки являются вторичными и компактными;
- derived/recovery/readiness/finalization explanations не должны доминировать на главном экране.

Если между графиком и текстовым status surface есть конфликт за главное внимание пользователя, приоритет всегда у графика.

## Chart rendering boundary

### Mandatory visual boundary

Первый usable trainer workspace обязан показывать:

- основной `price chart` как `bar chart only`;
- overlay `Alligator`;
- overlay `Fractals`;
- отдельный нижний indicator pane с `AO`.

### What must be visible to the user

На chart-first экране пользователь обязан сразу видеть:

- текущую bar-based price action;
- текущее положение replay на графике;
- `Alligator` поверх основного price chart;
- `Fractals` поверх основного price chart;
- `AO` в отдельном нижнем блоке;
- текущий видимый торговый контекст для входа/сопровождения/выхода.

### What is explicitly required in v1

- бары, а не свечи;
- один главный chart viewport;
- overlays `Alligator` и `Fractals` на price chart;
- отдельная нижняя pane для `AO`;
- достаточная читаемость для ручной торговой работы.

### What is not required at this stage

- candlestick mode;
- broad study library;
- custom indicator marketplace;
- multi-chart layouts;
- docking/preset system;
- full drawing toolkit;
- advanced chart annotation workspace;
- broad media/charting platform behavior.

## Replay UX boundary

Replay должен ощущаться как рынок, а не как debug state machine.

### Required controls

- `Play`
- `Pause`
- `Advance / Step`
- `Speed`
- visible current replay state

### Required replay visibility

Пользователь должен без длинного текста понимать:

- идет replay или стоит на паузе;
- какой сейчас момент рынка;
- какая скорость проигрывания активна;
- достигнут ли конец данных;
- в каком replay mode он находится;
- как replay state связан с active/pending trade state.

### UX rule

Replay controls должны быть короткими, ясными и action-oriented. Их задача - управлять рынком, а не объяснять внутреннюю механику runtime.

### Relation to trade state

Связь replay и trading должна быть читаема сразу:

- нет активной сделки;
- есть pending entry;
- есть active trade;
- trade partially closed;
- trade closed and ready for review.

Пользователь не должен разбирать lifecycle prose, чтобы понять, можно ли сейчас открыть, отменить, сопровождать или закрыть сделку.

## Trading UX boundary

Trading panel v1 фиксируется как compact product-facing control surface.

### Required actions

- `Buy Market`
- `Sell Market`
- `Buy Stop`
- `Sell Stop`
- `Cancel Entry`
- `Partial Close`
- `Close`
- optional `SL`
- optional `TP`

### Required immediately visible trade facts

Пользователь должен видеть сразу, без чтения длинного текста:

- active trade: `yes/no`
- side
- entry
- volume
- stop loss
- take profit
- pending entry
- remaining open volume

### Trading panel rules

- panel отражает one-active-trade boundary;
- panel не должен поощрять parallel portfolio-like flow;
- panel показывает торговые факты компактно;
- panel использует существующие trade owners и не становится новым owner logic.

### Not required in v1

- complex power-user order ticket;
- broker-terminal style depth tools;
- advanced order ladder;
- portfolio exposure module;
- rich multi-position management shell.

## Compact context boundary

На главном экране допустим только компактный рабочий контекст.

### Allowed on the main surface

- instrument / dataset;
- replay mode and state;
- current session state;
- compact trade state;
- compact note/review availability;
- compact warnings that change immediate user action.

### Must move to secondary or hidden surfaces

- long lifecycle explanations;
- extensive review chains;
- readiness text dumps;
- pause-point text;
- recovery prose;
- repetitive derived summaries;
- verbose finalization explanations;
- diagnostics useful mainly to engineering.

Правило: если блок не помогает принять следующее торговое действие или следующий replay/review action, он не должен занимать primary surface.

## Review entry boundary

Review должен входить в основной рабочий контур, но не должен превращать главный экран в текстовую свалку.

### Entry rules

- После закрытия сделки пользователь должен видеть явный `Open review` entry point.
- Review entry должен быть доступен из compact result/trade context, а не спрятан в diagnostics.
- Review должен быть связан с конкретным `tradeId` или session context по уже принятым journal rules.

### Review form shape

Review должен выглядеть как рабочая форма:

- короткие структурированные поля;
- явная связь с note и trade context;
- bounded Bill Williams fields;
- ясные flags / violations links;
- optional snapshot refs там, где уже разрешено schema.

### Required relation model

Review surface должна явно связывать:

- `PreTradeNote`
- `PostTradeReview`
- Bill Williams fields
- `BehavioralFlag`
- `RuleViolation`

Но эта связь не должна превращаться в long textual chain на primary screen.

## Secondary vs debug separation

`Desktop Trainer Workspace v1` обязан явно развести три уровня поверхностей.

### Primary workspace

Это то, что нужно для основной торговой работы:

- top replay/session bar;
- main chart;
- trading panel;
- compact context;
- review entry.

### Secondary panels

Это полезные, но не центральные surfaces:

- trade result;
- session history;
- review summary;
- linked notes;
- secondary guidance.

### Debug/dev diagnostics

Это инженерные surfaces:

- internal derived state visibility;
- recovery diagnostics;
- readiness diagnostics;
- low-level finalization details;
- controller/debug text.

### Separation rule

То, что полезно инженеру, может существовать, но не должно оставаться центром пользовательского интерфейса. Debug usefulness не является аргументом для размещения на primary screen.

## Acceptance scenario

Документ считается продуктово состоятельным, если по этой границе пользователь без знания внутренних документов может:

1. открыть приложение;
2. выбрать prepared dataset или импортировать raw historical data;
3. создать новую сессию или восстановить подходящую прошлую;
4. попасть на chart-first экран;
5. увидеть bar chart с `Alligator` + `Fractals` и отдельным `AO` below main chart;
6. запустить replay;
7. открыть сделку;
8. сопровождать ее;
9. закрыть ее;
10. открыть review;
11. заполнить или обновить review как рабочую форму;
12. продолжить или завершить сессию.

## Explicit non-goals

Этот документ не открывает:

- rewrite runtime;
- смену source-of-truth ownership;
- mentor layer;
- mobile layer;
- sync/cloud scope;
- dashboard/BI scope;
- broad charting platform;
- full broker terminal design;
- UI kit overhaul;
- новую архитектуру поверх уже принятой.

Это не rewrite. Это bounded product-facing boundary reset для desktop operating surface.

## Relationship to current desktop shell

Текущее состояние `desktop_shell/` нужно учитывать как implementation constraint, но нельзя принимать как продуктовую норму.

Следствие для будущей реализации:

- текущий shell можно использовать как техническую базу;
- его text/status-heavy layout не является обязательным шаблоном;
- migration должна идти bounded refactor path, а не broad rewrite;
- новый workspace может требовать минимального follow-up к module-level desktop framing, если существующий `03_MODULES/DESKTOP_WORKSPACE.md` остается слишком shell-centric.

## Minimal follow-up if module framing proves too narrow

Если в реализации выяснится, что `03_MODULES/DESKTOP_WORKSPACE.md` концептуально расходится с этой новой chart-first boundary, допустим только один минимальный follow-up:

- узкий alignment pass, который уточнит product-facing priority of chart-first primary workspace, secondary surfaces и debug separation без переписывания replay/trading/journal contracts.

Этот follow-up должен быть отдельной bounded задачей.
