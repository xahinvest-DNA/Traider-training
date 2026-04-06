# NEXT TASK

Last updated: 2026-04-06
Status: ready
Task ID: T-131
Task type: planning

## Goal
Run one bounded `Post-Acceptance Desktop Frontier Selection` pass so the repository can choose the next strongest product-facing frontier now that the assembled desktop trainer workspace has passed acceptance as a coherent loop.

## Why this is next
`T-130` confirmed that the current desktop workspace is accepted as a coherent `dataset -> chart -> replay -> trade -> close -> review` trainer loop, so the next step should be choosing the next frontier deliberately rather than continuing incremental UI work by momentum.

## What should change
1. Identify the strongest next product-facing frontier from the accepted desktop workspace baseline.
2. Reject weaker follow-ups that are cosmetic, platform-like, or validation-complete.
3. Produce one bounded recommendation for the next coding or planning slice.

## What must stay unchanged
- no new implementation inside the selection pass
- no chart/startup/trader-panel/review-subsystem rewrite
- no dashboard/mobile/sync/mentor/platform scope

## Recommended validation
Use the accepted desktop workspace boundary plus current state/docs to compare candidate next frontiers and select one bounded next step only.

## Required handoff format
Use `05_CODEX/HANDOFF_TEMPLATE.md` exactly.
