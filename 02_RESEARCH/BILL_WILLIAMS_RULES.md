# Bill Williams Rules

Дата фиксации: 2026-03-15
Статус: spec/reference v1
Приоритет: highest

## 1. Назначение документа

`BILL_WILLIAMS_RULES.md` фиксирует минимальный методологический контракт v1 для Bill Williams-слоя внутри Trader Trainer.

Документ нужен, чтобы:

- задать единый словарь `setup taxonomy`;
- зафиксировать `compliance labels` и `review tags`;
- отделить методологическую классификацию setup от behavioral classification;
- связать методологические нарушения с `RuleViolation`;
- связать поведенческие ошибки с `BehavioralFlag`;
- согласовать `PreTradeNote` и `PostTradeReview` со структурированным словарем v1;
- не менять уже принятые source-of-truth и analytics ownership contracts.

## 2. Scope and Boundaries

### Что входит

- минимальный словарь setup taxonomy v1 для Bill Williams;
- compliance labels v1;
- review tags v1;
- mapping в `RuleViolation`;
- граница с `BehavioralFlag`;
- tag contract для `PreTradeNote` и `PostTradeReview`;
- contract with `JOURNAL_SCHEMA.md` and `JOURNAL_ANALYTICS.md`;
- MVP boundary и later expansion boundary.

### Что не входит

- полный движок сигналов Bill Williams;
- полная machine-verifiable формализация всех вариаций Profitunity;
- UI/UX для разметки setup;
- mentor scoring framework;
- probability/confidence engine;
- перепроектирование trade storage, journal schema или analytics ownership.

## 3. Методологические принципы v1

- Bill Williams в проекте трактуется как методология принятия решений, а не только как набор индикаторов.
- `Setup classification` отвечает на вопрос: что это за setup по методу.
- `Compliance label` отвечает на вопрос: насколько конкретное действие соответствует методу.
- `Review tags` отвечают на вопрос: как качественно оценить setup, исполнение, сопровождение и выход.
- `RuleViolation` фиксирует нарушение явного правила метода или режима.
- `BehavioralFlag` фиксирует поведенческий паттерн, даже если методологический setup сам по себе был валиден.
- Один и тот же trade может одновременно иметь:
  - valid Bill Williams setup;
  - behavioral problem;
  - no formal rule violation.

## 4. Scope of Bill Williams v1

Bill Williams v1 в проекте опирается на минимальное практическое ядро:

- `Alligator` как контекстный фильтр;
- `Fractal breakout` как базовый структурный сигнал;
- `Awesome Oscillator (AO)` как источник momentum/acceleration confirmation;
- логика `First Wise Man`, `Second Wise Man`, `Third Wise Man` в упрощенном обучающем словаре;
- идея работы только в согласии с направлением и состоянием рынка, а не против него без явной причины;
- add-on как допустимое наращивание внутри одной сделки, если оно методологически поддержано.

В v1 не требуется покрыть весь канон Profitunity и все спорные вариации из книг.

## 5. Bill Williams Setup Taxonomy v1

### 5.1. Общая структура setup

Каждый Bill Williams setup v1 должен быть описываем как structured classification со следующими полями:

- `setupFamily`
- `setupCode`
- `direction`
- `timeframeContext`
- `confirmationRequirement optional`
- `invalidationCondition optional`
- `notesExamples optional`

### 5.2. Поля taxonomy

#### setupFamily

Смысл:

- крупная группа методологического сигнала.

Допустимые значения v1:

- `first_wise_man`
- `second_wise_man`
- `third_wise_man`
- `fractal_breakout`
- `ao_add_on`
- `balance_line_context`
- `mixed_bw_setup`
- `unclear_bw_setup`

#### setupCode

Смысл:

- стабильный короткий код setup для notes, review и analytics.

Рекомендуемые коды v1:

- `BW_1WM_LONG`
- `BW_1WM_SHORT`
- `BW_2WM_LONG`
- `BW_2WM_SHORT`
- `BW_3WM_LONG`
- `BW_3WM_SHORT`
- `BW_FRACTAL_LONG`
- `BW_FRACTAL_SHORT`
- `BW_AO_ADDON_LONG`
- `BW_AO_ADDON_SHORT`
- `BW_BALANCE_LINE_LONG`
- `BW_BALANCE_LINE_SHORT`
- `BW_MIXED_LONG`
- `BW_MIXED_SHORT`
- `BW_UNCLEAR`

#### direction

Допустимые значения:

