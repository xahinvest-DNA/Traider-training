# Market Model

Дата фиксации: 2026-03-14
Статус: spec v1
Приоритет: highest

## 1. Назначение модуля

Market model нужен для того, чтобы replay engine и trading engine работали не с абстрактной ценой, а с формализованным рынком и инструментом.

Модуль описывает:

- универсальные свойства торгового инструмента;
- правила цены и единиц измерения;
- правила объема;
- execution-related свойства, нужные для честного расчета сделки;
- профиль рынка для первого боевого контура FX/CFD.

Граница ответственности:

- `market model` описывает, что такое инструмент и какие у него торговые свойства;
- `replay engine` воспроизводит историю и поставляет текущее состояние рынка;
- `trading engine` принимает торговые решения и исполняет сделки, используя правила из market model и snapshot из replay engine.

## 2. Уровни модели

### Universal market core

Общий слой доменной модели, не завязанный на конкретный рынок.

Содержит:

- `InstrumentSpec`
- `MarketProfile`
- `PricingRules`
- `TradingSessionRules`
- `CostRules`

### Market profile

Профиль рынка фиксирует набор допущений для конкретного типа инструмента.

В v1:

- основной профиль: `FX_CFD_V1`

### Instrument specification

Конкретное описание торгуемого инструмента.

Примеры:

- `EURUSD`
- `GBPUSD`
- `XAUUSD`
- `US30.cash`

### Pricing rules

Описывают:

- минимальный шаг цены;
- точность котировки;
- связь между tick, point, pip;
- расчет стоимости движения цены.

### Execution-related properties

Описывают:

- допустимый диапазон объема;
- шаг объема;
- spread mode;
- commission rules;
- swap rules;
- правила торговых сессий;
- свойства, которые trading engine использует для исполнения и расчета сделки.

## 3. Сущность Instrument

### InstrumentSpec

#### `instrumentId`

- Смысл: внутренний стабильный идентификатор инструмента.
- Тип: `string`
- Обязательность: обязательно
- Зачем в v1: ссылка в dataset, replay session, trade records.

#### `symbol`

- Смысл: пользовательский символ инструмента.
- Тип: `string`
- Обязательность: обязательно
- Зачем в v1: отображение в UI и журнале.

#### `marketType`

- Смысл: тип рынка или профиля.
- Тип: `enum`
- Обязательность: обязательно
- Значения v1: `fx_spot_like`, `cfd_index`, `cfd_metal`
- Зачем в v1: выбор pricing и execution assumptions.

#### `baseCurrency`

- Смысл: базовая валюта инструмента.
- Тип: `string | null`
- Обязательность: обязательно для FX, optional для CFD
- Зачем в v1: расчеты pip value и PnL в FX-парах.

#### `quoteCurrency`

- Смысл: валюта котировки.
- Тип: `string`
- Обязательность: обязательно
- Зачем в v1: расчет цены, PnL и стоимости движения.

#### `pricePrecision`

- Смысл: количество знаков после запятой в нормализованной цене.
- Тип: `integer`
- Обязательность: обязательно
- Зачем в v1: storage, replay, PnL и UI consistency.

#### `tickSize`

- Смысл: минимальный шаг изменения цены в dataset/internal model.
- Тип: `decimal`
- Обязательность: обязательно
- Зачем в v1: нормализация цены и проверка корректности котировок.

#### `pointSize`

- Смысл: минимальная отображаемая единица цены в модели платформы.
- Тип: `decimal`
- Обязательность: обязательно
- Зачем в v1: UI, журнал, расчет point movement.

#### `lotStep`

- Смысл: минимальный шаг объема.
- Тип: `decimal`
- Обязательность: обязательно
- Зачем в v1: валидация объема ордера.

#### `minLot`

- Смысл: минимально допустимый объем.
- Тип: `decimal`
- Обязательность: обязательно
- Зачем в v1: защита от невалидных ордеров.

#### `maxLot`

- Смысл: максимально допустимый объем.
- Тип: `decimal`
- Обязательность: обязательно
- Зачем в v1: защита от нереалистичных объемов.

#### `contractSize`

- Смысл: размер контракта на 1.00 lot.
- Тип: `decimal`
- Обязательность: обязательно
- Зачем в v1: расчет PnL и стоимости движения.

