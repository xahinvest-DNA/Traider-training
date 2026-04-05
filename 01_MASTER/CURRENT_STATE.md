# Current State

Last updated: 2026-04-05
Current stage: bounded desktop workflow validation is completed after the post-Partial-Close audit; one recurring transition-state coherence friction is now the strongest validated later slice candidate
Active module: `T-117 Desktop Workflow Validation / Friction Discovery Pass` is completed, with `Desktop Transition-State Coherence` identified as the strongest justified later slice candidate
Active question: whether to activate the bounded transition-state coherence candidate as the next coding pass without letting the repository drift into broader feature growth

## Where the project is now

The project is in the sequential implementation stage of the first working prototype through narrow vertical slices built on top of already accepted master, module, and tech documents.

At this point:

- replay bootstrap is implemented in `runtime_bootstrap/`;
- the minimal executable trading loop is implemented for `BuyMarket/SellMarket -> post-tick fill -> active Position -> manual close -> trade trace`;
- the local-first `TrainingSession` / `PreTradeNote` / `PostTradeReview` loop is implemented with local persistence and restart recovery;
- minimum Bill Williams review hooks are implemented as a bounded vocabulary layer;
- manual `BehavioralFlag` / `RuleViolation` capture is implemented inside the local review flow;
- derived review output is implemented as a derive-on-read layer over persisted trade and journal facts;
- minimum session result metrics are implemented as a bounded derive-on-read extension;
- session timeline projection is implemented as a one-session derived chronology;
- chart snapshot references are implemented as bounded context refs for note/review;
- snapshot timeline exposure is implemented inside the current local session timeline;
- snapshot-aware review output is implemented inside derived trade review results without a new persistence layer;
- explicit local session finalization is implemented with close-state projection, active-trade/running-replay blockers, pending-review guardrails, and restart recovery;
- compact session-level review summary is implemented as a bounded derive-on-read projection over finalization state, review completion, flags/violations, and snapshot-aware outputs;
- the bounded MVP acceptance pass is implemented and covered by the end-to-end scenario `dataset -> replay -> one trade -> review -> summary -> finalization -> restart recovery`;
- the implementation-facing boundary and the first coding slice for the desktop shell are implemented in `desktop_shell/` over accepted runtime projections;
- bounded chart/replay refinement is implemented in the desktop shell through lightweight chart helpers and Tk canvas rendering over current replay projections;
- bounded session/trade context refinement is implemented in the desktop shell through compact readable context/result blocks over trading and journal projections;
- bounded notes/review authoring refinement is implemented in the desktop shell through clearer sections, multi-line content entry, bounded BW vocabulary selectors, and authoring status/hints over the current journal projection;
- bounded current-session history/result refinement is implemented in the desktop shell through compact history status, latest trade result highlights, and current-session timeline preview over existing derived projections;
- bounded workflow guidance/action feedback refinement is implemented in the desktop shell through compact next-step guidance, finalization blocker visibility, recent action feedback, and explicit Force Finalize access over existing runtime contracts;
- bounded desktop shell layout/usability polish is implemented through projection-driven control availability hints and button enable/disable behavior over the current single-session workflow;
- bounded desktop MVP acceptance / smoke pass is implemented through an explicit end-to-end desktop shell scenario over replay, trade, review, result/history, finalization, and restart recovery;
- bounded desktop runtime/application launch path is implemented through launch helpers, `python -m desktop_shell`, and `run_desktop_shell.py` over the current accepted shell;
- bounded desktop handoff/readiness is implemented through readiness snapshot helpers and non-GUI readiness reports over the current accepted shell/controller;
- bounded MVP consolidation / pause point is implemented through explicit non-GUI MVP freeze-state snapshots and reports over the current accepted desktop shell;
- the first post-MVP direction is explicitly selected as `Bill Williams Method Depth`, with mentor/mobile/sync/dashboard/platform work still deferred;
- the first Bill Williams method-depth boundary is explicitly fixed as a review-depth-first slice centered on richer structured `PostTradeReview` method facets, with automation/mentor/dashboard/mobile/sync work still deferred;
- richer structured Bill Williams `PostTradeReview` method facets are implemented with validation, persistence, derived review output, desktop authoring support, and restart recovery;
- derive-on-read Bill Williams declared-vs-reviewed intent delta is implemented across review output, session summary, and desktop result/history/context surfaces;
- derive-on-read Bill Williams review completeness is implemented across review output, session summary, and desktop result/history/context surfaces, including missing-part exposure;
- derive-on-read Bill Williams review prompts are implemented in desktop workflow guidance from existing intent-delta and review-completeness state;
- derive-on-read Bill Williams session-level field coverage is implemented across review output, session summary, and desktop summary/history surfaces;
- derive-on-read Bill Williams review sequence guidance is implemented across review output, session summary, and desktop workflow/result/history surfaces;
- derive-on-read Bill Williams review weak spots are implemented across review output, session summary, and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review progress is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review momentum is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review stability is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review swings are implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review floor is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review ceiling is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review band is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review headroom is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review pressure is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review target is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review focus is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review cue is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review badge is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review pill is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review chip is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review tag is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review token is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review marker is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review glyph is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review sigil is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review seal is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review crest is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review emblem is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review insignia is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review standard is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review banner is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review pennant is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review streamer is implemented across session summary and desktop summary/history/workflow surfaces;
- dataset-quality finalization link is implemented across session finalization projection, readiness/pause-point reports, and desktop finalization/workflow surfaces, including finalized-session blocker visibility;
- dataset-quality restart-recovery note is implemented across recovered finalized-session journal projection, readiness/pause-point reports, and desktop workflow surfaces;
- dataset-quality recovery feedback is implemented across recovered finalized-session desktop action feedback and workflow guidance surfaces;
- dataset-quality recovery acknowledgment is implemented as one compact persisted session-scoped state plus explicit desktop action so a reopened finalized warned session can mark recovery context as seen and stop repeating the active reminder;
- desktop chart snapshot authoring is implemented through one bounded controller path plus explicit desktop note/review authoring actions so existing local ChartSnapshot refs can now be created and linked from the shell without screenshot automation, gallery UX, media validation, or sync scope;
- the Variant 2 operating layer is now present through `01_MASTER/SSOT_MAP.md`, `05_CODEX/NEXT_TASK.md`, `05_CODEX/IMPLEMENTATION_RULES.md`, `05_CODEX/HANDOFF_TEMPLATE.md`, and `05_CODEX/CODEX_WORKLOG.md`, so the repository can act as the live operating system for bounded Codex passes instead of depending on chat-only continuity;
- derive-on-read Bill Williams review rule context is implemented across current trade review output, session summary, and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review discipline cue is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review discipline badge is implemented across session summary and desktop summary/history/workflow surfaces;
- derive-on-read Bill Williams review discipline token is implemented across current trade review output, session summary, and desktop context/history/workflow surfaces;
- derive-on-read Bill Williams review discipline marker is implemented across current trade review output, session summary, and desktop context/history/workflow surfaces;
- derive-on-read Bill Williams review discipline glyph is implemented across current trade review output, session summary, and desktop context/history/workflow surfaces;
- derive-on-read Bill Williams review discipline sigil is implemented across current trade review output, session summary, and desktop context/history/workflow surfaces;
- derive-on-read Bill Williams review discipline seal is implemented across current trade review output, session summary, and desktop context/history/workflow surfaces;
- derive-on-read Bill Williams review discipline crest is implemented across current trade review output, session summary, and desktop context/history/workflow surfaces;
- derive-on-read Bill Williams review discipline emblem is implemented across current trade review output, session summary, and desktop context/history/workflow surfaces;
- derive-on-read Bill Williams review discipline reason is implemented across current trade review output, session summary, and desktop context/history/workflow surfaces;
- derive-on-read Bill Williams review evidence status is implemented across current trade review output, session review summary, and desktop result/history/context/workflow surfaces using only existing review facts and linked snapshot refs, with restart recovery covered from existing local facts;
- derive-on-read Bill Williams review evidence follow-up is implemented across current trade review output, session review summary, and desktop result/history/context/workflow surfaces so missing or partial chart evidence now maps to one compact next-step cue rebuilt from existing local facts after restart;
- derive-on-read Current Trade Review Digest is implemented across current trade review output, session review summary, and desktop result/history/context/workflow surfaces so the latest/current closed trade now exposes one compact takeaway headline, primary gap, and next step rebuilt from existing local facts after restart;
- the bounded post-digest audit rejects further digest layering, evidence layering, cosmetic polish, workflow-engine-style quick-action orchestration, dashboard/media expansion, mentor logic, and mobile/sync/new-persistence drift as the wrong current frontier, and records no strong bounded next implementation slice inside the current review loop;
- the broader post-review-loop audit rejects further review-derived layering, replay garnish, import hardening as the main next frontier, add-on/partial-close expansion, and replay-mode polishing as weaker candidates, and selects Initial Trade Protection as the strongest next local desktop product lane because it improves active trade discipline inside the core training loop;
- bounded Initial Trade Protection is implemented across runtime trading contracts, desktop trading/context/result surfaces, and restart recovery so the current one-trade replay workflow now supports optional initial `stopLoss` / `takeProfit` without creating a broader risk engine, new persistence, or a new workflow owner;
- the bounded post-Initial-Trade-Protection audit rejects further protection-lane continuation such as trailing stops, break-even automation, SL/TP edit history, pending-order orchestration, add-on or partial-close expansion, review-loop backfill, cosmetic polish, and mentor/dashboard/media/mobile/sync drift, and selects Current Trade Plan Context as the strongest next local desktop slice because the live trade loop still loses the user's own declared setup/thesis/risk plan after entry;
- bounded Current Trade Plan Context is implemented as a derive-on-read layer over linked `PreTradeNote` and trade facts, and is surfaced only through existing desktop `context`, `result`, and `workflow` projections so active/current and just-closed trades keep declared setup/thesis/risk-plan facts visible without creating a new owner of truth, persisted summary, mentor layer, or workflow engine;
- the bounded post-Current-Trade-Plan-Context audit rejects further plan management, plan scoring, richer note workflow, checklist or acknowledgment logic, protection-lane continuation, review/digest/evidence backfill, cosmetic polish, mentor/dashboard/media/mobile/sync drift, and selects Pending Stop Entry as the strongest next local desktop slice because the live trade loop still lacks the accepted trigger-based entry path already implied by the trading and desktop contracts;
- bounded Pending Stop Entry is implemented across runtime trading contracts, desktop trading/context/workflow surfaces, and restart recovery so the one-trade replay workflow now supports one visible `BuyStop` / `SellStop` trigger-based entry path plus minimal manual cancel before trigger, without creating pending-order orchestration, multiple pending orders, expiry logic, or new persistence;
- bounded Partial Close is implemented across runtime trading contracts, desktop trading/context/result/workflow surfaces, and restart recovery so the one-trade replay workflow now supports accepted active-trade volume reduction inside the same trade lifecycle without creating a broader position-management subsystem, richer risk automation, or new persistence;
- the bounded post-Pending-Stop-Entry audit rejects further pending-order management, protection-lane continuation, plan-management drift, review backfill, cosmetic polish, and mentor/dashboard/media/mobile/sync/new-persistence drift, and selects Partial Close as the strongest next bounded local desktop slice because the live trade loop still lacks accepted active-trade volume reduction inside the existing one-trade lifecycle;
- a bounded raw-dataset import path is implemented in `runtime_bootstrap/import_pipeline.py` for CSV/TSV/JSON tick files into normalized local dataset artifacts with explicit warning counts/previews plus hard rejection for non-finite or inverted-spread ticks;
- desktop launch now accepts raw dataset files, auto-imports them into local normalized artifacts before controller bootstrap, auto-relaunches through the ASCII-path Tk-capable interpreter `C:\Python311\python.exe` when the current Python cannot initialize Tk/Tcl, and still falls back to a non-GUI readiness report if no working Tk runtime is available;
- compact dataset-quality status and raw-import warning previews are now surfaced in replay headers and non-GUI readiness reports without adding new persistence or provider-management layers;
- compact dataset-quality context is now propagated through trading and journal desktop projections, then surfaced inside trade context, latest result, review summary, and workflow guidance for warned datasets;
- one compact review-facing dataset-quality link is now derived from warned execution context and surfaced through current trade review output, session review summary, result/history surfaces, and workflow guidance;
- the symbolic review-discipline naming chain is intentionally paused at `review_discipline_emblem`, with `review_discipline_insignia` deferred after realignment in favor of a more product-meaningful next slice;
- `tests/test_replay_bootstrap.py` and `tests/test_desktop_shell.py` cover the runtime core, MVP acceptance scenario, desktop shell bootstrap, chart/context/authoring/history/workflow/control helper logic, desktop shell smoke acceptance, launch-path helpers/entrypoints, readiness helpers/reports, MVP pause-point reports, and desktop-shell-level recovery flow.

