# GAIA Portfolio Case Study

> Goal-oriented Autonomous Intelligence for Adaptive GUI Testing

## 1. One-liner

GAIA는 자연어 QA 목표를 받아 브라우저 화면을 의미 단위로 해석하고, 단계별 행동과 증거를 누적해 최종 성공 여부를 검증하는 AI 기반 GUI QA 자동화 런타임이다.

## 2. Project Snapshot

| 항목 | 내용 |
| --- | --- |
| 기간 | 2025-2026 Capstone Design |
| 역할 | 기획, AI QA 런타임 설계, 브라우저 자동화 디버깅, benchmark harness, PySide6 데스크톱 앱, Vercel/Supabase 웹 보드, 발표/시연 시스템 구축 |
| 핵심 기술 | Python, PySide6, Playwright/OpenClaw runtime, LLM orchestration, Next.js, Supabase Realtime, Vercel, Grafana/Pushgateway, pytest |
| 대표 산출물 | Goal-driven QA agent, Role Tree/ref action runtime, Multi-call Context Ledger, Human vs GAIA live battle board, desktop control app, benchmark artifacts |
| 최종 검증 | Python unit 718 passed, web lint/build passed, harness docs lint passed |

## 3. Problem

기존 QA의 큰 문제는 반복 작업과 비용이다. 웹 서비스가 조금만 바뀌어도 기존 자동화 스크립트는 깨지고, 사람이 직접 회귀 테스트를 반복하면 시간과 비용이 커진다.

이 프로젝트는 단순히 "브라우저를 대신 클릭하는 봇"을 만드는 것이 아니라, 다음 질문에 답하는 시스템을 만드는 데 집중했다.

- 사용자의 자연어 목표를 실행 가능한 QA 흐름으로 바꿀 수 있는가?
- 현재 화면에서 어떤 요소를 눌러야 하는지 안정적으로 판단할 수 있는가?
- LLM이 "성공했다"고 말했을 때, 실제로 성공했는지 검증할 수 있는가?
- 실패했을 때 단순 실패가 아니라 왜 실패했는지 evidence와 reason code로 남길 수 있는가?
- 시연/운영 환경에서 사람이 GAIA와 비교해볼 수 있는 실시간 보드를 만들 수 있는가?

## 4. What I Built

### 4.1 Goal-driven QA Runtime

사용자가 입력한 자연어 목표를 기반으로 GAIA가 현재 화면을 읽고, 다음 행동을 결정하고, 실행 결과를 기록하도록 만들었다.

핵심 흐름:

1. 자연어 목표 입력
2. Role Tree snapshot 수집
3. Actor LLM이 다음 action 결정
4. ref 기반 action 실행
5. action result, DOM 변화, screenshot, reason code 기록
6. Judge LLM이 목표 달성 여부 검증
7. benchmark artifact와 dashboard로 결과 저장

### 4.2 Role Tree + ref 기반 Action Contract

초기에는 selector나 좌표 기반 접근이 쉽게 깨질 수 있었다. 그래서 화면을 픽셀이나 CSS selector가 아니라 버튼, 링크, 입력창 같은 의미 단위로 해석하는 Role Tree 방식을 중심에 두었다.

예시:

```text
WebArea
  Navigation
    link "Menu"
    button "Search"
  Main
    heading "Apple Pencil"
    combobox "iPad model"
```

LLM은 임의의 CSS selector를 만드는 대신, 현재 snapshot에서 식별된 `ref`를 사용해 action을 요청한다.

```text
click(ref="e42")
fill(ref="e17", value="예비군")
```

이 구조 덕분에 "무엇을 눌렀는지"가 추적 가능해졌고, 실패했을 때도 stale ref, not actionable, pointer intercepted 같은 원인을 분리할 수 있었다.

### 4.3 Multi-call Context Ledger

LLM API를 여러 번 호출하면 이전 단계의 맥락이 끊기기 쉽다. 이를 막기 위해 하나의 QA 실행을 step별 ledger로 관리했다.

ledger에 남긴 정보:

- 직전 action
- action success/fail
- reason code
- state change 여부
- screenshot/ref 기록
- 수집된 text evidence
- judge 판정 결과

이 구조는 단순 로그가 아니라 다음 LLM 판단에 들어가는 실행 상태 메모리 역할을 한다.

### 4.4 Evidence-based Judge

초기에는 LLM이 "목표 달성"이라고 말해도 실제 화면이 그 상태인지 확신하기 어려웠다. 그래서 actor의 자기 보고를 그대로 믿지 않고, 별도 judge가 DOM, 화면 변화, 성공 indicator, screenshot evidence를 함께 검토하도록 했다.

판정 기준:

- 목표 문장과 현재 DOM이 일치하는가?
- 클릭 이후 의미 있는 state change가 있었는가?
- 성공을 나타내는 텍스트나 UI indicator가 있는가?
- 최종 screenshot이 사용자의 목표를 뒷받침하는가?
- 실패라면 자동화 한계인지, 사이트 차단인지, 모델 판단 오류인지 분리 가능한가?

### 4.5 Human vs GAIA Live Demo Platform

캡스톤 시연용으로 사람이 직접 QA를 수행하고, GAIA가 같은 미션을 수행한 결과를 웹 보드에서 비교하는 시스템을 만들었다.

구성:

- PySide6 데스크톱 앱: 운영자가 사이트/케이스 선택, GAIA 실행, 로그와 증거 확인
- Next.js web board: Human/GAIA 결과 비교, 승패, 실행 시간, 증거 이미지 표시
- Human input page: 참가자 이름, 선택 전화번호, 성공 이유, 증거 screenshot 제출
- Supabase Realtime: 웹 보드에 기록 실시간 반영
- Vercel deployment: 다른 컴퓨터에서도 접근 가능한 시연 환경

event-driven 흐름:

```text
case_selected
  -> gaia_run_started
  -> human_timer_started
  -> gaia_record_created / gaia_record_updated
  -> human_record_created
  -> board_recomputed
  -> new_run_started
```

## 5. Results

| 지표 | 결과 |
| --- | --- |
| 현재 external public manifest | 35 sites / 173 scenarios |
| 초기 KPI benchmark pack | scenario success rate 91.33%, primary success rate 91.95%, avg 62.25s |
| Human vs GAIA 30-case run | 30/30 success, avg 76.5s, progress-stop failure 0.0 |
| 최종 프로젝트 검증 | Python unit 718 passed, web lint/build passed |
| live demo board | Supabase-backed `battle-live` session, Human/GAIA records, screenshot evidence, winner comparison |