- `long`
- `short`
- `neutral optional for unclear review only`

#### timeframeContext

Смысл:

- рабочий таймфрейм setup и, при необходимости, higher-timeframe reference.

Минимум v1:

- `primaryTimeframe`
- `higherTimeframe optional`

#### confirmationRequirement optional

Смысл:

- какие подтверждения ожидались для признания setup sufficiently valid.

Примеры:

- `alligator_awake_and_open`
- `fractal_outside_alligator_mouth`
- `ao_direction_supports_entry`
- `price_outside_alligator_mouth`
- `valid_add_on_after_initial_breakout`

#### invalidationCondition optional

Смысл:

- какие условия делают setup слабым, спорным или недействительным.

Примеры:

- `signal_inside_alligator_mouth`
- `entry_against_alligator_context`
- `missing_fractal_breakout`
- `late_after_primary_move`
- `no_confirming_momentum`

#### notesExamples optional

Смысл:

- короткая текстовая подсказка или reference для review.

### 5.3. Minimal setup families v1

#### First Wise Man

Назначение:

- ранний разворотный или первичный вход после смены поведения рынка.

Taxonomy role:

- используется как отдельная family;
- в v1 допускается более общая методологическая интерпретация без полной канонизации всех candle-pattern деталей.

#### Second Wise Man

Назначение:

- momentum-driven continuation/add-on signal с опорой на AO.

Taxonomy role:

- в v1 нужен прежде всего как отдельная family для add-on validity и review.

#### Third Wise Man

Назначение:

- вход или наращивание через фрактальный прорыв вне пасти Аллигатора.

Taxonomy role:

- в v1 это один из ключевых setup families, пригодный и для first entry, и для continuation.

#### Fractal Breakout

Назначение:

- базовый структурный сигнал прорыва фрактала в правильном контексте Alligator.

Taxonomy role:

- допускается как самостоятельная family even when review не фиксирует Wise Man wording explicitly.

#### AO Add-on

Назначение:

- add-on внутри уже валидного trade lifecycle, когда наращивание поддержано AO-based continuation context.

Taxonomy role:

- нужен отдельно, потому что в проекте add-on разрешен, но должен быть методологически отделен от импульсивного добора.

#### Balance Line Context

Назначение:

- контекстный setup family для случаев, когда решение связано прежде всего с линиями Alligator / balance-line logic.

Taxonomy role:

- не является главным family для MVP, но нужен как fallback structured tag вместо free-text.

#### Mixed BW Setup

Назначение:

- setup, где review достоверно видит Bill Williams context, но не может честно свести ситуацию к одному чистому family.

#### Unclear BW Setup

Назначение:

- случай, где Bill Williams interpretation не может быть классифицирован достаточно надежно.

## 6. Compliance Labels v1

### 6.1. Назначение

`Compliance labels` описывают качество соответствия конкретного entry/add-on/exit методологии Bill Williams.

Они не заменяют trade facts и не являются сами по себе `BehavioralFlag` или `RuleViolation`.

### 6.2. Минимальный словарь v1

- `valid_setup`
- `weak_setup`
- `unconfirmed_setup`
- `late_entry`
- `early_entry`
- `add_on_valid`
- `add_on_invalid`
- `exit_by_rule`
- `exit_outside_rule`
- `unclear_setup`
- `not_bill_williams`

### 6.3. Смысл label'ов

#### valid_setup

- setup классифицирован как Bill Williams;
- минимальные подтверждения для выбранной family присутствуют.

#### weak_setup

- setup формально похож на Bill Williams, но контекст неполный, слабый или методологически уступающий.

#### unconfirmed_setup

- идея setup присутствует, но требуемое подтверждение отсутствует или спорно.

#### late_entry

- entry соответствует направлению метода, но сделан после прохождения значимой части импульса.

#### early_entry

- идея метода угадывается, но вход был сделан до необходимого подтверждения.

#### add_on_valid

- add-on соответствует уже активному Bill Williams trade context.

#### add_on_invalid

- add-on выполнен без корректного continuation context или против логики методики.

#### exit_by_rule

- выход соответствует допустимому методологическому выходу или защитной логике метода.

#### exit_outside_rule

- выход совершен вне методологического плана, хотя сам по себе мог быть дисциплинарно оправдан.

#### unclear_setup

- review недостаточно уверен для точной классификации.

#### not_bill_williams

- сделка или действие не должны быть засчитаны как Bill Williams setup.

## 7. Review Tags v1