#### `pipValueRule`

- Смысл: правило расчета стоимости pip для инструмента.
- Тип: `object`
- Обязательность: обязательно
- Зачем в v1: единообразный расчет pip value и PnL.

Минимальные поля:

- `pip_size`
- `calculation_mode`
- `settlement_currency`

#### `tradingSessionRules`

- Смысл: правила открытия/закрытия рынка по времени.
- Тип: `object`
- Обязательность: обязательно
- Зачем в v1: исполнение ордеров и ограничения replay/trading.

#### `swapRules`

- Смысл: правила свопа и переноса через ночь.
- Тип: `object`
- Обязательность: обязательно
- Зачем в v1: расчет holding cost.

Минимальный v1:

- `enabled`
- `long_swap_per_lot`
- `short_swap_per_lot`
- `triple_swap_day`

#### `commissionRules`

- Смысл: правила комиссии.
- Тип: `object`
- Обязательность: обязательно
- Зачем в v1: расчет trade cost.

Минимальный v1:

- `enabled`
- `commission_model`
- `value`
- `currency`
- `apply_per_side`

#### `spreadMode`

- Смысл: источник и правило спреда.
- Тип: `enum`
- Обязательность: обязательно
- Значения v1: `fixed`, `variable`, `dataset_driven`
- Зачем в v1: определить, откуда trading engine берет effective spread.

## 4. Первый профиль v1 - FX/CFD

### Что реально поддерживается в v1

- FX пары с bid/ask tick history;
- CFD на металлы;
- CFD на индексы, если они нормализуются как bid/ask tick stream с известным contract spec.

### Допущения для FX/CFD

- один инструмент на replay session;
- bid/ask quotes есть в dataset или могут быть надежно нормализованы;
- контрактные свойства инструмента известны заранее;
- broker-specific margin logic не моделируется;
- spread может идти из dataset либо быть задан fixed rule для controlled training scenarios.

### Что откладывается

- фьючерсы с expiry logic;
- акции с corporate actions;
- опционы;
- multi-leg instruments;
- portfolio correlation logic;
- broker-specific leverage tiers.

### Разная точность котировки

В v1 инструменты с разной precision поддерживаются через `pricePrecision` и `tickSize`.

Примеры:

- `EURUSD`: 5 digits, `tickSize = 0.00001`
- `USDJPY`: 3 digits, `tickSize = 0.001`
- `XAUUSD`: 2 или 3 digits в зависимости от источника, но после import должен быть единый normalized precision

## 5. Ценообразование и единицы измерения

### Отличия между tick, point, pip, bar

- `tick` - одно рыночное событие с конкретной котировкой и timestamp.
- `point` - минимальная единица цены в модели платформы.
- `pip` - доменная единица движения цены для FX-like инструментов.
- `bar` - агрегированное состояние множества тиков за timeframe bucket.

### Как считается движение цены

Базовая формула:

- `price_move = exit_price - entry_price`

В point:

- `point_move = price_move / pointSize`

В tick units:

- `tick_move = price_move / tickSize`

В pip:

- `pip_move = price_move / pip_size`

### Как хранится цена

В v1 цена хранится как нормализованное decimal значение с `pricePrecision`, а не как float UI.

Правило:

- internal storage и execution calculations используют decimal-like semantics;
- display formatting отделен от storage.

### Как рассчитывается стоимость движения

Базовая формула:

- `gross_price_delta_value = price_move * contractSize * volume_lots`

Конкретный settlement зависит от `pipValueRule` и quote currency.

### Как рассчитывается стоимость пункта / pip value

Минимальный режим v1:

- если `quoteCurrency == accountCurrency`, pip value считается напрямую;
- если нет, используется `pipValueRule.calculation_mode`, но cross-currency conversion beyond simple direct quote может быть отложен.

Для v1 рекомендуется:

- ограничить первый боевой набор инструментов такими случаями, где pip value можно считать надежно без сложного conversion chain.

### Как рассчитывается PnL в v1

`net_pnl = gross_pnl - spread_cost - slippage_cost - commission_cost - swap_cost`

Где:

