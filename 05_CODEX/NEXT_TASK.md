# NEXT TASK

Last updated: 2026-04-05
Status: completed
Task ID: T-120
Task type: diagnostic

## Goal
Run one bounded diagnostic pass on the current desktop shell launch so the repository can determine why real runs can open into a practically non-tradable state with most trade controls disabled, and distinguish launch misuse from persisted session state, controller/projection mismatch, gating logic bug, or a real startup-state product defect.

## Result
`T-120 Desktop Shell Startup-State Diagnostic Pass` is completed. The strongest diagnosis is a real product-facing startup-state defect: the default launch recovers a persisted generic market-entry `EntryRequested` state from `desktop_shell/.local_state`, control gating correctly blocks new entry actions because `entry_pending_present` is true, but existing trade/workflow/finalization surfaces still tell an idle/no-trade story instead of a staged-entry story.

## Diagnostic coverage
1. Default launch config and default storage path.
2. Actual recovered state under `desktop_shell/.local_state/local_runtime_state.json`.
3. Controller bootstrap and workspace view on the recovered default state.
4. Trade-control gating in `desktop_shell/control_surface.py`.
5. Journal finalization gating in `runtime_bootstrap/journal_runtime.py`.
6. Transition/workflow coherence for recovered startup state.
7. Fresh clean storage bootstrap for comparison.
8. Recovered-state replay advance to confirm the stuck-looking startup is still a live lifecycle state rather than a dead shell.

## Root cause assessment
- Wrong launch mode / wrong startup path: rejected
- Dataset quality issue: rejected
- Controller/projection mismatch: partially involved but not the strongest root cause
- Gating logic bug: strongest
- Broader startup UX problem: secondary consequence, not the primary root cause

## Evidence
1. Default launch always uses `desktop_shell/.local_state` via `desktop_shell/launch.py`, so prior local session state is recovered automatically when `local_runtime_state.json` exists.
2. The observed persisted state contains:
   - `lifecycle_state: EntryRequested`
   - `pending_order_id: order-0001`
   - one placed `BuyMarket` order
   - no active trade yet
3. `desktop_shell/control_surface.py` disables `Buy/Sell/BuyStop/SellStop` whenever `entry_pending_present` is true.
4. `runtime_bootstrap/journal_runtime.py` treats `pending_order_id` as an active finalization blocker.
5. `desktop_shell/transition_state.py` only treats pending stop entry as staged entry, not generic market-entry pending state.
6. In the observed startup state, desktop surfaces therefore disagree:
   - control availability blocks new entries
   - finalization sees active blocking state
   - trade context reports idle/no-trade
   - workflow guidance says to open a trade
7. A clean storage bootstrap is tradable immediately with `Buy/Sell/BuyStop/SellStop` active.
8. The recovered default state becomes active-trade state after replay advances, confirming this is not a dead dataset or wrong mode.

## Practical user answer
- Yes, the trainer can be used right now in intended `training` mode.
- It is immediately tradable when the shell boots from a fresh local storage state, or when the recovered session is already in a genuinely idle state.
- The observed run landed outside that condition because default launch recovered an old local session that already had a pending market entry at tick 0.
- Trading actions looked unavailable because new entry actions were correctly blocked by that pending order, but existing desktop surfaces failed to explain that a staged generic entry was already in progress.

## Strongest conclusion
This is primarily a product bug / startup-state defect worth fixing, not merely a wrong launch or user-usage issue.

## Constraints kept
- no runtime files changed
- no desktop-shell files changed
- no tests changed
- `03_MODULES/*` not changed
- `04_TECH/*` not changed
- `01_MASTER/DECISIONS.md` not changed

## Acceptance criteria status
- The current non-tradable startup behavior is investigated through the real launch/gating path: completed
- The result identifies the strongest root cause with concrete evidence: completed
- The result clearly distinguishes expected behavior, poor UX, and actual bug if applicable: completed
- The result answers the practical question of why trading actions are unavailable in the observed run: completed
- The pass ends with exactly one strongest conclusion: completed
- No unrelated scope drift is introduced: completed
- `CURRENT_STATE.md`, `TASKS.md`, `NEXT_TASK.md`, and `CODEX_WORKLOG.md` are synchronized to the diagnostic result: completed

## Recommended next step
Implement one bounded `Desktop Startup Pending-Entry Actionability` fix using `05_CODEX/DESKTOP_STARTUP_PENDING_ENTRY_ACTIONABILITY.md`.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
