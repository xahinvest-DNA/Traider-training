# Repository Settings

Last updated: 2026-07-10
Status: required repository administration baseline

## Purpose

This file records GitHub settings that cannot be enforced by repository code alone. Apply them in GitHub after the engineering-baseline pull request is merged.

## Main branch protection

Create a ruleset for `main` with:

- require a pull request before merging;
- require at least one approval when another reviewer is available;
- dismiss stale approvals after new commits;
- require all conversations to be resolved;
- require branches to be up to date before merging;
- require status checks:
  - `Runtime core / Ubuntu / Python 3.11`;
  - `Full suite / Windows / Python 3.11`;
- block force pushes;
- block branch deletion;
- include administrators unless an emergency override is explicitly needed.

## Merge policy

Recommended:

- enable squash merge;
- make squash the normal merge method;
- disable merge commits after confirming no existing workflow depends on them;
- optionally disable rebase merge for a single consistent history;
- automatically delete head branches after merge.

One bounded task should become one commit on `main`.

## Security and maintenance

Enable where available:

- dependency graph;
- Dependabot alerts;
- secret scanning;
- push protection;
- private vulnerability reporting;
- GitHub Actions read permissions by default, with per-workflow write permissions only when required.

## Codex integration

Repository-native instructions, skills, and hooks do not require an API key.

The optional `openai/codex-action@v1` workflow should be enabled only after:

1. adding `OPENAI_API_KEY` as an Actions secret;
2. approving the exact review prompt;
3. limiting workflow permissions to read-only contents and PR comment access;
4. confirming expected usage and cost;
5. keeping normal CI as the primary required gate.

Codex review must supplement, not replace, tests and human/ChatGPT review.

## Local Codex setup

After pulling the baseline:

1. open the repository in Codex;
2. inspect `/hooks`;
3. review and trust `.codex/hooks.json` and both hook scripts;
4. verify the repository skills appear under Skills;
5. restart Codex if newly added skills are not visible;
6. run a read-only orientation task before the first coding packet.

## Administration note

These settings live in GitHub administration and are not automatically applied by committing this file. Record any deviation here so repository expectations and actual settings do not drift.