#!/usr/bin/env python3
"""CPU-only authority, asset, source and test preparation before Lane6 contract."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
PACK=ROOT/"docs/vm_tlb/review_packs/C16_QWEN_COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CANARY_PREP_109_V1"
CANARY=ROOT/"util/vm_tlb/c16/qwen_decode_mode_deconflation_canary"
sys.path.insert(0,str(CANARY))
import canary as previous

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(["git","-C",str(ROOT),*args],text=True).strip()
def save(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")

def main():
    PACK.mkdir(parents=True,exist_ok=True)
    previous.asset_recheck()
    asset=json.loads((previous.PACK/"ASSET_INPUT_RECHECK.json").read_text())
    save(PACK/"ASSET_INPUT_PREP.json",asset)
    authority={"mode_canary_commit":git("rev-parse","9122fac5c50dbf19706636fc03978a356ffd800f"),
               "mode_canary_tree":git("rev-parse","9122fac5c50dbf19706636fc03978a356ffd800f^{tree}"),
               "observer_v2_commit":git("rev-parse","f63d39c8d90ced038445c264fa8242c524a1aa6f"),
               "observer_v2_tree":git("rev-parse","f63d39c8d90ced038445c264fa8242c524a1aa6f^{tree}"),
               "observer_v2_runner_source_sha256":"7f2a76a375eaa4f652553fc523f785a753180ef1402291e54beb2256ed02bb22",
               "observer_v2_extracted_module_sha256":sha(HERE/"observer_v2.py")}
    assert authority["mode_canary_commit"]=="9122fac5c50dbf19706636fc03978a356ffd800f"
    assert authority["observer_v2_commit"]=="f63d39c8d90ced038445c264fa8242c524a1aa6f"
    assert authority["mode_canary_tree"]=="d9049ad2d506dcdfd1dd90f8e07c7b495b44111e"
    save(PACK/"UPSTREAM_AUTHORITY.json",authority)
    for script in ("observer_v2.py","runner.py","static_check.py","postprocess.py","test_postprocess.py","run_guard.py","verify_tree.py","publish.py","contract_poll.py","prepare.py","test_infrastructure.py"):
        subprocess.run([sys.executable,"-m","py_compile",str(HERE/script)],check=True)
    static=subprocess.run([sys.executable,str(HERE/"static_check.py")],capture_output=True,text=True,check=True)
    tests=subprocess.run([sys.executable,str(HERE/"test_postprocess.py")],capture_output=True,text=True,check=True)
    infra=subprocess.run([sys.executable,str(HERE/"test_infrastructure.py")],capture_output=True,text=True,check=True)
    save(PACK/"TESTS.json",{"status":"PASS","python_compile_count":11,"static_check_output":static.stdout.strip(),
                            "directed_postprocess_output":tests.stdout.strip(),"infrastructure_output":infra.stdout.strip(),
                            "cuda_initialized":False,"gpu_lock_acquired":False})
    save(PACK/"PREP_STATUS.json",{"goal":"C16_QWEN_COMPILED_NO_CUDAGRAPH_OBSERVER_V2_CANARY_109_V1",
                                  "status":"PREPARED_WAITING_FOR_LANE6_CONTRACT","cpu_only":True,"cuda_initialized":False,
                                  "gpu_lock_acquired":False,"gpu_active_seconds":0,
                                  "observer_source_exact":True,"mode_b_runner_prepared":True,
                                  "contract_authority_checked":False,"execution_authorized":False})
    (PACK/"README.md").write_text("# Qwen compiled/no-CUDA-Graph Observer V2 canary: CPU preparation\n\nThis pack records CPU-only preparation. The Lane6 contract is not yet present, so GPU execution is blocked. `UPSTREAM_AUTHORITY.json` pins the accepted Mode A/B canary and Observer V2 source. `STATIC_QUALIFICATION.json` proves exact semantic AST extraction, zero per-occurrence CUDA Events, balanced NVTX, ordinal and shape receipts. `ASSET_INPUT_PREP.json` rechecks the fixed Qwen model and inputs. `TESTS.json` records compilation and directed synthetic gates. `CONTRACT_POLL.tsv` records five-minute Lane6 checks.\n\nNo CUDA initialization, model load, GPU lock, observer run, NSYS, NCU, Tier0, or holdout occurred in this preparation.\n")
    files=sorted(p for p in PACK.iterdir() if p.is_file() and p.name not in ("SHA256SUMS","CONTRACT_POLL.tsv"))
    (PACK/"SHA256SUMS").write_text("".join(f"{sha(p)}  {p.name}\n" for p in files))
    print(json.dumps({"status":"PREPARED_WAITING_FOR_LANE6_CONTRACT","files":len(files)}))

if __name__=="__main__":main()
