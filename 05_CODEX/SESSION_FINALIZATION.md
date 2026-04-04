# Session Finalization

Дата фиксации: 2026-03-30
Статус: implementation boundary v1
Приоритет: current

## Purpose and Scope

`SESSION_FINALIZATION.md` фиксирует bounded slice для explicit local session finalization поверх уже working replay/trading/journal loop.

Цель шага:

- ввести явное завершение текущей local `TrainingSession`;
- дать bounded guardrails around reviewed-vs-pending closure state;
- отразить terminal close-state в desktop-facing session projection;
- не вводить multi-session shell, dashboard workflow, sync semantics or new analytics layer.

Документ не меняет source-of-truth boundaries `DATA_SCHEMA.md`, `JOURNAL_SCHEMA.md`, `JOURNAL_ANALYTICS.md` и `DESKTOP_WORKSPACE.md`.

## Why this Slice is Next

Этот шаг логичен сейчас, потому что:

- replay, trading и local journal loop уже работают end-to-end;
- derived review output и session metrics уже показывают reviewed/pending state;
- desktop surface уже нуждается в explicit session close state, а не только в implicit pause/finish semantics;
- это можно закрыть узко, не вводя multi-session browser или dashboard layer.

## Preconditions / Dependencies

Слайс опирается на уже working dependencies:

- `TrainingSession` как primary session entity;
- existing local journal runtime and restart recovery;
- existing derived review output with pending/reviewed trade state;
- existing session metrics and desktop-facing journal projection;
- current one-session operating model in `DESKTOP_WORKSPACE.md`.

## In-Scope Behavior

В этот slice входит:

- explicit local `finalize_session()` workflow in runtime;
- bounded finalization guardrails for active trade, running replay and pending post-trade review state;
- support for force-finalization only where strictly needed for pending reviews;
- persisted finalization state on `TrainingSession`;
- desktop-facing finalization projection with blockers and readiness state;
- restart recovery of the same finalized session state.

## Explicit Out-of-Scope

В этот slice не входит:

- multi-session history shell;
- session archive browser;
- dashboard expansion;
- sync and cross-device reconciliation;
- mentor workflow;
- session scoring;
- reopen workflow for finalized sessions;
- advanced review completion orchestration.

## Runtime Contract

Runtime contract for this slice:

- session finalization remains one-session local-first workflow only;
- finalization state is persisted only on `TrainingSession`;
- finalization reads existing trade/review readiness from already derived/current source facts;
- no new `SessionSummary`, archive record or separate close-log entity is introduced.

## Minimum TrainingSession Finalization Contract

Minimum persisted additions on `TrainingSession` may include:

- `finalizationStatus = open | finalized`
- `finalizedAt optional`
- `finalizationReason optional`

Existing `status`, `endedAt` and `endSimulationTime` may still be used, but explicit finalization state must remain separate from ordinary replay pause/finish semantics.

## Guardrail Contract

Finalization must be blocked when:

- an active trade is still open;
- replay is still running;
- there are pending closed trades without `PostTradeReview`, unless `force = true` is explicitly used.

Force-finalization in this slice:

- may bypass pending review guardrail only;
- must not bypass active-trade or running-replay blockers.

## Desktop-Facing Finalization Projection

Desktop-facing journal projection may expose at minimum:

- `finalizationStatus`
- `isSessionFinalized`
- `finalizedAt`
- `finalizationReason`
- `activeTradePresent`
- `replayRunning`
- `pendingReviewTradeIds[]`
- `pendingReviewTradeCount`
- `requiresForceToFinalize`
- `canFinalizeWithoutForce`
- `canFinalizeWithForce`

Desktop still reads this projection only and does not become session owner.

## Persistence Expectations

Persistence expectations remain strict:

- finalization state persists only inside `TrainingSession`;
- no separate finalization log or archive cache is introduced;
- restart recovery must restore finalized/open state and the same blocker projection;
- any later archive shell or multi-session list remains a separate slice.

## Acceptance Scenario

1. User starts a local training session.
2. Opens and closes one or more trades.
3. Leaves at least one trade without `PostTradeReview`.
4. Desktop tries to finalize session.
5. Runtime blocks finalization unless `force = true`.
6. User finalizes explicitly after reviews, or force-finalizes acknowledging pending review state.
7. Desktop sees explicit finalized session state.
8. User restarts the app.
9. Runtime restores the same finalization state and blocker projection.

## Acceptance Criteria

Слайс считается принятым, если:

- runtime exposes explicit session finalization workflow;
- active trade and running replay always block finalization;
- pending review state blocks non-force finalization;
- force-finalization only bypasses pending review blocker;
- finalization state persists and recovers after restart;
- desktop-facing journal projection exposes bounded close-state projection;
- implementation does not expand into multi-session history, dashboards, sync or archive workflows.

## Non-Goals / Deferred Items

Отложено на later steps:

- reopen finalized session workflow;
- multi-session archive and browsing;
- finalized session list screen;
- session score / grade;
- mentor approval workflow;
- sync-aware finalization merge semantics.

## Risks / Boundary Protections

Главные риски:

- смешать replay finish semantics и explicit session close semantics в одну неявную переменную;
- превратить finalization slice в session archive subsystem;
- silently bypass pending review guardrails;
- сделать desktop owner of finalization state instead of journal runtime.

Boundary protections:

- explicit finalization remains bounded to current local session;
- finalization state persists only on `TrainingSession`;
- desktop only reads readiness/blocker projection;
- anything beyond one-session close-state requires a separate later slice.
