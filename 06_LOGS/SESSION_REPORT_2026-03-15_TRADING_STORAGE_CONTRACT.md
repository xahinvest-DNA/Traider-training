# Session Report - 2026-03-15 - Trading Storage Contract

## Тема сессии

Проектирование storage-level модели v1 для `Order`, `Position`, `PositionLeg`, `TradeRecord`, `ExecutionRecord` и связей с journal/analytics.

## Что было сделано

- в `03_MODULES/TRADING_ENGINE.md` добавлен раздел `Data Schema / Storage Contract v1`;
- storage contract согласован с replay/data/import/runtime решениями;
- зафиксировано разделение на append-only trace сущности и mutable active snapshots;
- обновлены `01_MASTER/DECISIONS.md` и `01_MASTER/CURRENT_STATE.md`.

## Ключевые принятые решения

- `ExecutionRecord` и входные факты `PositionLeg` — append-only;
- `Position` и `TradeRecord` — mutable active snapshots до завершения сделки;
- `Order` сохраняется не только runtime, но и как audit trail;
- storage contract остается DB-agnostic и local-first compatible;
- journal/analytics обязаны видеть не только итог сделки, но и полную execution trace.

## Что осталось открытым

- stop loss как hard-rule или soft-rule в v1;
- expiry policy для pending stop orders;
- event-level история изменения SL/TP;
- точный persistence contract для journal/session сущностей.

## Следующий шаг

Вынести storage contract в отдельную техническую `DATA_SCHEMA` спецификацию и описать persistence contracts между trade сущностями и journal/analytics.
