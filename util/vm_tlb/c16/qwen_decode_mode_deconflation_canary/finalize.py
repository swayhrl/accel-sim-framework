#!/usr/bin/env python3
"""CPU-only durability and review-pack finalization for the completed canary."""
import csv
import fcntl
import hashlib
import json
from pathlib import Path

from canary import LOCK, PACK, RAW_BASE, git, gpu_query, sha, tsv, write_json

RUN = "20261002T045340Z"
REMOTE = Path("/root/share/mnt164/huangrulin/c16_ai_workload/provenance/c16_qwen_decode_mode_deconflation_canary_109_v1") / RUN
COPYBACK = Path("/data/c16/qwen_decode_mode_deconflation_canary_v1/copyback_verify") / RUN
ATTEMPTS = ["20261002T044649Z","20261002T045024Z",RUN]

def main():
    remote = json.loads((PACK / "REMOTE_VERIFY.json").read_text())
    copyback = json.loads((PACK / "COPYBACK_VERIFY.json").read_text())
    assert remote["status"] == copyback["status"] == "PASS"
    assert remote["file_count"] == copyback["file_count"] == 22
    assert remote["manifest_count"] == copyback["manifest_count"] == 3
    index=[]
    manifest_shas={}
    for attempt in ATTEMPTS:
        local_root = RAW_BASE / attempt
        rel = Path(".") if attempt == RUN else Path("attempts") / attempt
        published_root = REMOTE / rel
        copyback_root = COPYBACK / rel
        for path in sorted(local_root.iterdir()):
            if not path.is_file():
                continue
            published = published_root / path.name
            copied = copyback_root / path.name
            expected = sha(path)
            assert copied.stat().st_size == path.stat().st_size and sha(copied) == expected
            index.append({"attempt":attempt,"local_path":str(path),"durable_path":str(published),
                          "copyback_path":str(copied),"size_bytes":path.stat().st_size,"sha256":expected})
        manifest_shas[attempt] = sha(local_root / "RAW_SHA256SUMS")
    tsv(PACK / "RAW_INDEX.tsv", index, ["attempt","local_path","durable_path","copyback_path","size_bytes","sha256"])
    write_json(PACK / "PUBLISH_RECEIPT.json", {
        "status":"PASS_DURABLE_PUBLISH_AND_COPYBACK","remote_host":"hrl174new",
        "durable_root":str(REMOTE),"copyback_root":str(COPYBACK),
        "attempts":ATTEMPTS,"payload_file_count":22,"indexed_file_count":len(index),
        "manifest_sha256_by_attempt":manifest_shas,
        "remote_verify_sha256":sha(PACK / "REMOTE_VERIFY.json"),
        "copyback_verify_sha256":sha(PACK / "COPYBACK_VERIFY.json"),
    })
    cache=[]
    for point in ("MP02","MP03"):
        for mode in ("A","B"):
            r=json.loads((RAW_BASE / RUN / f"{point}_{mode}.json").read_text())
            identity=r["runtime_identity"]
            path=Path(identity["compile_cache_path"])
            files=sorted(p for p in path.rglob("*") if p.is_file()) if path.exists() else []
            hashes=[(str(p.relative_to(path)),p.stat().st_size,sha(p)) for p in files]
            cache.append({"point":point,"mode":mode,"path":str(path),
                          "preexisted_before_mode_load":identity["compile_cache_preexisted"],
                          "file_count":len(files),"total_bytes":sum(x[1] for x in hashes),
                          "content_identity_sha256":hashlib.sha256(json.dumps(hashes,separators=(",", ":")).encode()).hexdigest(),
                          "compiled_submodules":identity["compiled_modules"]})
    write_json(PACK / "COMPILE_CACHE_IDENTITY.json",cache)
    with LOCK.open("a+") as f:
        fcntl.flock(f,fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(f,fcntl.LOCK_UN)
    q=gpu_query()
    write_json(PACK / "GPU_POSTFLIGHT.json",{"lock_reacquired_and_released":True,"gpu":q,
                                            "no_unknown_compute_process":not q["compute_processes"]})
    assert not q["compute_processes"]
    write_json(PACK / "ATTEMPT_HISTORY.json",{
        "history":[
            {"attempt":ATTEMPTS[0],"role":"ENGINEERING_FAILURE_EXCLUDED_FROM_SCIENCE","issue":"runner receipt serialization used wrong CUDA graph manager field","gpu_active_seconds":10.394024517852813},
            {"attempt":ATTEMPTS[1],"role":"ENGINEERING_IDENTITY_RECEIPT_EXCLUDED_FROM_SCIENCE","issue":"outer model inspected instead of compiled Qwen2Model; NONE enum serialized as empty","gpu_active_seconds":31.631662938045338},
            {"attempt":RUN,"role":"FORMAL_CANARY","gpu_active_seconds":55.082401091000065}],
        "total_gpu_active_seconds_conservative":97.10808854689822,
        "result_directed_repeat":False})
    readme = f"""# C16 Qwen decode execution-mode deconflation canary, node 109

Final decision: `MODE_DECONFLATION_CORRECTNESS_PASS_FOR_OBSERVER_REVIEW_ONLY`.

The final authorized contract is `{git('rev-parse','c4a61e8f2d4d96587e0006726e21796a360404e7')}` (tree `d0370fa0fba6566161558c6f7b34b3c5eebb14e5`, contract SHA256 `bc547a652ed04db9c3e1e1e7020be53ac76052bd76bfdad6d89eee0f69678501`). `CONTRACT_AUTHORITY.json` and `ASSET_INPUT_RECHECK.json` contain the entry gates.

Mode A and B both used `VLLM_COMPILE`, the compiled `Qwen2Model` submodule, `inductor`, BF16, `FlashAttentionImpl`, and `UnquantizedLinearMethod`. A used `FULL_AND_PIECEWISE` and the tested decode shapes each registered 31 full CUDA Graph replays. B used `CUDAGraphMode.NONE` with zero capture/replay events. The identity-only CUDA inventory records BF16 GEMM/GEMV, FlashAttention and fused kernels without duration claims.

MP02: 1 row, 512 frozen prompt tokens, 32 exact generated tokens and 32 exact sampled-token logprobs. MP03: one real B4 request, four mapped 512-token rows, each with 32 exact generated tokens and sampled-token logprobs. The frozen tolerance was `0.05 + 0.01 * abs(A)`; maximum observed absolute delta was zero. The CPU-only verifier in `util/vm_tlb/c16/qwen_decode_mode_deconflation_canary/validate.py` passed 32 checks.

Three engineering attempts consumed a conservative total of 97.108089 GPU-active seconds under the 120-second cap. The first two failed on receipt logic and are excluded from science; all raw bytes were preserved. `ATTEMPT_HISTORY.json` and `GPU_ACTIVE_BUDGET.json` give the accounting. No observer, NSYS, NCU, NVBit, SASS, Accel-Sim, Tier0 rerun, or holdout was run.

Start with `FINAL_DECISION.json`, then `MODE_RUNTIME_IDENTITY.tsv`, `FREE_RUNNING_CORRECTNESS_BY_ROW_STEP.tsv`, `BACKEND_KERNEL_IDENTITY.tsv`, and `RAW_INDEX.tsv`. The raw payload is durable at `{REMOTE}`. `PUBLISH_RECEIPT.json`, `REMOTE_VERIFY.json`, and `COPYBACK_VERIFY.json` record per-file verification. `SHA256SUMS` covers this review pack. The historical MP02/MP03 `STOP_POINT_CORRECTNESS` remains unchanged. This pass only admits a separate observer qualification review; `automatic_next_goal=false`.
"""
    (PACK / "README.md").write_text(readme)
    (PACK / "OPEN_ISSUES.md").write_text("# Open issues\n\nObserver qualification requires separate project review. No further GPU or science step is authorized by this canary.\n")
    for path in PACK.glob("*.tsv"):
        data = path.read_bytes()
        if b"\r\n" in data:
            path.write_bytes(data.replace(b"\r\n", b"\n"))
    pack_files=sorted(p for p in PACK.iterdir() if p.is_file() and p.name != "SHA256SUMS")
    (PACK / "SHA256SUMS").write_text("".join(f"{sha(p)}  {p.name}\n" for p in pack_files))
    print(json.dumps({"status":"PASS","indexed_files":len(index),"pack_files":len(pack_files)}))

if __name__ == "__main__":
    main()
