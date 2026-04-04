# Review Flags And Violations

Дата фиксации: 2026-03-19
Статус: implementation boundary
Приоритет: high

## 1. Purpose and Scope

`REVIEW_FLAGS_VIOLATIONS.md` фиксирует следующий bounded implementation slice после minimum Bill Williams review hooks: persisted manual `BehavioralFlag` and `RuleViolation` capture inside local review flow.

Документ нужен, чтобы:

- перевести already accepted `BehavioralFlag` / `RuleViolation` schema from `JOURNAL_SCHEMA.md` в minimum runtime-backed implementation;
- дать review flow возможность сохранять behavioral and rule findings как primary journal entities;
- не смешать их с Bill Williams setup tags, compliance labels или analytics counters;
- не превратить этот шаг в analytics engine, scoring model, mentor workflow или derived detection platform.

## 2. Why this Slice is Next

Этот slice идет следующим, потому что:

- local `TrainingSession` / `PreTradeNote` / `PostTradeReview` loop уже работает;
- minimum Bill Williams structured hooks уже работают;
- `BehavioralFlag` and `RuleViolation` already accepted as source-of-truth journal entities, но пока не живут в runtime;
- следующий полезный шаг review loop — начать хранить explicit behavioral and rule findings, не раздувая analytics.

## 3. Preconditions / Dependencies

Source documents:

- `04_TECH/JOURNAL_SCHEMA.md`
- `03_MODULES/JOURNAL_ANALYTICS.md`
- `03_MODULES/BILL_WILLIAMS_LAYER.md`
- `05_CODEX/JOURNAL_REVIEW_LOOP.md`
- `05_CODEX/BILL_WILLIAMS_REVIEW_HOOKS.md`

Runtime prerequisites:

- local `TrainingSession` persistence;
- local `PostTradeReview` persistence;
- stable `tradeId` / `executionId` / `sessionId` links;
- post-close review flow already exists.

## 4. In-Scope Behavior

В этот slice входят:

- manual creation of `BehavioralFlag` from review flow;
- manual creation of `RuleViolation` from review flow;
- linking `BehavioralFlag.reviewRef -> PostTradeReview.reviewId`;
- linking `RuleViolation.relatedReviewRef -> PostTradeReview.reviewId`;
- linking both entities to `sessionId` and, for trade scope, to `tradeId`;
- bounded runtime validation for `flagCode`, `ruleCode`, `scope`, `severity`, `source`;
- local persistence and restart recovery of flags and violations;
- desktop-facing projection of latest flags/violations counts and last created entries.

## 5. Explicit Out-of-Scope

Не входят:

- derived detection;
- automatic flagging from runtime events;
- execution-scope automation;
- severity-weighted scoring;
- analytics counters as persisted artifacts;
- mentor review workflow;
- sync;
- dashboards;
- chart evidence management beyond simple refs;
- rule engine or auto-classification.

## 6. Minimum Contract

### BehavioralFlag

First implementation supports:

- `source = manual`
- `scope = trade` or `session`
- `severity = info | warning | high`
- `flagCode` from bounded accepted vocabulary
- optional `description`
- optional `reviewRef`
- trade scope requires `tradeId`

### RuleViolation

First implementation supports:

- `source = manual_review`
- `scope = trade` or `session`
- `severity = soft | hard`
- `ruleCode` from bounded accepted vocabulary
- optional `description`
- optional `relatedReviewRef`
- trade scope requires `tradeId`

## 7. Minimum Vocabulary Contract

### BehavioralFlag codes

- `overtrading`
- `post_loss_revenge_trading`
- `averaging_down`
- `oversized_position`
- `impulsive_entry`
- `no_stop_entry`
- `premature_exit`
- `rule_violation_setup`
- `risk_escalation_after_win`
- `risk_escalation_after_loss`
- `holding_loser_too_long`
- `cost_blind_trading`

### RuleViolation codes

- `bw_setup_missing_confirmation`
- `bw_entry_without_fractal_context`
- `bw_entry_against_alligator_context`
- `session_second_independent_trade_attempt`
- `execution_outside_session_rule`
- `invalid_position_size`
- `missing_stop_loss`
- `manual_plan_deviation`
- `exam_mode_backseek_attempt`
- `exam_mode_restart_attempt`

## 8. Persistence Expectations

- `BehavioralFlag` and `RuleViolation` persist as primary journal entities;
- no duplication of trade facts;
- analytics remains derive-on-read;
- local restart restores full flags/violations history;
- flags and violations may coexist with BW review hooks but do not replace them.

## 9. Acceptance Scenario

1. user closes a trade and creates `PostTradeReview`;
2. user adds one `BehavioralFlag` linked to that review and trade;
3. user adds one `RuleViolation` linked to that review and trade;
4. runtime persists them locally;
5. desktop projection shows that review now has linked flags/violations;
6. after restart, review, flag and violation links are restored.

## 10. Acceptance Criteria

Slice is accepted if:

- manual `BehavioralFlag` creation works with bounded vocabulary validation;
- manual `RuleViolation` creation works with bounded vocabulary validation;
- invalid codes/scopes/severities/sources are rejected;
- trade-scoped entities require `tradeId`;
- values persist and recover after restart;
- no analytics summaries or scoring are introduced;
- no auto-detection or rule engine is introduced.

## 11. Risks / Boundary Protections

Risks:

- mixing flags/violations with BW setup tags;
- silently turning manual review capture into derived detection;
- dragging analytics and scoring into the same step;
- over-expanding scope into execution-level evidence handling.

Protections:

- manual-only first implementation;
- compact accepted vocabulary;
- trade/session scope only;
- no analytics writes;
- no mentor/sync/dashboard expansion.
