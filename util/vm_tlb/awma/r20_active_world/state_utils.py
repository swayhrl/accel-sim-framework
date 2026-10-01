#!/usr/bin/env python3
"""Conservative R20 Data-array inventory, GPU snapshot and restore helpers."""

import dataclasses
import hashlib
from collections.abc import Mapping

import numpy as np
import warp as wp


def enumerate_data_arrays(root):
    """Return path->Warp array for every nonempty Data field, including nested structs."""
    found = {}
    seen_objects = set()

    def visit(value, path):
        if isinstance(value, wp.array):
            if int(np.prod(value.shape, dtype=np.int64)) > 0 and value.ptr:
                found[path] = value
            return
        if value is None or isinstance(value, (str, bytes, int, float, bool)):
            return
        identity = id(value)
        if identity in seen_objects:
            return
        if dataclasses.is_dataclass(value):
            seen_objects.add(identity)
            for field in dataclasses.fields(value):
                visit(getattr(value, field.name), f"{path}.{field.name}" if path else field.name)
        elif isinstance(value, Mapping):
            seen_objects.add(identity)
            for key, member in value.items():
                visit(member, f"{path}[{key}]")
        elif isinstance(value, (tuple, list)):
            seen_objects.add(identity)
            for index, member in enumerate(value):
                visit(member, f"{path}[{index}]")

    visit(root, "")
    return found


def make_gpu_snapshot(data):
    arrays = enumerate_data_arrays(data)
    snapshots = {}
    for path, array in arrays.items():
        clone = wp.empty_like(array)
        wp.copy(clone, array)
        snapshots[path] = clone
    wp.synchronize()
    return snapshots


def restore_gpu_snapshot(data, snapshots):
    arrays = enumerate_data_arrays(data)
    if set(arrays) != set(snapshots):
        raise RuntimeError(f"Data field set changed: added={set(arrays)-set(snapshots)}, missing={set(snapshots)-set(arrays)}")
    for path, source in snapshots.items():
        dest = arrays[path]
        if tuple(source.shape) != tuple(dest.shape) or source.dtype != dest.dtype:
            raise RuntimeError(f"Data shape/dtype mismatch at {path}")
        wp.copy(dest, source)
    wp.synchronize()


def sha_numpy(value):
    return hashlib.sha256(np.ascontiguousarray(value).view(np.uint8).tobytes()).hexdigest()


def digest_fields(data, field_paths):
    arrays = enumerate_data_arrays(data)
    digest = {}
    for path in field_paths:
        if path in arrays:
            value = arrays[path].numpy()
            digest[path] = {"shape": list(value.shape), "dtype": str(value.dtype), "sha256": sha_numpy(value)}
    return digest
