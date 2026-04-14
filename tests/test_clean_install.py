import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


def test_clean_install_from_built_wheel(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    dist_dir = tmp_path / "dist"
    venv_dir = tmp_path / "venv"

    build_proc = _run(
        [sys.executable, "-m", "build", "--sdist", "--outdir", str(dist_dir)],
        repo_root,
    )
    assert build_proc.returncode == 0, build_proc.stdout + build_proc.stderr

    venv_proc = _run([sys.executable, "-m", "venv", str(venv_dir)], repo_root)
    assert venv_proc.returncode == 0, venv_proc.stdout + venv_proc.stderr

    child_python = venv_dir / "bin" / "python"
    pip_proc = _run([str(child_python), "-m", "pip", "install", "--upgrade", "pip"], repo_root)
    assert pip_proc.returncode == 0, pip_proc.stdout + pip_proc.stderr

    sdist_path = next(dist_dir.glob("zpe_ft-*.tar.gz"))
    install_proc = _run([str(child_python), "-m", "pip", "install", str(sdist_path)], repo_root)
    assert install_proc.returncode == 0, install_proc.stdout + install_proc.stderr

    import_proc = _run(
        [
            str(child_python),
            "-c",
            "import zpe_finance; print(zpe_finance.__all__[:4])",
        ],
        repo_root,
    )
    assert import_proc.returncode == 0, import_proc.stdout + import_proc.stderr