## Accepted boundaries

- The project is run as a single system of documents.
- Desktop is the main bounded operating surface.
- Mobile remains a later review/view layer.
- The product core is replay + manual trading + local journal.
- `04_TECH/DATA_SCHEMA.md` remains the source of truth for trade persistence.
- `04_TECH/JOURNAL_SCHEMA.md` remains the source of truth for session/journal persistence.
- `03_MODULES/JOURNAL_ANALYTICS.md` keeps analytics derive-on-read by default.
- `TrainingSession` is the primary session entity; a separate `JournalSession` is not introduced in v1.
- Trading engine v1 stays post-tick, single-lifecycle, and conservative on ambiguity.
- The minimal executable trading loop must not silently expand into new trading logic, a pending-order platform, or replay redesign.
- The local-first journal loop must not silently expand into mentor, mobile, sync, or advanced analytics.
- Bill Williams hooks must not silently turn into auto-classification, a signal engine, or a scoring layer.
- Manual `BehavioralFlag` / `RuleViolation` persistence must not silently turn into derived detection or a dashboard subsystem.
- Derived review output remains read-only and must not turn into a persisted analytics cache or `SessionSummary`.
- Session result metrics remain a bounded derive-on-read extension and must not silently grow into a full analytics subsystem.
- Session timeline projection remains a one-session derived read model and must not turn into a persisted timeline cache or multi-session history shell.
- Chart snapshot references remain bounded context refs and must not silently grow into screenshot automation, gallery, sync, or a media pipeline.
- Snapshot timeline exposure remains a bounded derived extension and must not silently grow into gallery, preview rendering, media cache, or annotation workspace.
- Snapshot-aware review output remains a bounded derive-on-read extension and must not silently grow into gallery, preview rendering, media validation, or a persisted review summary layer.
- Session finalization remains a bounded one-session close-state workflow and must not silently expand into multi-session archive, reopen workflow, dashboard layer, or sync-aware finalization orchestration.
- Compact session review summary remains a derived-only current-session projection and must not silently expand into a dashboard subsystem, persisted summary cache, or multi-session session cards.
- MVP acceptance pass validates the current local-first runtime as the first working prototype boundary and must not be used as an excuse for feature growth under a hardening label.
- Desktop shell boundary and coding slices keep the UI as a projection consumer over the accepted runtime, not as a new owner of domain logic or persistence.
- Chart/context/authoring/history/workflow/control refinements, desktop smoke verification, launch-path helpers, readiness reports, and MVP pause-point reporting remain lightweight projection-driven layers and must not pull in rich authoring, a heavy UI platform, archive shell behavior, dashboard behavior, thick UI workflow state, or packaging/platform scope.
- Bill Williams review depth remains review-authored and vocabulary-backed first; it must not silently become a signal engine, mentor overlay system, analytics cache, or platform-expansion label.
- Structured review facets inside `PostTradeReview` must remain human-authored bounded method interpretation, not derived certainty or scoring.