주의: 위 수치는 특정 benchmark artifact와 실행 조건 기준이다. 전체 웹에 대한 보편 성공률로 과장하지 않고, "정의된 benchmark set에서의 결과"로 설명한다.

## 6. What Worked Well

### 6.1 QA 결과를 evidence로 남긴 점

단순히 성공/실패만 저장하지 않고, reason, screenshot, DOM evidence, duration, provider/model metadata를 함께 남겼다. 이 덕분에 실패 케이스를 나중에 다시 분석할 수 있었다.

### 6.2 Role/ref 기반 action이 디버깅에 유리했다

LLM이 어떤 요소를 클릭하려 했는지 `ref`로 추적할 수 있어, "모델이 잘못 골랐는지", "브라우저 actionability가 실패했는지", "사이트가 막았는지"를 분리할 수 있었다.

### 6.3 실패를 숨기지 않고 분류했다

CAPTCHA, 로그인 gate, bot-wall, Access Denied, 서비스 장애는 억지로 성공 처리하지 않고 `BLOCKED_USER_ACTION` 또는 실패 원인으로 분리했다. 이 점은 실제 QA 도구로 볼 때 신뢰성을 높인다.

### 6.4 데모 운영까지 연결했다

CLI에서 끝나는 프로젝트가 아니라, PySide6 앱, 웹 점수판, Supabase Realtime, Vercel 배포, 증거 사진 확대, 기록 삭제/타이머 초기화까지 실제 시연 운영에 필요한 기능을 붙였다.

### 6.5 속도보다 신뢰도를 우선했다

fast mode와 일반 모드를 비교하면서 빠른 실행이 항상 좋은 결과는 아니라는 것을 확인했다. 최종적으로는 29/30처럼 빠른 실험보다, 30/30 clean baseline을 더 안전한 기준으로 삼았다.

## 7. What Failed / Hard Lessons

### 7.1 "보이는 요소"가 항상 클릭 가능한 것은 아니었다

KakaoMap 케이스에서 스카이뷰 버튼이 화면에 보이는데도 클릭이 실패했다. 원인은 의미상 visible한 요소라도 overlay가 pointer event를 가로채면 Playwright actionability 기준에서는 클릭 불가능하다는 점이었다.

배운 점:

- DOM visibility와 actionability는 다르다.
- 실패 메시지 분류가 잘못되면 agent가 같은 ref를 반복하며 loop에 빠진다.
- browser-agent 디버깅은 "LLM 판단"과 "브라우저 실행 실패"를 분리해야 한다.

### 7.2 LLM은 기다리면 안 되는 상황에서도 wait을 선택했다

일부 케이스에서 모델이 완료 가능 상태인데도 계속 wait하거나, 자신이 이미 달성한 상태를 인식하지 못하는 문제가 있었다.

대응:

- 완료 판단을 actor 자기 보고에만 맡기지 않음
- judge가 현재 DOM과 evidence를 보고 완료 선언 가능 여부를 재검토
- 반복 wait / no state change / progress stop을 failure reason으로 분리

### 7.3 빠른 모드가 항상 좋은 것은 아니었다

fast mode는 일부 케이스에서 속도를 줄였지만, 토큰 사용량과 판단 안정성 측면에서 trade-off가 있었다.

대응:

- 시연에서는 fast mode를 켜되, benchmark headline은 clean baseline 기준으로 설명
- 속도 개선과 성공률 개선을 분리해서 판단

### 7.4 웹 보드가 처음에는 케이스별로만 묶여 잘못된 결과를 보여줬다

한 케이스를 여러 사람이 반복 수행할 수 있는데, 초기에는 `scenarioId`만 기준으로 묶어 이전 사람의 결과와 새 GAIA 결과가 섞일 수 있었다.

대응:

- `battleRunId`를 도입해 실행 단위로 Human/GAIA record를 연결
- 같은 scenario라도 여러 run을 별도 카드로 유지
- 점수판 문구를 "케이스별 대결"에서 "실행별 대결"로 수정

### 7.5 시연 타이머가 stale state 때문에 자동 실행되는 문제가 있었다

이전 `battle-live` session state가 남아 있으면 새 참가자가 들어왔을 때 타이머가 이미 오래 돌고 있는 것처럼 보였다.

대응:

- 선택 완료와 시작을 분리
- `테스트 시작 준비` 화면을 추가
- 실제 시작 버튼을 누른 시점에만 timer start 기록
- timer reset / record delete operator controls 추가

### 7.6 제출 UX가 느리거나 실패해 보이는 문제가 있었다

스크린샷 data URL이 큰 경우 `/api/records` 응답과 목록 조회가 느려져, 사용자가 제출 버튼을 눌렀는데 완료 피드백이 늦게 보였다.

대응:

- 제출 중 로딩 상태와 optimistic UI 방향 도입
- inline image size trimming
- Realtime-first + polling fallback 전략 유지
- WebSocket 신규 도입보다 payload 축소와 API 응답 최적화를 우선

### 7.7 발표 화면에 raw 로그가 너무 많이 노출됐다

개발자에게 필요한 로그와 교수/방문객이 보는 화면은 달라야 했다. 초기 화면은 `ERROR`, local path, runner metadata가 그대로 보여 시연 신뢰도를 떨어뜨릴 수 있었다.

대응:

- raw log는 내부에 보존
- 기본 presentation surface에서는 high-level progress, recovery, success event만 표시
- `ERROR`를 audience-facing `RECOVERY`로 변환해 불필요한 불안감을 줄임

### 7.8 프로젝트 설득의 실패 가능성

임베디드시스템공학과 캡스톤에서 하드웨어가 없는 AI/QA 소프트웨어 프로젝트였기 때문에, 교수진 입장에서는 학과 정체성과 직접 연결되는 임팩트가 약하게 느껴졌을 수 있다.

배운 점:

- 기술 깊이와 평가 기준은 다를 수 있다.
- 청중이 기대하는 도메인 언어로 문제를 다시 번역해야 한다.
- "AI agent를 만들었다"보다 "반복 QA 비용을 줄이고 evidence 기반 검증을 자동화했다"가 더 명확한 설득 문장이다.

## 8. Troubleshooting Stories in STAR Format

