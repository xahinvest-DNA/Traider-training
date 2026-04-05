# CODEX WORKLOG

Purpose: append one compact entry after each Codex pass so future sessions can reconstruct what changed without relying on chat history.

---

## 2026-04-04 — Variant 2 operating layer bootstrap

### Goal
Add the missing operating-layer documents required for the ChatGPT ↔ user ↔ Codex workflow so the repository can function as a true source-of-truth project system instead of relying on manual chat transfer.

### Files created
- `01_MASTER/SSOT_MAP.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/CODEX_WORKLOG.md`
- `05_CODEX/IMPLEMENTATION_RULES.md`
- `05_CODEX/HANDOFF_TEMPLATE.md`

### What was done
- Added an explicit source-of-truth map for navigation and conflict resolution.
- Added a single active `NEXT_TASK.md` packet for the next bounded Codex step.
- Added this running worklog so each future pass can append structured outcomes.
- Added implementation rules that force Codex to respect scope, SSOT files, and documentation updates.
- Added a handoff template so future results arrive in a consistent structure.

### What was not changed
- Existing master documents were not rewritten.
- The historical long-form `TASKS.md` ledger was preserved.
- Runtime code, desktop shell code, module docs, and tech schemas were not touched.

### Why this matters
The repository already had strong architecture and documentation. The main missing layer was operational: there was no explicit SSOT map, no single current task packet, and no structured Codex handoff log. Those gaps caused unnecessary manual transfer between chats.

### Remaining gap after this step
- `00_INDEX.md` still does not link these new operating documents.
- `CURRENT_STATE.md` and `TASKS.md` do not yet explicitly mention the new Variant 2 operating mode.
- The next Codex pass should execute the audit described in `05_CODEX/NEXT_TASK.md` and then synchronize the state files.

### Recommended next step
Run the bounded product-value audit defined in `05_CODEX/NEXT_TASK.md`, select one strongest next slice, then update `CURRENT_STATE.md`, `TASKS.md`, and this worklog in the same pass.

## 2026-04-04 — Variant 2 sync and next-slice audit

### Goal
Synchronize the repository with the new Variant 2 operating layer, run the bounded post-snapshot-authoring audit, and choose one strongest next coding slice without drifting into runtime churn, recovery-tail polish, media workflow, dashboards, mentor logic, mobile, or sync.

### Files created
- `05_CODEX/BILL_WILLIAMS_REVIEW_EVIDENCE_STATUS.md`

### Files updated
- `00_INDEX.md`
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/CODEX_WORKLOG.md`

### What was done
- Synced `00_INDEX.md` with `SSOT_MAP.md` and the new Variant 2 operating-layer documents so the repository itself now exposes the active operating stack.
- Ran a bounded audit after desktop chart snapshot authoring and rejected low-value candidates such as more recovery-tail polish, more symbolic Bill Williams label chaining, and dashboard-like session-summary expansion.
- Selected `Bill Williams Review Evidence Status` as the strongest next slice because it gives snapshot authoring direct training value inside the current review loop.
- Added one new implementation-facing document for that slice and promoted it into the active task packet as `T-102`.
- Updated `CURRENT_STATE.md` and the long-form `TASKS.md` ledger so the next frontier is explicit in repository state instead of chat memory.

### What was not changed
- Runtime code was not changed.
- Desktop shell code was not changed.
- Tests were not changed.
- Module contracts and tech schemas were not changed.
- `DECISIONS.md` was not changed because the audit did not require a new project-level decision.

### Why this matters
The project had already closed the recovery-tail and made chart snapshots usable from desktop authoring. The next strongest user-visible gain was to connect that snapshot context to the quality of Bill Williams review instead of adding more surfaces or more labels. This keeps the post-MVP track product-facing and bounded.

### Remaining gap after this step
- `Bill Williams Review Evidence Status` is now defined but not yet implemented in runtime, desktop projections, or tests.
- The next Codex pass should execute `T-102` directly from `NEXT_TASK.md` and keep the implementation strictly derive-on-read and current-session scoped.

### Recommended next step
Implement `T-102: Bill Williams Review Evidence Status Slice`.

## 2026-04-04 — T-102 Bill Williams Review Evidence Status

### Goal
Implement one bounded derive-on-read evidence-status layer so the current desktop-first review flow can show whether reviewed Bill Williams interpretation is backed by linked chart context, without adding persistence, media workflow, dashboards, mentor logic, mobile, or sync.

### Files updated
- `runtime_bootstrap/review_projection.py`
- `desktop_shell/context_surface.py`
- `desktop_shell/history_surface.py`
- `desktop_shell/workflow_surface.py`
- `tests/test_replay_bootstrap.py`
- `tests/test_desktop_shell.py`
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/CODEX_WORKLOG.md`

