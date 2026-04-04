# Product Scope

Дата фиксации: 2026-03-15
Статус: master document
Приоритет: highest

## 1. Purpose of Scope Document

`PRODUCT_SCOPE.md` фиксирует продуктовую границу первого рабочего контура Trader Trainer.

Документ нужен, чтобы:

- перевести уже принятые архитектурные решения в продуктовый scope;
- зафиксировать, что именно обязано войти в первый рабочий прототип;
- отделить обязательные части от later phases;
- остановить расползание MVP после завершения базовых architecture contracts.

Этот документ не проектирует новую архитектуру и не меняет уже принятые constraints.

## 2. Product Core

Trader Trainer в первом контуре - это `desktop-first` тренажер ручной торговли на исторических данных по системе Bill Williams.

Продуктовое ядро первого контура:

- replay исторического рынка без показа будущего;
- ручное исполнение сделки пользователем;
- базовое сопровождение позиции в рамках принятой торговой модели;
- журнал до/во время/после сделки;
- базовая аналитика результата, стоимости, дисциплины и методологических ошибок;
- структурированная Bill Williams review-разметка.

Первый контур не является:

- универсальной платформой для любых методов торговли;
- полноценным брокерским терминалом;
- mobile-first продуктом;
- аналитической BI-системой;
- облачной collaborative платформой.

## 3. Primary User and Primary Use Case

### Primary User

Основной пользователь v1:

- один трейдер, который вручную тренирует принятие решений по Bill Williams на исторических данных.

### Primary Use Case

Основной сценарий v1:

1. Пользователь выбирает или импортирует нормализованный исторический dataset.
2. Открывает desktop workspace по одному инструменту.
3. Запускает replay без доступа к будущим данным.
4. Ведет ручную торговлю по Bill Williams.
5. Фиксирует pre-trade и post-trade размышления.
6. Получает trade trace, review и базовую аналитику по сделке и сессии.

## 4. In-Scope for First Working Prototype

В первый рабочий прототип входят:

- один инструмент на активную training session;
- replay historical market data как обязательное ядро;
- tick-driven replay core с bar-based presentation;
- режимы `Training`, `Exam`, `Review Replay` в минимально рабочем виде;
- ручное выставление и сопровождение ордеров в рамках принятого trading model;
- ограничение `one active trade simultaneously`;
- хранение `TradeRecord` и `ExecutionRecord` как обязательной trace-базы;
- базовые journal entities: `TrainingSession`, `PreTradeNote`, `PostTradeReview`, `BehavioralFlag`, `RuleViolation`;
- базовая аналитика результата, издержек, удержания, частоты и дисциплины;
- Bill Williams structured taxonomy и review support на уровне v1;
- import pipeline до normalized internal dataset;
- local persistence и recovery trade/session/journal facts;
- desktop workspace как основной рабочий контур.

## 5. Out-of-Scope for First Working Prototype

Вне первого рабочего прототипа:

- multi-instrument portfolio trading;
- несколько независимых одновременно активных сделок;
- broker-grade margin and account engine;
- универсальная поддержка любых торговых методов;
- полноценная mobile trading environment;
- production cloud collaboration;
- full mentor platform;
- продвинутый Bill Williams auto-detection engine;
- широкий охват рынков за пределами carefully selected v1 profile;
- heavy dashboards, caches и secondary read models как обязательная часть продукта.

## 6. Desktop Scope

Desktop в v1 является основным рабочим контуром.

Desktop scope включает:

- запуск и управление replay;
- отображение графика по одному инструменту и рабочим таймфреймам;
- торговую панель для ручного открытия и сопровождения сделки;
- работу с pre-trade notes и post-trade review;
- просмотр trade trace и базовых session metrics;
- review по Bill Williams taxonomy.

Desktop scope не обязан в v1 включать:

- сложные multi-window workspace presets;
- профессиональный multi-monitor terminal behavior;
- расширенный layout system;
- mentor collaboration tools.

## 7. Mobile Scope

Mobile в v1 не является полноценной торговой средой.

Mobile scope в первом контуре:

- не блокирует запуск первого рабочего прототипа;
- допускается только как later or near-later read-only review layer;
- не является обязательным модулем для принятия MVP.

Mobile explicitly не входит в MVP как:

- live trading terminal;
- replay control authority;
- место исполнения сделок;
- основной session management interface.

## 8. Journal/Analytics Scope

