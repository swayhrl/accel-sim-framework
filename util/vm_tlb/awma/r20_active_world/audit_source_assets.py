#!/usr/bin/env python3
"""CPU-only R20 exact source, asset, lock and window pre-registration."""

import hashlib
import json
import subprocess
import tomllib
from pathlib import Path

import numpy as np


ROOT = Path("/data/c16/awma/r20_active_world_native_v1")
SOURCE = ROOT / "source/mujoco_warp"
MENAGERIE = ROOT / "source/mujoco_menagerie"
BENCH = SOURCE / "benchmarks/unitree_g1"
RAW = ROOT / "raw"
EXPECTED_MJW = "3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5"
EXPECTED_MENAGERIE = "affef0836947b64cc06c4ab1cbf0152835693374"


def file_sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head(path):
    return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()


def main():
    assert git_head(SOURCE) == EXPECTED_MJW
    assert git_head(MENAGERIE) == EXPECTED_MENAGERIE
    lock_path = SOURCE / "uv.lock"
    lock = tomllib.loads(lock_path.read_text())
    packages = {entry["name"]: entry["version"] for entry in lock["package"] if "version" in entry}
    files = [
        SOURCE / "pyproject.toml",
        lock_path,
        SOURCE / "mujoco_warp/_src/cli.py",
        SOURCE / "mujoco_warp/_src/io.py",
        SOURCE / "mujoco_warp/_src/solver.py",
        BENCH / "__init__.py",
        BENCH / "scene_hfield.xml",
        BENCH / "unitree_g1_mjlab.xml",
        BENCH / "shuffle_dance.npz",
        BENCH / "assets/hfield.png",
    ]
    menagerie_assets = sorted((MENAGERIE / "unitree_g1/assets").iterdir())
    files.extend(path for path in menagerie_assets if path.is_file())
    for path in files:
        assert path.is_file(), path
    assets = [
        {"path": str(path), "bytes": path.stat().st_size, "sha256": file_sha(path)}
        for path in files
    ]

    with np.load(BENCH / "shuffle_dance.npz", allow_pickle=False) as archive:
        npz_arrays = {name: archive[name] for name in archive.files}
    assert "ctrl" in npz_arrays and "times" in npz_arrays
    ctrl = npz_arrays["ctrl"]
    times = npz_arrays["times"]
    assert ctrl.ndim == 2 and len(ctrl) > 0
    assert times.ndim == 1 and len(times) in (len(ctrl), len(ctrl) + 1)
    assert np.all(np.isfinite(times)) and np.all(np.diff(times) > 0)
    model_dt = 0.005  # exact XML option; runtime model must independently confirm
    sample_times = times
    if len(times) == len(ctrl):
        final_dt = float(np.diff(times)[-1]) if len(times) > 1 else model_dt
        sample_times = np.append(times, times[-1] + final_dt)
    L = int(np.round((sample_times[-1] - sample_times[0]) / model_dt))
    assert L >= 64, f"control replay too short: {L}"
    W = min(L, 512)
    K = min(32, W // 8)
    discovery = [W // 4, W // 4 + K]
    holdout = [(3 * W) // 4, (3 * W) // 4 + K]
    assert discovery[1] <= W and holdout[1] <= W
    payload = {
        "stage": "AWMA_R20_ACTIVE_WORLD_NATIVE_109_V1",
        "source_commit": git_head(SOURCE),
        "menagerie_commit": git_head(MENAGERIE),
        "uv_lock_sha256": file_sha(lock_path),
        "package_versions_from_lock": {
            name: packages.get(name, "MISSING")
            for name in ("mujoco", "warp-lang", "numpy", "absl-py", "etils", "mujoco-warp")
        },
        "asset_count": len(assets),
        "menagerie_asset_count": sum(path.is_file() for path in menagerie_assets),
        "assets": assets,
        "npz_arrays": {
            name: {"shape": list(value.shape), "dtype": str(value.dtype), "finite": bool(np.all(np.isfinite(value)))}
            for name, value in npz_arrays.items()
        },
        "replay_input_class": "AUTHOR_BENCHMARK_REPLAY_WITH_DETERMINISTIC_CONTROL_PERTURBATION",
        "control_raw_length": len(ctrl),
        "control_replay_length_formula_L": L,
        "model_timestep_from_xml": model_dt,
        "W": W,
        "K": K,
        "discovery_half_open": discovery,
        "holdout_half_open_SEALED": holdout,
        "window_choice_based_only_on_length": True,
    }
    (RAW / "SOURCE_ASSET_WINDOW_RECEIPT.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    with (RAW / "ASSET_SHA256SUMS").open("w") as stream:
        for record in assets:
            stream.write(f"{record['sha256']}  {record['path']}\n")
    print(json.dumps({key: payload[key] for key in (
        "source_commit", "menagerie_commit", "package_versions_from_lock",
        "control_raw_length", "control_replay_length_formula_L", "W", "K",
        "discovery_half_open", "holdout_half_open_SEALED", "asset_count"
    )}, sort_keys=True))


if __name__ == "__main__":
    main()
