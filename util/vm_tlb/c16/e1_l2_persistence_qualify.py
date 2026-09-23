#!/usr/bin/env python3
"""Freeze runtime capability, exact qweight regions, and helper smoke qualification."""

import hashlib
import json
from pathlib import Path

import torch
from awq import AutoAWQForCausalLM

from e1_cuda_persistence import LIBRARY, PersistenceHelper, qweight_region


AWQ = "/data/c16/models/.incoming/qwen2p5_7b_instruct_awq/b25037543e9394b818fdfca67ab2a00ecc7dd641"
OUT = Path("/data/c16/e1_l2_persistence_intervention_v1")
HEADER = Path("/usr/local/cuda-12.8/include/cuda_runtime_api.h")
ACCEPTED = {
    "l2_bytes": 67_108_864,
    "max_persisting_l2_bytes": 46_137_344,
    "max_access_policy_window_bytes": 134_213_632,
}


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    torch.cuda.init()
    helper = PersistenceHelper()
    runtime = helper.query_capability()
    model = AutoAWQForCausalLM.from_quantized(AWQ, fuse_layers=False)
    targets = {
        "layer0.mlp.up_proj.qweight": model.model.model.layers[0].mlp.up_proj,
        "layer14.mlp.up_proj.qweight": model.model.model.layers[14].mlp.up_proj,
        "layer0.mlp.down_proj.qweight": model.model.model.layers[0].mlp.down_proj,
    }
    regions = [qweight_region(module, name) for name, module in targets.items()]
    for region in regions:
        if not region["contiguous"] or region["bytes"] <= 0:
            raise RuntimeError(f"unsafe qweight interval: {region['tensor_name']}")
        if region["bytes"] > runtime["max_access_policy_window_bytes"]:
            raise RuntimeError(f"qweight window exceeds runtime maximum: {region['tensor_name']}")
    primary = targets["layer0.mlp.up_proj.qweight"]
    primary_bytes = primary.qweight.numel() * primary.qweight.element_size()
    if primary_bytes > runtime["max_persisting_l2_bytes"]:
        raise RuntimeError("primary qweight exceeds persisting-L2 maximum")
    smoke = helper.begin_condition("QUALIFICATION_SMOKE", primary_bytes, primary.qweight, 1.0)
    torch.cuda.synchronize()
    smoke = helper.end_condition(smoke)
    result = {
        "status": "PASS",
        "runtime_execution_authority": runtime,
        "accepted_historical_values": ACCEPTED,
        "runtime_matches_accepted": {key: runtime[key] == value for key, value in ACCEPTED.items()},
        "supported_api_path": {
            "set_limit": "cudaDeviceSetLimit(cudaLimitPersistingL2CacheSize)",
            "query_limit": "cudaDeviceGetLimit(cudaLimitPersistingL2CacheSize)",
            "stream_window": "cudaStreamSetAttribute(cudaStreamAttributeAccessPolicyWindow)",
            "reset": "cudaCtxResetPersistingL2Cache",
            "hit_property": "cudaAccessPropertyPersisting",
            "miss_property": "cudaAccessPropertyStreaming",
        },
        "cuda_runtime_header": str(HEADER),
        "cuda_runtime_header_sha256": file_sha(HEADER),
        "helper_library": str(LIBRARY),
        "helper_library_sha256": file_sha(LIBRARY),
        "qweight_regions": regions,
        "smoke_policy_receipt": smoke,
    }
    (OUT / "CUDA_CAPABILITY_AND_CENSUS.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "runtime": runtime, "qweight_bytes": [row["bytes"] for row in regions]}, sort_keys=True))


if __name__ == "__main__":
    main()
