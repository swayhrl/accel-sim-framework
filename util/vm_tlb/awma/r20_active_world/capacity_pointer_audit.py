#!/usr/bin/env python3
"""B1024 Data backing-address alias ledger; no performance measurement."""

import json
import os
import subprocess
from pathlib import Path

import mujoco
import warp as wp

from state_utils import enumerate_data_arrays


ROOT = Path("/data/c16/awma/r20_active_world_native_v1")
SCENE = ROOT / "scene/unitree_g1_hfield"
RAW = ROOT / "raw"


def memory_snapshot():
    line = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=memory.free,memory.total", "--format=csv,noheader,nounits"], text=True
    ).strip().splitlines()[0]
    free_mib, total_mib = (int(part.strip()) for part in line.split(","))
    return {"free_MiB": free_mib, "total_MiB": total_mib, "free_fraction": free_mib / total_mib}


def main():
    assert os.environ.get("R20_GPU_LOCK_HELD") == "1"
    wp.config.kernel_cache_dir = str(ROOT / "cache/warp")
    wp.init()
    import mujoco_warp as mjw
    from mujoco_warp._src.io import load_trajectory, override_model

    entry = json.loads((RAW / "DISCOVERY_ENTRY_STATE_MANIFEST.json").read_text())
    prior = {row["field_path"]: row for row in entry["manifest"]}
    device = wp.get_device("cuda:0")
    before = memory_snapshot()
    mjm = mujoco.MjSpec.from_file(str(SCENE / "scene_hfield.xml")).compile()
    mjd = mujoco.MjData(mjm)
    assert len(load_trajectory(str(SCENE / "shuffle_dance.npz"), mjm, mjd)) == 1000
    with wp.ScopedDevice(device):
        m = mjw.put_model(mjm)
        override_model(m, ["opt.warn_overflow=~ITERATIONS|~LS_ITERATIONS"])
        d = mjw.put_data(mjm, mjd, nworld=1024, nconmax=48, njmax=192)
        with wp.ScopedCapture() as capture:
            mjw.step(m, d)
        wp.synchronize()
        arrays = enumerate_data_arrays(d)
        assert set(arrays) == set(prior), f"Field inventory differs: {set(arrays)^set(prior)}"
        rows = []
        intervals = []
        for path, array in arrays.items():
            meta = prior[path]
            assert list(array.shape) == meta["warp_shape"]
            assert str(array.dtype) == meta["warp_dtype"]
            start = int(array.ptr)
            size = int(meta["bytes"])
            rows.append({
                "field_path": path,
                "logical_bytes": size,
                "device_ptr_hex": hex(start),
                "start": start,
                "end_exclusive": start + size,
                "warp_shape": meta["warp_shape"],
                "warp_dtype": meta["warp_dtype"],
            })
            intervals.append((start, start + size))
        intervals.sort()
        merged = []
        for start, end in intervals:
            if merged and start <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], end)
            else:
                merged.append([start, end])
        unique_bytes = sum(end - start for start, end in merged)
        after = memory_snapshot()
        result = {
            "stage": "AWMA_R20_ACTIVE_WORLD_NATIVE_109_V1",
            "classification": "B1024_DATA_ARRAY_ALIAS_DEDUP_CAPACITY_LEDGER_NOT_DRAM_TRAFFIC",
            "source_discovery_entry_state_sha256": entry["state_npz_sha256"],
            "source_manifest_field_count": len(prior),
            "array_field_count": len(rows),
            "sum_logical_field_bytes_with_aliases": sum(row["logical_bytes"] for row in rows),
            "alias_dedup_address_interval_union_bytes": unique_bytes,
            "merged_device_intervals": len(merged),
            "alias_or_overlap_bytes": sum(row["logical_bytes"] for row in rows) - unique_bytes,
            "device_memory_before": before,
            "device_memory_after_model_data_graph_capture": after,
            "unattributed_device_reservation_note": "nvidia-smi delta includes model arrays, graph executable, Warp CUDA context/JIT cache and allocator reservations; do not treat as solver scratch or DRAM traffic",
            "graph_local_solver_scratch_bytes": "UNKNOWN_NOT_IN_DATA_FIELDS",
            "rows": rows,
        }
        (RAW / "CAPACITY_POINTER_LEDGER.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps({key: result[key] for key in (
            "array_field_count", "sum_logical_field_bytes_with_aliases",
            "alias_dedup_address_interval_union_bytes", "alias_or_overlap_bytes",
            "device_memory_before", "device_memory_after_model_data_graph_capture"
        )}, sort_keys=True))


if __name__ == "__main__":
    main()