이 섹션은 면접에서 가장 강하게 써먹을 수 있는 부분이다. "성공했습니다"가 아니라 "어디서 깨졌고, 어떻게 원인을 분리했고, 어떤 기준으로 고쳤는지"를 STAR 형식으로 정리한다.

아래 기록은 단순 최신 코드 기준이 아니라, 2025년 초기 서버/MCP/vision 실험부터 2026년 role/ref runtime, benchmark harness, GUI, live battle platform까지의 커밋 흐름을 기준으로 정리했다. Merge, README, 단순 중간 저장 커밋은 같은 변화 묶음에 흡수했고, 실제 구조가 바뀐 전환점 커밋을 evidence로 남겼다.

> 공개 포트폴리오에서는 특정 vendor/runtime 이름보다 "browser automation runtime", "Playwright actionability", "role/ref 기반 실행 계약"으로 표현하는 편이 좋다. 내부 면접 질문이 들어오면 아래 commit evidence로 깊게 설명한다.

### 8.0 Commit History Debugging Map

| 기간 / 전환점 | Commit evidence | 이전 코드/전략 | 실패 신호 | 도입/삭제한 코드 | 포트폴리오 해석 |
| --- | --- | --- | --- | --- | --- |
| 초기 서버에서 전용 자동화 호스트로 분리 | `9bf251b6` | `server/main.py` 안에 브라우저 자동화와 API가 섞여 있었다. | QA 실행 경로가 커질수록 서버 코드가 복잡해지고 테스트 실행 책임이 불분명했다. | `mcp/main.py`, `mcp/requirements.txt` 추가, `server/main.py` 대량 축소. | 브라우저 제어를 독립 host로 분리한 첫 아키텍처 전환. |
| DSL 실행 실험에서 LLM+vision agent로 전환 | `76954c20`, `e5d54c54` | AI가 만든 테스트 시나리오 DSL을 그대로 실행하는 방식. | 실제 웹에서는 selector/step이 쉽게 깨지고, 결과 검증이 스크립트에 묶였다. | `gaia/src/phase4/agent.py`, `intelligent_orchestrator.py`, `llm_vision_client.py`, GUI controller 추가. 기존 Vite/desktop 실험과 서버 node_modules 제거. | "정적 테스트 실행기"에서 "화면을 보고 판단하는 QA agent"로 이동. |
| 우선순위 스케줄러와 멀티페이지 orchestration | `66119e28`, `0579fd36` | 단일 테스트를 순차적으로 실행하는 흐름. | 여러 케이스를 돌릴 때 비용, 우선순위, 상태 추적이 약했다. | `gaia/src/scheduler/*`, `master_orchestrator.py`, 4-tier status, cost optimization 추가. | QA 실행을 단발 실행이 아니라 운영 가능한 scheduler 문제로 봄. |
| 병렬 검증에서 LLM 검증으로 전환 | `8df7c25d`, `ebbaa832`, `6934f736`, `64b0cc86` | 병렬 selector/cache 기반 검증과 actor 자기 보고에 가까운 검증. | 화면 toast, 동적 상태, 자연어 목표 일치 여부를 기존 검증이 놓쳤다. | Vision AI mandatory verification, Master Orchestrator natural language matching, screenshot reuse 추가. | "클릭 성공"보다 "목표 달성 검증"이 어려운 문제라는 걸 발견. |
| role 기반 접근의 시작 | `8e35a315` | selector/vision 중심 판단. | 화면이 조금 바뀌면 selector가 깨지고, LLM이 어떤 요소를 조작했는지 추적이 어려웠다. | `exploratory_agent.py`에 role 기반 흐름 대량 추가, `mcp_host.py` 보강. | 이후 Role Tree/ref action contract의 씨앗. |
| browser automation runtime 전환 | `167311d7`, `e47cbad6`, `e0fc4a4d` | 자체 MCP host와 goal-driven runtime이 섞인 상태. | ref 실행, 모달, close fallback, post-click watch가 산발적으로 생김. | `openclaw_protocol.py`, `observability.py`, `state_store.py`, `mcp_ref_*` runtime 추가. | 자연어 목표를 action contract로 실행하는 구조가 본격화. |
| raw role tree 중심으로 프롬프트 재정렬 | `5e992cb2`, `d5816396` | 요약/가공된 화면 설명에 의존. | LLM에게 전달되는 화면 표현이 실제 action ref와 어긋날 수 있었다. | raw role tree prompt, full role tree 흐름 도입. | 모델에게 "예쁜 설명"보다 실행 가능한 현재 화면 계약을 주는 방향으로 전환. |
| 사이트 특화 로직 제거 | `e38542fc`, `b12a09ec`, `d4e72b1b`, `17c7db3f`, `7ea9a12f` | filter, read-only, site-specific completion/signal check가 runtime 안에 섞임. | 특정 케이스 성공률은 오르지만 일반화가 깨지고, 다른 사이트에서 오판 가능성이 커졌다. | site-specific completion 삭제, read-only 경로 제거, filter semantic validator/generic policy 제거. | "성공률을 올리는 패치"보다 "범용 runtime"을 우선한 delete-first 의사결정. |
| run history와 context memory 도입 | `33b6fa98`, `00417a50` | step 단위 기록은 있었지만 실행 전체의 장기 상태/증거 축적이 약했다. | LLM이 이전 판단, 실패 feedback, evidence를 잊고 같은 행동을 반복했다. | `run_history_runtime.py`, `agent_memory_runtime.py`, text evidence memory 추가. | Multi-call Context Ledger로 이어진 핵심 기반. |
| benchmark가 anecdote에서 artifact로 전환 | `7da5ee5e`, `1c95ebed`, `2d62d082`, `286e9eab` | "몇 개 케이스 성공" 식의 수동 확인. | 발표/면접에서 수치를 말하려면 재현 가능한 manifest와 결과 저장이 필요했다. | `run_goal_benchmark.py`, external public manifest, benchmark manager, Grafana rollup 추가. | 성공률 주장을 artifact-backed result로 바꿈. |
| 실패 원인과 preflight 강화 | `bdf88507`, `62d4e958`, `59787253` | 실패는 로그를 직접 읽어야 알 수 있었다. | bot-wall, auth, modal, blocked, no-state-change가 한데 섞였다. | auth hints, modal runtime, benchmark blocking, preflight diagnostics, fail reason dashboard 추가. | 실패를 숨기지 않고 분류하는 엔지니어링 문화. |
| ref-first visual fallback 실험과 제한 | `0b91fe2e`, `bcc86903` | 화면에서 못 찾으면 coordinate/visual fallback이 매력적인 우회책처럼 보였다. | fallback이 강하면 성공처럼 보이나 action contract가 흐려지고 재현성이 떨어질 수 있었다. | ref-first fallback 추가 후 visual coordinate fallback은 기본 비활성화. | "많이 누르는 agent"보다 "왜 눌렀는지 설명 가능한 agent"를 선택. |
| GUI가 실제 운영 도구로 바뀜 | `68e94f62`, `2ef71e85`, `cb0c860f`, `5ee9afcb`, `b68387d6`, `82441c24`, `58e9d2e3` | 기능은 있지만 Step 3, 선택 완료, 카드 grid, Grafana link 등 실제 사용 흐름이 깨짐. | 시연 중 클릭이 안 되거나 좁은 폭에서 UI가 잘리고, 결과 확인이 불편했다. | Toss-style GUI, visible Result Action Bar, scroll area, critical issue fixes, responsive card grid. | "되는 코드"에서 "사람 앞에서 운영 가능한 앱"으로 전환. |
| Human-in-the-loop와 외부 채널 | `ca4f13c8`, `a9e5acb8`, `58dce55a` | agent가 혼자 해결하지 못하는 입력/인증/질문을 어색하게 처리. | Telegram, human answer, legacy report 경로에서 상태가 끊겼다. | `human_answer_runtime.py`, intervention flow, Telegram tests, legacy report fix 추가. | 자동화 한계를 인정하고 사람 개입 계약을 명시. |
| live battle platform | `df4a3eab`, `3a348bf0`, `b0f3ed6c`, `ef2af956`, `17f5cf6f`, `c96c3cf0`, `9a32400d` | CLI/GUI 실행 결과가 전시용 대결 경험으로 연결되지 않았다. | 사람/GAIA 기록 매칭, stale timer, submit latency, 증거 표시, reset/delete 운영 문제가 발생. | Next.js/Vercel/Supabase board, GAIA upload API, ready/start split, operator controls, run-scoped grouping. | 기술 데모를 현장 운영 가능한 product surface로 마무리. |

