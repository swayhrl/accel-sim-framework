#!/usr/bin/env python3
"""Check fixed safetensors structure without loading tensor payloads or CUDA."""

from collections import Counter
import json
from pathlib import Path
import struct


ROOT = Path("/data/c16/aiarch_hybrid_asset_qualification_20261110_v1/models/qwen3_5_4b")
SHARDS = (
    "model.safetensors-00001-of-00002.safetensors",
    "model.safetensors-00002-of-00002.safetensors",
)
DTYPE_BYTES = {"BF16": 2, "F16": 2, "F32": 4, "F64": 8, "I8": 1, "U8": 1,
               "I16": 2, "U16": 2, "I32": 4, "U32": 4, "I64": 8, "U64": 8}


def inspect(path: Path) -> tuple[dict, int, int]:
    with path.open("rb") as source:
        header_bytes = source.read(8)
        if len(header_bytes) != 8:
            raise ValueError(f"{path.name}: missing header length")
        header_size = struct.unpack("<Q", header_bytes)[0]
        if header_size > 100_000_000:
            raise ValueError(f"{path.name}: implausible header size {header_size}")
        header = json.loads(source.read(header_size))
    tensors = {name: value for name, value in header.items() if name != "__metadata__"}
    spans = []
    logical_bytes = 0
    for name, value in tensors.items():
        dtype = value["dtype"]
        shape = value["shape"]
        start, end = value["data_offsets"]
        elements = 1
        for dimension in shape:
            elements *= dimension
        expected = elements * DTYPE_BYTES[dtype]
        if start < 0 or end - start != expected:
            raise ValueError(f"{path.name}:{name}: invalid offsets or dtype/shape size")
        spans.append((start, end))
        logical_bytes += expected
    spans.sort()
    previous_end = 0
    for start, end in spans:
        if start != previous_end:
            raise ValueError(f"{path.name}: gap or overlap at {start} after {previous_end}")
        previous_end = end
    if path.stat().st_size != 8 + header_size + previous_end:
        raise ValueError(f"{path.name}: payload end does not match file size")
    return tensors, header_size, logical_bytes


def main() -> None:
    index = json.loads((ROOT / "model.safetensors.index.json").read_text())
    weight_map = index["weight_map"]
    summary = {"shards": {}, "dtype_tensors": {}, "dtype_bytes": {},
               "component_bytes": {}, "total_tensors": 0, "logical_bytes": 0}
    dtype_counts = Counter()
    dtype_bytes = Counter()
    component_bytes = Counter()
    names = set()
    for filename in SHARDS:
        tensors, header_size, logical_bytes = inspect(ROOT / filename)
        expected_names = {name for name, shard in weight_map.items() if shard == filename}
        if set(tensors) != expected_names:
            raise ValueError(f"{filename}: header tensor names differ from index")
        if names & set(tensors):
            raise ValueError(f"{filename}: duplicate tensor names")
        names.update(tensors)
        dtype_counts.update(value["dtype"] for value in tensors.values())
        for tensor_name, value in tensors.items():
            nbytes = value["data_offsets"][1] - value["data_offsets"][0]
            dtype_bytes[value["dtype"]] += nbytes
            component = ".".join(tensor_name.split(".")[:2])
            component_bytes[component] += nbytes
        summary["shards"][filename] = {
            "file_bytes": (ROOT / filename).stat().st_size,
            "header_bytes": header_size,
            "tensors": len(tensors),
            "logical_bytes": logical_bytes,
        }
        summary["logical_bytes"] += logical_bytes
    if names != set(weight_map) or summary["logical_bytes"] != index["metadata"]["total_size"]:
        raise ValueError("index tensor set or total_size mismatch")
    summary["total_tensors"] = len(names)
    summary["dtype_tensors"] = dict(sorted(dtype_counts.items()))
    summary["dtype_bytes"] = dict(sorted(dtype_bytes.items()))
    summary["component_bytes"] = dict(sorted(component_bytes.items()))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
