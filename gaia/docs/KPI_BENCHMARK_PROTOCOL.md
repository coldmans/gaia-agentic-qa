# KPI benchmark protocol

GAIA 성능 주장은 한 번의 성공 로그가 아니라 동일 조건의 baseline/candidate artifact로 검증한다.

## Suites

| Suite | Path | Purpose |
| --- | --- | --- |
| Public read-only | `gaia/tests/scenarios/boj_readonly_suite.json` | 공개 페이지 탐색과 ref 기반 실행 baseline |
| External diversity | `gaia/tests/scenarios/external_public_manifest.json` | 서로 다른 공개 사이트에서의 일반화 확인 |
| Authenticated service | `gaia/tests/scenarios/inuu_service_suite.json` | 로그인, 검색, 필터, 상태 변경 |
| Recovery stress | `gaia/tests/scenarios/recovery_stress_suite.json` | stale ref, overlay, resnapshot, retry 복구 |

인증 suite는 `GAIA_TEST_USERNAME`과 `GAIA_TEST_PASSWORD`를 환경변수로 주입한다. CAPTCHA,
로그인 gate, bot wall처럼 사람이 필요한 상태는 성공이나 일반 실패로 위장하지 않고
`BLOCKED_USER_ACTION`으로 분리한다.

## Metrics

- `scenario_success_rate`: 전체 실행 중 `SUCCESS` 비율
- `primary_success_rate`: 사용자 개입이 필요한 blocked 실행을 제외한 성공률
- `reproducibility_rate`: 같은 시나리오를 반복했을 때 모두 성공한 비율
- `progress_stop_failure_rate`: timeout, stuck, no-progress 종료 비율
- `self_recovery_rate`: recovery event가 발생한 실행 중 최종 성공 비율
- `intervention_rate`: `BLOCKED_USER_ACTION` 비율
- `actor_llm_ms_avg`, `judge_llm_ms_avg`: 행동 선택과 완료 검증의 평균 LLM 지연
- `actor_prompt_chars_total`, `judge_prompt_chars_total`: 단계별 입력 크기 비교용 문자 수

문자 수는 토큰 수의 대체 지표다. 모델별 토크나이저 비용을 주장할 때는 별도 토큰 계측을
사용한다.

## Run

단일 suite:

```bash
GAIA_LLM_MODEL=gpt-5.5 GAIA_RAIL_ENABLED=0 \
python scripts/run_goal_benchmark.py \
  --suite gaia/tests/scenarios/boj_readonly_suite.json \
  --repeats 2 \
  --timeout-cap 120 \
  --session-prefix boj-readonly
```

KPI pack:

```bash
GAIA_LLM_MODEL=gpt-5.5 GAIA_RAIL_ENABLED=0 \
python scripts/run_kpi_benchmark_pack.py \
  --suite gaia/tests/scenarios/boj_readonly_suite.json \
  --suite gaia/tests/scenarios/recovery_stress_suite.json \
  --repeats 2 \
  --timeout-cap 180 \
  --session-prefix gaia-kpi
```

외부 공개 manifest:

```bash
GAIA_LLM_MODEL=gpt-5.5 GAIA_RAIL_ENABLED=0 \
python scripts/run_kpi_benchmark_pack.py \
  --suite-manifest gaia/tests/scenarios/external_public_manifest.json \
  --repeats 1 \
  --timeout-cap 600 \
  --session-prefix external-public
```

## Compare

같은 모델, reasoning effort, runtime isolation, suite, timeout으로 baseline과 candidate를 각각
실행한 뒤 비교한다.

```bash
python scripts/compare_benchmark_runs.py \
  --baseline artifacts/baseline \
  --candidate artifacts/candidate \
  --output-dir artifacts/comparison \
  --fail-on-regression
```

성능 개선으로 채택하려면 성공률이 떨어지지 않고, 진행 멈춤이 늘지 않으며, 측정 대상 지연이나
입력 크기가 유의미하게 감소해야 한다. 외부 사이트 상태가 달라진 실행은 같은 조건 비교로
간주하지 않는다.