### What was done
- Added derive-on-read Bill Williams review evidence status in `runtime_bootstrap/review_projection.py` from existing `PostTradeReview` method facts plus linked chart snapshot refs already stored in notes/reviews.
- Surfaced the new signal through existing desktop result, history, context, and workflow helpers without introducing a new UI subsystem.
- Added lightweight current-session evidence-present vs evidence-missing counts to session review output and summary.
- Covered restart recovery in runtime and desktop tests by rebuilding controllers/runtime from the same local storage and asserting the same evidence status after reopen.
- Fixed one summary/history-surface regression caught by the full suite before closing the slice.

### What was not changed
- No new persistence entities were introduced.
- `runtime_bootstrap/desktop_projection.py` was not expanded with a new state model.
- No new module docs or schema docs were changed.
- No new desktop subsystem or workflow owner was introduced.

### Why this matters
Snapshot authoring now has direct training value inside the review loop: the user can see when a reviewed Bill Williams interpretation is actually backed by linked chart context and when it is not.

### Remaining gap after this step
- The repository now needs a bounded audit to select the next strongest post-MVP slice after evidence-status, rather than continuing the evidence chain by inertia.

### Recommended next step
Run `T-103: Post-Evidence-Status Next-Slice Audit`.

## 2026-04-04 — T-103 Post-Evidence-Status Next-Slice Audit

### Goal
Run one bounded managerial audit after `Bill Williams Review Evidence Status` so the repository selects the single strongest next product-facing slice instead of continuing the evidence chain mechanically or drifting into recovery-tail polish, media workflow, dashboards, mentor logic, mobile, sync, or new persistence.

### Files created
- `05_CODEX/BILL_WILLIAMS_REVIEW_EVIDENCE_FOLLOW_UP.md`

### Files updated
- `00_INDEX.md`
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/CODEX_WORKLOG.md`

### What was done
- Audited the current frontier after `T-102` against product value, scope control, and current desktop-first/local-first boundaries.
- Rejected low-value candidates such as more evidence labels, recovery-tail micro-polish, and broader dashboard-like summary expansion.
- Selected `Bill Williams Review Evidence Follow-Up` as the strongest next slice because the real remaining friction is not visibility of missing evidence anymore, but actionability inside the review loop.
- Added one bounded implementation-facing document for the selected slice and promoted it into the active task packet as `T-104`.
- Synchronized project state so repository documents now point to the selected next coding slice instead of the completed audit.

### What was not changed
- Runtime code was not changed.
- Desktop shell code was not changed.
- Tests were not changed.
- Module contracts and tech schemas were not changed.
- `DECISIONS.md` was not changed because no project-level decision was required.

### Why this matters
`T-102` solved diagnosis. The strongest remaining user-visible gain is to make that diagnosis actionable with one bounded next-step cue, rather than adding more passive evidence-related signals.

### Remaining gap after this step
- `Bill Williams Review Evidence Follow-Up` is now defined but not yet implemented in runtime, desktop projections, or tests.

### Recommended next step
Implement `T-104: Bill Williams Review Evidence Follow-Up Slice`.


## 2026-04-04 ? T-104 Bill Williams Review Evidence Follow-Up

### Goal
Implement one bounded derive-on-read follow-up layer so the current desktop-first review flow can show the safest next evidence-completion step when reviewed Bill Williams interpretation still has missing or partial linked chart context, without adding persistence, queueing, blocker state, media workflow, dashboards, mentor logic, mobile, or sync.

### Files updated
- `runtime_bootstrap/review_projection.py`
- `desktop_shell/context_surface.py`
- `desktop_shell/history_surface.py`
- `desktop_shell/workflow_surface.py`
- `tests/test_replay_bootstrap.py`
- `tests/test_desktop_shell.py`
- `00_INDEX.md`
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/CODEX_WORKLOG.md`

### What was done
- Added one derive-on-read evidence follow-up in `runtime_bootstrap/review_projection.py` on top of the existing evidence-status layer.
- Kept the follow-up action-oriented instead of diagnostic-only: missing evidence now maps to `link_any_chart_evidence`, and partial evidence maps to the specific missing snapshot side when existing facts allow it.
- Added lightweight current-session follow-up-needed counts and latest follow-up status/text to session review summary output.
- Surfaced the new signal only through existing result/history/context/workflow helpers.
- Adjusted workflow guidance so it no longer implies the review is fully ready when an evidence follow-up step is still needed.
- Covered restart recovery in runtime and desktop tests using the same existing local storage facts after reopen.

### What was not changed
- No new persistence entities, queues, acknowledgments, blockers, or workflow-engine state were introduced.
- `runtime_bootstrap/desktop_projection.py` was not expanded into a new owner of state.
- No new desktop subsystem, gallery/media flow, dashboard behavior, mentor logic, mobile layer, or sync behavior was introduced.
- No module docs or schema docs were changed.

