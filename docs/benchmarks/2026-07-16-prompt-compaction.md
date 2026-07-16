# Prompt compaction A/B check

Date: 2026-07-16

This check isolates the default raw role-tree compaction added to the actor
prompt. It is deliberately small and should not be interpreted as a general
success-rate or latency claim.

## Setup

- Scenario: `HN_001_TOP_STORY_TITLE`
- Provider/model: OpenAI, GPT-5.5, normal mode
- Browser policy: warm process, cold scenario state
- Repeats: 2 per variant
- Result: 2/2 success in both variants

## Results

| Metric | Full role tree | Compacted role tree | Delta |
| --- | ---: | ---: | ---: |
| Mean actor prompt characters | 77,520 | 48,304 | -37.7% |
| Mean actor LLM latency | 15.816s | 13.368s | -15.5% |
| Mean judge LLM latency | 6.247s | 7.714s | +23.5% |
| Mean end-to-end duration | 27.52s | 26.84s | -2.5% |

The prompt reduction is deterministic for these snapshots. Latency is noisy at
this sample size: the judge became slower even though its prompt path was
unchanged. The accepted conclusion is therefore limited to a material actor
prompt reduction with no observed success regression in this check.

The default budget is controlled by
`GAIA_OPENCLAW_RAW_TREE_CHAR_LIMIT=36000`; set it to `0` to disable compaction.
