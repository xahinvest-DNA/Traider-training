# Data Import

Дата фиксации: 2026-03-14
Статус: spec v1
Приоритет: highest

## 1. Назначение модуля

Data import отвечает за превращение сырого исторического файла в внутренний dataset, пригодный для replay engine и дальнейшего review.

Связи:

- с `replay engine`: поставляет нормализованный dataset handle, а не raw provider format;
- с `market model`: использует `InstrumentSpec` и `MarketProfile` для нормализации precision, session rules и quality checks;
- с `internal storage`: сохраняет ticks, derived bars, metadata и quality report.

## 2. Источники данных

### Какие источники рассматриваются для v1

- user-supplied tick CSV/TSV/JSON exports;
- platform-managed imported datasets, подготовленные internal import pipeline;
- mixed model: пользователь загружает raw dataset, система нормализует и сохраняет свой internal format.

### Рекомендуемый источник v1

Рекомендуемый режим v1:

- `user-supplied raw dataset -> normalized internal dataset`

Причина:

- не привязывает продукт к MT5;
- сохраняет local-first модель;
- позволяет контролировать quality policy.

### Минимально допустимое качество tick dataset

- timestamps должны быть неубывающими;
- bid и ask должны присутствовать;
- precision должна быть приводимой к `InstrumentSpec.pricePrecision`;
- длительные пропуски допустимы только как честные low-liquidity или market-closed участки;
- dataset должен пройти validation и quality policy.

### Происхождение dataset

В v1 поддерживается:

- `user_supplied`
- `platform_managed`
- `mixed`

Рекомендуемый primary mode:

- `mixed`: пользователь или система приносят raw dataset, но replay всегда работает только с normalized internal dataset.

## 3. Raw Input Format

### Минимальные поля raw tick

#### `timestamp`

- Обязательность: обязательно
- Использование: ordering, replay time, bar building
- Можно ли пропустить: нет

#### `bid`

- Обязательность: обязательно
- Использование: buy/sell execution logic, spread
- Можно ли пропустить: нет

#### `ask`

- Обязательность: обязательно
- Использование: buy/sell execution logic, spread
- Можно ли пропустить: нет

#### `last`

- Обязательность: optional
- Использование: later phases или диагностика quality
- Можно ли пропустить: да

#### `volume`

- Обязательность: optional
- Использование: analytics и completeness hints
- Можно ли пропустить: да

#### `sourceId`

- Обязательность: желательно
- Использование: traceability dataset
- Можно ли пропустить: да, но manifest тогда должен содержать source info

#### `qualityFlags`

- Обязательность: optional
- Использование: перенос провайдерских маркеров качества
- Можно ли пропустить: да

## 4. Normalization Pipeline

Последовательность v1:

1. ingest raw file
2. validate schema
3. normalize timestamp
4. normalize precision
5. validate monotonic order
6. detect duplicates
7. detect gaps
8. mark anomalies
9. persist internal format
10. build derived bars

### 1. Ingest raw file

- определить parser по формату;
- привязать dataset к `instrumentId` и source metadata.

### 2. Validate schema

- проверить наличие обязательных полей;
- проверить типы и parseability.

### 3. Normalize timestamp

- привести timestamps к единой timezone;
- привести формат к UTC-based internal representation или другой единой canonical zone, зафиксированной в manifest.

### 4. Normalize precision

- привести цены к `InstrumentSpec.pricePrecision`;
- зафиксировать original precision и normalized precision в metadata.

### 5. Validate monotonic order

- out-of-order ticks должны быть выявлены;
- при hard violation dataset отклоняется или сортируется только в безопасном controllable режиме import, зафиксированном в quality report.

### 6. Detect duplicates

- идентифицировать дубликаты полного raw tick или одинаковые timestamps;
- пометить их, но не удалять слепо без policy.

### 7. Detect gaps

- вычислить интервалы между соседними тиками;
- сравнить их с expected trading session state;
- пометить `market_closed_gap` или `unexpected_gap`.

### 8. Mark anomalies

- stale quote
- extreme spread spike
- out-of-order attempt
- missing field
- duplicated tick cluster

### 9. Persist internal format

- сохранить normalized ticks;
- сохранить metadata и quality report;
- сохранить dataset manifest.

### 10. Build derived bars

