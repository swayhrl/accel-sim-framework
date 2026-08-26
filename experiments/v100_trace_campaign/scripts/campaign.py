#!/usr/bin/env python3
"""Serial, resumable NVBit trace campaign runner for the TLS/C2P V100 suite."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import threading
import time
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
CAMPAIGN_DIR = SCRIPT_DIR.parent
MANIFEST_PATH = CAMPAIGN_DIR / "manifest.json"
FREEZE_NAME = "frozen-reconstruction.json"
FRAMEWORK_IDENTITY_NAME = "trace-campaign-framework-source.json"

# AutoDL normally exposes CUDA only through interactive-shell startup files.
# The runner must also work after SSH disconnects or inside tmux.
_cuda_home = Path(os.environ.get("CUDA_HOME", "/usr/local/cuda"))
if (_cuda_home / "bin" / "nvcc").is_file():
    os.environ["PATH"] = str(_cuda_home / "bin") + os.pathsep + os.environ.get("PATH", "")


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_manifest() -> dict[str, Any]:
    with MANIFEST_PATH.open() as handle:
        manifest = json.load(handle)
    if manifest.get("schema") != "accel-sim-v100-trace-campaign-v1":
        raise RuntimeError("unsupported manifest schema")
    return manifest


def manifest_sha256() -> str:
    return sha256(MANIFEST_PATH)


def expand(value: str, work_root: Path) -> str:
    return value.replace("${WORK_ROOT}", str(work_root)).replace(
        "${INPUT_ROOT}", str(work_root / "inputs")
    )


def select_cases(manifest: dict[str, Any], selected: str) -> list[dict[str, Any]]:
    cases = manifest["cases"]
    if selected == "all":
        return cases
    wanted = {item.strip() for item in selected.split(",") if item.strip()}
    found = [case for case in cases if case["id"] in wanted]
    missing = wanted - {case["id"] for case in found}
    if missing:
        raise RuntimeError(f"unknown case(s): {', '.join(sorted(missing))}")
    return found


def command_output(argv: list[str], cwd: Path | None = None) -> str:
    try:
        return subprocess.check_output(argv, cwd=cwd, text=True, stderr=subprocess.STDOUT)
    except (OSError, subprocess.CalledProcessError) as exc:
        return f"<unavailable: {exc}>"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def framework_identity(framework_root: Path) -> dict[str, Any]:
    """Read deployment identity when AutoDL has only a minimal tracer tree."""
    path = framework_root / FRAMEWORK_IDENTITY_NAME
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid framework identity: {path}: {exc}") from exc
    if payload.get("schema") != "accel-sim-v100-framework-source-v1":
        raise RuntimeError(f"unsupported framework identity schema: {path}")
    return payload


class DiskGuard:
    def __init__(self, path: Path, min_gib: int, process: subprocess.Popen[str]):
        self.path = path
        self.min_gib = min_gib
        self.process = process
        self.triggered = False
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=2)

    def _run(self) -> None:
        while not self._stop.wait(30):
            free_gib = shutil.disk_usage(self.path).free // (1024**3)
            if free_gib < self.min_gib and self.process.poll() is None:
                self.triggered = True
                os.killpg(self.process.pid, signal.SIGTERM)
                return


def run_logged(
    argv: list[str],
    env: dict[str, str],
    cwd: Path,
    log_path: Path,
    min_free_gib: int | None,
) -> tuple[int, bool]:
    with log_path.open("w") as log:
        log.write("timestamp_utc=" + utc_now() + "\n")
        log.write("cwd=" + str(cwd) + "\n")
        log.write("argv=" + json.dumps(argv) + "\n")
        log.flush()
        process = subprocess.Popen(
            argv,
            cwd=cwd,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=True,
        )
        guard = DiskGuard(cwd, min_free_gib, process) if min_free_gib is not None else None
        if guard:
            guard.start()
        code = process.wait()
        if guard:
            guard.stop()
            return code, guard.triggered
        return code, False


def trace_ready(case_dir: Path) -> bool:
    traces = case_dir / "traces"
    kernelslist = traces / "kernelslist.g"
    if not kernelslist.is_file() or not (traces / "stats.csv").is_file():
        return False
    kernel_paths = [
        line.strip()
        for line in kernelslist.read_text().splitlines()
        if line.strip().startswith("kernel-")
    ]
    if not kernel_paths:
        return False
    for relative in kernel_paths:
        path = traces / relative
        if not path.is_file() or path.stat().st_size == 0:
            return False
        if relative.endswith(".xz"):
            # Do not decompress every large trace as part of the disk guard,
            # but reject an incomplete xz stream before raw trace evidence is
            # deleted.  The six-byte signature is sufficient to catch the
            # asynchronous zero-byte final-output failure seen on AutoDL.
            with path.open("rb") as handle:
                if handle.read(6) != b"\xfd7zXZ\x00":
                    return False
    return True


def archive_ready(work_root: Path, case_id: str) -> bool:
    archive = work_root / "archives" / f"{case_id}.tar.zst"
    digest = archive.with_suffix(archive.suffix + ".sha256")
    if archive.is_file() and digest.is_file():
        recorded = digest.read_text().split()[0] if digest.read_text().split() else ""
        if recorded == sha256(archive):
            return True
    # The external offloader writes this receipt only after rsync and a local
    # SHA256 verification succeed. It lets the serial producer free its small
    # AutoDL data disk without causing a resumed campaign to retrace a case.
    receipt = work_root / "offloaded" / f"{case_id}.json"
    if not receipt.is_file():
        return False
    try:
        payload = json.loads(receipt.read_text())
    except json.JSONDecodeError:
        return False
    digest_text = str(payload.get("archive_sha256", ""))
    return (
        payload.get("schema") == "accel-sim-v100-offload-receipt-v1"
        and payload.get("case_id") == case_id
        and len(digest_text) == 64
        and all(char in "0123456789abcdef" for char in digest_text)
    )


def provenance(framework_root: Path, work_root: Path, case: dict[str, Any]) -> dict[str, Any]:
    tracer = framework_root / "util/tracer_nvbit/tracer_tool/tracer_tool.so"
    executable = Path(expand(case["executable"], work_root))
    inputs_lock = work_root / "inputs/inputs.lock.generated.json"
    identity = framework_identity(framework_root)
    git_commit = command_output(["git", "-C", str(framework_root), "rev-parse", "HEAD"]).strip()
    source_commit = identity.get("source_commit")
    return {
        "timestamp_utc": utc_now(),
        "case": case,
        "framework_root": str(framework_root),
        "framework_commit": source_commit or git_commit,
        "framework_git_commit": git_commit,
        "framework_source_identity": identity or None,
        "nvidia_smi": command_output(
            ["nvidia-smi", "--query-gpu=name,uuid,compute_cap,driver_version,memory.total", "--format=csv,noheader"]
        ).strip(),
        "nvcc": command_output(["nvcc", "--version"]).strip(),
        "tracer_sha256": sha256(tracer) if tracer.is_file() else None,
        "binary_sha256": sha256(executable) if executable.is_file() else None,
        "inputs_lock_sha256": sha256(inputs_lock) if inputs_lock.is_file() else None,
        "frozen_reconstruction": load_freeze(work_root),
    }


def load_freeze(work_root: Path) -> dict[str, Any] | None:
    path = work_root / "inputs" / FREEZE_NAME
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid frozen-input decision: {path}: {exc}") from exc
    if payload.get("schema") != "accel-sim-v100-frozen-reconstruction-v1":
        raise RuntimeError(f"unsupported frozen-input decision schema: {path}")
    if payload.get("manifest_sha256") != manifest_sha256():
        raise RuntimeError("frozen-input decision does not match the current manifest")
    lock = work_root / "inputs" / "inputs.lock.generated.json"
    if not lock.is_file() or payload.get("inputs_lock_sha256") != sha256(lock):
        raise RuntimeError("frozen-input decision does not match the staged input lock")
    return payload


def input_is_approved(case: dict[str, Any], work_root: Path, allow_candidate: bool) -> bool:
    if case["input_status"] == "frozen" or allow_candidate:
        return True
    frozen = load_freeze(work_root)
    return frozen is not None and case["id"] in frozen.get("case_ids", [])


def normalize_single_context_metadata(traces: Path, case_id: str) -> None:
    """Expose the current tracer's ctx-suffixed stats as the stable stats.csv API.

    The post processor understands ctx-suffixed kernel lists directly.  More
    than one CUDA context needs a separate, explicit trace policy because
    kernel IDs are per context; silently merging it would corrupt a trace.
    """
    global_order = traces / "global-kernel-order.txt"
    if global_order.is_file():
        # The tracer recorded the CUDA callback order across all contexts.
        # Post-processing this one list preserves that order; passing the
        # directory would instead process each ctx-suffixed list separately.
        stats_by_trace: dict[str, str] = {}
        for stats_file in traces.glob("stats_ctx_*"):
            for line in stats_file.read_text().splitlines():
                if line.startswith("kernel-"):
                    stats_by_trace[line.split(",", 1)[0]] = line
        ordered_stats = []
        for command in global_order.read_text().splitlines():
            if command.startswith("kernel-"):
                if command not in stats_by_trace:
                    raise RuntimeError(
                        f"{case_id} global launch order references missing stats: {command}"
                    )
                ordered_stats.append(stats_by_trace[command])
        if not ordered_stats:
            raise RuntimeError(f"{case_id} global launch order contains no kernels")
        (traces / "stats.csv").write_text(
            "kernel id, kernel mangled name, grid_dimX, grid_dimY, grid_dimZ, "
            "#blocks, block_dimX, block_dimY, block_dimZ, #threads, "
            "total_insts, total_reported_insts\n"
            + "\n".join(ordered_stats)
            + "\n"
        )
        return
    stats_files = sorted(traces.glob("stats_ctx_*"))
    kernel_lists = sorted(traces.glob("kernelslist_ctx_*"))
    if len(stats_files) != 1 or len(kernel_lists) != 1:
        raise RuntimeError(
            f"{case_id} used {len(stats_files)} stats and {len(kernel_lists)} kernel-list CUDA contexts; "
            "raw output is retained and requires an explicit multi-context policy"
        )
    shutil.copyfile(stats_files[0], traces / "stats.csv")


def validate(manifest: dict[str, Any], framework_root: Path, work_root: Path, require_bins: bool) -> int:
    ids = [case["id"] for case in manifest["cases"]]
    if len(ids) != len(set(ids)):
        raise RuntimeError("case ids are not unique")
    # The TLS/C2P campaign remains hard-gated to its fourteen paper cases.  A
    # separately versioned manifest can reuse this safe runner for a small
    # follow-up collection without weakening the original campaign invariant.
    expected_ids = int(manifest.get("expected_case_count", 14))
    if len(ids) != expected_ids:
        raise RuntimeError(f"expected {expected_ids} cases, found {len(ids)}")
    for case in manifest["cases"]:
        if not case["argv"] and case["input_status"] not in {"candidate", "frozen"}:
            raise RuntimeError(f"bad input status for {case['id']}")
        if require_bins:
            executable = Path(expand(case["executable"], work_root))
            if not executable.is_file() or not os.access(executable, os.X_OK):
                raise RuntimeError(f"missing executable for {case['id']}: {executable}")
    tracer = framework_root / "util/tracer_nvbit/tracer_tool/tracer_tool.so"
    post = framework_root / "util/tracer_nvbit/tracer_tool/traces-processing/post-traces-processing"
    if not tracer.is_file() or not post.is_file():
        raise RuntimeError("framework tracer or post-processing binary is missing")
    print(f"PASS cases={len(ids)} framework={framework_root} work_root={work_root}")
    return 0


def make_env(framework_root: Path, case_dir: Path, phase: str) -> dict[str, str]:
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = "0"
    if phase in {"discovery", "trace"}:
        env["TRACES_FOLDER"] = str(case_dir)
        env["USER_DEFINED_FOLDERS"] = "1"
        env["CUDA_INJECTION64_PATH"] = str(
            framework_root / "util/tracer_nvbit/tracer_tool/tracer_tool.so"
        )
        env["TOOL_COMPRESS"] = "1"
        env["TRACE_FILE_COMPRESS"] = "1"
        env["DYNAMIC_KERNEL_RANGE"] = "1000000" if phase == "discovery" else ""
    return env


def run_case(
    framework_root: Path,
    work_root: Path,
    case: dict[str, Any],
    phase: str,
    allow_candidate: bool,
    min_free_gib: int,
) -> None:
    if not input_is_approved(case, work_root, allow_candidate):
        raise RuntimeError(
            f"{case['id']} uses candidate inputs. Freeze inputs or pass --allow-candidate explicitly."
        )
    if phase == "trace" and archive_ready(work_root, case["id"]):
        print(f"SKIP verified archive exists: {case['id']}")
        return
    executable = Path(expand(case["executable"], work_root))
    if not executable.is_file() or not os.access(executable, os.X_OK):
        raise RuntimeError(f"missing executable: {executable}")
    case_dir = work_root / "runs" / case["id"]
    case_dir.mkdir(parents=True, exist_ok=True)
    write_json(case_dir / "provenance.json", provenance(framework_root, work_root, case))
    argv = [str(executable)] + [expand(arg, work_root) for arg in case["argv"]]
    (case_dir / f"{phase}.command.json").write_text(json.dumps(argv, indent=2) + "\n")
    traces = case_dir / "traces"
    if phase in {"discovery", "trace"}:
        if traces.exists():
            shutil.rmtree(traces)
    env = make_env(framework_root, case_dir, phase)
    return_code, disk_guard_triggered = run_logged(
        argv,
        env,
        case_dir,
        case_dir / f"{phase}.log",
        min_free_gib if phase == "trace" else None,
    )
    if disk_guard_triggered:
        raise RuntimeError(f"{case['id']} stopped by disk guard at {min_free_gib} GiB")
    if return_code != 0:
        raise RuntimeError(f"{case['id']} {phase} exited {return_code}; see {case_dir / f'{phase}.log'}")
    if phase == "native":
        print(f"PASS native {case['id']}")
        return
    if phase == "discovery":
        # Discovery deliberately sets DYNAMIC_KERNEL_RANGE beyond the normal
        # launch range.  NVBit still creates per-context metadata, but it may
        # contain no selected kernels.  That is useful host/context evidence,
        # not a malformed full trace, so do not apply the full-trace global
        # ordering requirement here.  The trace phase below remains strict.
        context_lists = sorted(traces.glob("kernelslist_ctx_*"))
        if not context_lists:
            raise RuntimeError(f"{case['id']} discovery produced no CUDA-context metadata")
        selected = sum(
            1
            for path in context_lists
            for line in path.read_text().splitlines()
            if line.startswith("kernel-")
        )
        print(
            f"PASS discovery {case['id']} contexts={len(context_lists)} "
            f"selected_kernels={selected}"
        )
        return

    normalize_single_context_metadata(traces, case["id"])
    post = framework_root / "util/tracer_nvbit/tracer_tool/traces-processing/post-traces-processing"
    post_input = traces / "global-kernel-order.txt"
    post_code, _ = run_logged(
        [str(post), str(post_input if post_input.is_file() else traces)],
        os.environ.copy(),
        case_dir,
        case_dir / "postprocess.log",
        min_free_gib,
    )
    if post_code != 0 or not trace_ready(case_dir):
        raise RuntimeError(f"{case['id']} trace validation failed; raw files are retained for diagnosis")
    for raw in list(traces.glob("*.trace")) + list(traces.glob("*.trace.xz")):
        raw.unlink()
    for kernelslist in traces.glob("kernelslist*"):
        if kernelslist.name != "kernelslist.g":
            kernelslist.unlink()
    archive_case(work_root, case_dir, case["id"])
    print(f"PASS trace {case['id']}")


def archive_case(work_root: Path, case_dir: Path, case_id: str) -> None:
    archive_dir = work_root / "archives"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive = archive_dir / f"{case_id}.tar.zst"
    temporary = archive.with_name(archive.name + ".partial")
    if temporary.exists():
        temporary.unlink()
    subprocess.run(
        ["tar", "--use-compress-program=zstd -T0 -3", "-cf", str(temporary), "-C", str(case_dir.parent), case_id],
        check=True,
    )
    temporary.replace(archive)
    digest = archive.with_suffix(archive.suffix + ".sha256")
    digest.write_text(f"{sha256(archive)}  {archive.name}\n")
    remote = os.environ.get("TRACE_ARCHIVE_REMOTE")
    if remote:
        subprocess.run(["rclone", "copy", "--checksum", str(archive), remote], check=True)
        subprocess.run(["rclone", "copy", "--checksum", str(digest), remote], check=True)


def freeze_inputs(work_root: Path, cases: list[dict[str, Any]], rationale: str) -> None:
    lock = work_root / "inputs" / "inputs.lock.generated.json"
    if not lock.is_file():
        raise RuntimeError("stage inputs before freezing: missing inputs.lock.generated.json")
    rationale = rationale.strip()
    if len(rationale) < 12:
        raise RuntimeError("--rationale must state why these candidate inputs are being frozen")
    payload = {
        "schema": "accel-sim-v100-frozen-reconstruction-v1",
        "timestamp_utc": utc_now(),
        "meaning": "Frozen reconstruction inputs; this is not evidence that the paper used these exact inputs.",
        "manifest_sha256": manifest_sha256(),
        "inputs_lock_sha256": sha256(lock),
        "case_ids": [case["id"] for case in cases],
        "rationale": rationale,
    }
    path = work_root / "inputs" / FREEZE_NAME
    write_json(path, payload)
    print(f"PASS frozen_reconstruction={path} cases={len(cases)}")


def main() -> int:
    global MANIFEST_PATH
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "smoke", "status"):
        child = sub.add_parser(name)
        child.add_argument("--framework-root", required=True, type=Path)
        child.add_argument("--work-root", required=True, type=Path)
        child.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    run = sub.add_parser("run")
    run.add_argument("--framework-root", required=True, type=Path)
    run.add_argument("--work-root", required=True, type=Path)
    run.add_argument("--phase", choices=("native", "discovery", "trace"), required=True)
    run.add_argument("--case", default="all")
    run.add_argument("--allow-candidate", action="store_true")
    run.add_argument("--minimum-free-gib", type=int, default=200)
    run.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    freeze = sub.add_parser("freeze")
    freeze.add_argument("--framework-root", required=True, type=Path)
    freeze.add_argument("--work-root", required=True, type=Path)
    freeze.add_argument("--case", default="all")
    freeze.add_argument("--rationale", required=True)
    freeze.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    args = parser.parse_args()
    MANIFEST_PATH = args.manifest.resolve()
    framework_root = args.framework_root.resolve()
    work_root = args.work_root.resolve()
    manifest = load_manifest()
    if args.command == "validate":
        return validate(manifest, framework_root, work_root, require_bins=(work_root / "bin").exists())
    if args.command == "status":
        frozen = load_freeze(work_root)
        for case in manifest["cases"]:
            state = "approved" if input_is_approved(case, work_root, False) else case["input_status"]
            print(f"{case['id']}: input={state} archive={'ready' if archive_ready(work_root, case['id']) else 'pending'}")
        if frozen:
            print(f"frozen_reconstruction={work_root / 'inputs' / FREEZE_NAME}")
        return 0
    if args.command == "freeze":
        freeze_inputs(work_root, select_cases(manifest, args.case), args.rationale)
        return 0
    if args.command == "smoke":
        validate(manifest, framework_root, work_root, require_bins=True)
        smoke_case = next(case for case in manifest["cases"] if case["id"] == "tls-shoc-reduction")
        run_case(framework_root, work_root, smoke_case, "discovery", True, 200)
        print("PASS tracer smoke")
        return 0
    if args.minimum_free_gib < 1:
        raise RuntimeError("--minimum-free-gib must be positive")
    validate(manifest, framework_root, work_root, require_bins=True)
    for case in select_cases(manifest, args.case):
        run_case(
            framework_root,
            work_root,
            case,
            args.phase,
            args.allow_candidate,
            args.minimum_free_gib,
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