### 7.1. Принцип

`Review tags` - это качественные метки для review и обучения. Они не подменяют:

- `setupCode`
- `complianceLabel`
- `RuleViolation`
- `BehavioralFlag`

### 7.2. Категории review tags

#### Setup-quality tags

- `setup_clear`
- `setup_weak`
- `setup_unconfirmed`
- `setup_late`
- `setup_early`
- `setup_mixed`
- `setup_unclear`
- `not_bw_setup`

#### Execution-quality tags

- `entry_precise`
- `entry_late`
- `entry_early`
- `entry_sloppy`
- `good_price_location`
- `poor_price_location`
- `cost_acceptable`
- `cost_expensive`

#### Management-quality tags

- `management_consistent`
- `management_inconsistent`
- `valid_add_on`
- `invalid_add_on`
- `protection_present`
- `protection_weak`
- `position_managed_by_rule`
- `position_managed_ad_hoc`

#### Exit-quality tags

- `exit_by_method`
- `exit_too_early`
- `exit_too_late`
- `exit_protective`
- `exit_emotional`
- `exit_unclear`

#### Context-quality tags

- `alligator_supportive`
- `alligator_sleeping`
- `fractal_context_valid`
- `fractal_context_invalid`
- `ao_supportive`
- `ao_unsupportive`
- `timeframe_alignment_present`
- `timeframe_alignment_unclear`

## 8. Three-Layer Classification Boundary

### 8.1. Methodological setup classification

Сюда входят:

- `setupFamily`
- `setupCode`
- `direction`
- `timeframeContext`
- `complianceLabel`
- review tags о качестве setup и execution относительно метода

Это отвечает на вопрос:

- что это за setup по Bill Williams и насколько он методологически чист.

### 8.2. Behavioral classification

Сюда входят `BehavioralFlag` examples:

- `impulsive_entry`
- `post_loss_revenge_trading`
- `overtrading`
- `hesitation_delayed_action`
- `cost_blind_trading`
- `holding_loser_too_long`

Это отвечает на вопрос:

- как человек себя вел.

### 8.3. Hard/soft rule violations

Сюда входят `RuleViolation.ruleCode`:

- явное нарушение entry/add-on/exit/protection/mode rule.

Это отвечает на вопрос:

- какое правило было нарушено.

### 8.4. Где overlap допустим

Допустим overlap:

- `late_entry` как compliance label и `impulsive_entry` как behavioral flag;
- `add_on_invalid` как compliance label и `bw_invalid_add_on` as rule violation;
- `not_bill_williams` как compliance label и `manual_plan_deviation` как rule violation.

Смысл:

- одно описывает методологическое качество;
- второе описывает нарушение правила;
- третье описывает поведение.

### 8.5. Где overlap запрещен

Запрещено:

- использовать `BehavioralFlag` вместо `setupCode`;
- использовать `RuleViolation` вместо `complianceLabel`;
- считать free-text review tags source of truth для trade facts;
- дублировать один и тот же смысл одновременно как `BehavioralFlag` и `RuleViolation`, если это чисто методологическая проблема без behavioral content.

Пример:

- `signal_inside_alligator_mouth` сам по себе должен жить как methodological non-compliance or rule violation, а не как behavioral flag.

## 9. RuleViolation Mapping

### 9.1. Общий принцип

`RuleViolation` создается там, где есть явное отклонение от принятого Bill Williams method contract или session discipline rule.

Не каждый слабый setup обязан становиться `RuleViolation`.

### 9.2. Entry rule violations

Рекомендуемые классы:

- `bw_setup_missing_confirmation`
- `bw_entry_without_fractal_context`
- `bw_entry_against_alligator_context`
- `bw_entry_inside_alligator_mouth`
- `bw_entry_not_classifiable`

Когда использовать:

- entry заявлен как Bill Williams, но не проходит минимальный методологический фильтр.

### 9.3. Add-on rule violations

Рекомендуемые классы:

- `bw_invalid_add_on`
- `bw_add_on_without_open_context`
- `bw_add_on_without_ao_support`
- `bw_add_on_after_method_exit_signal`

### 9.4. Stop / protection rule violations

Рекомендуемые классы:

- `missing_stop_loss`
- `bw_protection_missing`
- `bw_protection_removed_without_reason`

Примечание:

- этот слой зависит от окончательной policy про обязательность stop loss;
- до отдельного решения часть таких случаев может считаться `soft` violation.

### 9.5. Exit rule violations