### Why this matters
`T-102` solved diagnosis and `T-104` solved actionability: the user now sees the next useful evidence-completion step instead of just another passive evidence status. No further evidence-layer continuation is needed right now because the product gap has shifted away from evidence visibility/actionability and back to selecting the next strongest bounded frontier.

### Remaining gap after this step
- The repository now needs a bounded audit to choose the next strongest post-MVP slice after evidence follow-up instead of extending the evidence chain further.

### Recommended next step
Run `T-105: Post-Evidence-Follow-Up Next-Slice Audit`.

## 2026-04-04 — T-105 Post-Evidence-Follow-Up Next-Slice Audit

### Goal
Run one bounded managerial audit after `Bill Williams Review Evidence Follow-Up` so the repository selects the single strongest next product-facing slice instead of continuing the evidence chain with more labels, extra follow-up states, recovery-tail polish, or drift into media workflow, dashboards, mentor logic, mobile, sync, or new persistence.

### Files created
- `05_CODEX/CURRENT_TRADE_REVIEW_DIGEST.md`

### Files updated
- `00_INDEX.md`
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/CODEX_WORKLOG.md`

### What was done
- Audited the frontier after `T-104` using the current desktop-first/local-first workflow and explicitly rejected low-value candidates that would continue the evidence chain, reopen recovery-tail polish, expand dashboards/media, drift into mentor logic, or introduce queue/blocker orchestration.
- Selected `Current Trade Review Digest` as the strongest next bounded slice because the main remaining user-visible gap is fragmented feedback across many existing review signals, not missing evidence diagnosis or evidence actionability.
- Added one new implementation-facing boundary document for the selected digest slice.
- Promoted the digest slice into the active task packet as `T-106`.
- Synchronized project state so the repository now points to the chosen next implementation target instead of the completed audit.

### What was not changed
- Runtime code was not changed.
- Desktop shell code was not changed.
- Tests were not changed.
- Module contracts and tech schemas were not changed.
- `DECISIONS.md` was not changed because no project-level decision was required.

### Why this matters
`T-102` and `T-104` already closed the evidence diagnosis/actionability gap. The strongest next user-visible gain is now to package the existing review signals into one compact trade-level takeaway, which improves the usefulness of the current review loop without creating new architecture or reopening drift areas.

### Remaining gap after this step
- `Current Trade Review Digest` is now defined but not yet implemented in runtime, desktop projections, or tests.

### Recommended next step
Implement `T-106: Current Trade Review Digest Slice`.

## 2026-04-04 - T-106 Current Trade Review Digest Slice

### What was done
- Implemented one bounded derive-on-read current-trade digest in `runtime_bootstrap/review_projection.py` over existing review status, evidence follow-up, review completeness, and already surfaced rule/discipline pressure.
- Exposed the digest through existing desktop `result`, `history`, `context`, and `workflow` surfaces only, without adding a new subsystem, screen, workflow owner, or persistence layer.
- Added targeted runtime and desktop coverage for the required digest states `not_applicable`, `pending_review`, `reviewed_clear`, and `reviewed_gap_open`, including restart recovery from the same local facts after reopen.
- Synchronized project state and promoted a bounded post-digest audit into the next active task packet as `T-107`.

### What was not changed
- Module documents and tech schemas were not changed.
- Runtime persistence entities were not changed.
- No new dashboard, mentor, mobile, sync, media, or workflow-engine layer was introduced.
- `DECISIONS.md` was not changed because no project-level decision was required.

### Why this matters
The current review loop now gives one compact trade-level takeaway for the latest/current closed trade, so users can understand the outcome of review faster without reading a scattered set of small signals or treating the digest as a new owner of truth.

### Remaining gap after this step
- The strongest next bounded slice after the digest still needs to be selected by an explicit frontier audit instead of by mechanically extending the digest/evidence chain.

### Recommended next step
Run `T-107: Post-Digest Next-Slice Audit`.

## 2026-04-04 - T-107 Post-Digest Next-Slice Audit

### What was done
- Audited the frontier after `T-106` using the current desktop-first/local-first review workflow and tested whether any additional bounded slice inside that loop would create stronger user-visible value than the already implemented diagnosis, actionability, and digest layers.
- Explicitly rejected weak candidates: further digest layering, further evidence layering, cosmetic wording/polish, workflow-style quick-action orchestration over existing review steps, mentor logic, dashboard/media expansion, and mobile/sync/new-persistence drift.
- Recorded a `recommend only` result because no strong bounded next implementation slice remains inside the current review loop without crossing into decorative layering or orchestration logic.
- Promoted a broader post-review-loop frontier audit into the active task packet as `T-108`.

### What was not changed
- Runtime code was not changed.
- Desktop shell code was not changed.
- Tests were not changed.
- Module documents and tech schemas were not changed.
- `DECISIONS.md` was not changed because no project-level decision was required.

### Why this matters
The review loop already has bounded diagnosis, actionability, and compact synthesis. Forcing another micro-slice in the same lane would mostly repackage existing guidance or start orchestrating the user's next step. The honest product move is to stop the chain here and reassess the broader local desktop frontier.

### Remaining gap after this step
- The repository still needs one broader post-review-loop audit to identify the next real product-facing frontier beyond the exhausted review-derived lane.

### Recommended next step
Run `T-108: Post-Review-Loop Frontier Audit`.

## 2026-04-04 - T-108 Post-Review-Loop Frontier Audit

### What was done
- Audited the broader local desktop frontier after the review-loop lane was intentionally closed and compared broader candidates instead of reviving review-derived micro-slices.
- Considered and rejected weaker candidates: more review/digest/evidence layering, cosmetic polish, mentor logic, dashboard/media expansion, workflow-engine/queue/blocker drift, replay-garnish work, raw-import hardening as the main next frontier, and add-on/partial-close expansion.
- Selected `Initial Trade Protection` as the strongest next frontier because it improves the active trade loop itself and opens a new productive lane beyond post-trade presentation work.
- Added one new implementation-facing boundary document for the selected frontier and promoted it into the active task packet as `T-109`.

### What was not changed
- Runtime code was not changed.
- Desktop shell code was not changed.
- Tests were not changed.
- Module documents and tech schemas were not changed.
- `DECISIONS.md` was not changed because no project-level decision was required.

### Why this matters
The strongest remaining user-visible gain is no longer inside post-trade review. It is inside the live trade loop: the product still over-relies on `entry -> manual close`, while accepted trading contracts already allow bounded protective structure. Implementing initial trade protection extends the core training value more than any further review-derived cue.

### Remaining gap after this step
- `Initial Trade Protection` is now defined but not yet implemented in runtime, desktop projections, or tests.

### Recommended next step
Implement `T-109: Initial Trade Protection Slice`.


## 2026-04-04 - T-109 Initial Trade Protection Slice

### What was done
- Implemented bounded initial `stopLoss` / `takeProfit` support across the existing trading contracts so `BuyMarket` and `SellMarket` can open one trade with optional initial protection but without creating a broader risk-management owner.
- Added protective threshold handling in the post-tick replay loop so open protected trades close through the accepted trading/storage contract with `stop_loss_hit` or `take_profit_hit` when the next replay snapshots reach the configured threshold.
- Surfaced protection presence, current `stopLoss`, current `takeProfit`, and protective close reason through the existing desktop trading/context/result/history surfaces only, plus one minimal Tk input path for initial SL/TP entry.
- Added targeted runtime and desktop coverage for unprotected entry, SL-only, TP-only, both-protection, protective close, active protected-trade recovery, and closed protected-trade recovery from the same local trade facts after restart.
- Synchronized project state and promoted a bounded post-protection audit into the next active task packet as `T-110`.

### What was not changed
- Module documents and tech schemas were not changed.
- No new persistence entities or trade-protection history were introduced.
- No trailing stop, break-even automation, edit workflow, add-on, partial close, pending-order orchestration, dashboard/media scope, mentor logic, mobile, or sync behavior was introduced.
- `DECISIONS.md` was not changed because no project-level decision was required.

### Why this matters
The live trade loop is now materially stronger as a discipline trainer: one trade can be opened with bounded initial protection and can close for a protective reason from the same local replay facts, instead of relying only on `entry -> manual close`.

### Remaining gap after this step
- The repository now needs a bounded post-Initial-Trade-Protection audit so the next slice is chosen by product value rather than by reflexive extension of the protection lane.

### Recommended next step
Run `T-110: Post-Initial-Trade-Protection Next-Slice Audit`.

## 2026-04-04 - T-110 Post-Initial-Trade-Protection Next-Slice Audit

### Goal
Run one bounded managerial/product audit after Initial Trade Protection so the repository selects the next strongest local desktop product-facing slice without mechanically extending protection management, reopening review-derived micro-slices, or drifting into mentor, dashboard/media, workflow-engine, mobile, sync, or new-persistence scope.

### Files created
- `05_CODEX/CURRENT_TRADE_PLAN_CONTEXT.md`

### Files updated
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/CODEX_WORKLOG.md`

