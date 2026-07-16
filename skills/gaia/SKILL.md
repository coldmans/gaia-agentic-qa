---
name: "gaia-agentic-qa"
description: "Use when the user wants to run, benchmark, or diagnose GAIA's evidence-driven browser QA agent from a natural-language web goal."
---

# GAIA Agentic QA

Use the repository's CLI and benchmark harness. Do not replace the requested
OAuth flow with an API-key-first setup.

## Prerequisites

Check Python, Node.js, and npm:

```bash
python --version
node --version
npm --version
```

Install the needed extras from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[gui]"
```

## Authentication

Prefer the existing Codex OAuth session:

```bash
gaia auth login --provider openai --method oauth
```

Use manual API-key authentication only when the user explicitly asks for it.
Never print access or refresh tokens.

## Run one goal

```bash
gaia chat --gui --url https://example.com
```

## Run a benchmark

```bash
python scripts/run_goal_benchmark.py \
  --suite gaia/tests/scenarios/hacker_news_public_suite.json \
  --provider openai \
  --model gpt-5.5
```

Read `summary.json`, `results.json`, and the captured reason codes before
claiming success. Treat CAPTCHA, OTP, and account gates as blocked user action.

## Debugging order

1. Confirm the latest role-tree ref exists.
2. Separate actor choice from browser actionability failure.
3. Inspect state-change evidence and reason codes.
4. Compare actor and judge latency before optimizing.
5. Re-run the same scenario and isolation policy.

Do not add site-specific success heuristics to make one benchmark green.
