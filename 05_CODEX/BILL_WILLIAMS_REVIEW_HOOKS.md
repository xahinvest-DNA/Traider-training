# Bill Williams Review Hooks

Дата фиксации: 2026-03-19
Статус: implementation boundary
Приоритет: high

## 1. Purpose and Scope

`BILL_WILLIAMS_REVIEW_HOOKS.md` фиксирует следующий bounded implementation slice поверх already working local journal runtime: minimum Bill Williams structured review hooks.

Документ нужен, чтобы:

- перевести уже принятый Bill Williams vocabulary в минимально работающие persisted fields внутри `PreTradeNote` и `PostTradeReview`;
- не оставлять Bill Williams layer только на уровне reference docs;
- дать desktop/runtime возможность хранить declared intent и final reviewed classification в structured form;
- не превратить этот шаг в signal engine, mentor workflow, analytics expansion или rule engine.

Документ не меняет `DATA_SCHEMA.md`, не делает Bill Williams auto-classification и не вводит новый source of truth beyond existing journal entities.

## 2. Why this Slice is Next

Этот slice логичен сразу после local-first journal loop, потому что:

- `TrainingSession` / `PreTradeNote` / `PostTradeReview` уже реально persistятся и восстанавливаются локально;
- `DESKTOP_WORKSPACE.md` уже ожидает bounded Bill Williams structured review hooks;
- `BILL_WILLIAMS_RULES.md` и `BILL_WILLIAMS_LAYER.md` уже зафиксировали minimum vocabulary и границы runtime vs review-assisted classification;
- этот шаг добавляет методологическую ценность review flow без преждевременного захвата analytics, mentor или auto-detection scope.

## 3. Preconditions / Dependencies

Этот slice опирается на уже принятые документы:

- `04_TECH/JOURNAL_SCHEMA.md`
- `03_MODULES/BILL_WILLIAMS_LAYER.md`
- `02_RESEARCH/BILL_WILLIAMS_RULES.md`
- `03_MODULES/DESKTOP_WORKSPACE.md`
- `05_CODEX/JOURNAL_REVIEW_LOOP.md`

И на уже работающий runtime:

- local `TrainingSession` binding;
- `PreTradeNote` persistence;
- `PostTradeReview` persistence;
- bounded post-close review flow;
- local recovery after restart.

## 4. In-Scope Behavior

В этот slice входят:

- minimum structured `setupTag` support in `PreTradeNote`;
- minimum structured `setupTag` support in `PostTradeReview`;
- minimum structured `complianceLabel` support in `PostTradeReview`;
- bounded `reviewTags[]` support in `PostTradeReview` with vocabulary validation;
- local persistence and recovery of these structured fields;
- desktop-facing projection of structured Bill Williams fields;
- validation against compact accepted vocabulary from `BILL_WILLIAMS_RULES.md`.

## 5. Explicit Out-of-Scope

В этот slice не входят:

- runtime auto-classification;
- signal engine;
- chart-reading automation;
- `BehavioralFlag` / `RuleViolation` capture;
- mentor review workflow;
- dashboards and analytics expansion;
- scoring models;
- `ChartSnapshot` or media flow;
- full canonical coverage of all Profitunity variations.

## 6. Runtime Contract

Минимальный runtime contract:

- `PreTradeNote.setupTag` = declared Bill Williams intent only;
- `PostTradeReview.setupTag` = final reviewed setup assignment;
- `PostTradeReview.complianceLabel` = final reviewed methodological quality label;
- `PostTradeReview.reviewTags[]` = lightweight qualitative review metadata;
- runtime may validate vocabulary membership;
- runtime must not infer a final Bill Williams verdict from trade facts alone.

## 7. Minimum Vocabulary Contract

### setupTag

Минимально поддерживаемые values:

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

### complianceLabel

Минимально поддерживаемые values:

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

### reviewTags

Минимально поддерживаемый bounded subset first implementation:

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
- `management_consistent`
- `management_inconsistent`
- `valid_add_on`
- `invalid_add_on`
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

## 8. Persistence Expectations

Persistence contract for this slice:

- structured BW fields live only inside existing `PreTradeNote` / `PostTradeReview` entities;
- values persist locally and survive restart;
- structured tags do not become trade facts;
- post-trade BW classification may differ from pre-trade intent and both may coexist.

## 9. Acceptance Scenario

1. пользователь создает `PreTradeNote` с `setupTag`;
2. note persistится локально;
3. пользователь проходит trade loop и создает `PostTradeReview`;
4. review сохраняет `setupTag`, `complianceLabel`, `reviewTags[]`;
5. desktop/runtime показывает structured BW fields;
6. после restart values восстанавливаются локально.

## 10. Acceptance Criteria

Slice считается принятым, если:

- `PreTradeNote` принимает валидный `setupTag`;
- `PostTradeReview` принимает валидные `setupTag`, `complianceLabel`, `reviewTags[]`;
- invalid vocabulary values hard-reject'ятся at runtime boundary;
- values сохраняются и восстанавливаются после restart;
- Bill Williams fields не подменяют trade facts и не требуют auto-classification;
- slice не затягивает `BehavioralFlag`, `RuleViolation`, analytics, mentor, mobile или sync.

## 11. Risks / Boundary Protections

Основные риски:

- случайно превратить vocabulary validation в fake signal engine;
- смешать `reviewTags` с `complianceLabel`;
- начать тащить `RuleViolation` / `BehavioralFlag` в тот же coding step;
- зафиксировать слишком широкий vocabulary without implementation need.

Boundary protections:

- только review-assisted structured tags;
- only compact bounded vocabulary;
- no inference beyond validation;
- no new source-of-truth layer;
- no analytics expansion in this step.