### What was done
- Audited the frontier after `T-109` against user-visible gain, desktop-first/local-first boundaries, and anti-drift rules instead of continuing the protection lane by inertia.
- Explicitly rejected weak candidates: trailing stops, break-even automation, SL/TP edit history, pending-order orchestration, add-on expansion, partial-close expansion, review/digest/evidence backfill, cosmetic polish, and mentor/dashboard/media/mobile/sync/new-persistence drift.
- Selected `Current Trade Plan Context` as the strongest next bounded slice because the live trade loop still loses the user's declared setup/thesis/risk plan after entry even though those local facts already exist in linked `PreTradeNote` records.
- Added one new implementation-facing boundary document for the selected slice and promoted it into the active task packet as `T-111`.

### What was not changed
- Runtime code was not changed.
- Desktop shell code was not changed.
- Tests were not changed.
- Module documents and tech schemas were not changed.
- `DECISIONS.md` was not changed because no project-level decision was required.

### Why this matters
The strongest next gain is no longer more protection behavior. It is keeping the live trade anchored to the trader's own declared plan. That improves execution discipline and continuity inside the current desktop loop without creating a risk engine, mentor layer, or new owner of truth.

### Remaining gap after this step
- `Current Trade Plan Context` is now defined but not yet implemented in runtime, desktop projections, or tests.

