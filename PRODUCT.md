# Product

## Register

product

## Users

GAIA is used by a capstone demo operator, Human QA participants, and professors or visitors watching the result on a large monitor. The operator needs to select one prepared mission, start a Human vs GAIA run, keep the desktop control app docked beside the test browser, and recover quickly if a timer or record needs cleanup. Participants need a clear human-input page with the exact scenario, a low-friction submission flow, and raffle contact entry that does not distract from QA evidence. Viewers need to understand who won, why, and what evidence supports the result without reading raw debug output.

## Product Purpose

GAIA turns goal-driven browser QA into a live, inspectable Human vs GAIA demonstration. The desktop app coordinates benchmark selection, run state, logs, live screenshots, and web-board controls; the Vercel battle board records Human and GAIA timings, success reasons, screenshot evidence, and winner summaries for the fixed `battle-live` session. Success means the demo feels operational, honest, and technically credible under presentation pressure.

## Brand Personality

Reliable, fast, and field-ready. The interface should feel like a serious QA control surface: calm enough for an operator to trust, direct enough for a participant to use without explanation, and vivid enough that a professor can read the competition at a glance.

## Anti-references

Avoid mock data, local/debug internals, token or environment-variable noise, obvious "this is just a demo" placeholder language, redundant instructions, toy-like game UI, generic AI SaaS landing-page patterns, oversized decorative cards, and raw error severity that looks scarier than the actual state.

## Design Principles

1. Show the run state before decoration. Start readiness, running state, evidence arrival, elapsed time, and winner status must be visible without scrolling when possible.
2. Keep the operator in flow. The right-docked desktop app must support quick site/case selection, start, stop, reset, evidence review, and log scanning in a narrow vertical window.
3. Make evidence tangible. Screenshots and success reasons should be target-scoped, readable, and easy to enlarge; a single anonymous full-page image is not enough when the claim is specific.
4. Hide implementation seams from the audience. Debug URLs, storage modes, tokens, raw trace noise, and local paths belong in logs or settings, not in the default presentation surface.
5. Prefer earned familiarity. Standard buttons, tabs, fields, status chips, and dense dashboards are acceptable; novelty should support the live competition rather than invent new controls.

## Accessibility & Inclusion

Desktop and large-monitor readability are the priority. Text contrast should meet WCAG AA, Korean labels must be explicit, primary actions need clear focus states, and color-coded success/failure states must also use text or icons. Motion should communicate state only and respect reduced-motion settings. Mobile is secondary for the capstone demo flow.
