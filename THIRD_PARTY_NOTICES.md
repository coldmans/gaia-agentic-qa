# Third-party notices

GAIA contains a pinned browser-control runtime bundle derived from OpenClaw
2026.3.26. The bundled code remains under its original MIT license, reproduced
at `gaia/_runtime/openclaw/LICENSE`.

The runtime's npm lockfile also records transitive licenses for Playwright,
Sharp, Ajv, and their platform packages. Run `npm ci --omit=dev` inside
`gaia/_runtime/openclaw` to materialize those dependencies locally.

GAIA's original work is the goal-driven orchestration, role/ref action
contract integration, evidence ledger, recovery policies, independent judge,
benchmark harness, desktop operator experience, and live comparison board.
