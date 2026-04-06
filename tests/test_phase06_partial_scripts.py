import importlib.util
import sys
from datetime import date
from pathlib import Path

import pandas as pd


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_normalize_yfinance_frame_clamps_bar_bounds():
    repo_root = Path(__file__).resolve().parents[1]
    module = _load_module(repo_root / "scripts" / "run_phase06_partial.py", "run_phase06_partial_test")

    frame = pd.DataFrame(
        {
            "Open": [10.0],
            "High": [9.0],
            "Low": [11.0],
            "Close": [12.0],
            "Volume": [100.0],
        },
        index=pd.to_datetime(["2026-04-06T00:00:00Z"], utc=True),
    )

    normalized = module.normalize_yfinance_frame(frame, "SPY", pd)
    assert float(normalized.iloc[0]["open"]) == 10.0
    assert float(normalized.iloc[0]["close"]) == 12.0
    assert float(normalized.iloc[0]["low"]) == 10.0
    assert float(normalized.iloc[0]["high"]) == 12.0


def test_fetch_dukascopy_session_candidates_skip_weekends():
    repo_root = Path(__file__).resolve().parents[1]
    module = _load_module(repo_root / "scripts" / "fetch_dukascopy_ticks.py", "fetch_dukascopy_ticks_test")

    sessions = module._session_candidates(date(2026, 4, 6), 5)
    assert [item.isoformat() for item in sessions] == [
        "2026-03-31",
        "2026-04-01",
        "2026-04-02",
        "2026-04-03",
        "2026-04-06",
    ]


def test_check_truth_surface_report_distinguishes_ready_vs_blocked(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    module = _load_module(repo_root / "scripts" / "check_truth_surface.py", "check_truth_surface_test")

    blocked_report = module.build_truth_surface_report(
        {
            "catalog_id": "blocked",
            "status": "PENDING_LABEL_AUDIT",
            "query_slots": [{"slot_id": "slot-001", "truth_status": "PENDING_LABEL_AUDIT"}],
        },
        tmp_path / "blocked.json",
    )
    ready_report = module.build_truth_surface_report(
        {
            "catalog_id": "ready",
            "status": "READY",
            "queries": [{"query_id": "query-001", "truth_status": "READY", "audit_refs": ["analyst-001"]}],
        },
        tmp_path / "ready.json",
    )

    assert blocked_report["status"] == "blocked_missing_authority_truth"
    assert blocked_report["blocked_count"] == 1
    assert ready_report["status"] == "ready"
    assert ready_report["ready_count"] == 1