Journal и базовая analytics-диагностика обязательны для первого рабочего контура.

Обязательный scope:

- фиксация pre-trade notes;
- фиксация post-trade review;
- trade/execution trace;
- базовые outcome metrics;
- базовые cost metrics;
- holding time;
- basic win/loss accounting;
- basic behavioral/rule tracking;
- session-level review context.

Не обязательны для первого рабочего прототипа:

- advanced multi-session analytics;
- heavy dashboards;
- derived analytics caches beyond minimal needs;
- mentor scoring and ranking frameworks.

## 9. Bill Williams Scope

Bill Williams является обязательной методологической основой первого контура.

В scope v1 входят:

- structured setup taxonomy;
- compliance labels;
- review tags;
- связь с `RuleViolation` и `BehavioralFlag`;
- review-assisted method labeling как primary mode;
- limited runtime / rule-assisted classification only for deterministic cases.

Не входят в обязательный продуктовый scope v1:

- full machine-verifiable signal engine;
- полный канон всех Profitunity variations;
- advanced probability or confidence scoring;
- mentor-grade semantic grading.

## 10. Replay/Trading Scope

Replay и manual trading составляют ядро продукта.

Обязательный scope:

- tick-driven simulation;
- global time cursor;
- hidden future;
- manual market and stop order placement в рамках принятой модели;
- post-tick execution through accepted execution contract;
- single active trade lifecycle;
- open, manage and close flow for одной сделки;
- deterministic recording of execution trace.

Replay/trading scope v1 не должен расширяться до:

- automated strategy execution;
- portfolio engine;
- hedging/netting complexity;
- broker integration;
- execution outside normalized internal dataset flow.

## 11. Data Scope

Data scope v1 включает:

- import raw historical data into normalized internal dataset;
- first practical market profile `FX/CFD`;
- dataset quality validation;
- bar derivation from ticks;
- replay consumption only from normalized internal dataset.

Data scope v1 не включает:

- broad multi-market universal support;
- full exchange microstructure modeling;
- enterprise-grade data vendor management;
- synthetic data generation to hide gaps.

## 12. Local-First Scope

Local-first обязателен в первом контуре.

Это означает:

- session, trade, execution and journal facts должны жить локально;
- активная сессия должна переживать локальный restart;
- cloud sync не является prerequisite для основной работы;
- stable local IDs обязательны;
- review и базовая analytics должны быть доступны без облака.

Cloud layer допускается только later phase.

## 13. Explicit Non-Goals

Явные non-goals первого рабочего прототипа:

- стать универсальным strategy tester для всех методов;
- заменить MT5 или построить ядро на MT5;
- покрыть все рыночные профили и все типы инструментов;
- поддержать командную облачную работу как обязательный сценарий;
- дать production-ready mentor platform;
- внедрить полный automated Bill Williams signal engine;
- дать все уровни analytics, scoring и coaching сразу.

## 14. Scope Freeze Rules for MVP

Чтобы MVP не расползался, действуют следующие правила:

- наличие architecture/spec документа само по себе не делает функцию обязательной для MVP;
- в MVP попадает только то, что необходимо для первого рабочего пользовательского сценария;
- later-ready contracts могут существовать без product inclusion в первом контуре;
- mobile не может расширить scope desktop-first ядра;
- any new MVP candidate должен быть проверен против `VISION`, `CONSTRAINTS`, `DECISIONS`, `CURRENT_STATE` и этого документа;
- если функция не нужна для минимально замкнутого сценария replay -> manual trade -> journal -> review, она не должна автоматически входить в MVP.

## 15. Acceptance View of First Working Prototype

Первый рабочий прототип считается продуктово состоятельным, если:

1. Пользователь может выбрать или импортировать нормализованный dataset.
2. Пользователь может запустить replay по одному инструменту без доступа к будущему.
3. Пользователь может вручную открыть и закрыть сделку в пределах принятой trading model.
4. Система сохраняет `TradeRecord` и `ExecutionRecord` как достоверную trace-базу.
5. Пользователь может оставить pre-trade note и post-trade review.
6. Система сохраняет session/journal facts локально и восстанавливает их после restart.
7. Пользователь получает базовую аналитику по сделке и сессии.
8. Bill Williams review vocabulary usable in notes/review without превращения taxonomy в замену trade facts.

Если эти условия выполнены, первый рабочий контур продукта считается достигнутым, даже если later layers еще отсутствуют.