- `gross_pnl` зависит от направления сделки и цены входа/выхода;
- costs считаются отдельно и сохраняются в execution record и journal.

## 6. Лоты и объём

### Базовое правило v1

Текущая модель:

- `$100 -> 0.01`
- `$200 -> 0.02`
- `$1000 -> 0.10`
- `$10000 -> 1.00`

Это трактуется как:

- не свойство рынка;
- не универсальное правило платформы;
- а `volume sizing mode` первого контура.

### Что это означает

- это режим расчета позиции, используемый UI/training workflow;
- правило задает соответствие между размером пользовательского капитала и default lot size;
- оно должно храниться отдельно от `InstrumentSpec`.

### Как хранится

В v1 рекомендуется сущность:

- `PositionSizingProfile`

Минимальные поля:

- `profile_id`
- `mode = balance_linked_lot`
- `base_balance_amount = 100`
- `base_lot = 0.01`
- `rounding_rule`
- `min_lot_override optional`
- `max_lot_override optional`

### Как отделить от будущих режимов

Будущие режимы:

- `manual_lot`
- `risk_percent`
- `fixed_cash_risk`

Принцип:

- `InstrumentSpec` отвечает за допустимые границы объема;
- `PositionSizingProfile` отвечает за то, как пользователь выбирает объем;
- trading engine получает уже вычисленный `requested_volume`.

## 7. Издержки

### Обязательная структура v1

- `spread`
- `slippage`
- `commission`
- `swap`

### Что обязательно в v1

- spread: обязательно
- slippage: обязательно, но может быть `0` по profile/rule
- commission: обязательно как поддерживаемая сущность, даже если для части инструментов `enabled = false`
- swap: обязательно как поддерживаемая сущность для сделок с overnight holding

### Источник каждого значения

- `spread`: из текущего bid/ask snapshot или из fixed spread rule
- `slippage`: из execution policy trading engine
- `commission`: из `InstrumentSpec.commissionRules`
- `swap`: из `InstrumentSpec.swapRules`

### Как это передается в trading engine

Через связку:

- `InstrumentSpec`
- `ExecutionSnapshot`
- `ExecutionPolicy`

### Как это фиксируется в journal/analytics

В execution/trade record отдельно сохраняются:

- `spread_cost`
- `slippage_cost`
- `commission_cost`
- `swap_cost`
- `total_trade_cost`

## 8. Торговые сессии

### Как хранить правила

`tradingSessionRules` должны описывать:

- timezone
- weekly open/close windows
- session exceptions optional
- is_24x5_like

### Что делать, если рынок формально закрыт

Если `marketSessionState = closed`:

- replay может продолжать двигаться по данным, если в dataset есть следующий tick уже после открытия;
- trading engine не должен исполнять новый market order в закрытом состоянии;
- pending orders не исполняются до появления легитимного рынка после открытия.

### Влияние на replay и исполнение

- replay engine знает session state как часть dataset metadata и snapshot;
- trading engine использует session state как hard constraint для исполнения.

## 9. Ограничения и допущения v1

- один инструмент за сессию;
- один active trade lifecycle;
- первый market profile - FX/CFD;
- без portfolio model;
- без multi-asset correlation logic;
- без broker-specific margin engine;
- без сложной cross-currency pip value matrix для широкого списка инструментов;
- без exchange order book simulation.

## 10. Архитектурные решения и компромиссы

### Почему выбран такой market model

- он отделяет свойства рынка от replay logic;
- он отделяет свойства инструмента от выбора пользовательского объема;
- он дает минимально достаточную универсальность для роста beyond FX without overengineering.

### Рассмотренные альтернативы

#### Жестко зашитая FX-only модель

Плюсы:

- быстрее старт.

Минусы:

- плохая расширяемость;
- смешивание доменной модели и текущих частных допущений.

Статус:

- отклонено.

#### Сразу полная broker model

Плюсы:

- выше реализм.

Минусы:

- слишком тяжелый scope для v1;
- тормозит запуск первого прототипа.

Статус:

- отложено.

### Что сознательно отложено

- margin tiers;
- leverage simulation;
- exchange calendars с праздниками и особыми режимами;
- complex cross-currency conversion chains;
- broker-specific commission quirks;
- multi-asset portfolio semantics.
