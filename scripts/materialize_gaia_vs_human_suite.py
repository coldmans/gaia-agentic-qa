#!/usr/bin/env python3
"""Materialize an immutable benchmark suite from the GUI battle manifest."""
from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = WORKSPACE_ROOT / "gaia" / "tests" / "scenarios" / "gaia_vs_human_manifest.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def materialize_suite(
    manifest_path: Path,
    *,
    excluded_site_keys: Iterable[str] = (),
    workspace_root: Path = WORKSPACE_ROOT,
) -> dict[str, Any]:
    manifest = _load_json(manifest_path)
    excluded = {str(value).strip() for value in excluded_site_keys if str(value).strip()}
    sites = manifest.get("sites")
    if not isinstance(sites, list):
        raise ValueError(f"manifest sites must be an array: {manifest_path}")

    scenarios: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    included_sites: list[str] = []
    for site in sites:
        if not isinstance(site, dict):
            raise ValueError("every manifest site must be an object")
        site_key = str(site.get("site_key") or "").strip()
        if not site_key:
            raise ValueError("manifest site is missing site_key")
        if site_key in excluded:
            continue

        suite_rel = str(site.get("suite_path") or "").strip()
        allowed_ids = [str(value).strip() for value in site.get("allowed_scenarios") or [] if str(value).strip()]
        if not suite_rel or not allowed_ids:
            raise ValueError(f"site {site_key} needs suite_path and allowed_scenarios")
        suite_path = (workspace_root / suite_rel).resolve()
        suite_payload = _load_json(suite_path)
        source_rows = suite_payload.get("scenarios")
        if not isinstance(source_rows, list):
            raise ValueError(f"suite scenarios must be an array: {suite_path}")
        source_by_id = {
            str(row.get("id") or "").strip(): row
            for row in source_rows
            if isinstance(row, dict) and str(row.get("id") or "").strip()
        }

        included_sites.append(site_key)
        for scenario_id in allowed_ids:
            if scenario_id in selected_ids:
                raise ValueError(f"duplicate scenario id in manifest: {scenario_id}")
            source = source_by_id.get(scenario_id)
            if source is None:
                raise ValueError(f"scenario {scenario_id} not found in {suite_rel}")
            row = deepcopy(source)
            row["source_site_key"] = site_key
            row["source_suite_path"] = suite_rel
            scenarios.append(row)
            selected_ids.add(scenario_id)

    return {
        "schema_version": "gaia.benchmark-suite.v1",
        "suite_id": f"gaia_vs_human_{len(scenarios)}_portfolio",
        "site": {"name": "GAIA vs Human portfolio benchmark"},
        "selection": {
            "manifest_path": str(manifest_path.resolve().relative_to(workspace_root.resolve())),
            "excluded_site_keys": sorted(excluded),
            "included_site_keys": included_sites,
            "scenario_ids": [str(row["id"]) for row in scenarios],
        },
        "scenarios": scenarios,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--exclude-site-key", action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    payload = materialize_suite(
        args.manifest.expanduser().resolve(),
        excluded_site_keys=args.exclude_site_key,
    )
    output_path = args.output.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"materialized {len(payload['scenarios'])} scenarios -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