### Recommended next step
Implement `T-111: Current Trade Plan Context Slice`.

## 2026-04-04 - T-111 Current Trade Plan Context Slice

### What was done
- Implemented one bounded derive-on-read current-trade plan-context layer in `runtime_bootstrap/review_projection.py` and `runtime_bootstrap/journal_runtime.py` so linked `PreTradeNote` setup/thesis/risk-plan facts can be rebuilt from existing note and trade records without creating a new owner of truth or persisted summary.
- Surfaced the compact factual plan context only through existing desktop `context`, `result`, and `workflow` helpers in `desktop_shell/context_surface.py`, `desktop_shell/workflow_surface.py`, and the existing context render path in `desktop_shell/tk_app.py`.
- Kept the contract factual and compact: plan presence/absence plus declared `setupTag`, `thesisSummary`, and `riskPlan` when present, with active-trade and just-closed continuity from the same linked local facts.
- Added targeted runtime and desktop tests for plan-absent, setup-only, setup-plus-thesis, full setup/thesis/risk-plan, active-trade continuity, just-closed continuity, and restart recovery during both active and closed states.
- Synchronized project state and promoted a bounded post-plan-context audit into the next active task packet as `T-112`.

### What was not changed
- Module documents and tech schemas were not changed.
- No new persistence entities, plan-status machine, checklist engine, acknowledgment flow, or note-management workflow were introduced.
- No mentor advice, semantic grading, workflow-engine behavior, protection-lane expansion, dashboard/media scope, mobile, or sync behavior was introduced.
- `DECISIONS.md` was not changed because no project-level decision was required.

### Why this matters
The live/current trade loop now keeps the trader anchored to the trader's own declared plan instead of dropping that context after entry. This strengthens continuity and discipline inside the current desktop-first/local-first workflow without turning notes into a new summary owner or turning the UI into a coach.

### Remaining gap after this step
- The repository now needs a bounded post-Current-Trade-Plan-Context audit so the next slice is selected by product value instead of continuing plan visibility by inertia.

### Recommended next step
Run `T-112: Post-Current-Trade-Plan-Context Next-Slice Audit`.

## 2026-04-05 - T-112 Post-Current-Trade-Plan-Context Next-Slice Audit

### Goal
Run one bounded managerial/product audit after Current Trade Plan Context so the repository selects the next strongest local desktop product-facing slice without mechanically expanding plan visibility into plan management, reopening protection-lane growth, backfilling review-loop micro-slices, or drifting into mentor, dashboard/media, workflow-engine, mobile, sync, or new-persistence scope.

### Files created
- `05_CODEX/PENDING_STOP_ENTRY.md`

