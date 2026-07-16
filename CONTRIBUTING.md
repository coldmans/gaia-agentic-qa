# Contributing

Use a focused branch and keep behavior changes tied to a reproducible failure
or benchmark contract.

```bash
python -m pytest gaia/tests/unit -q
python -m compileall -q gaia
npm --prefix gaia-battle-web run lint
npm --prefix gaia-battle-web run build
```

For performance work, compare the same suite and runtime policy before and
after the change. Do not trade evidence quality for a faster headline.
