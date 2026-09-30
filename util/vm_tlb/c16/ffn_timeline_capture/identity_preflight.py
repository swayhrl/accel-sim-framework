#!/usr/bin/env python3
"""CPU-only verification of every bound FFN timeline capture identity."""

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    contract = json.loads(args.contract.read_text())
    failures = []

    def check(label, actual, expected):
        ok = actual == expected
        if not ok:
            failures.append({"field": label, "actual": actual, "expected": expected})
        return {"actual": actual, "expected": expected, "pass": ok}

    runner = args.repo / contract["runner"]["source_path"]
    model = Path(contract["model"]["path"])
    token = Path(contract["input"]["accepted_path"])
    checks = {
        "contract_sha256": check("contract_sha256", sha(args.contract), "cc081ee281b672bd8ff76cb8ae3e226194c0eec44f6f8916ed4fbbfb8facd2f9"),
        "patched_runner_sha256": check("patched_runner_sha256", sha(runner), contract["runner"]["patched_runner_sha256"]),
        "token_file_sha256": check("token_file_sha256", sha(token), contract["input"]["token_file_sha256"]),
    }
    for name, expected in contract["model"]["payload_sha256"].items():
        checks[f"model:{name}"] = check(f"model:{name}", sha(model / name), expected)
    deps = {
        "util/vm_tlb/c16/e1_cuda_persistence.py": "2a6e4aa4d0f5e240dd3ad52045354d5f63c692ea426cfc388ea6cc58829e4064",
        "util/vm_tlb/c16/e1_residency_common.py": "cb310aae6397c81a2d21f02186dc4ab80e5abe0110d14d948e0456185bfeb084",
    }
    for path, expected in deps.items():
        checks[f"dependency:{path}"] = check(f"dependency:{path}", sha(args.repo / path), expected)
    versions = {"python": platform.python_version(), "torch": importlib.metadata.version("torch"),
                "transformers": importlib.metadata.version("transformers"), "autoawq": importlib.metadata.version("autoawq")}
    for key, expected in (("python", "3.10.12"), ("torch", "2.5.1+cu124"), ("transformers", "4.46.3"), ("autoawq", "0.2.7.post3")):
        checks[f"runtime:{key}"] = check(f"runtime:{key}", versions[key], expected)
    smi = subprocess.check_output(["nvidia-smi", "--query-gpu=name,uuid,driver_version,memory.total", "--format=csv,noheader,nounits"], text=True).strip().split(", ")
    checks["gpu:name"] = check("gpu:name", smi[0], contract["runtime"]["gpu"]["name"])
    checks["gpu:uuid"] = check("gpu:uuid", smi[1], contract["runtime"]["gpu"]["uuid"])
    checks["runtime:driver"] = check("runtime:driver", smi[2], contract["runtime"]["driver"])
    nsys = Path(subprocess.check_output(["bash", "-lc", "command -v nsys"], text=True).strip()).resolve()
    nsys_version = subprocess.check_output([str(nsys), "--version"], text=True).strip()
    relevant_env = {k: v for k, v in os.environ.items() if k.startswith(("CUDA_", "PYTORCH_", "TRANSFORMERS_", "HF_", "AWQ_"))}
    result = {"status": "PASS" if not failures else "IDENTITY_MISMATCH_STOP", "failures": failures, "checks": checks,
              "authority": {"commit": "08f38d7163da95e895aaba10d72231a6d350dfe2", "contract_sha256": sha(args.contract)},
              "runner": {"path": str(runner), "sha256": sha(runner)}, "model": {"path": str(model)}, "input": {"path": str(token)},
              "runtime": versions | {"interpreter": sys.executable, "torch_cuda_build": "12.4", "semantic_environment": relevant_env},
              "nsys": {"path": str(nsys), "version": nsys_version, "sha256": sha(nsys)},
              "gpu": {"name": smi[0], "uuid": smi[1], "driver": smi[2], "nvidia_smi_memory_mib": int(smi[3]),
                      "accepted_cuda_memory_bytes": contract["runtime"]["gpu"]["memory_bytes"],
                      "accepted_cc": contract["runtime"]["gpu"]["cc"], "accepted_sm_count": contract["runtime"]["gpu"]["sm_count"]}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "failure_count": len(failures)}, sort_keys=True))
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
