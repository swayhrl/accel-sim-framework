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
NESTED_ROOT = REPO_ROOT / "gpu-simulator/gpgpu-sim"
REPORT_DIR = REPO_ROOT / ".local_reports"
LOG_DIR = REPO_ROOT / ".local_logs"
RUN_DIR = REPO_ROOT / ".local_runs"


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


def git_status(repo: Path = REPO_ROOT) -> str:
    return subprocess.getoutput(f"git -C {repo} status --short")


def git_head(repo: Path = REPO_ROOT) -> str:
    return subprocess.getoutput(f"git -C {repo} rev-parse HEAD").strip()


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


def selected_workload() -> dict:
    path = latest("A16A_latpc_selected_workload_*.json")
    if path:
        data = read_json(path)
        data["_source_path"] = rel(path)
        return data
    return {"selected_workload": "nw", "paper_workload": "NW", "kernelslist_path": "", "config_path": "gpu-simulator/gpgpu-sim/configs/tested-cfgs/SM7_QV100/gpgpusim.config", "_source_path": ""}


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


def run_logged(args: list[str], log: Path, cwd: Path = REPO_ROOT, env: dict[str, str] | None = None, timeout_sec: int | None = None) -> dict[str, str]:
    start = time.time()
    start_iso = iso()
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w") as f:
        f.write(f"command: {' '.join(args)}\n")
        f.write(f"cwd: {cwd}\n")
        f.write(f"start: {start_iso}\n\n")
        proc = subprocess.run(args, cwd=cwd, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=timeout_sec)
        f.write(f"\nend: {iso()}\nreturn_code: {proc.returncode}\n")
    return {"command": " ".join(args), "cwd": rel(cwd), "log_path": rel(log), "start_time": start_iso, "end_time": iso(), "wall_seconds": str(int(time.time() - start)), "return_code": str(proc.returncode)}


def stage_report(
    path: str | Path,
    title: str,
    status: str,
    start_iso: str,
    start_epoch: float,
    commands: list[str],
    outputs: list[str],
    summary: str,
    blocker: str,
    limitations: list[str],
    extra: str = "",
) -> None:
    body = [
        f"# {title}",
        "",
        f"- Start time: {start_iso}",
        f"- End time: {iso()}",
        f"- Wall seconds: {int(time.time() - start_epoch)}",
        f"- Status: {status}",
        f"- Blocker: {blocker}",
        "",
        "## Commands",
        "",
    ]
    body.extend([f"- `{cmd}`" for cmd in commands] or ["- none"])
    body.extend(["", "## Output Summary", "", summary or "none", "", "## Outputs", ""])
    body.extend([f"- `{o}`" for o in outputs] or ["- none"])
    body.extend(["", "## Limitations", ""])
    body.extend([f"- {l}" for l in limitations] or ["- none"])
    if extra:
        body.extend(["", extra.strip(), ""])
    body.extend(["", "## Git Status", "", "Top-level:", "", "```", git_status(REPO_ROOT), "```", "", "Nested gpu-simulator/gpgpu-sim:", "", "```", git_status(NESTED_ROOT), "```", ""])
    Path(path).write_text("\n".join(body))


_STAT_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_./-]*)\s*(?:=|:|\s)\s*([-+]?[0-9][0-9.eE+-]*).*$")


def parse_stats(path: str | Path) -> dict[str, str]:
    p = Path(path)
    out: dict[str, str] = {}
    if not p.exists():
        return out
    for line in p.read_text(errors="replace").splitlines():
        match = _STAT_RE.match(line)
        if match:
            out[match.group(1)] = match.group(2)
    return out


def num(stats: dict[str, str], key: str, default: float = 0.0) -> float:
    try:
        return float(stats.get(key, default))
    except ValueError:
        return default


def div(n: float, d: float) -> str:
    if d == 0:
        return ""
    return f"{n / d:.12g}"


def prepare_run_dir(run_dir: Path, kernelslist: Path, config: Path, trace_config: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    link = run_dir / "traces"
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(kernelslist.parent)
    shutil.copytree(config.parent, run_dir, dirs_exist_ok=True, ignore=shutil.ignore_patterns("gpgpusim.config"))
    (run_dir / "gpgpusim.config").write_text(config.read_text(errors="replace").replace("\r", "") + "\n#SASS\n#SASS-Driven Accel-Sim\n\n" + trace_config.read_text(errors="replace").replace("\r", ""))


def run_nw_variant(stamp: str, stage: str, mode: str, env_vars: dict[str, str]) -> tuple[dict[str, str], dict[str, str]]:
    selected = selected_workload()
    kernels = repo_path(selected.get("kernelslist_path", ""))
    config = repo_path(selected.get("config_path", "gpu-simulator/gpgpu-sim/configs/tested-cfgs/SM7_QV100/gpgpusim.config"))
    trace_config = REPO_ROOT / "gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
    run_dir = RUN_DIR / f"{stage}_{stamp}" / mode
    prepare_run_dir(run_dir, kernels, config, trace_config)
    log = LOG_DIR / f"{stage}_{stamp}_{mode}.log"
    sim = REPO_ROOT / "gpu-simulator/bin/release/accel-sim.out"
    env = source_env({"ACCELSIM_ROUND": stage, **env_vars})
    info = run_logged(["timeout", os.environ.get("ACCELSIM_A24_TIMEOUT_SEC", "900"), str(sim), "-config", "./gpgpusim.config", "-trace", "./traces/kernelslist.g"], log, cwd=run_dir, env=env)
    return info, parse_stats(log)


def behavior_fields(stats: dict[str, str]) -> dict[str, str]:
    return {
        "cycles": stats.get("gpu_tot_sim_cycle", "NA"),
        "instructions": stats.get("gpu_tot_sim_insn", "NA"),
        "IPC": stats.get("gpu_tot_ipc", "NA"),
        "L2_accesses": stats.get("L2_total_cache_accesses", "NA"),
        "L2_misses": stats.get("L2_total_cache_misses", "NA"),
    }


def compare_behavior(baseline: dict[str, str], other: dict[str, str]) -> dict[str, bool]:
    b = behavior_fields(baseline)
    o = behavior_fields(other)
    result = {}
    for key in b:
        try:
            result[key] = abs(float(b[key]) - float(o[key])) <= (1e-9 if key == "IPC" else 0.0)
        except ValueError:
            result[key] = False
    return result