- построить M5, M15, H1, H4, D1 из normalized tick history;
- пометить incomplete last bar.

## 5. Internal Storage Format

Внутренний storage v1 должен хранить:

- `ticks`
- `bars_by_timeframe`
- `dataset_metadata`
- `quality_report`
- `dataset_manifest`

### Ticks

Normalized tick records:

- `timestamp`
- `bid`
- `ask`
- `mid optional`
- `volume optional`
- `source_id optional`
- `quality_flags`

### Bars

Derived bars per timeframe:

- `timeframe`
- `bar_open_time`
- `bar_close_time`
- `open`
- `high`
- `low`
- `close`
- `tick_count`
- `is_complete`

### Metadata

- `instrument_id`
- `market_profile`
- `timezone_canonical`
- `dataset_start_time`
- `dataset_end_time`
- `row_count`
- `normalized_precision`

### Dataset manifest

Нужен обязательно.

Минимальные поля:

- `dataset_id`
- `instrument_id`
- `source_type`
- `source_id`
- `imported_at`
- `schema_version`
- `checksum`
- `quality_summary`

### Checksum / versioning

Нужны в v1:

- checksum для repeatability и обнаружения изменений;
- `schema_version` для эволюции internal format.

## 6. Dataset Quality Policy

### Базовый принцип

V1 не требует идеального dataset, но требует dataset, который не ломает честность replay и исполнения.

### Допустимость и пороги

#### Полнота

- минимально допустима полнота всего покрываемого периода с учетом реальных market-closed intervals;
- long missing segments внутри ожидаемо активной сессии должны идти как warning или hard reject в зависимости от масштаба.

#### Пропуски

- low-liquidity пропуски допустимы;
- большие неожиданные gaps внутри активной сессии - warning, а при систематичности hard reject.

#### Low-liquidity участки

- допустимы;
- не исправляются синтетически;
- должны быть помечены quality flags.

#### Out-of-order ticks

- единичные технически исправимые случаи допускаются только на этапе import с явной сортировкой и отметкой в report;
- массовые out-of-order случаи - hard reject.

#### Дубликаты

- дубликаты timestamp допустимы;
- дубликаты полного tick payload допустимы как warning, если не массовые;
- аномально большой кластер дубликатов - hard reject.

#### Отсутствующий ask/bid

- hard reject.

### Warning

- sparse liquidity stretches;
- isolated duplicate clusters;
- unusual spread spikes;
- repaired out-of-order rows below threshold;
- incomplete last bar.

### Hard reject

- отсутствует `timestamp`, `bid` или `ask`;
- timestamps не парсятся;
- dataset не приводится к monotonic order;
- массовые out-of-order ticks;
- систематически пустые цены;
- dataset слишком короткий для запуска replay по целевым TF;
- precision невозможно привести к instrument spec.

## 7. Построение баров

### Как бары производятся из тиков

- из normalized tick history;
- по timeframe bucket;
- строго после завершения normalizing pipeline.

### Когда бар считается открытым

- когда приходит первый tick нового timeframe bucket.

### Когда бар считается закрытым

- когда приходит первый tick следующего bucket того же timeframe.

### Incomplete last bar

В v1:

- сохраняется как `is_complete = false`;
- доступен replay engine и review layer;
- не считается synthetic closed bar.

### Консистентность replay и review

- replay engine читает те же derived bar artifacts, что и review layer;
- incomplete last bar должен одинаково трактоваться в replay state и review analytics как незавершенный.

## 8. Мульти-ТФ синхронизация

Из одной tick history строятся:

- M5
- M15
- H1
- H4
- D1

Гарантия единого момента рынка:

- все bars строятся от одного normalized tick stream;
- replay engine использует один `simulation_time`;
- переключение TF меняет только представление и active focus, а не рынок.

## 9. Контракт Replay Engine ↔ Data Layer

Replay engine получает от data layer:

- `DatasetHandle`
- последовательность normalized ticks
- доступ к derived bars
- dataset boundaries
- dataset metadata
- quality summary
- session state metadata

Replay engine не должен знать:

- raw file format;
- parser details;
- provider-specific anomalies;
- как именно проводилась нормализация.

### DatasetHandle

Минимальные поля:

