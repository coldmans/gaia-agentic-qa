# Benchmark methodology

Performance claims are valid only when the suite, model, profile policy, and
runtime isolation policy match.

## Baseline contract

- suite: GAIA vs Human 30-case read-only/mixed pack
- provider/model: OpenAI GPT-5.5
- isolation: warm browser process, cold scenario state
- result: 30/30 success
- average duration: 76.5 seconds
- progress-stop failures: 0
- human intervention: 0

This is the preserved capstone baseline from 2026-05-31. It is historical
evidence, not a current universal success-rate claim.

## Optimization loop

1. Run a representative six-case pack three times.
2. Compare success, median, p95, actor time, judge time, and prompt size.
3. Reject candidates that weaken completion evidence or increase progress stops.
4. Run the unchanged 30-case suite only after the small gate passes.

## Required output

Every run should retain:

- scenario status and duration;
- actor/judge LLM call count and milliseconds;
- actor/judge prompt character count;
- WAIT and inspect decision count;
- reason-code summary;
- recovery and blocked-user-action classification;
- runtime isolation and model metadata.

Generated results belong under `artifacts/` and stay out of Git. Publish only
sanitized summaries needed to substantiate a portfolio claim.