## Open items

- The concrete tech stack for desktop, mobile, storage, and sync beyond the current Python bootstrap.
- Incomplete bar and checkpoint semantics, if they are needed in MVP.
- Whether stop loss should be a hard rule in v1.
- Whether pending stop orders need an explicit expiry policy in the first prototype.
- Whether a separate persisted history of `stopLoss/takeProfit` changes is needed.
- How deeply to canonize `First Wise Man` and other setup families into machine-checkable variants.
- Whether a later separate structured vocabulary is needed for Bill Williams context regime beyond Alligator/AO/Fractal basics.
- Whether a later mentor-grade taxonomy is needed over the current reference layer.
- Whether a separate media manifest schema is needed for `ChartSnapshot` artifacts.
- Whether a severity-weighted scoring model for `BehavioralFlag` and `RuleViolation` is needed in v1.
- How far any later trade-protection work should go beyond bounded initial `stopLoss` / `takeProfit` before it becomes risk-engine drift.
- How far any later plan-context follow-up should go beyond compact factual recall before it becomes plan-management, mentor/scoring, or workflow-engine drift.
- How far the bounded raw-dataset import slice should go beyond the current CSV/TSV/JSON path before a separate acceptance/hardening step is required.

## Next step

If implementation resumes, activate one bounded `Desktop Transition-State Coherence` slice so the current desktop loop stops forcing the user to reconcile inconsistent transition-state messages across existing surfaces.