Рекомендуемые классы:

- `bw_exit_outside_rule`
- `bw_premature_exit_without_rule`
- `bw_exit_ignores_method_context`

### 9.6. Session / mode discipline violations if methodologically relevant

Рекомендуемые классы:

- `manual_plan_deviation`
- `exam_mode_backseek_attempt`
- `exam_mode_restart_attempt`
- `session_second_independent_trade_attempt`

### 9.7. Unclear / not-classifiable cases

Рекомендуемые классы:

- `bw_setup_unclear`
- `bw_method_not_applicable`

Правило:

- unclear case не должен автоматически считаться hard violation;
- сначала это classification boundary, а не наказание.

## 10. BehavioralFlag Boundary

### 10.1. Что не является Bill Williams rule violation, а является behavioral marker

Примеры:

- `impulsive_entry`
- `revenge_like_add_on`
- `overtrading`
- `hesitation_delayed_action`
- `cost_blind_trading`
- `holding_loser_too_long`
- `risk_escalation_after_loss`

### 10.2. Почему это не RuleViolation по умолчанию

- RuleViolation требует явной rule boundary;
- behavioral marker фиксирует pattern, даже если формальное правило не было нарушено.

Пример:

- трейдер мог войти по валидному фрактальному прорыву, но сделать это импульсивно после серии убытков и слишком крупным объемом.

В этом случае:

- setup может быть `valid_setup`;
- `BehavioralFlag` может быть `post_loss_revenge_trading`;
- `RuleViolation` может отсутствовать, если явное rule не нарушено.

### 10.3. Как coexist работает без конфликта

Одна сделка может иметь одновременно:

- `setupCode = BW_FRACTAL_LONG`
- `complianceLabel = valid_setup`
- `BehavioralFlag.flagCode = hesitation_delayed_action`
- `RuleViolation.ruleCode = missing_stop_loss`

Это не конфликт, потому что слои отвечают на разные вопросы.

## 11. Tag Contract with JOURNAL_SCHEMA

### 11.1. PreTradeNote

`PreTradeNote` в v1 может получать:

- `setupTag` as structured or enum-backed reference to `setupCode`
- `complianceLabel optional`
- `timeframeContext`
- `thesisSummary`
- `riskPlan`

Рекомендуемая трактовка:

- `setupTag` обязателен only when user explicitly declares Bill Williams intent;
- `complianceLabel` в `PreTradeNote` допускается как planned/expected label, но окончательная review classification должна жить в post-trade layer.

### 11.2. PostTradeReview

`PostTradeReview` в v1 может получать:

- `reviewTags[]`
- `setupTag`
- `complianceLabel`
- `relatedRuleViolationRefs optional`
- `relatedBehavioralFlagRefs optional`

### 11.3. References to RuleViolation / BehavioralFlag

Могут ссылаться на:

- `RuleViolation.ruleCode`
- `BehavioralFlag.flagCode`

Но не должны дублировать их как самостоятельный source of truth.

### 11.4. Нужен ли отдельный structured vocabulary для Bill Williams review labels в v1

Рекомендуемое решение:

- да, минимальный structured vocabulary нужен уже в v1;
- он должен быть компактным и жить в этом документе как reference taxonomy;
- он не требует отдельной новой persistence entity.

## 12. Contract with JOURNAL_ANALYTICS

### Какие теги участвуют в аналитике как persisted classifications

Могут участвовать later в аналитике:

- `setupCode`
- `complianceLabel`
- `BehavioralFlag.flagCode`
- `RuleViolation.ruleCode`

### Какие теги остаются review metadata

Остаются review metadata by default:

- большая часть `reviewTags`
- свободные комментарии в `PreTradeNote`
- свободные комментарии в `PostTradeReview`

### Какие counts later можно агрегировать

Допустимые future aggregates:

- count of `valid_setup`
- count of `weak_setup`
- count of `late_entry`
- count of `add_on_valid` / `add_on_invalid`
- count of `exit_by_rule` / `exit_outside_rule`
- setup-family distribution
- method compliance rate by session/series

### Что не должно становиться source of truth для trade facts

- setup taxonomy tags;
- review tags;
- compliance labels.

Они не должны заменять:

- entry/exit prices;
- execution timestamps;
- costs;
- volume changes;
- execution reasons.

### Future mentor review and progress tracking

Taxonomy v1 может later использоваться для:

- mentor review filters;
- student progression tracking;
- consistency scoring;
- setup repetition analysis.