### Story 1. KakaoMap: 보이는 버튼이 클릭되지 않는 actionability 문제

**Commit evidence:** `67791a5a fix: stabilize OpenClaw benchmark reruns`, `762db3f3 perf: defer OpenClaw post-action snapshots`, `8debfcb8 fix: recover failed link navigation`, `ef0c9912 fix: preserve failed ref tracking`

**Situation**
KakaoMap 경로 탐색 케이스에서 스카이뷰 버튼이 화면에는 보이는데 GAIA가 반복적으로 클릭에 실패했다. 처음에는 LLM이 잘못된 버튼을 고른 것처럼 보였지만, 실제로는 브라우저 action 단계에서 `not found or not visible`류의 실패가 반복됐다.

**Task**
문제의 원인이 LLM 판단 오류인지, ref stale 문제인지, Playwright/OpenClaw actionability 실패인지 분리해야 했다. 단순 fallback을 추가하면 특정 사이트에는 통할 수 있지만, 다른 사이트에서 같은 문제가 반복될 수 있었다.

**Action**
OpenClaw raw snapshot과 Playwright action 실패 경로를 직접 추적했다. 그 결과 DOM/Role Tree 기준으로는 visible인 요소라도 overlay가 pointer event를 가로채면 실제 클릭은 불가능하다는 점을 확인했다. 이후 실패 ref를 보존하고, action 실패를 `pointer_intercepted`, `not_actionable`, `stale ref`처럼 분리할 수 있도록 runtime과 테스트를 보강했다. 또한 post-action snapshot을 매번 무겁게 뜨지 않고 필요한 시점에만 진단하도록 조정해 속도 부담을 줄였다.

**Result**
문제를 "LLM이 멍청해서 클릭을 못함"이 아니라 "semantic visibility와 browser actionability가 다름"으로 재정의했다. 이 경험은 GAIA의 핵심 차별점인 실패 원인 분류와 evidence-based debugging의 대표 사례가 됐다.

**Interview angle**
"브라우저 자동화에서 visible과 actionable은 다르다. 저는 이 차이를 실제 KakaoMap failure에서 발견했고, 모델 판단과 브라우저 실행 실패를 분리하는 runtime 진단으로 고쳤다."

### Story 2. 반복 wait / no-state-change: LLM이 자기 상태를 모르는 문제

**Commit evidence:** `361c9d83 fix: tighten goal completion harness`, `67791a5a fix: stabilize OpenClaw benchmark reruns`, `762db3f3 perf: defer OpenClaw post-action snapshots`, `8816706f fix: roll back unstable agent harness changes`

**Situation**
일부 케이스에서 화면은 이미 목표 상태에 도달했는데도 LLM이 계속 `wait`을 선택하거나, 반대로 클릭 후 아무 변화가 없는데도 진행 중이라고 착각했다. 이 문제는 성공률뿐 아니라 실행 시간에도 영향을 줬다.

**Task**
LLM의 단일 판단에 의존하지 않고, 현재 화면이 실제로 목표를 만족하는지 더 안정적으로 확인해야 했다. 동시에 너무 무거운 검증을 매 step마다 넣으면 속도가 느려지는 trade-off도 해결해야 했다.

**Action**
action 이후 DOM 변화, state change, text evidence, screenshot evidence를 ledger에 남기고, actor의 완료 주장을 별도 judge가 다시 확인하도록 했다. `no_state_change`, 반복 wait, progress stop을 실패/복구 신호로 분리했다. 이후 불안정하게 추가한 harness 변경은 `8816706f`에서 롤백해, 성공률을 떨어뜨리는 과한 로직보다 검증된 baseline을 우선했다.

**Result**
모델이 "기다리자"라고 말해도 runtime이 현재 evidence를 기반으로 완료 가능 여부를 다시 판단하는 구조가 됐다. 빠른 실험보다 안정적인 30/30 baseline을 기준으로 삼을 수 있었고, 실패 원인을 모델 추론/브라우저 상태/외부 차단으로 더 명확히 나눌 수 있었다.

**Interview angle**
"LLM agent는 스스로 상태를 잘 안다고 가정하면 위험하다. 저는 action result와 evidence ledger를 기준으로 모델 판단을 검증하는 구조를 넣었다."

### Story 3. Human vs GAIA 결과가 서로 다른 실행끼리 섞인 문제

