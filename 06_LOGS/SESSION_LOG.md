# Session Log

## 2026-03-14

- Тема: Инициализация Project Brain и фиксация стартового контекста Trader Trainer.
- Что обсуждали: структуру проекта, master-документы, ключевые модули первого контура, правила хранения контекста вне чата.
- Что приняли: Project Brain как основную операционную модель; desktop-first; mobile review; replay + trading + journal как ядро; Bill Williams как обязательную основу.
- Что отклонили: хранение контекста только в чате; зависимость архитектурного ядра от MT5; mobile как равноправную полную торговую платформу на старте.
- Что осталось открытым: replay core design, market model, data schema, MVP boundaries, tech stack.
- Следующий шаг: детальное проектирование replay engine.

## 2026-03-14 - Replay Engine Spec

- Тема: Формальная инженерная спецификация Replay Engine v1.
- Что обсуждали: time cursor, event model, dataset format, replay modes, contracts с trading/journal/UI, API и edge cases.
- Что приняли: tick-driven simulation; один global time cursor; training/exam/review modes; fast-forward без пропуска событий; отсутствие synthetic fillers; один инструмент на сессию.
- Что отклонили: bar-driven replay как ядро; независимое время по таймфреймам; fast-forward с пропуском событий; synthetic empty bars в v1.
- Что осталось открытым: качество tick dataset для v1; checkpoint semantics; policy для incomplete bars; speed constraints в exam mode.
- Следующий шаг: проектирование market data layer и точного контракта исполнения с trading engine.
