# Desktop Shell Instructions

These rules extend the root `AGENTS.md` for files under `desktop_shell/`.

## Ownership

- The desktop shell is a thin command and projection consumer.
- Do not calculate market truth, execution outcomes, PnL, indicators, or journal truth inside widgets.
- Add a runtime/domain capability first, then expose it through the controller and projections.
- Do not read raw datasets or persistence files directly from the UI.

## UX boundary

- Keep the primary workspace chart-first.
- Keep replay controls, trader actions, active trade context, and the review entry legible without turning the shell into a broker terminal.
- Prefer one clear next action over additional explanatory labels.
- Preserve Training, Exam, and Review mode restrictions in visible control availability.

## Validation

- Controller and formatting helpers require headless tests.
- Changes to Tk layout, launch, focus, keyboard handling, or drag interaction also require a manual Windows/Tk smoke check.
- Never classify a UI snapshot as product acceptance solely from constant status strings.