**Commit evidence:** `df4a3eab feat: add live battle web board`, `3a348bf0 feat: connect GAIA benchmark to battle board`, `b0f3ed6c fix: harden live battle case flow`, `9a32400d feat: finalize GAIA capstone demo flow`

**Situation**
시연장에서는 같은 공, 즉 같은 시나리오를 여러 사람이 반복해서 뽑을 수 있었다. 그런데 초기 점수판은 `scenarioId` 중심으로 Human과 GAIA 결과를 묶었기 때문에, 이전 참가자의 Human 결과와 새 GAIA 결과가 한 카드에 섞일 수 있었다.

**Task**
점수판의 기본 단위를 "시나리오"가 아니라 "실행"으로 바꿔야 했다. 같은 시나리오라도 참가자와 GAIA가 한 번 붙은 실행은 별도 기록으로 남아야 했다.

**Action**
GAIA 실행 시작 시점에 `battleRunId`를 만들고, Human 제출에도 같은 run id를 metadata로 저장하도록 했다. Human participant id도 run-scoped로 생성해 같은 이름이 다시 제출해도 이전 row를 덮어쓰지 않게 했다. `BattleBoardClient`와 `lib/cases.ts`에서는 scenario grouping을 execution grouping으로 바꾸고, UI 문구도 "케이스별 대결"에서 "실행별 대결"로 수정했다.

**Result**
같은 시나리오를 여러 번 실행해도 각 run이 별도 카드로 유지됐다. 이름, 성공 이유, 스크린샷, GAIA 결과가 서로 다른 실행끼리 섞이는 문제를 막았고, 실제 전시 운영 방식에 맞는 데이터 모델로 바뀌었다.

**Interview angle**
"처음에는 데이터 모델이 시연 운영 방식을 충분히 반영하지 못했다. 현장 사용 흐름을 보고 aggregate key를 scenario에서 execution으로 바꾸면서 문제를 해결했다."

### Story 4. stale timer: 참가자 페이지가 2700초부터 시작한 문제

**Commit evidence:** `ef2af956 fix: wait for GAIA start signal before timing`, `17f5cf6f feat: add battle web operator controls`, `9a32400d feat: finalize GAIA capstone demo flow`

**Situation**
Human 입력 페이지에 들어갔을 때 이전 `battle-live` 세션의 `humanStartedAt` 값이 남아 있어 타이머가 이미 수십 분 돌아간 것처럼 보였다. 시연장에서는 이 한 번의 UI 오류만으로도 시스템이 불안정해 보일 수 있었다.

**Task**
참가자가 페이지를 여는 시점과 실제 QA 시작 시점을 분리해야 했다. 운영자가 케이스를 선택했을 때는 "준비 상태"만 보여주고, GAIA/운영자의 시작 신호가 들어올 때부터 타이머가 돌아야 했다.

**Action**
`humanStartedAt`을 바로 현재 시각으로 쓰지 않고, 준비 상태를 나타내는 sentinel 값을 사용했다. 사용자가 제출 페이지에 들어와도 시작 신호가 없으면 `GAIA 시작 신호 대기` 상태를 보여주고, 운영자가 시작 버튼을 누를 때만 실제 시작 시간을 기록하도록 바꿨다. 추가로 타이머 초기화와 기록 삭제 operator control을 넣어 시연 중 stale state를 즉시 복구할 수 있게 했다.

**Result**
페이지 진입만으로 타이머가 시작되지 않게 됐다. 시연 플로우가 `선택 완료 -> 시작 준비 -> 시작 -> 제출`로 명확해졌고, 운영자가 실수하거나 이전 기록이 남아 있어도 빠르게 초기화할 수 있었다.

**Interview angle**
"상태 관리 버그는 기능 오류보다 신뢰도에 더 치명적이었다. 저는 사용자의 실제 이벤트 흐름을 기준으로 timer ownership을 다시 설계했다."

### Story 5. 제출이 느려 보이는 문제와 screenshot payload 최적화

**Commit evidence:** `c96c3cf0 feat: polish battle web demo flow`, `17f5cf6f feat: add battle web operator controls`

**Situation**
Human이 제출 버튼을 눌렀을 때 완료 표시가 몇 초 늦게 보이는 문제가 있었다. 특히 증거 screenshot을 data URL로 저장하면 `/api/records` 응답과 목록 조회 payload가 커져 웹 보드가 느려질 수 있었다.

**Task**
새로운 WebSocket 서버를 붙이기 전에, 현재 구조에서 체감 지연의 원인을 줄여야 했다. 시연 시간에는 "저장 중인지 멈춘 건지"를 사용자가 바로 알아야 했다.

**Action**
제출 중 UI 상태를 명확히 하고, 성공 이유 20자 이상과 screenshot 1개 이상 조건을 submit handler 내부에서도 검증했다. inline image가 지나치게 큰 경우 metadata에서 trimming하고 skipped reason을 남기도록 했다. Realtime-first 업데이트와 polling fallback은 유지하되, 먼저 payload와 API 응답을 줄이는 방향을 선택했다.

**Result**
사용자는 제출 직후 시스템이 반응하고 있다는 피드백을 받게 됐고, 비정상적으로 큰 screenshot이 전체 record 조회를 느리게 만드는 문제를 줄였다. "WebSocket을 붙이면 해결"이 아니라 payload 구조와 UX feedback을 먼저 고치는 판단을 했다.

**Interview angle**
"성능 문제를 transport 문제로 단정하지 않고, API payload, Realtime, optimistic UI를 나눠서 봤다."

### Story 6. 개발자 로그와 관객용 화면을 분리한 문제

**Commit evidence:** `9a32400d feat: finalize GAIA capstone demo flow`, `c96c3cf0 feat: polish battle web demo flow`

**Situation**
QA Desktop은 개발 중에는 raw log가 필요했지만, 전시 큰 모니터에서는 `ERROR`, local path, runner metadata가 그대로 보이면 실패한 프로그램처럼 보였다. 실제로는 복구 가능한 action 실패인데도 빨간 에러처럼 노출되는 문제가 있었다.

**Task**
내부 디버깅 정보는 보존하면서, 교수/방문객이 보는 presentation surface는 진행 상태와 증거 중심으로 정리해야 했다.