### Files updated
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/CODEX_WORKLOG.md`

### What was done
- Audited the frontier after `T-111` against user-visible gain, desktop-first/local-first boundaries, and anti-drift rules instead of continuing the plan-context lane by inertia.
- Explicitly rejected weak candidates: plan management, plan scoring, richer note workflow, checklist logic, acknowledgment/orchestration behavior, protection-lane continuation, add-on/partial-close expansion, pending-order orchestration drift, review/digest/evidence backfill, cosmetic polish, and mentor/dashboard/media/mobile/sync/new-persistence drift.
- Selected `Pending Stop Entry` as the strongest next bounded slice because the live trade loop still lacks the accepted trigger-based entry path already implied by the trading and desktop contracts, making it a stronger gain than any further plan-recall extension.
- Added one new implementation-facing boundary document for the selected slice and promoted it into the active task packet as `T-113`.

### What was not changed
- Runtime code was not changed.
- Desktop shell code was not changed.
- Tests were not changed.
- Module documents and tech schemas were not changed.
- `DECISIONS.md` was not changed because no project-level decision was required.

### Why this matters
The strongest next gain is no longer another recall or guidance layer. It is expanding the executable live trade loop with one accepted trigger-based entry path. That improves the product more directly than continuing plan visibility, while still staying inside the current one-trade local desktop boundary.

### Remaining gap after this step
- `Pending Stop Entry` is now defined but not yet implemented in runtime, desktop projections, or tests.

### Recommended next step
Implement `T-113: Pending Stop Entry Slice`.


## 2026-04-05 - T-113 Pending Stop Entry Slice

### What was done
- Implemented one bounded `BuyStop` / `SellStop` trigger-based entry path in `runtime_bootstrap/trading_loop.py` on top of existing `OrderRecord`, `TradeRecord`, and `ExecutionRecord` ownership only, including post-tick trigger execution and one-active-pending-stop-at-most enforcement.
- Extended `runtime_bootstrap/types.py` and `runtime_bootstrap/journal_runtime.py` only where strictly needed so pending stop facts, minimal manual cancel-before-trigger, and restart recovery persist through the same existing local order/trade state.
- Exposed pending stop visibility and input only through existing desktop surfaces in `desktop_shell/controller.py`, `desktop_shell/control_surface.py`, `desktop_shell/context_surface.py`, `desktop_shell/workflow_surface.py`, and `desktop_shell/tk_app.py`, without creating a new screen, workflow owner, or pending-order subsystem.
- Added targeted runtime and desktop tests for market-entry compatibility, `BuyStop`, `SellStop`, pending visibility, post-tick trigger execution, minimal manual cancellation, active/recovered pending state, triggered-state recovery, and one-trade / one-pending-stop constraints.
- Synchronized project state and promoted a bounded post-pending-stop-entry audit into the next active task packet as `T-114`.

### What was not changed
- Module documents and tech schemas were not changed.
- No new persistence entities, queue/scheduler state, expiry logic, OCO/bracket behavior, multi-order coordination, or pending-order edit history were introduced.
- No add-on, partial close, trailing stop, break-even, mentor logic, dashboard/media scope, mobile, or sync behavior was introduced.
- `DECISIONS.md` was not changed because no project-level decision was required.

### Why this matters
The live trade loop is no longer market-entry-only. The user can now stage one accepted stop-triggered entry inside the current one-trade replay workflow, which makes the desktop trainer meaningfully closer to the accepted trading contract without turning the product into a broader pending-order management system.

### Remaining gap after this step
- The next strongest local desktop product-facing frontier still needs to be selected explicitly instead of continuing pending-order handling by inertia.

### Recommended next step
Run `T-114: Post-Pending-Stop-Entry Next-Slice Audit`.


## 2026-04-05 - T-114 Post-Pending-Stop-Entry Next-Slice Audit

### Goal
Run one bounded managerial/product audit after Pending Stop Entry so the repository selects the next strongest local desktop product-facing slice without mechanically extending pending-order handling, reopening protection/review/plan micro-lanes, or drifting into mentor, dashboard/media, workflow-engine, mobile, sync, or new-persistence scope.

### Files created
- `05_CODEX/PARTIAL_CLOSE.md`

### Files updated
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/CODEX_WORKLOG.md`

### What was done
- Audited the frontier after `T-113` against user-visible gain, desktop-first/local-first boundaries, and anti-drift rules instead of continuing the pending-order lane by inertia.
- Explicitly rejected weak candidates: pending-order expiry, multi-order coordination, richer order editing history, OCO/bracket behavior, trailing stops, break-even automation, protection-lane continuation, plan-management drift, review/digest/evidence backfill, cosmetic polish, and mentor/dashboard/media/mobile/sync/new-persistence drift.
- Selected `Partial Close` as the strongest next bounded slice because the live trade loop still lacks accepted active-trade volume reduction inside the one-trade lifecycle, making it a stronger user-visible gain than any further pending-order expansion.
- Added one new implementation-facing boundary document for the selected slice and promoted it into the active task packet as `T-115`.

### What was not changed
- Runtime code was not changed.
- Desktop shell code was not changed.
- Tests were not changed.
- Module documents and tech schemas were not changed.
- `DECISIONS.md` was not changed because no project-level decision was required.

### Why this matters
`T-113` already made the entry side of the live loop meaningfully stronger. The next highest product gain is now to improve management of an already opened trade, not to keep adding more pending-order handling. Partial close expands the executable trade loop itself while staying inside already accepted trading/storage ownership.

### Remaining gap after this step
- `Partial Close` is now defined but not yet implemented in runtime, desktop projections, or tests.

### Recommended next step
Implement `T-115: Partial Close Slice`.

## 2026-04-05 - Phase A SSOT sync for T-115 Partial Close

### Goal
Synchronize the operating-layer source-of-truth documents before implementation so the repository has one unambiguous active frontier for T-115 Partial Close.

### Files updated
-  0_INDEX.md
-  1_MASTER/CURRENT_STATE.md
-  5_CODEX/TASKS.md
-  5_CODEX/CODEX_WORKLOG.md

