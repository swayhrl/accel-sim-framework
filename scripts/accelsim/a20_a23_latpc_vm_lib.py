#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = REPO_ROOT / ".local_reports"
LOG_DIR = REPO_ROOT / ".local_logs"
RUN_DIR = REPO_ROOT / ".local_runs"
NESTED_ROOT = REPO_ROOT / "gpu-simulator/gpgpu-sim"


def ensure_dirs() -> None:
    REPORT_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)
    RUN_DIR.mkdir(exist_ok=True)
    (REPO_ROOT / "review_packs").mkdir(exist_ok=True)


def ts() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def clean(value: object) -> str:
    return str(value or "").replace("\r", "").replace("\n", "").strip()


def rel(path: str | Path) -> str:
    p = Path(path)
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


def latest(pattern: str) -> Path | None:
    ensure_dirs()
    paths = sorted(REPORT_DIR.glob(pattern), key=lambda p: p.stat().st_mtime)
    return paths[-1] if paths else None


def write_csv(path: str | Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with Path(path).open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: clean(row.get(field, "")) for field in fields})


def read_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="") as f:
        return list(csv.DictReader(f))


def write_json(path: str | Path, data: object) -> None:
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def read_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())


def git_status(repo: Path = REPO_ROOT) -> str:
    return subprocess.getoutput(f"git -C {repo} status --short")


def git_head(repo: Path = REPO_ROOT) -> str:
    return subprocess.getoutput(f"git -C {repo} rev-parse HEAD").strip()


def stage_report(
    path: str | Path,
    title: str,
    status: str,
    start_iso: str,
    start_epoch: float,
    commands: list[str],
    inputs: list[str],
    outputs: list[str],
    blocker: str,
    limitations: list[str],
    extra: str = "",
) -> None:
    body = [
        f"# {title}",
        "",
        f"- Status: {status}",
        f"- Start time: {start_iso}",
        f"- End time: {iso()}",
        f"- Wall clock seconds: {int(time.time() - start_epoch)}",
        f"- Top-level commit: {git_head(REPO_ROOT)}",
        f"- Nested simulator commit: {git_head(NESTED_ROOT)}",
        f"- Blocker: {blocker}",
        "",
        "## Commands",
        "",
    ]
    body.extend([f"- `{cmd}`" for cmd in commands] or ["- none"])
    body.extend(["", "## Inputs", ""])
    body.extend([f"- `{i}`" for i in inputs] or ["- none"])
    body.extend(["", "## Outputs", ""])
    body.extend([f"- `{o}`" for o in outputs] or ["- none"])
    body.extend(["", "## Limitations", ""])
    body.extend([f"- {l}" for l in limitations] or ["- none"])
    if extra:
        body.extend(["", extra.strip(), ""])
    body.extend(["", "## Git Status", "", "Top-level:", "", "```", git_status(REPO_ROOT), "```", "", "Nested gpu-simulator/gpgpu-sim:", "", "```", git_status(NESTED_ROOT), "```", ""])
    Path(path).write_text("\n".join(body))


def selected_workload() -> dict:
    path = latest("A16A_latpc_selected_workload_*.json")
    if path:
        data = read_json(path)
        data["_source_path"] = rel(path)
        return data
    return {"selected_workload": "nw", "paper_workload": "NW", "_source_path": "", "kernelslist_path": "", "config_path": "gpu-simulator/gpgpu-sim/configs/tested-cfgs/SM7_QV100/gpgpusim.config"}


def repo_path(value: str | Path) -> Path:
    p = Path(clean(value))
    return p if p.is_absolute() else REPO_ROOT / p


def source_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = os.environ.copy()
    try:
        raw = subprocess.check_output(["bash", "-lc", f"cd {REPO_ROOT} && source scripts/accelsim/accelsim_env.sh >/dev/null && env -0"], stderr=subprocess.DEVNULL)
        for item in raw.split(b"\0"):
            if item and b"=" in item:
                key, value = item.split(b"=", 1)
                env[key.decode()] = value.decode(errors="replace")
    except Exception:
        pass
    if extra:
        env.update(extra)
    return env


def run_logged(args: list[str], log: Path, cwd: Path = REPO_ROOT, env: dict[str, str] | None = None) -> dict[str, str]:
    start = time.time()
    start_iso = iso()
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w") as f:
        f.write(f"command: {' '.join(args)}\n")
        f.write(f"cwd: {cwd}\n")
        f.write(f"start: {start_iso}\n\n")
        proc = subprocess.run(args, cwd=cwd, env=env, stdout=f, stderr=subprocess.STDOUT)
        f.write(f"\nend: {iso()}\nreturn_code: {proc.returncode}\n")
    return {"command": " ".join(args), "cwd": rel(cwd), "log_path": rel(log), "start_time": start_iso, "end_time": iso(), "wall_seconds": str(int(time.time() - start)), "return_code": str(proc.returncode)}


def prepare_accelsim_run_dir(run_dir: Path, kernelslist: Path, config: Path, trace_config: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    link = run_dir / "traces"
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(kernelslist.parent)
    shutil.copytree(config.parent, run_dir, dirs_exist_ok=True, ignore=shutil.ignore_patterns("gpgpusim.config"))
    (run_dir / "gpgpusim.config").write_text(config.read_text(errors="replace").replace("\r", "") + "\n#SASS\n#SASS-Driven Accel-Sim\n\n" + trace_config.read_text(errors="replace").replace("\r", ""))


_ASSIGN_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_./-]*)\s*(?:=|:|\s)\s*([-+]?[0-9][0-9.eE+-]*).*$")


def parse_stats(log_path: str | Path) -> dict[str, str]:
    stats: dict[str, str] = {}
    path = Path(log_path)
    if not path.exists():
        return stats
    for line in path.read_text(errors="replace").splitlines():
        m = _ASSIGN_RE.match(line)
        if m:
            stats[m.group(1)] = m.group(2)
    return stats


def stat(stats: dict[str, str], *keys: str) -> str:
    for key in keys:
        if key in stats:
            return stats[key]
    return "NA"
