from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.materialize_gaia_vs_human_suite import materialize_suite


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_materialize_suite_preserves_manifest_order_and_excludes_site(tmp_path) -> None:
    _write_json(
        tmp_path / "suite-a.json",
        {"scenarios": [{"id": "A2", "goal": "second"}, {"id": "A1", "goal": "first"}]},
    )
    _write_json(tmp_path / "suite-b.json", {"scenarios": [{"id": "B1", "goal": "excluded"}]})
    manifest = tmp_path / "manifest.json"
    _write_json(
        manifest,
        {
            "sites": [
                {"site_key": "a", "suite_path": "suite-a.json", "allowed_scenarios": ["A1", "A2"]},
                {"site_key": "b", "suite_path": "suite-b.json", "allowed_scenarios": ["B1"]},
            ]
        },
    )

    payload = materialize_suite(manifest, excluded_site_keys=["b"], workspace_root=tmp_path)

    assert payload["suite_id"] == "gaia_vs_human_2_portfolio"
    assert [row["id"] for row in payload["scenarios"]] == ["A1", "A2"]
    assert payload["scenarios"][0]["source_site_key"] == "a"
    assert payload["selection"]["excluded_site_keys"] == ["b"]


def test_materialize_suite_rejects_missing_allowed_scenario(tmp_path) -> None:
    _write_json(tmp_path / "suite.json", {"scenarios": [{"id": "A1"}]})
    manifest = tmp_path / "manifest.json"
    _write_json(
        manifest,
        {"sites": [{"site_key": "a", "suite_path": "suite.json", "allowed_scenarios": ["MISSING"]}]},
    )

    with pytest.raises(ValueError, match="MISSING"):
        materialize_suite(manifest, workspace_root=tmp_path)