### What was stale
-  0_INDEX.md still pointed to the older Current Trade Review Digest frontier in its header, active focus, implementation-doc link, and next-step guidance.
-  1_MASTER/CURRENT_STATE.md still contained one stale historical bullet that named Current Trade Review Digest as the selected next slice, which contradicted the current top-level Partial Close frontier.
-  5_CODEX/TASKS.md contained duplicated active T-115 blocks with contradictory stale outcomes from older history branches.

### What was synchronized
- Updated  0_INDEX.md so the active module, current focus, implementation-doc pointer, and next steps all point to T-115 Partial Close.
- Removed the stale contradictory digest-selection bullet from  1_MASTER/CURRENT_STATE.md while preserving the rest of the implementation history.
- Cleaned  5_CODEX/TASKS.md so T-114 remains completed and exactly one active T-115 block remains.
- Kept  5_CODEX/NEXT_TASK.md unchanged because it was already aligned to T-115, allowed files, and acceptance criteria.

### Why this mattered before implementation
The repository had real operating drift: different top-level documents named different active frontiers, and TASKS.md exposed multiple conflicting active T-115 entries. Fixing that first restores one clean SSOT path before any runtime or desktop behavior changes begin.

### What was not changed
- Runtime code was not changed.
- Desktop shell code was not changed.
- Tests were not changed.
- Module documents, tech schemas, and  1_MASTER/DECISIONS.md were not changed.

### Recommended next step
Read the active T-115 source-of-truth set and implement the bounded Partial Close slice.

## 2026-04-05 - T-115 Partial Close Slice

### Goal
Implement one bounded partial-close slice so the current desktop-first/local-first product can support accepted active-trade volume reduction inside the one-trade replay workflow without turning the product into broader position management, richer risk automation, mentor logic, dashboard/media scope, mobile, sync, or new persistence.

