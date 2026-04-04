# Bill Williams Review Evidence Follow-Up

Дата фиксации: 2026-04-04
Статус: implementation boundary v1
Приоритет: current

## Purpose and Scope

`BILL_WILLIAMS_REVIEW_EVIDENCE_FOLLOW_UP.md` фиксирует bounded slice для одного компактного follow-up layer поверх уже реализованного `Bill Williams Review Evidence Status`.

Цель шага:

- превратить уже видимый evidence-status из пассивного статуса в один понятный review-facing next step;
- сделать это derive-on-read поверх уже существующего evidence-status, review facts и linked snapshot refs;
- помочь пользователю не просто увидеть `missing` или `partial` evidence, а понять, что именно стоит доделать внутри текущего local desktop review flow;
- не превратить review loop в mentor workflow, gallery/media workspace, scoring model, dashboard layer или новую persistence subsystem.

Документ не меняет source-of-truth boundaries `04_TECH/JOURNAL_SCHEMA.md`, `03_MODULES/JOURNAL_ANALYTICS.md`, `03_MODULES/BILL_WILLIAMS_LAYER.md` и `03_MODULES/DESKTOP_WORKSPACE.md`.

## Why this Slice is Next

Этот шаг логичен сразу после `Bill Williams Review Evidence Status`, потому что:

- текущий evidence-status уже показывает, где reviewed Bill Williams interpretation не подкреплена linked chart context;
- но current session summary и workflow пока дают в основном диагностический сигнал, а не один явный bounded follow-up;
- user-visible friction теперь не в отсутствии еще одного статуса, а в том, что `missing` / `partial` evidence не всегда переводится в ясное действие внутри review loop;
- это можно закрыть узко, без новых entities, без gallery/media scope и без продолжения decorative derive-on-read chain.

## Preconditions / Dependencies

Слайс опирается на уже working dependencies:

- structured `PostTradeReview` Bill Williams method facets;
- current derive-on-read Bill Williams review evidence status;
- local `ChartSnapshot` persistence and desktop authoring flow;
- snapshot-aware trade review output;
- current desktop result/history/context/workflow surfaces.

## In-Scope Behavior

В этот slice входит:

- one compact derive-on-read `bill_williams_review_evidence_follow_up` for latest/current reviewed trade where evidence is `missing` or `partial`;
- bounded current-session follow-up summary for whether reviewed trades still need evidence completion;
- short workflow-facing follow-up text that tells the user the safest next review action;
- desktop-facing visibility only through existing result/history/context/workflow surfaces;
- rebuild of the same follow-up state after local restart from existing source facts.

## Explicit Out-of-Scope

В этот slice не входит:

- new snapshot storage or media entities;
- screenshot automation;
- gallery or image browser;
- mentor coaching or scoring;
- forced validation of snapshot quality;
- multi-session evidence queue;
- dashboard cards;
- mobile or sync continuity.

## Runtime Contract

Runtime contract for this slice:

- follow-up remains derive-on-read only;
- follow-up is computed only from existing evidence-status and linked snapshot context already available in review output;
- follow-up is advisory and workflow-oriented, not a hard blocker and not a correctness verdict;
- absence of follow-up means evidence is either already present or not applicable.

## Minimum Follow-Up Contract

Minimum trade-level follow-up may expose:

- `bill_williams_review_evidence_follow_up_status`
- `bill_williams_review_evidence_follow_up_text`

Recommended bounded status values in this slice:

- `not_applicable`
- `follow_up_not_needed`
- `link_pre_trade_snapshot`
- `link_review_snapshot`
- `link_any_chart_evidence`

Derivation rule for this slice:

- `not_applicable` when no meaningful Bill Williams reviewed interpretation exists yet;
- `follow_up_not_needed` when evidence status is already `linked_evidence_present`;
- `link_any_chart_evidence` when evidence status is `linked_evidence_missing`;
- `link_review_snapshot` when evidence status is `linked_evidence_partial` and pre-trade context exists but review-context snapshot is still missing;
- `link_pre_trade_snapshot` only if future runtime cases distinguish the inverse partial case from existing source facts.

Session-level minimum extension may expose only:

- `reviewed_trades_requiring_bw_evidence_follow_up_count`
- `latest_bill_williams_review_evidence_follow_up_status`
- `latest_bill_williams_review_evidence_follow_up_text`

These remain lightweight current-session guidance fields, not a task manager or dashboard subsystem.

## Desktop-Facing Needs

Desktop can use this slice to:

- show one clear next step when reviewed Bill Williams interpretation still lacks chart support;
- keep the action visible in existing result/history/context/workflow surfaces;
- reduce the gap between seeing a missing-evidence status and knowing what to do next;
- preserve desktop as a thin projection consumer only.

## Persistence Expectations

Persistence expectations remain strict:

- no new source entities are introduced;
- no follow-up queue or acknowledgment state is introduced;
- source facts remain `PostTradeReview`, `ChartSnapshot`, existing snapshot refs, and derive-on-read evidence status;
- follow-up state is rebuilt from restored local source facts after restart.

## Acceptance Scenario

1. User starts a local desktop training session.
2. Creates a reviewed Bill Williams interpretation.
3. Current review output derives evidence status from existing linked chart refs.
4. If evidence is missing or partial, desktop surfaces show one compact follow-up telling the user the next useful evidence action.
5. If evidence is already present, follow-up stays neutral and does not add noise.
6. User restarts the app.
7. Runtime restores source facts and rebuilds the same follow-up state.

## Acceptance Criteria

Слайс считается принятым, если:

- current trade review output can expose one bounded Bill Williams review evidence follow-up when evidence is still missing or partial;
- current session summary exposes only lightweight follow-up count/status for reviewed trades that still need evidence completion;
- desktop surfaces can show the new follow-up through existing result/history/context/workflow surfaces only;
- restart recovery rebuilds the same follow-up state from existing local facts;
- no new persistence entity, gallery/media workflow, mentor logic, scoring, dashboard layer, mobile, or sync scope is introduced.

## Non-Goals / Deferred Items

Отложено на later steps:

- follow-up completion workflow with persisted acknowledgment;
- hard finalization blockers for missing evidence;
- image preview or media browsing;
- multi-session evidence completion queue;
- mentor-grade evidence scoring.

## Risks / Boundary Protections

Главные риски:

- silently turning follow-up into a workflow engine or blocker system;
- duplicating existing evidence status instead of adding a clearer next step;
- drifting into media workflow or mentor guidance;
- building a queue/dashboard abstraction instead of one bounded current-session cue.

Boundary protections:

- one compact follow-up layer only;
- derive-on-read only;
- current-session scope only;
- no new persistence or action state;
- anything beyond one bounded follow-up prompt requires a separate later slice.
