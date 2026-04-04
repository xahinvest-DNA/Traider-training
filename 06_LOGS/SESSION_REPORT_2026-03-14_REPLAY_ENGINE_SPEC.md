# Session Report - 2026-03-14 - Replay Engine Spec

## Тема сессии

Подготовка инженерной спецификации Replay Engine v1 для проекта Trader Trainer.

## Цель сессии

Детализировать `03_MODULES/REPLAY_ENGINE.md` до уровня, на котором можно без двусмысленности проектировать и начинать первый рабочий прототип replay-движка.

## Что было сделано

- полностью переработан `03_MODULES/REPLAY_ENGINE.md`;
- зафиксирована формальная модель времени на базе одного global time cursor;
- описана event model replay core;
- определен минимальный входной формат tick dataset для v1;
- описаны режимы Training Mode, Exam Mode, Review Replay Mode;
- формализованы контракты с `TRADING_ENGINE`, `JOURNAL_ANALYTICS`, `DESKTOP_WORKSPACE`;
- зафиксирован минимальный API прототипа;
- описан `ReplayState`;
- перечислены edge cases и осознанно отложенные части;
- обновлен `01_MASTER/DECISIONS.md`;
- обновлен `01_MASTER/CURRENT_STATE.md`.

## Ключевые принятые решения

- replay v1 строится как tick-driven simulation;
- UI остается bar-based;
- один global time cursor является единственным источником времени;
- bars являются производным состоянием от тиков;
- fast-forward не пропускает события, а только ускоряет их consumption;
- seek назад и restart запрещены в exam mode внутри текущей сессии;
- gaps и low-liquidity участки не заполняются синтетическими данными;
- v1 ограничен одним инструментом и одной активной сделкой.

## Что осталось открытым

- минимально допустимое качество и происхождение tick dataset для v1;
- необходимость checkpoint как отдельной сущности training workflow;
- правила обработки incomplete last bar в review/analytics;
- ограничения speed policy в exam mode.

## Следующий шаг

Сформализовать market data layer и уточнить контракт между replay engine и trading engine на уровне условий исполнения ордеров, snapshot state и требований к dataset.