### Files updated
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/CODEX_WORKLOG.md`
- `runtime_bootstrap/trading_loop.py`
- `runtime_bootstrap/journal_runtime.py`
- `runtime_bootstrap/review_projection.py`
- `desktop_shell/controller.py`
- `desktop_shell/control_surface.py`
- `desktop_shell/context_surface.py`
- `desktop_shell/tk_app.py`
- `desktop_shell/workflow_surface.py`
- `tests/test_replay_bootstrap.py`
- `tests/test_desktop_shell.py`

### What was done
- Added one bounded manual partial-close path in the trading loop so an active trade can close a requested positive sub-volume up to the current open volume while staying inside the same `TradeRecord` / `PositionRecord` / `ExecutionRecord` ownership model.
- Recorded dedicated partial-close execution trace, accumulated realised PnL on the closed portion, preserved the remaining active volume, and kept later manual full close plus protective close working on the remainder.
- Extended bounded desktop-facing projections and existing shell surfaces so partial-close availability, remaining/opened/closed volume, partially closed state, and current result/workflow guidance are visible without adding a new subsystem.
- Added coverage for partial-close execution, later full close, protective close after partial, restart recovery of partially closed state, and desktop-shell visibility/recovery.
- Synchronized operating docs from active `T-115` to completed `T-115`, with the next recommended move set to a bounded post-Partial-Close audit rather than another implementation lane by inertia.

### What was not changed
- `03_MODULES/*` was not changed.
- `04_TECH/*` was not changed.
- `01_MASTER/DECISIONS.md` was not changed.
- No broader position-management lane, ladders, preset fractions, add-on, trailing stop, break-even automation, mentor/dashboard/media/mobile/sync scope, or new persistence was introduced.

### Why this matters
The live one-trade replay loop no longer collapses active-trade management to all-or-nothing exits. The product now supports one accepted partial-close step inside the existing lifecycle while preserving conservative ownership, recovery, and existing desktop surfaces.

### Remaining gap after this step
- The strongest next bounded frontier still needs to be selected explicitly instead of continuing trade-management growth by inertia.

### Recommended next step
Run one bounded post-Partial-Close next-slice audit.

## 2026-04-05 - Post-T115 SSOT/doc sync

### Goal
Synchronize the operating-layer source-of-truth documents after `T-115 Partial Close` completion so the repository no longer presents Partial Close as the active implementation frontier.

### Files updated
- `00_INDEX.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/CODEX_WORKLOG.md`

### What was stale
- `00_INDEX.md` still described `Partial Close` as the current implementation focus even though the implementation had already been completed and other SSOT files had moved on to the post-implementation audit state.
- `05_CODEX/NEXT_TASK.md` still reflected the completed `T-115` implementation packet rather than the correct audit packet for the next repository step.

### What was synchronized
- Updated `00_INDEX.md` so the active module and current focus now point to the bounded post-Partial-Close audit/result state instead of an active Partial Close implementation lane.
- Reframed `05_CODEX/NEXT_TASK.md` away from the completed implementation packet and into the bounded audit/result state needed for the post-`T-115` operating layer.

### Why this mattered before the audit
Running the next-step audit on top of stale repository navigation would have left the project presenting `T-115` as both completed and still active. This pass restores one honest operating-layer story before the audit result is recorded.

### What was not changed
- Runtime code was not changed.
- Desktop shell code was not changed.
- Tests were not changed.
- Module documents, tech schemas, and `01_MASTER/DECISIONS.md` were not changed.

### Recommended next step
Run the bounded post-Partial-Close next-slice audit and record exactly one explicit result.

## 2026-04-05 - T-116 Post-Partial-Close Next-Slice Audit

### Goal
Run one bounded managerial/product audit after `T-115 Partial Close` to determine whether the current local desktop-first product has one clearly strongest next bounded implementation frontier, without drifting into broader position management, pending-order growth, protection automation, review backfill, cosmetic polish, mentor logic, dashboard/media scope, mobile, sync, or new persistence.

### Files updated
- `00_INDEX.md`
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/CODEX_WORKLOG.md`

### What was reviewed
- The current post-`T-115` product boundary in master, roadmap, scope, MVP, module, schema, and operating docs.
- Plausibly adjacent local desktop candidates after Partial Close.
- Whether any candidate strengthens the user-visible desktop training loop without hidden subsystem growth.

### Explicitly rejected weak candidates
- Broader position-management continuation such as add-on entry, richer scale-out, ladders, or preset close flows.
- Pending-order continuation such as expiry, OCO/bracket behavior, or richer orchestration.
- Protection-automation continuation such as trailing stop, break-even automation, or richer SL/TP editing history.
- Review/digest/evidence backfill.
- Cosmetic desktop polish.
- Mentor/dashboard/media/mobile/sync/new-persistence drift or any hidden architecture rewrite.

### Audit result
- No strong bounded next implementation slice is justified yet.
- No new implementation-facing frontier document was created because the audit did not justify activating one.
- The repository is synchronized to a post-audit state where `T-115 Partial Close` remains completed and no new active implementation frontier is selected.

### Why this matters
The project avoids sliding into the next coding lane by inertia. The operating layer now records a deliberate hold state instead of pretending that a weak adjacent candidate is strong enough to become the next local desktop frontier.

### What was not changed
- Runtime code was not changed.
- Desktop shell code was not changed.
- Tests were not changed.
- Module documents, tech schemas, and `01_MASTER/DECISIONS.md` were not changed.

### Recommended next step
Do not activate another implementation lane until a stronger bounded local desktop frontier is explicitly justified in a separate selection pass.

## 2026-04-05 - T-117 Desktop Workflow Validation / Friction Discovery Pass

### Goal
Run one bounded validation pass on the already implemented desktop-first/local-first workflow so the repository can identify real recurring product friction from realistic usage, instead of extending adjacent features by inertia.

### Files updated
- `00_INDEX.md`
- `01_MASTER/CURRENT_STATE.md`
- `05_CODEX/TASKS.md`
- `05_CODEX/NEXT_TASK.md`
- `05_CODEX/CODEX_WORKLOG.md`
- `05_CODEX/DESKTOP_TRANSITION_STATE_COHERENCE.md`

### Validation coverage
- Empty desktop start / readiness-to-action state
- Market entry into active trade without declared plan
- Active trade with initial protection
- Pending stop staging and cancellation
- Pending stop trigger into active trade
- Partial close while trade remains active
- Full note -> trade -> review -> finalization flow
- Restart recovery for partially closed active trade
- Closed trade with review still pending

### Real recurring friction found
- Transition-state language is not fully coherent across existing `trade`, `workflow`, `result`, `finalization`, `readiness`, and `pause-point` surfaces.
- Pending-entry and finalized/recovered states can force the user to reconcile contradictory or misleading status wording across surfaces before understanding the actual next step.
- Clean dataset states can still surface warned-dataset copy in finalization/readiness/pause-point reporting, which makes the product appear less trustworthy than the underlying facts warrant.

### Explicitly rejected weak candidates
- Cosmetic-only polish without repeated workflow break
- Learning-curve discomfort that does not create recurring continuity loss
- Adjacent feature inertia in position management, pending-order growth, protection automation, or review/evidence backfill
- Mentor/dashboard/media/mobile/sync/new-persistence drift
- Hidden architecture rewrite temptation

### Validation result
- The strongest recurring friction point is bounded desktop transition-state coherence.
- One future implementation-facing candidate is justified and recorded as `05_CODEX/DESKTOP_TRANSITION_STATE_COHERENCE.md`.
- No implementation work started in this pass; the repository is synchronized only to the validation result.

### What was not changed
- Runtime code was not changed.
- Desktop shell code was not changed.
- Tests were not changed.
- Module documents, tech schemas, and `01_MASTER/DECISIONS.md` were not changed.

### Recommended next step
If implementation resumes, activate one bounded `Desktop Transition-State Coherence` slice and keep it strictly inside existing workflow/result/finalization/readiness surfaces.

