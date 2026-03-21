"""Minimal Comet logging sidecar for FT operational runs."""

from __future__ import annotations

import importlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


DEFAULT_WORKSPACE = "zer0pa"
DEFAULT_PROJECT = "zpe-ft"


def _json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    return str(value)


@dataclass
class CometRunLogger:
    """Small wrapper around the Comet SDK with a no-op fallback."""

    artifact_root: Path
    script_name: str
    enabled: bool
    reason: str
    workspace: str
    project_name: str
    experiment: Any | None = None
    experiment_key: str = ""
    experiment_url: str = ""

    @classmethod
    def start(
        cls,
        artifact_root: Path,
        script_name: str,
        *,
        run_name: str = "",
        tags: Iterable[str] = (),
        parameters: Mapping[str, Any] | None = None,
        others: Mapping[str, Any] | None = None,
    ) -> "CometRunLogger":
        api_key = os.environ.get("COMET_API_KEY", "").strip()
        workspace = os.environ.get("COMET_WORKSPACE", DEFAULT_WORKSPACE).strip() or DEFAULT_WORKSPACE
        project_name = os.environ.get("COMET_PROJECT_NAME", DEFAULT_PROJECT).strip() or DEFAULT_PROJECT
        if not api_key:
            return cls(
                artifact_root=artifact_root,
                script_name=script_name,
                enabled=False,
                reason="api_key_missing",
                workspace=workspace,
                project_name=project_name,
            )

        try:
            comet_ml = importlib.import_module("comet_ml")
        except ImportError:
            return cls(
                artifact_root=artifact_root,
                script_name=script_name,
                enabled=False,
                reason="sdk_missing",
                workspace=workspace,
                project_name=project_name,
            )

        experiment_config = None
        experiment_name = run_name.strip() or f"{script_name}:{artifact_root.name}"
        if hasattr(comet_ml, "ExperimentConfig"):
            experiment_config = comet_ml.ExperimentConfig(
                name=experiment_name,
                tags=list(tags),
            )

        experiment = comet_ml.start(
            api_key=api_key,
            workspace=workspace,
            project_name=project_name,
            experiment_config=experiment_config,
        )
        logger = cls(
            artifact_root=artifact_root,
            script_name=script_name,
            enabled=True,
            reason="online",
            workspace=workspace,
            project_name=project_name,
            experiment=experiment,
            experiment_key=_string_attr(experiment, "get_key"),
            experiment_url=_string_attr(experiment, "get_url") or str(getattr(experiment, "url", "")),
        )
        if not experiment_config and tags and hasattr(experiment, "add_tags"):
            experiment.add_tags(list(tags))
        if parameters:
            logger.log_parameters(parameters)
        if others:
            logger.log_others(others)
        return logger

    def log_parameters(self, parameters: Mapping[str, Any]) -> None:
        if not self.enabled or not parameters:
            return
        if hasattr(self.experiment, "log_parameters"):
            self.experiment.log_parameters({str(key): _json_safe(value) for key, value in parameters.items()})
            return
        for key, value in parameters.items():
            if hasattr(self.experiment, "log_parameter"):
                self.experiment.log_parameter(str(key), _json_safe(value))

    def log_metrics(self, metrics: Mapping[str, Any]) -> None:
        if not self.enabled or not metrics:
            return
        serializable: dict[str, float] = {}
        for key, value in metrics.items():
            if isinstance(value, bool):
                serializable[str(key)] = float(int(value))
            elif isinstance(value, (int, float)):
                serializable[str(key)] = float(value)
        if serializable and hasattr(self.experiment, "log_metrics"):
            self.experiment.log_metrics(serializable)

    def log_others(self, values: Mapping[str, Any]) -> None:
        if not self.enabled or not values or not hasattr(self.experiment, "log_other"):
            return
        for key, value in values.items():
            self.experiment.log_other(str(key), _json_safe(value))

    def log_assets(self, paths: Iterable[Path]) -> list[str]:
        logged: list[str] = []
        if not self.enabled or not hasattr(self.experiment, "log_asset"):
            return logged
        for path in paths:
            resolved = Path(path)
            if not resolved.exists() or not resolved.is_file():
                continue
            self.experiment.log_asset(str(resolved), metadata={"script_name": self.script_name})
            logged.append(str(resolved))
        return logged

    def finalize(
        self,
        *,
        status: str,
        metrics: Mapping[str, Any] | None = None,
        others: Mapping[str, Any] | None = None,
        assets: Iterable[Path] = (),
    ) -> Path:
        logged_assets = self.log_assets(assets)
        self.log_metrics(metrics or {})
        self.log_others({"run_status": status, **(others or {})})
        if self.enabled and hasattr(self.experiment, "end"):
            self.experiment.end()

        payload = {
            "script_name": self.script_name,
            "enabled": self.enabled,
            "reason": self.reason,
            "workspace": self.workspace,
            "project_name": self.project_name,
            "experiment_key": self.experiment_key,
            "experiment_url": self.experiment_url,
            "status": status,
            "logged_assets": logged_assets,
            "metrics": _json_safe(metrics or {}),
            "others": _json_safe(others or {}),
        }
        safe_name = self.script_name.replace("/", "_").replace(" ", "_")
        status_path = self.artifact_root / f"comet_status_{safe_name}.json"
        status_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return status_path


def _string_attr(obj: Any, attr_name: str) -> str:
    attr = getattr(obj, attr_name, None)
    if not callable(attr):
        return ""
    value = attr()
    return str(value) if value is not None else ""
