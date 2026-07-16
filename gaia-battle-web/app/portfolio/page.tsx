import type { Metadata } from "next";

import styles from "./portfolio.module.css";

export const metadata: Metadata = {
  title: "GAIA Portfolio Case Study",
  description: "AI GUI QA automation runtime portfolio case study",
};

const stats = [
  { label: "개발 기간", value: "2025-2026", detail: "초기 MCP 실험부터 live demo까지" },
  { label: "최신 회귀", value: "26/30", detail: "0 agent FAIL · 4 external/time blockers" },
  { label: "검증 범위", value: "35 sites", detail: "173 public scenarios manifest" },
  { label: "핵심 구조", value: "4-layer", detail: "Actor, action, ledger, judge" },
];

const wins = [
  "자연어 QA 목표를 role/ref 기반 action contract로 실행",
  "LLM 자기 보고를 그대로 믿지 않고 evidence-based judge로 재검증",
  "실패 원인을 stale ref, no-state-change, bot-wall, auth gate 등으로 분리",
  "PySide6 앱, Vercel board, Supabase Realtime을 연결한 현장 시연 시스템 구축",
];

const failures = [
  {
    title: "보이는 버튼이 클릭되지 않았다",
    detail:
      "DOM상 visible인 요소라도 overlay가 pointer event를 가로채면 실행은 실패했다. 이후 visible과 actionable을 분리해 reason code와 실패 ref를 남겼다.",
  },
  {
    title: "LLM이 이미 끝난 상황에서도 wait을 골랐다",
    detail:
      "actor가 자기 상태를 잘 모른다는 걸 확인했다. step별 action result, state change, screenshot evidence를 ledger에 남기고 judge가 완료 여부를 다시 보게 했다.",
  },
  {
    title: "특화 로직이 범용성을 망쳤다",
    detail:
      "특정 사이트 성공률을 올리는 site-specific check를 넣었다가 runtime이 케이스 모음으로 변했다. 이후 filter/read-only 특화 경로를 삭제하고 범용 contract로 되돌렸다.",
  },
  {
    title: "웹 점수판 결과가 서로 다른 실행끼리 섞였다",
    detail:
      "처음에는 scenario 단위로 묶어 같은 케이스를 여러 사람이 실행하면 기록이 섞였다. battleRunId를 도입해 실행 단위로 Human/GAIA 결과를 연결했다.",
  },
];

const timeline = [
  {
    period: "2025.10",
    title: "전용 browser automation host 분리",
    before: "server/main.py 중심의 섞인 구조",
    after: "MCP host와 LLM vision agent 구조",
    commits: "9bf251b6, e5d54c54",
  },
  {
    period: "2026.01-02",
    title: "role/ref 실행 계약 도입",
    before: "selector, vision 중심 판단",
    after: "Role Tree snapshot과 ref action contract",
    commits: "8e35a315, 167311d7",
  },
  {
    period: "2026.04",
    title: "특화 로직 삭제",
    before: "site/filter/read-only 특수 경로",
    after: "generic runtime과 evidence-based verification",
    commits: "e38542fc, b12a09ec, d4e72b1b",
  },
  {
    period: "2026.05",
    title: "benchmark와 dashboard artifact화",
    before: "수동 성공 사례와 산발 로그",
    after: "manifest, runner, Grafana, fail reason dashboard",
    commits: "1c95ebed, 286e9eab, 59787253",
  },
  {
    period: "2026.05-06",
    title: "Human vs GAIA live demo 완성",
    before: "CLI/GUI 결과가 현장 참여 경험과 분리",
    after: "Vercel board, Supabase Realtime, run-scoped records",
    commits: "df4a3eab, ef2af956, 9a32400d",
  },
];

const stories = [
  {
    title: "KakaoMap actionability failure",
    situation: "스카이뷰 버튼이 보이는데 클릭이 반복 실패했다.",
    action:
      "LLM 판단, stale ref, browser actionability를 분리해 분석하고 pointer interception을 reason code로 보존했다.",
    result: "문제를 모델 오류가 아니라 runtime 진단 문제로 재정의해 같은 ref 반복 loop를 줄였다.",
  },
  {
    title: "Multi-call Context Ledger",
    situation: "LLM API를 여러 번 호출하면 이전 실패와 증거 맥락이 끊겼다.",
    action:
      "action result, state change, screenshot, text evidence, judge result를 step ledger로 묶었다.",
    result: "단일 프롬프트가 아니라 하나의 QA 실행 상태로 판단을 이어가게 만들었다.",
  },
  {
    title: "특화 fallback 제거",
    situation: "특정 사이트를 맞추는 로직이 늘어날수록 범용성이 떨어졌다.",
    action:
      "site-specific completion, read-only special path, filter semantic validator를 삭제하고 generic rule로 회귀했다.",
    result: "성공률을 예쁘게 보이는 패치보다 설명 가능한 runtime 구조를 선택했다.",
  },
  {
    title: "Live battle run grouping",
    situation: "같은 시나리오를 여러 사람이 실행하면 이전 기록과 새 기록이 섞였다.",
    action:
      "battleRunId를 도입하고 Human/GAIA record를 execution 단위로 묶었다.",
    result: "현장 운영 방식과 데이터 모델이 맞아져 점수판 신뢰도가 올라갔다.",
  },
];