## What must not be lost in a new chat

- The main project risk is context fragmentation between sessions.
- A new chat must rely on `CURRENT_STATE.md`, `DECISIONS.md`, `ROADMAP.md`, and the active Codex boundary document.
- Replay remains the architectural center of the product.
- Trade facts remain owned by `DATA_SCHEMA.md`; journal facts remain owned by `JOURNAL_SCHEMA.md`.
- Derived outputs, timelines, and metrics must not replace primary entities.
- `DERIVED_REVIEW_OUTPUT.md`, `SNAPSHOT_TIMELINE_EXPOSURE.md`, `SNAPSHOT_AWARE_REVIEW_OUTPUT.md`, `SESSION_FINALIZATION.md`, `SESSION_REVIEW_SUMMARY.md`, `MVP_ACCEPTANCE_PASS.md`, `DESKTOP_SHELL_IMPLEMENTATION.md`, `DESKTOP_CHART_REPLAY_REFINEMENT.md`, `DESKTOP_SESSION_TRADE_CONTEXT_REFINEMENT.md`, `DESKTOP_NOTES_REVIEW_AUTHORING_REFINEMENT.md`, `DESKTOP_CURRENT_SESSION_HISTORY_RESULT_REFINEMENT.md`, `DESKTOP_WORKFLOW_GUIDANCE_ACTION_FEEDBACK.md`, `DESKTOP_SHELL_LAYOUT_USABILITY_POLISH.md`, `DESKTOP_MVP_ACCEPTANCE_SMOKE_PASS.md`, `DESKTOP_LAUNCH_PATH.md`, `DESKTOP_HANDOFF_READINESS.md`, `MVP_PAUSE_POINT.md`, `FIRST_POST_MVP_DIRECTION.md`, `BILL_WILLIAMS_REVIEW_DEPTH.md`, `BILL_WILLIAMS_REVIEW_DELTA.md`, `BILL_WILLIAMS_REVIEW_COMPLETENESS.md`, `BILL_WILLIAMS_REVIEW_PROMPTS.md`, `BILL_WILLIAMS_REVIEW_COVERAGE.md`, `BILL_WILLIAMS_REVIEW_SEQUENCE.md`, `BILL_WILLIAMS_REVIEW_WEAK_SPOTS.md`, `BILL_WILLIAMS_REVIEW_PROGRESS.md`, `BILL_WILLIAMS_REVIEW_MOMENTUM.md`, `BILL_WILLIAMS_REVIEW_STABILITY.md`, `BILL_WILLIAMS_REVIEW_SWINGS.md`, `BILL_WILLIAMS_REVIEW_FLOOR.md`, `BILL_WILLIAMS_REVIEW_CEILING.md`, `BILL_WILLIAMS_REVIEW_BAND.md`, `BILL_WILLIAMS_REVIEW_HEADROOM.md`, `BILL_WILLIAMS_REVIEW_PRESSURE.md`, `BILL_WILLIAMS_REVIEW_TARGET.md`, `BILL_WILLIAMS_REVIEW_FOCUS.md`, `BILL_WILLIAMS_REVIEW_CUE.md`, `BILL_WILLIAMS_REVIEW_BADGE.md`, `BILL_WILLIAMS_REVIEW_PILL.md`, `BILL_WILLIAMS_REVIEW_CHIP.md`, `BILL_WILLIAMS_REVIEW_TAG.md`, `BILL_WILLIAMS_REVIEW_TOKEN.md`, `BILL_WILLIAMS_REVIEW_MARKER.md`, `BILL_WILLIAMS_REVIEW_GLYPH.md`, `BILL_WILLIAMS_REVIEW_SIGIL.md`, `BILL_WILLIAMS_REVIEW_SEAL.md`, `BILL_WILLIAMS_REVIEW_CREST.md`, `BILL_WILLIAMS_REVIEW_EMBLEM.md`, `BILL_WILLIAMS_REVIEW_INSIGNIA.md`, `BILL_WILLIAMS_REVIEW_STANDARD.md`, `BILL_WILLIAMS_REVIEW_BANNER.md`, `BILL_WILLIAMS_REVIEW_PENNANT.md`, `BILL_WILLIAMS_REVIEW_STREAMER.md`, `BILL_WILLIAMS_REVIEW_RIBBON.md`, `BILL_WILLIAMS_REVIEW_RULE_CONTEXT.md`, `BILL_WILLIAMS_REVIEW_DISCIPLINE_CUE.md`, `BILL_WILLIAMS_REVIEW_DISCIPLINE_BADGE.md`, `BILL_WILLIAMS_REVIEW_DISCIPLINE_TOKEN.md`, `BILL_WILLIAMS_REVIEW_DISCIPLINE_MARKER.md`, `BILL_WILLIAMS_REVIEW_DISCIPLINE_GLYPH.md`, `BILL_WILLIAMS_REVIEW_DISCIPLINE_SIGIL.md`, `BILL_WILLIAMS_REVIEW_DISCIPLINE_SEAL.md`, `BILL_WILLIAMS_REVIEW_DISCIPLINE_CREST.md`, `BILL_WILLIAMS_REVIEW_DISCIPLINE_EMBLEM.md`, and `BILL_WILLIAMS_REVIEW_DISCIPLINE_PAUSE_REALIGNMENT.md` already fix derive-on-read / bounded workflow boundaries; they must not silently expand into persisted cache, gallery, archive shell, dashboard subsystems, thick UI workflow state, signal-engine drift, packaging/platform scope, or broad later-phase drift.
- `desktop_shell/` already exists as a thin UI layer over accepted runtime projections; the next step must not turn it into a new domain layer or large UI platform.
- `INITIAL_TRADE_PROTECTION.md` now fixes the bounded live-trade protection contract; follow-up work must not silently turn that slice into a broader risk-management subsystem.
- `CURRENT_TRADE_PLAN_CONTEXT.md` now fixes the bounded live-trade plan-recall contract; follow-up work must not silently turn plan visibility into plan management, mentor scoring, note orchestration, or a new plan-summary owner.
- `PENDING_STOP_ENTRY.md` now fixes the next bounded live-trade frontier; follow-up work must not silently turn pending stop support into a broader pending-order orchestration or risk-management subsystem.
- Any step beyond the bounded local-first desktop workflow requires a separate Project Brain fixation.