- `dataset_id`
- `instrument_id`
- `market_profile`
- `tick_stream_ref`
- `bars_ref`
- `metadata_ref`
- `quality_report_ref`
- `dataset_start_time`
- `dataset_end_time`

## 10. Контракт Trading Engine ↔ Replay Engine

### Что получает trading engine

Trading engine получает `ExecutionSnapshot` после каждого примененного tick event.

### Какие проверки он имеет право делать

После каждого нового `TickArrived`, когда replay state уже обновлен, trading engine имеет право проверять:

- market order fill;
- stop order trigger;
- stop loss;
- take profit;
- partial close;
- add-on entry.

### Что считается ценой исполнения в v1

- buy market: по `ask` текущего snapshot плюс slippage rule;
- sell market: по `bid` текущего snapshot плюс slippage rule;
- buy stop trigger: когда market reaches trigger condition по ask-side semantics;
- sell stop trigger: когда market reaches trigger condition по bid-side semantics;
- stop loss / take profit: по стороне закрытия позиции, соответствующей выходу из сделки.

### Как учитываются bid/ask/spread/slippage

- spread является естественной разницей `ask - bid` либо берется из fixed rule;
- effective execution price = raw side price + slippage adjustment;
- costs считаются и логируются как отдельные execution components.

### Как фиксируется причина исполнения

В каждом execution event:

- `execution_reason`
- `trigger_type`
- `trigger_snapshot_timestamp`
- `source_order_id`

Минимальные значения `execution_reason`:

- `market_entry`
- `pending_order_trigger`
- `stop_loss_hit`
- `take_profit_hit`
- `partial_close_manual`
- `add_on_entry`
- `forced_close_end_of_session` later phase

## 11. Execution Snapshot

Минимальный `ExecutionSnapshot`:

- `timestamp`
- `symbol`
- `bid`
- `ask`
- `mid`
- `activeBarByTimeframe`
- `replayMode`
- `marketSessionState`
- `liquidityFlags`
- `dataQualityFlags`
- `datasetPosition`

Где:

- `activeBarByTimeframe` = map TF -> current bar snapshot
- `marketSessionState` = `open | closed | preopen_like | unknown`
- `datasetPosition` включает `tick_index`, `is_end_of_data`, `dataset_start_time`, `dataset_end_time`

Обязательные правила:

- snapshot read-only;
- snapshot всегда описывает уже примененное состояние рынка;
- trading engine не работает по устаревшему snapshot после следующего тика.

## 12. Edge Cases

### Missing ticks

- честно отражаются как gap или sparse interval;
- synthetic filler не создается.

### Duplicated ticks

- помечаются quality flags;
- replay воспроизводит normalized sequence как есть.

### Out-of-order ticks

- не должны доходить до replay после successful import;
- если обнаружены после import, dataset считается broken.

### Stale quote

- помечается quality flags;
- trading engine видит флаг и может логировать degraded execution context.

### Incomplete bar

- сохраняется как incomplete;
- не форсируется в closed bar.

### Gap at session boundary

- допустим;
- классифицируется отдельно как session-boundary gap.

### Weekend / market close

- если рынок закрыт, market order fill не допускается;
- pending order ждет reopen and next valid tick.

### Extreme spread spike

- не исправляется;
- маркируется как anomaly;
- trading engine использует фактический snapshot.

### Jump into sparse area

- replay engine получает первый tick `>= target`;
- snapshot несет flags sparse/liquidity anomaly if applicable.

## 13. Артефакты на выходе

В рамках этой спецификации должны быть согласованы и при необходимости обновлены:

- `03_MODULES/MARKET_MODEL.md`
- `03_MODULES/DATA_IMPORT.md`
- `03_MODULES/TRADING_ENGINE.md`
- `01_MASTER/DECISIONS.md`
- `01_MASTER/CURRENT_STATE.md`

## Открытые вопросы, требующие отдельного обсуждения

1. Допускается ли для первого рабочего профиля нормализованный pseudo-tick source или нужен только provider-grade real tick.
2. Какой порог repaired out-of-order ticks считать еще допустимым warning, а какой уже hard reject.
3. Нужно ли в v1 поддерживать cross-currency pip value для инструментов, где settlement currency не совпадает с quote currency.
4. Какой exact slippage policy нужен в v1: fixed, random within band, deterministic by liquidity flag.
