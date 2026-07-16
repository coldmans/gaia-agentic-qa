# Repository guide

Keep changes centered on GAIA's evidence-driven QA runtime.

1. Read `README.md` and the nearest relevant source before editing.
2. Preserve role/ref evidence and independent verification contracts.
3. Prefer removing duplicate fallback paths over adding another heuristic.
4. Keep generated artifacts, browser profiles, credentials, and build output out of Git.
5. Run focused tests first, then the full unit suite before publishing.

Core checks:

```bash
python -m pytest gaia/tests/unit -q
python -m compileall -q gaia
npm --prefix gaia-battle-web run lint
npm --prefix gaia-battle-web run build
```
