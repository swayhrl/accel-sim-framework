#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = REPO_ROOT / ".local_reports"
LOG_DIR = REPO_ROOT / ".local_logs"
RUN_DIR = REPO_ROOT / ".local_runs"


def ensure_local_dirs() -> None:
    REPORT_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)
    RUN_DIR.mkdir(exist_ok=True)


def ts() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def clean(value: object) -> str:
    return str(value or "").replace("\r", "").replace("\n", "").strip()


def rel(path: str | Path) -> str:
    p = Path(path)
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


def repo_path(value: str | Path) -> Path:
    p = Path(clean(value))
    return p if p.is_absolute() else REPO_ROOT / p


def latest(pattern: str) -> Path | None:
    ensure_local_dirs()
    files = sorted(REPORT_DIR.glob(pattern), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def read_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())


def write_json(path: str | Path, data: object) -> None:
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def write_csv(path: str | Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with Path(path).open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: clean(row.get(field, "")) for field in fields})


def read_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="") as f:
        return list(csv.DictReader(f))


def command_text(args: list[str]) -> str:
    return " ".join(args)


def run_logged(args: list[str], log_path: str | Path, cwd: str | Path | None = None, env: dict[str, str] | None = None) -> dict[str, object]:
    start = time.time()
    start_iso = iso_now()
    log = Path(log_path)
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w") as f:
        f.write(f"command: {command_text(args)}\n")
        f.write(f"cwd: {cwd or REPO_ROOT}\n")
        f.write(f"start: {start_iso}\n\n")
        proc = subprocess.run(args, cwd=cwd or REPO_ROOT, stdout=f, stderr=subprocess.STDOUT, env=env)
        f.write(f"\nend: {iso_now()}\nreturn_code: {proc.returncode}\n")
    return {
        "command": command_text(args),
        "cwd": str(cwd or REPO_ROOT),
        "log_path": rel(log),
        "start_time": start_iso,
        "end_time": iso_now(),
        "wall_seconds": str(int(time.time() - start)),
        "return_code": str(proc.returncode),
    }


def git_output(args: list[str]) -> str:
    return subprocess.getoutput("git " + " ".join(args))


def git_status_short() -> str:
    return subprocess.getoutput("git status --short")


def baseline_commit() -> str:
    return subprocess.getoutput("git rev-parse HEAD").strip()


def selected_workload() -> dict:
    path = latest("A16A_latpc_selected_workload_*.json")
    if not path:
        return {
            "selected_workload": "nw",
            "paper_workload": "NW",
            "kernelslist_path": "",
            "config_path": "gpu-simulator/gpgpu-sim/configs/tested-cfgs/SM7_QV100/gpgpusim.config",
            "_source_path": "",
            "status": "FALLBACK_NO_A16_SELECTION",
        }
    data = read_json(path)
    data["_source_path"] = rel(path)
    return data


def source_accelsim_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = os.environ.copy()
    try:
        raw = subprocess.check_output(
            ["bash", "-lc", f"cd {REPO_ROOT} && source scripts/accelsim/accelsim_env.sh >/dev/null && env -0"],
            stderr=subprocess.DEVNULL,
        )
        for item in raw.split(b"\0"):
            if item and b"=" in item:
                key, value = item.split(b"=", 1)
                env[key.decode()] = value.decode(errors="replace")
    except Exception:
        pass
    if extra:
        env.update(extra)
    return env


def write_stage_report(
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
    end_iso = iso_now()
    wall = int(time.time() - start_epoch)
    body = [
        f"# {title}",
        "",
        f"- Status: {status}",
        f"- Start time: {start_iso}",
        f"- End time: {end_iso}",
        f"- Wall clock seconds: {wall}",
        f"- Baseline commit at stage start: {baseline_commit()}",
        f"- Blocker: {blocker}",
        "",
        "## Commands",
        "",
    ]
    body.extend([f"- `{cmd}`" for cmd in commands] or ["- none"])
    body.extend(["", "## Inputs", ""])
    body.extend([f"- `{item}`" for item in inputs] or ["- none"])
    body.extend(["", "## Outputs", ""])
    body.extend([f"- `{item}`" for item in outputs] or ["- none"])
    body.extend(["", "## Limitations", ""])
    body.extend([f"- {item}" for item in limitations] or ["- none"])
    if extra:
        body.extend(["", extra.strip(), ""])
    body.extend(["", "## Git Status", "", "```", git_status_short(), "```", ""])
    Path(path).write_text("\n".join(body))


def extract_stat_lines(log_path: str | Path, prefix: str = "latpc_") -> list[dict[str, str]]:
    path = Path(log_path)
    rows: list[dict[str, str]] = []
    if not path.exists():
        return rows
    pattern = re.compile(r"^\s*(" + re.escape(prefix) + r"[A-Za-z0-9_./-]*)\s*(?:=|:)\s*(.+?)\s*$")
    for line_no, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        match = pattern.match(line)
        if match:
            rows.append({"stat_key": match.group(1), "stat_value": match.group(2).strip(), "line_no": str(line_no), "log_path": rel(path)})
    return rows
