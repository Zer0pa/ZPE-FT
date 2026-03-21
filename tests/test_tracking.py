import sys
import types
from pathlib import Path

from zpe_finance.tracking import DEFAULT_OPIK_URL, create_tracking_bundle


class _FakeProject:
    def __init__(self, name: str, project_id: str, url: str):
        self.name = name
        self.id = project_id
        self.url = url


class _FakeCometAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.projects = {
            ("zer0pa", "zpe-ft"): _FakeProject(
                "zpe-ft",
                "classic-project-id",
                "https://www.comet.com/zer0pa/zpe-ft",
            )
        }

    def get_project(self, workspace: str, name: str):
        return self.projects.get((workspace, name))

    def create_project(self, workspace: str, name: str):
        self.projects[(workspace, name)] = _FakeProject(
            name,
            "created-project-id",
            f"https://www.comet.com/{workspace}/{name}",
        )


class _FakeExperiment:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.name = ""
        self.parameters = []
        self.metrics = []
        self.assets = []
        self.text = []
        self.url = "https://www.comet.com/zer0pa/zpe-ft/experiments/fake-tracking"
        self.ended = False

    def set_name(self, name: str):
        self.name = name

    def log_parameter(self, key: str, value):
        self.parameters.append((key, value))

    def log_metrics(self, metrics):
        self.metrics.append(metrics)

    def log_asset(self, path: str):
        self.assets.append(path)

    def log_text(self, text: str):
        self.text.append(text)

    def get_key(self):
        return "fake-classic-key"

    def end(self):
        self.ended = True


class _FakeApiError(Exception):
    def __init__(self, status_code: int):
        super().__init__(f"status={status_code}")
        self.status_code = status_code


class _FakeOpikProject:
    def __init__(self, name: str, project_id: str):
        self.name = name
        self.id = project_id


class _FakeProjectsClient:
    def __init__(self):
        self.project = _FakeOpikProject("zpe-ft", "opik-project-id")

    def retrieve_project(self, *, name: str):
        if name != self.project.name:
            raise _FakeApiError(404)
        return self.project

    def create_project(self, *, name: str):
        self.project = _FakeOpikProject(name, "created-opik-project-id")


class _FakeTrace:
    def __init__(self):
        self.id = "trace-123"
        self.metadata = []
        self.output = None

    def log_metadata(self, metadata):
        self.metadata.append(metadata)

    def end(self, *, output):
        self.output = output


class _FakeOpikClient:
    def __init__(self, *, project_name: str, workspace: str, host: str, api_key=None, **kwargs):
        self.project_name = project_name
        self.workspace = workspace
        self.host = host
        self.api_key = api_key
        self.kwargs = kwargs
        self.rest_client = types.SimpleNamespace(projects=_FakeProjectsClient())
        self._config = types.SimpleNamespace(url_override=host)
        self.trace_calls = []
        self.flushed = False
        self.ended = False

    def auth_check(self):
        return None

    def get_project_url(self, project_name: str):
        return f"{self.host}/projects/{project_name}"

    def trace(self, *, name: str, project_name: str, metadata, input, thread_id: str):
        self.trace_calls.append(
            {
                "name": name,
                "project_name": project_name,
                "metadata": metadata,
                "input": input,
                "thread_id": thread_id,
            }
        )
        return _FakeTrace()

    def flush(self):
        self.flushed = True

    def end(self):
        self.ended = True


def _install_fake_tracking_modules(monkeypatch):
    comet_ml_module = types.ModuleType("comet_ml")
    comet_ml_module.Experiment = _FakeExperiment
    comet_ml_api_module = types.ModuleType("comet_ml.api")
    comet_ml_api_module.API = _FakeCometAPI

    opik_module = types.ModuleType("opik")
    opik_module.Opik = _FakeOpikClient
    opik_error_module = types.ModuleType("opik.rest_api.core.api_error")
    opik_error_module.ApiError = _FakeApiError
    opik_api_objects = types.ModuleType("opik.api_objects")
    opik_api_objects.opik_client = types.SimpleNamespace(
        url_helpers=types.SimpleNamespace(
            get_project_url_by_trace_id=lambda *, trace_id, url_override: f"{url_override}/traces/{trace_id}"
        )
    )

    monkeypatch.setitem(sys.modules, "comet_ml", comet_ml_module)
    monkeypatch.setitem(sys.modules, "comet_ml.api", comet_ml_api_module)
    monkeypatch.setitem(sys.modules, "opik", opik_module)
    monkeypatch.setitem(sys.modules, "opik.rest_api.core.api_error", opik_error_module)
    monkeypatch.setitem(sys.modules, "opik.api_objects", opik_api_objects)


def test_create_tracking_bundle_uses_finance_defaults_and_finishes(monkeypatch, tmp_path: Path):
    _install_fake_tracking_modules(monkeypatch)
    monkeypatch.setenv("COMET_API_KEY", "classic-key")
    monkeypatch.setenv("OPIK_API_KEY", "opik-key")
    monkeypatch.delenv("COMET_PROJECT_NAME", raising=False)
    monkeypatch.delenv("OPIK_PROJECT_NAME", raising=False)
    monkeypatch.delenv("COMET_WORKSPACE", raising=False)
    monkeypatch.delenv("OPIK_WORKSPACE", raising=False)
    monkeypatch.delenv("OPIK_URL_OVERRIDE", raising=False)

    asset_path = tmp_path / "artifact.json"
    asset_path.write_text("{\"ok\": true}\n", encoding="utf-8")

    bundle = create_tracking_bundle(
        run_name="phase06-tracking-probe",
        input_payload={"gate": "EV-01"},
        metadata={"lane": "finance"},
    )
    assert bundle.workspace == "zer0pa"
    assert bundle.classic_project == "zpe-ft"
    assert bundle.opik_project == "zpe-ft"
    assert bundle.opik_host == DEFAULT_OPIK_URL
    assert bundle.classic_check.status == "EXISTS"
    assert bundle.opik_check.status == "EXISTS"
    assert bundle.comet.enabled is True
    assert bundle.opik.enabled is True

    bundle.log_tool_result("task01", {"latency_ms": 1.5}, {"series_count": 33})
    result = bundle.finish(
        artifact_paths=[str(asset_path)],
        output_payload={"status": "completed"},
    )

    assert result["classic_experiment_key"] == "fake-classic-key"
    assert result["classic_experiment_url"].endswith("/fake-tracking")
    assert result["opik_trace_id"] == "trace-123"
    assert result["opik_trace_url"] == f"{DEFAULT_OPIK_URL}/traces/trace-123"

    experiment = bundle.comet.experiment
    assert experiment is not None
    assert ("task01.series_count", 33) in experiment.parameters
    assert {"task01/latency_ms": 1.5} in experiment.metrics
    assert str(asset_path) in experiment.assets

    trace = bundle.opik_trace
    assert trace is not None
    assert trace.metadata[-1]["metrics"] == {"task01/latency_ms": 1.5}
    assert trace.output == {"status": "completed"}


def test_create_tracking_bundle_disables_adapters_without_keys(monkeypatch):
    _install_fake_tracking_modules(monkeypatch)
    monkeypatch.delenv("COMET_API_KEY", raising=False)
    monkeypatch.delenv("OPIK_API_KEY", raising=False)

    bundle = create_tracking_bundle(
        run_name="phase06-tracking-disabled",
        input_payload={"gate": "EV-01"},
        metadata={"lane": "finance"},
    )

    assert bundle.classic_check.status == "EXISTS"
    assert bundle.opik_check.status == "EXISTS"
    assert bundle.comet.enabled is False
    assert bundle.opik.enabled is False