**Action**
raw log는 내부 저장소에 유지하고, 기본 화면에는 audience-friendly log만 보여주도록 포맷팅했다. 복구 가능한 action 실패는 `ERROR` 대신 `RECOVERY` 수준으로 보여주고, runner id나 local path 같은 정보는 기본 화면에서 숨겼다. 또한 오른쪽에 도킹되는 데스크톱 앱 레이아웃을 좁은 폭에서도 깨지지 않도록 재배치하고, step별 증거 thumbnail과 확대 dialog를 추가했다.

**Result**
시연 화면은 "개발 중인 로그 콘솔"이 아니라 "운영 가능한 QA control surface"에 가까워졌다. 발표자는 원할 때 증거를 확대해 보여줄 수 있고, 관객은 raw stack trace 없이도 진행 상황을 이해할 수 있게 됐다.

**Interview angle**
"운영 UI에서는 정확한 로그보다 적절한 추상화가 중요했다. raw data는 버리지 않고, 관객용 presentation layer만 분리했다."

### Story 7. 빠른 실험과 신뢰 가능한 baseline을 구분한 문제

**Commit evidence:** `fa59c7db feat: wire GAIA battle demo mode`, `8816706f fix: roll back unstable agent harness changes`, `9a32400d feat: finalize GAIA capstone demo flow`

**Situation**
시연 전 fast mode와 agent harness 변경을 넣으면서 일부 실행은 빨라졌지만, 인증 오류나 suite 차이 때문에 결과 해석이 애매해졌다. 빠른 29/30 run과 안정적인 30/30 run 중 어떤 것을 대표 수치로 말해야 하는지 선택해야 했다.

**Task**
포트폴리오와 발표에서 과장되지 않으면서도 기술 성과를 보여줄 수 있는 기준을 정해야 했다. 속도 최적화와 성공률 안정성을 같은 지표로 섞으면 안 됐다.

**Action**
불안정한 agent harness 변경은 롤백하고, clean 30/30 baseline을 대표 수치로 유지했다. fast mode는 시연용 옵션과 최적화 가능성으로 설명하고, 인증 오류나 외부 서비스 차단은 browser-action regression과 분리했다.

**Result**
성능 주장을 보수적으로 유지할 수 있었다. 면접이나 발표에서 "우리는 성공률을 좋게 보이려고 실패를 숨겼다"가 아니라, "실행 조건과 실패 원인을 분리해서 해석했다"라고 말할 수 있는 근거가 생겼다.

**Interview angle**
"좋은 숫자보다 재현 가능한 숫자가 중요했다. 그래서 빠른 실험은 optimization candidate로 두고, clean baseline을 결과로 사용했다."

### Story 8. 초기 서버/스크립트 구조가 커지면서 전용 browser host로 분리한 문제

**Commit evidence:** `9bf251b6 feat: Create dedicated MCP host for browser automation`, `76954c20 MCP 호스트에 AI가 생성한 테스트 시나리오(DSL)를 실제 브라우저에서 실행하는 엔진을 구현합니다.`, `e5d54c54 feat: Implement LLM-powered browser automation with vision analysis`

**Situation**
초기에는 `server/main.py` 중심으로 API와 브라우저 실행 로직이 함께 존재했다. 간단한 테스트 실행에는 충분했지만, QA 시나리오가 DSL, 브라우저 실행, 결과 수집, LLM 판단으로 커지면서 하나의 서버 파일에 책임이 몰렸다.

**Task**
브라우저 제어를 API 서버의 부속 기능이 아니라 독립 실행 가능한 automation host로 분리해야 했다. 그래야 나중에 GUI, CLI, benchmark runner가 같은 실행 경로를 재사용할 수 있었다.

**Action**
`9bf251b6`에서 `mcp/main.py`를 새로 만들고 `server/main.py`를 크게 줄여 브라우저 자동화 책임을 host로 이동했다. 이후 `e5d54c54`에서는 기존 Vite/desktop/server node_modules 실험 흔적을 대량 제거하고, `gaia/src/phase4/agent.py`, `intelligent_orchestrator.py`, `llm_vision_client.py`, `mcp_host.py` 같은 GAIA 중심 구조로 재편했다.

**Result**
프로젝트가 "웹 서버에 붙은 자동화 코드"에서 "LLM이 브라우저를 조작하는 QA runtime"으로 바뀌었다. 이 분리가 있었기 때문에 뒤에서 role/ref runtime, benchmark, GUI, live battle board를 같은 실행 개념 위에 쌓을 수 있었다.

**Interview angle**
"처음부터 정답 아키텍처를 만든 게 아니라, 서버 코드가 비대해지는 실패를 겪고 browser automation host를 별도 책임으로 분리했다."

### Story 9. Vision-only 검증이 불안정해서 role/ref 계약으로 이동한 문제

**Commit evidence:** `8df7c25d 병렬 검증 -> llm 검증`, `ebbaa832 Improve agent validation with mandatory Vision AI verification`, `8e35a315 role 기반`, `167311d7 openclaw 방식 도입`, `5e992cb2 Refocus Gaia prompts on raw OpenClaw role trees`, `d5816396 full role tree`

**Situation**
중간 단계에서는 screenshot과 Vision AI 검증을 강화했다. 실제로 toast message나 화면 상태를 잡는 데 도움이 됐지만, vision만으로는 "어떤 버튼을 눌렀는지", "다음 action이 어떤 요소를 대상으로 하는지"가 안정적으로 남지 않았다.

**Task**
화면을 이미지로 보는 능력과 브라우저에서 실행 가능한 action 사이에 계약을 만들어야 했다. LLM이 "저 버튼"이라고 말하는 수준이 아니라, 현재 snapshot의 role/ref를 기준으로 action을 요청해야 했다.

**Action**
`8e35a315`에서 role 기반 접근을 도입했고, `167311d7` 이후 browser automation runtime과 ref action 경로를 붙였다. `5e992cb2`, `d5816396`에서는 모델에게 가공된 요약 대신 raw/full role tree를 전달하도록 프롬프트를 재정렬했다.

**Result**
검증은 vision/evidence를 쓰되, 실행은 role/ref contract에 묶는 구조가 만들어졌다. 덕분에 실패 시 "모델이 틀린 요소를 골랐는지", "ref가 stale인지", "브라우저 actionability가 막혔는지"를 분리할 수 있었다.

**Interview angle**
"Vision은 강력하지만 action contract가 없으면 디버깅이 어렵다. 그래서 저는 화면 이해와 실행 대상을 role/ref로 연결했다."

### Story 10. 사이트 특화 성공 판정이 오히려 범용성을 해친 문제