const resumeBullets = [
  "자연어 QA 목표를 Role Tree snapshot과 ref 기반 action으로 변환하는 browser QA agent를 설계하고 구현",
  "DOM 변화, screenshot evidence, reason code, judge call을 결합한 evidence-based completion 검증 구조 구축",
  "PySide6 데스크톱 앱, Next.js/Vercel 웹 보드, Supabase Realtime을 연결한 Human vs GAIA 시연 플랫폼 구현",
  "benchmark manifest와 Grafana dashboard로 성공률, 평균 시간, 실패 원인을 artifact 기반으로 관리",
];

export default function PortfolioPage() {
  return (
    <main className={styles.page}>
      <section className={styles.hero}>
        <div className={styles.heroTop}>
          <span className={styles.brand}>GAIA Portfolio</span>
          <a className={styles.ghostLink} href="#stories">
            STAR 보기
          </a>
        </div>
        <p className={styles.kicker}>AI GUI QA Automation Runtime</p>
        <h1>실패를 숨기지 않고, 실행 가능한 QA 런타임으로 바꾼 프로젝트</h1>
        <p className={styles.heroCopy}>
          GAIA는 자연어 QA 목표를 받아 브라우저 화면을 의미 단위로 해석하고, 단계별 행동과
          증거를 누적해 최종 성공 여부를 검증하는 AI 기반 GUI QA 자동화 시스템입니다.
        </p>
        <div className={styles.heroActions}>
          <a href="#timeline">개발 히스토리</a>
          <a href="#resume">이력서 문장</a>
        </div>
      </section>

      <section className={styles.statsGrid} aria-label="project stats">
        {stats.map((stat) => (
          <article className={styles.statCard} key={stat.label}>
            <span>{stat.label}</span>
            <strong>{stat.value}</strong>
            <p>{stat.detail}</p>
          </article>
        ))}
      </section>

      <section className={styles.splitSection}>
        <article className={styles.panel}>
          <span className={styles.sectionLabel}>성공했던 지점</span>
          <h2>단순 클릭 봇이 아니라 검증 가능한 runtime으로 만들었다</h2>
          <ul className={styles.cleanList}>
            {wins.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
        <article className={`${styles.panel} ${styles.darkPanel}`}>
          <span className={styles.sectionLabel}>실패했던 지점</span>
          <h2>실패가 설계 방향을 바꿨다</h2>
          <div className={styles.failureStack}>
            {failures.map((failure) => (
              <details key={failure.title} className={styles.failureCard}>
                <summary>{failure.title}</summary>
                <p>{failure.detail}</p>
              </details>
            ))}
          </div>
        </article>
      </section>

      <section id="timeline" className={styles.timelineSection}>
        <div className={styles.sectionHeader}>
          <span className={styles.sectionLabel}>Commit-derived history</span>
          <h2>처음부터 잘 만든 게 아니라, 계속 갈아엎으며 수렴했다</h2>
          <p>
            단순 merge/README 커밋은 묶고, 구조가 바뀐 전환점 커밋 기준으로 before, failure
            signal, after를 정리했습니다.
          </p>
        </div>
        <div className={styles.timeline}>
          {timeline.map((item) => (
            <article className={styles.timelineItem} key={item.title}>
              <span>{item.period}</span>
              <h3>{item.title}</h3>
              <dl>
                <div>
                  <dt>Before</dt>
                  <dd>{item.before}</dd>
                </div>
                <div>
                  <dt>After</dt>
                  <dd>{item.after}</dd>
                </div>
              </dl>
              <code>{item.commits}</code>
            </article>
          ))}
        </div>
      </section>

      <section id="stories" className={styles.storySection}>
        <div className={styles.sectionHeader}>
          <span className={styles.sectionLabel}>STAR troubleshooting</span>
          <h2>면접에서 바로 말할 수 있는 디버깅 스토리</h2>
        </div>
        <div className={styles.storyGrid}>
          {stories.map((story, index) => (
            <article className={styles.storyCard} key={story.title}>
              <span className={styles.storyIndex}>{String(index + 1).padStart(2, "0")}</span>
              <h3>{story.title}</h3>
              <div>
                <strong>Situation</strong>
                <p>{story.situation}</p>
              </div>
              <div>
                <strong>Action</strong>
                <p>{story.action}</p>
              </div>
              <div>
                <strong>Result</strong>
                <p>{story.result}</p>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className={styles.architecture}>
        <span className={styles.sectionLabel}>Core architecture</span>
        <h2>Multi-call Context Ledger</h2>
        <div className={styles.flow}>
          <div>Actor Call</div>
          <div>Action Result</div>
          <div>Evidence Memory</div>
          <div>Judge Call</div>
        </div>
        <p>
          하나의 긴 프롬프트가 아니라, step별 LLM 호출을 하나의 QA 실행 상태로 묶어 이전 action,
          실패 feedback, screenshot evidence, 현재 DOM을 계속 이어갑니다.
        </p>
      </section>

      <section id="resume" className={styles.resumeSection}>
        <span className={styles.sectionLabel}>Resume-ready bullets</span>
        <h2>이력서에 바로 옮길 수 있는 문장</h2>
        <ul className={styles.resumeList}>
          {resumeBullets.map((bullet) => (
            <li key={bullet}>{bullet}</li>
          ))}
        </ul>
      </section>

      <footer className={styles.footer}>
        <strong>Interview positioning</strong>
        <p>
          웹 QA는 클릭보다 성공 검증이 어렵다. GAIA는 자연어 목표, Role Tree, ref action,
          evidence ledger, judge를 하나의 runtime으로 묶고, 실패를 reason code와 artifact로
          남기는 방향으로 설계됐다.
        </p>
      </footer>
    </main>
  );
}
