#!/usr/bin/env python3
"""Exact parent Data restoration and R20R1 GPU snapshot serialization."""

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import warp as wp


PARENT_TOOLS = Path(__file__).resolve().parents[1] / "r20_active_world"
sys.path.insert(0, str(PARENT_TOOLS))
from state_utils import digest_fields, enumerate_data_arrays, sha_numpy  # noqa: E402


def file_sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def restore_parent_data(data, parent_raw, expected_sha):
    path = Path(parent_raw) / "DISCOVERY_ENTRY_FULL_DATA.npz"
    manifest_path = Path(parent_raw) / "DISCOVERY_ENTRY_STATE_MANIFEST.json"
    if file_sha(path) != expected_sha:
        raise RuntimeError("Parent t128 step-entry payload SHA mismatch")
    manifest = json.loads(manifest_path.read_text())
    if manifest["state_npz_sha256"] != expected_sha:
        raise RuntimeError("Parent t128 manifest/payload SHA mismatch")
    arrays = enumerate_data_arrays(data)
    paths = {row["field_path"] for row in manifest["manifest"]}
    if set(arrays) != paths:
        raise RuntimeError(f"Data field set changed: {set(arrays) ^ paths}")
    temporaries = []
    with np.load(path, allow_pickle=False) as archive:
        for row in manifest["manifest"]:
            target = arrays[row["field_path"]]
            source = archive[row["key"]]
            if sha_numpy(source) != row["sha256"]:
                raise RuntimeError(f"Parent Data array SHA mismatch at {row['field_path']}")
            temporary = wp.array(source, dtype=target.dtype, device=target.device)
            if tuple(temporary.shape) != tuple(target.shape):
                raise RuntimeError(f"Parent Data logical shape mismatch at {row['field_path']}: {temporary.shape} != {target.shape}")
            wp.copy(target, temporary)
            temporaries.append(temporary)
    wp.synchronize()
    for row in manifest["manifest"]:
        if sha_numpy(arrays[row["field_path"]].numpy()) != row["sha256"]:
            raise RuntimeError(f"Restored Data byte mismatch at {row['field_path']}")
    return manifest


def allocate_data_buffers(data):
    arrays = enumerate_data_arrays(data)
    return {path: wp.empty_like(array) for path, array in arrays.items()}


def record_data_copy(data, buffers):
    arrays = enumerate_data_arrays(data)
    if set(arrays) != set(buffers):
        raise RuntimeError(f"Data field set changed at solver boundary: {set(arrays) ^ set(buffers)}")
    for path, destination in buffers.items():
        source = arrays[path]
        if tuple(source.shape) != tuple(destination.shape) or source.dtype != destination.dtype:
            raise RuntimeError(f"Data field layout changed at solver boundary: {path}")
        wp.copy(destination, source)


def snapshot_to_npz(buffers, path):
    payload = {}
    manifest = []
    for index, (field_path, array) in enumerate(buffers.items()):
        value = array.numpy()
        key = f"array_{index:04d}"
        payload[key] = value
        manifest.append({
            "key": key,
            "field_path": field_path,
            "logical_shape": list(array.shape),
            "warp_dtype": str(array.dtype),
            "numpy_shape": list(value.shape),
            "numpy_dtype": str(value.dtype),
            "bytes": value.nbytes,
            "sha256": sha_numpy(value),
        })
    np.savez_compressed(path, **payload)
    return {"path": str(path), "sha256": file_sha(path), "field_count": len(manifest), "logical_bytes": sum(row["bytes"] for row in manifest), "manifest": manifest}


def restore_recorded_snapshot(data, record):
    """Restore a R20R1 recorded Data snapshot to already-captured Data pointers."""
    path = Path(record["path"])
    if file_sha(path) != record["sha256"]:
        raise RuntimeError("Recorded solver-entry Data snapshot SHA mismatch")
    arrays = enumerate_data_arrays(data)
    rows = record["manifest"]
    if set(arrays) != {row["field_path"] for row in rows}:
        raise RuntimeError("Recorded solver-entry field set differs from Data")
    temporaries = []
    with np.load(path, allow_pickle=False) as archive:
        for row in rows:
            target = arrays[row["field_path"]]
            source = archive[row["key"]]
            if sha_numpy(source) != row["sha256"]:
                raise RuntimeError(f"Recorded solver-entry array SHA mismatch at {row['field_path']}")
            temporary = wp.array(source, dtype=target.dtype, device=target.device)
            if tuple(temporary.shape) != tuple(target.shape):
                raise RuntimeError(f"Recorded solver-entry shape mismatch at {row['field_path']}")
            wp.copy(target, temporary)
            temporaries.append(temporary)
    wp.synchronize()
    for row in rows:
        if sha_numpy(arrays[row["field_path"]].numpy()) != row["sha256"]:
            raise RuntimeError(f"Recorded solver-entry restore failed at {row['field_path']}")


def restored_field_digests(data, paths):
    return digest_fields(data, paths)