**Commit evidence:** `e38542fc Remove site-specific completion and signal checks`, `b12a09ec 특화 로직 제거`, `d4e72b1b read-only 경로 제거`, `17c7db3f Remove filter-specific goal policy`, `7ea9a12f Remove filter semantic validator from generic runtime`

**Situation**
특정 사이트/특정 필터 케이스의 성공률을 올리기 위해 site-specific completion check, read-only 경로, filter semantic validator 같은 코드가 runtime에 들어갔다. 단기적으로는 성공처럼 보였지만, runtime이 점점 특수 케이스 모음으로 변했다.

**Task**
포트폴리오에서 어필할 수 있는 것은 "특정 사이트를 하드코딩했다"가 아니라 "여러 사이트에 적용 가능한 QA runtime"이었다. 특화 로직을 제거하면서도 목표 달성 검증은 유지해야 했다.

**Action**
`e38542fc`에서 site-specific completion과 signal check를 제거했고, `d4e72b1b`에서 read-only 경로를 크게 삭제했다. 이후 `17c7db3f`, `7ea9a12f`로 filter-specific policy와 generic runtime에 섞인 semantic validator를 제거했다.

**Result**
코드는 일부 케이스에서 덜 공격적으로 보일 수 있지만, runtime의 설명 가능성과 범용성이 좋아졌다. 면접에서는 이걸 "더 많은 fallback을 넣은 경험"보다 "잘못된 fallback을 삭제한 경험"으로 말하는 게 훨씬 강하다.

**Interview angle**
"성공률을 올리는 가장 쉬운 방법은 하드코딩이지만, 저는 범용 runtime을 위해 오히려 특화 로직을 삭제했다."

### Story 11. 수동 성공 사례를 benchmark artifact로 바꾼 문제

**Commit evidence:** `7da5ee5e 벤치 도입`, `1c95ebed Add external public benchmark pack`, `2d62d082 Add benchmark monitoring and shared suites`, `286e9eab Add external public Grafana rollups`, `59787253 fail reason describe`

**Situation**
초기에는 "이 케이스 됐다"는 식의 수동 확인과 산발적인 결과 파일이 많았다. 하지만 발표나 포트폴리오에서는 재현 가능한 benchmark set, 실행 로그, 실패 분류가 있어야 신뢰할 수 있다.

**Task**
성공률과 실패 원인을 사람이 말로 설명하는 것이 아니라, manifest와 runner, dashboard가 뒷받침하도록 만들어야 했다.

**Action**
`7da5ee5e`에서 `scripts/run_goal_benchmark.py`와 결과 artifact를 도입했다. 이후 `1c95ebed`에서 external public manifest를 확장하고, `2d62d082`, `286e9eab`로 monitoring/Grafana rollup을 붙였다. `59787253`에서는 dashboard에 fail reason 설명을 추가했다.

**Result**
GAIA는 단순 데모가 아니라 benchmarkable system이 됐다. 성공률, 평균 시간, 실패 원인을 artifact로 남길 수 있게 됐고, 나중에 30-case run이나 external public manifest 결과를 보수적으로 설명할 수 있는 기반이 생겼다.

**Interview angle**
"AI agent 프로젝트에서 중요한 건 데모 영상보다 재현 가능한 evaluation harness다. 저는 runner, manifest, Grafana까지 붙여 결과를 artifact화했다."

### Story 12. GUI가 예뻐졌지만 실제 사용 흐름에서 깨진 문제

**Commit evidence:** `68e94f62 feat(gui): Toss 디자인 시스템 기반 GUI 전면 개편`, `2ef71e85 fix(gui): Step 3에 visible Result Action Bar 추가`, `cb0c860f fix(gui): Step 3 페이지를 QScrollArea로 감싸 KPI 카드 squeeze 방지`, `5ee9afcb fix(gui): GUI QA 2라운드`, `b68387d6 fix(gui): 4가지 critical 이슈 수정`, `82441c24 fix(gui): 빠른 목표 / 기획서 / AI 모드에서 '선택 완료' 무반응 버그 수정`, `58e9d2e3 fix(gui): Step 1 사이트 카드 그리드 반응형 강화`

**Situation**
GUI를 Toss 스타일로 전면 개편하면서 화면은 좋아졌지만, 실제 사용자가 클릭하고 실행하는 흐름에서는 문제가 계속 나왔다. Step 3 결과 버튼이 안 보이거나, KPI 카드가 눌리거나, 선택 완료가 무반응이거나, 좁은 화면에서 카드가 잘렸다.

**Task**
시연용 앱은 "예쁜 화면"보다 "현장에서 실수 없이 누를 수 있는 운영 도구"여야 했다. 특히 오른쪽에 QA 앱을 좁게 붙이고 왼쪽에 테스트 브라우저를 띄우는 시연 레이아웃에서도 깨지면 안 됐다.

**Action**
Result Action Bar를 항상 보이게 하고, Step 3을 scroll area로 감싸며, 진행률/케이스 클릭/1:1 매칭/Grafana URL 같은 critical issue를 수정했다. 빠른 목표/기획서/AI 모드의 선택 완료 무반응을 고치고, 사이트 카드 grid를 반응형으로 보강했다.

**Result**
GUI는 단순 wrapper가 아니라 실제 운영 control surface가 됐다. 시연자가 케이스 선택, 실행, 로그 확인, 증거 확인, 결과 링크 이동을 한 화면에서 처리할 수 있게 됐다.

**Interview angle**
"프론트엔드는 미감만이 아니라 운영 동선이다. 저는 GUI QA를 여러 라운드 돌려 실제 시연 레이아웃에서 깨지는 부분을 고쳤다."

### Story 13. 사람이 개입해야 하는 상황을 agent 실패로만 처리하지 않은 문제

**Commit evidence:** `ca4f13c8 feat: add structured human answer flow`, `a9e5acb8 Fix Telegram intervention input flow`, `58dce55a Fix legacy goal completion human-answer reports`, `fe745663 feat: 멀티유저 상호작용 하네스 추가`

**Situation**
웹 QA에는 로그인, CAPTCHA, 사용자 선택, Telegram 같은 외부 입력이 필요할 때가 있다. 이를 무조건 자동화 실패로 처리하면 실제 운영에서는 쓸 수 없고, 무조건 우회하려고 하면 위험하다.

**Task**
agent가 혼자 못 하는 상황과 사람이 개입해야 하는 상황을 계약으로 분리해야 했다. 사람의 답변이 들어온 후에도 실행 ledger와 report가 끊기지 않아야 했다.