Но это later derived layer, а не новая primary persistence.

## 13. PreTradeNote / PostTradeReview Tag Contract

### PreTradeNote minimal tag contract v1

Минимально допустимые structured fields:

- `setupTag`
- `direction`
- `timeframeContext`
- `thesisSummary optional`
- `riskPlan optional`

### PostTradeReview minimal tag contract v1

Минимально допустимые structured fields:

- `setupTag`
- `complianceLabel`
- `reviewTags[]`
- `relatedRuleViolationRefs optional`
- `relatedBehavioralFlagRefs optional`
- `outcomeAssessment optional`
- `disciplineAssessment optional`

## 14. Minimal MVP vs Later Expansion Boundary

### MVP minimum

Первый прототип обязан иметь:

- минимальный `setup taxonomy`;
- минимальный набор `compliance labels`;
- минимальный набор `review tags`;
- явную границу между methodological / behavioral / violation layers;
- совместимость с `PreTradeNote`, `PostTradeReview`, `RuleViolation`, `BehavioralFlag`.

### Что сознательно откладывается

- полный канон всех setup variations Profitunity;
- сложная многоуровневая scoring system;
- mentor scoring framework;
- probability ranking / confidence engine;
- advanced multi-timeframe semantic grading;
- fully automated Bill Williams rule engine;
- exhaustive machine-readable candle-pattern canon for every Wise Man variant.

## 15. Recommended Minimal Vocabulary v1

### setup families

- `first_wise_man`
- `second_wise_man`
- `third_wise_man`
- `fractal_breakout`
- `ao_add_on`
- `balance_line_context`
- `mixed_bw_setup`
- `unclear_bw_setup`

### compliance labels

- `valid_setup`
- `weak_setup`
- `unconfirmed_setup`
- `late_entry`
- `early_entry`
- `add_on_valid`
- `add_on_invalid`
- `exit_by_rule`
- `exit_outside_rule`
- `unclear_setup`
- `not_bill_williams`

### review tags

- `setup_clear`
- `setup_weak`
- `setup_unconfirmed`
- `setup_late`
- `setup_early`
- `setup_mixed`
- `setup_unclear`
- `not_bw_setup`
- `entry_precise`
- `entry_sloppy`
- `good_price_location`
- `poor_price_location`
- `management_consistent`
- `management_inconsistent`
- `valid_add_on`
- `invalid_add_on`
- `protection_present`
- `protection_weak`
- `exit_by_method`
- `exit_too_early`
- `exit_too_late`
- `exit_emotional`
- `alligator_supportive`
- `alligator_sleeping`
- `fractal_context_valid`
- `fractal_context_invalid`
- `ao_supportive`
- `ao_unsupportive`
- `timeframe_alignment_present`
- `timeframe_alignment_unclear`

## 16. Consistency Rules

- Bill Williams taxonomy не меняет source-of-truth роль `DATA_SCHEMA.md`.
- Bill Williams taxonomy не меняет source-of-truth роль `JOURNAL_SCHEMA.md`.
- `setupTag` and `complianceLabel` не могут заменять raw execution facts.
- `BehavioralFlag` не должен использоваться как substitute for setup classification.
- `RuleViolation` не должен использоваться как substitute for review metadata.
- unclear classification допускается и лучше ложной точности.
- один и тот же trade может иметь несколько review tags, но не должен иметь несколько взаимоисключающих final compliance labels без explicit reviewer note.

## 17. Open Questions

1. Насколько глубоко канонизировать `First Wise Man` в v1: держать его как family-level label или уже переводить в более строгие machine-checkable variants.
2. Нужно ли уже в v1 выделять отдельный structured vocabulary для `Bill Williams context regime` beyond Alligator/AO/Fractal basics.
3. Нужна ли later отдельная сущность для mentor-grade и student-progress labels поверх этой taxonomy.
4. Когда проект перейдет к `BILL_WILLIAMS_LAYER.md`, нужно будет отдельно решить, какие части taxonomy deterministically auto-detectable, а какие остаются review-assisted classification.

## 18. Критерии готовности документа

- Setup taxonomy v1 описан явно.
- Compliance labels v1 описаны явно.
- Review tags v1 описаны явно.
- Граница между setup classification, `BehavioralFlag` и `RuleViolation` описана явно.
- Есть связка с `PreTradeNote` и `PostTradeReview`.
- Taxonomy не ломает source-of-truth и analytics ownership contracts.
- MVP boundary зафиксирован.
