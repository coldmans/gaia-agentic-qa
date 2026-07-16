import type { BattleRecord } from "./types";

export type CaseVerdict =
  | "HUMAN_FASTER"
  | "GAIA_FASTER"
  | "TIE"
  | "HUMAN_WIN"
  | "GAIA_WIN"
  | "BOTH_FAILED"
  | "WAITING";

export type BattleCase = {
  runId: string;
  scenarioId: string;
  label: string;
  humans: BattleRecord[];
  gaias: BattleRecord[];
  bestHuman: BattleRecord | null;
  bestGaia: BattleRecord | null;
  verdict: CaseVerdict;
  latestAt: string;
};

const RUN_PAIR_WINDOW_MS = 10 * 60 * 1000;

function metadataText(value: unknown) {
  if (value === null || value === undefined || value === "") return "";
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") return String(value);
  return "";
}

function runIdSlug(value: unknown) {
  return metadataText(value).toLowerCase().replace(/[^a-z0-9가-힣_-]+/gi, "-").replace(/-+/g, "-").replace(/^-|-$/g, "");
}

function explicitRecordRunId(record: BattleRecord) {
  return runIdSlug(record.metadata?.battleRunId || record.metadata?.sessionStartedAt);
}

function recordTimeMs(record: BattleRecord) {
  const parsed = new Date(record.updatedAt || record.createdAt).getTime();
  return Number.isNaN(parsed) ? 0 : parsed;
}

function fallbackRunId(record: BattleRecord) {
  return [
    record.participantType,
    record.participantId || record.id,
    record.updatedAt || record.createdAt,
  ]
    .filter(Boolean)
    .join(":");
}

function pairedRunId(scenarioId: string, records: BattleRecord[]) {
  const explicit = records.map(explicitRecordRunId).find(Boolean);
  if (explicit) return `${scenarioId}:${explicit}`;
  return `${scenarioId}:${records.map(fallbackRunId).join("|")}`;
}

export function isDemoLikeRecord(record: BattleRecord) {
  const joined = [
    record.sessionId,
    record.scenarioId,
    record.scenarioLabel,
    record.reason,
    metadataText(record.metadata?.evidenceSource),
    metadataText(record.metadata?.suiteId),
  ]
    .join(" ")
    .toLowerCase();
  return (
    joined.includes("smoke") ||
    joined.includes("evidence-demo") ||
    joined.includes("remote smoke") ||
    joined.includes("원격 저장 검증") ||
    joined.includes("cli 타이머 연동 검증")
  );
}

function pickRepresentative(records: BattleRecord[]): BattleRecord | null {
  if (!records.length) return null;
  const successes = records.filter(
    (record) => record.status === "SUCCESS" && typeof record.durationSeconds === "number",
  );
  if (successes.length) {
    return [...successes].sort((a, b) => b.updatedAt.localeCompare(a.updatedAt))[0];
  }
  return [...records].sort((a, b) => b.updatedAt.localeCompare(a.updatedAt))[0];
}

function decideVerdict(human: BattleRecord | null, gaia: BattleRecord | null): CaseVerdict {
  const humanWon = human?.status === "SUCCESS";
  const gaiaWon = gaia?.status === "SUCCESS";
  if (humanWon && gaiaWon) {
    const humanSeconds = human?.durationSeconds ?? Number.POSITIVE_INFINITY;
    const gaiaSeconds = gaia?.durationSeconds ?? Number.POSITIVE_INFINITY;
    if (humanSeconds < gaiaSeconds) return "HUMAN_FASTER";
    if (gaiaSeconds < humanSeconds) return "GAIA_FASTER";
    return "TIE";
  }
  if (humanWon) return "HUMAN_WIN";
  if (gaiaWon) return "GAIA_WIN";
  if (human && gaia) return "BOTH_FAILED";
  return "WAITING";
}

// Group records by execution attempt, not only by scenario. The same printed
// case can be drawn many times during the demo, and each run must remain
// visible instead of refreshing the previous row.
export function groupBattleCases(records: BattleRecord[]): BattleCase[] {
  const scenarioBuckets = new Map<string, BattleRecord[]>();
  for (const record of records.filter((entry) => !isDemoLikeRecord(entry))) {
    const key = record.scenarioId || "live-mission";
    scenarioBuckets.set(key, [...(scenarioBuckets.get(key) || []), record]);
  }

  const pairedGroups: Array<{ runId: string; records: BattleRecord[] }> = [];
  for (const [scenarioId, scenarioRecords] of scenarioBuckets.entries()) {
    const humans = scenarioRecords
      .filter((record) => record.participantType === "human")
      .sort((a, b) => recordTimeMs(a) - recordTimeMs(b));
    const gaias = scenarioRecords
      .filter((record) => record.participantType === "gaia")
      .sort((a, b) => recordTimeMs(a) - recordTimeMs(b));
    const usedGaiaIndexes = new Set<number>();

    for (const human of humans) {
      const humanRunId = explicitRecordRunId(human);
      let matchedIndex = -1;
      if (humanRunId) {
        matchedIndex = gaias.findIndex(
          (gaia, index) => !usedGaiaIndexes.has(index) && explicitRecordRunId(gaia) === humanRunId,
        );
      }
      if (matchedIndex < 0) {
        let bestDiff = Number.POSITIVE_INFINITY;
        for (let index = 0; index < gaias.length; index += 1) {
          if (usedGaiaIndexes.has(index)) continue;
          const diff = Math.abs(recordTimeMs(human) - recordTimeMs(gaias[index]));
          if (diff <= RUN_PAIR_WINDOW_MS && diff < bestDiff) {
            bestDiff = diff;
            matchedIndex = index;
          }
        }
      }

      const group = matchedIndex >= 0 ? [human, gaias[matchedIndex]] : [human];
      if (matchedIndex >= 0) usedGaiaIndexes.add(matchedIndex);
      pairedGroups.push({ runId: pairedRunId(scenarioId, group), records: group });
    }

    gaias.forEach((gaia, index) => {
      if (usedGaiaIndexes.has(index)) return;
      pairedGroups.push({ runId: pairedRunId(scenarioId, [gaia]), records: [gaia] });
    });
  }

  const cases = pairedGroups.map(({ runId, records: group }) => {
    const humans = group.filter((record) => record.participantType === "human");
    const gaias = group.filter((record) => record.participantType === "gaia");
    const bestHuman = pickRepresentative(humans);
    const bestGaia = pickRepresentative(gaias);
    const scenarioId = group.find((record) => record.scenarioId)?.scenarioId || "live-mission";
    const label =
      gaias.find((record) => record.scenarioLabel)?.scenarioLabel ||
      humans.find((record) => record.scenarioLabel)?.scenarioLabel ||
      scenarioId;
    const latestAt = group.reduce((latest, record) => (record.updatedAt > latest ? record.updatedAt : latest), "");
    return {
      runId,
      scenarioId,
      label,
      humans,
      gaias,
      bestHuman,
      bestGaia,
      verdict: decideVerdict(bestHuman, bestGaia),
      latestAt,
    };
  });

  return cases.sort((a, b) => b.latestAt.localeCompare(a.latestAt));
}