**Action**
`human_answer_runtime.py`를 추가해 사람 답변 흐름을 구조화했고, Telegram bridge의 intervention input flow를 고쳤다. legacy goal completion report도 human answer를 반영하도록 수정했다. 멀티유저 상호작용 하네스는 이후 Human vs GAIA 시연에서 event-driven turn scheduling을 설명하는 기반이 됐다.

**Result**
GAIA는 모든 것을 몰래 우회하는 agent가 아니라, 자동화 한계를 명시하고 human-in-the-loop로 이어갈 수 있는 QA runtime에 가까워졌다.

**Interview angle**
"자동화에서 중요한 건 다 자동으로 하는 척이 아니라, 사람이 필요한 경계를 명확히 정의하는 것이다."

### Story 14. 데모 점수판이 실제 전시 운영 모델과 맞지 않았던 문제

**Commit evidence:** `df4a3eab feat: add live battle web board`, `3a348bf0 feat: connect GAIA benchmark to battle board`, `b0f3ed6c fix: harden live battle case flow`, `ef2af956 fix: wait for GAIA start signal before timing`, `17f5cf6f feat: add battle web operator controls`, `c96c3cf0 feat: polish battle web demo flow`, `9a32400d feat: finalize GAIA capstone demo flow`

**Situation**
Human vs GAIA 웹 보드는 처음에는 "기록이 보인다" 수준이었다. 그런데 실제 전시에서는 한 사람이 공을 뽑고, 같은 시나리오가 여러 번 반복될 수 있고, GAIA는 다른 컴퓨터에서 돌며, 사람은 휴대폰/다른 PC로 증거를 제출한다.

**Task**
웹 보드를 실제 운영 모델에 맞춰야 했다. 케이스 선택, 준비 상태, 타이머 시작, Human 제출, GAIA 업로드, 승패 계산, 기록 삭제/초기화가 같은 이벤트 흐름 안에 있어야 했다.

**Action**
Next.js/Vercel/Supabase 기반 live board를 만들고, GAIA benchmark runner가 `/api/records`로 증거를 업로드하도록 연결했다. 이후 run-scoped grouping, ready/start split, timer reset, record delete, screenshot evidence 확대, submission validation, audience-friendly scoreboard를 보강했다.

**Result**
CLI benchmark 결과가 전시 가능한 product surface로 변했다. 이 과정에서 데이터 모델, UX feedback, Realtime 업데이트, 운영자 제어까지 모두 실제 현장 요구를 반영하게 됐다.

**Interview angle**
"기술 데모를 실제 사용자가 참여하는 운영 시스템으로 바꾸면서 event-driven data model과 UX 상태 관리를 같이 설계했다."

## 9. Resume Bullets

아래 문장들은 이력서에 바로 넣을 수 있는 버전이다.

- 자연어 QA 목표를 Role Tree snapshot과 ref 기반 action으로 변환하는 goal-driven browser QA agent를 설계하고 구현했다.
- LLM actor의 자기 보고를 그대로 신뢰하지 않고, DOM 변화, screenshot evidence, reason code, judge call을 결합한 evidence-based completion 검증 구조를 구축했다.
- PySide6 데스크톱 앱, Next.js/Vercel 웹 보드, Supabase Realtime을 연결해 Human vs GAIA QA 대결 시연 플랫폼을 구현했다.
- 동일 시나리오의 반복 실행이 섞이는 문제를 `battleRunId` 기반 execution grouping으로 해결해 Human/GAIA 결과 매칭 정확도를 개선했다.
- 35개 사이트 / 173개 시나리오 manifest와 benchmark artifacts를 운영하며, 대표 30-case run에서 30/30 success, 평균 76.5초를 기록했다.
- Playwright/OpenClaw actionability 실패, stale ref, pointer interception, no-state-change loop 등 browser-agent 실패 원인을 분류하고 복구 전략을 개선했다.
- 발표/전시 환경을 위해 raw debug log와 audience-facing log를 분리하고, 증거 screenshot 확대, 타이머/기록 초기화, 좁은 패널 레이아웃을 포함한 운영 UI를 개선했다.

## 10. Interview Positioning

면접에서 이 프로젝트를 소개할 때는 다음 순서가 좋다.

1. "웹 QA는 클릭보다 성공 검증이 어렵다."
2. "그래서 GAIA는 자연어 목표, Role Tree, ref action, evidence ledger, judge를 하나의 runtime으로 묶었다."
3. "실패를 숨기지 않고 reason code와 artifact로 남겼다."
4. "브라우저 agent 특유의 어려움인 stale ref, pointer interception, wait loop, bot-wall을 실제 benchmark에서 겪고 분리했다."
5. "마지막에는 사람과 GAIA가 같은 미션을 수행하는 live demo platform까지 배포했다."

## 11. What I Would Improve Next

- 사이트 유형별 runtime parameter 자동 튜닝
- wait/retry/vision fallback의 ablation study
- screenshot payload를 storage 기반으로 분리해 web response 경량화
- CAPTCHA/login-gate를 우회하지 않는 human-in-the-loop contract 정교화
- evidence target selection을 더 정밀화해 full-page screenshot 의존도 축소
- benchmark 결과를 CI와 연결해 회귀 탐지 자동화
- 포트폴리오 공개용으로 개인정보/내부 URL/secret이 제거된 demo dataset 구성

## 12. Honest Retrospective

이 프로젝트는 수상 여부와 별개로, 단순 기능 구현보다 많은 시행착오가 있었다.

성공한 지점은 AI agent를 "말만 하는 모델"이 아니라 실제 브라우저에서 행동하고, 실패를 기록하고, 증거로 검증하는 runtime으로 만든 것이다.

실패한 지점은 기술의 깊이를 청중이 바로 이해할 수 있는 도메인 언어로 충분히 번역하지 못했을 가능성이다. 특히 하드웨어 중심 학과에서 소프트웨어/AI QA 프로젝트는 평가자가 기대한 문제 정의와 어긋났을 수 있다.

하지만 취업 포트폴리오 관점에서는 이 실패 자체가 강점이 될 수 있다. 이 프로젝트는 성공률만 자랑하는 결과물이 아니라, 실제 웹 자동화가 깨지는 이유를 추적하고, 운영 가능한 시연 시스템으로 수렴시킨 엔지니어링 경험이기 때문이다.
