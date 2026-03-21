import importlib
import json
from pathlib import Path

from zpe_finance.comet_logging import CometRunLogger


class _FakeExperimentConfig:
    def __init__(self, *, name, tags):
        self.name = name
        self.tags = list(tags)


class _FakeExperiment:
    def __init__(self):
        self.logged_parameters = []
        self.logged_metrics = []
        self.logged_others = []
        self.logged_assets = []
        self.ended = False
        self.url = "https://www.comet.com/zer0pa/zpe-ft/experiments/fake"

    def get_key(self):
        return "fake-experiment-key"

    def log_parameters(self, payload):
        self.logged_parameters.append(payload)

    def log_metrics(self, payload):
        self.logged_metrics.append(payload)

    def log_other(self, key, value):
        self.logged_others.append((key, value))

    def log_asset(self, filename, metadata=None):
        self.logged_assets.append((filename, metadata))

    def end(self):
        self.ended = True


class _FakeCometModule:
    ExperimentConfig = _FakeExperimentConfig

    def __init__(self):
        self.experiment = _FakeExperiment()
        self.calls = []

    def start(self, **kwargs):
        self.calls.append(kwargs)
        return self.experiment


def test_comet_logger_writes_disabled_status_without_api_key(monkeypatch, tmp_path: Path):
    monkeypatch.delenv("COMET_API_KEY", raising=False)

    logger = CometRunLogger.start(tmp_path, "run_real_market_refresh")
    status_path = logger.finalize(status="completed")
    status = json.loads(status_path.read_text(encoding="utf-8"))

    assert status["enabled"] is False
    assert status["reason"] == "api_key_missing"
    assert status["status"] == "completed"


def test_comet_logger_logs_parameters_metrics_and_assets(monkeypatch, tmp_path: Path):
    fake_module = _FakeCometModule()

    def fake_import(name: str):
        if name == "comet_ml":
            return fake_module
        return importlib.import_module(name)

    monkeypatch.setenv("COMET_API_KEY", "test-key")
    monkeypatch.setenv("COMET_WORKSPACE", "zer0pa")
    monkeypatch.setenv("COMET_PROJECT_NAME", "zpe-ft")
    monkeypatch.setattr(importlib, "import_module", fake_import)

    asset_path = tmp_path / "artifact.json"
    asset_path.write_text("{\"ok\": true}\n", encoding="utf-8")

    logger = CometRunLogger.start(
        tmp_path,
        "freeze_real_market_corpus",
        run_name="freeze-real-market",
        tags=("phase-06", "freeze"),
        parameters={"artifact_root": str(tmp_path)},
        others={"gate": "EV-01"},
    )
    logger.log_metrics({"series_count": 2, "pass": True})
    status_path = logger.finalize(
        status="completed",
        metrics={"latency_p95_ms": 0.24},
        others={"verdict": "INCONCLUSIVE"},
        assets=(asset_path,),
    )

    status = json.loads(status_path.read_text(encoding="utf-8"))
    assert fake_module.calls[0]["workspace"] == "zer0pa"
    assert fake_module.calls[0]["project_name"] == "zpe-ft"
    assert fake_module.experiment.logged_parameters[0]["artifact_root"] == str(tmp_path)
    assert {"series_count": 2.0, "pass": 1.0} in fake_module.experiment.logged_metrics
    assert {"latency_p95_ms": 0.24} in fake_module.experiment.logged_metrics
    assert any(key == "gate" and value == "EV-01" for key, value in fake_module.experiment.logged_others)
    assert any(key == "run_status" and value == "completed" for key, value in fake_module.experiment.logged_others)
    assert fake_module.experiment.logged_assets[0][0] == str(asset_path)
    assert fake_module.experiment.ended is True
    assert status["enabled"] is True
    assert status["experiment_key"] == "fake-experiment-key"
