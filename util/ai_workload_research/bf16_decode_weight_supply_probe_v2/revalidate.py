"""CPU-only minimal V1 authority requalification; never initializes model/CUDA/NVML."""
import os,json,hashlib,time,importlib.metadata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"docs/ai_workload_research/runs/QWEN_BF16_DECODE_WEIGHT_SUPPLY_PROBE_109_V2"
V1=Path("/home/huangrulin/workspace/worktrees/accel-sim-aiarch-bf16-decode-weight-supply-probe-109-v1/docs/ai_workload_research/runs/QWEN_BF16_DECODE_WEIGHT_SUPPLY_PROBE_109_V1")
def sha_file(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1024**2),b""):h.update(chunk)
    return h.hexdigest()
def canonical(v):return hashlib.sha256(json.dumps(v,separators=(",",":")).encode()).hexdigest()
def main():
    start=time.time();runtime=json.load(open(OUT/"SOURCE_AND_RUNTIME.json"));model=Path(runtime["model_path"]);files=[]
    for f in runtime["asset_files"]:
        p=model/f["path"];before=p.stat();assert before.st_size==f["size_bytes"]
        h=sha_file(p);after=p.stat();assert h==f["sha256"] and (before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns)
        files.append(dict(path=str(p),sha256=h,size=after.st_size,inode=after.st_ino,mtime_ns=after.st_mtime_ns,ctime_ns=after.st_ctime_ns,status="PASS"))
    site=Path("/data/c16/envs/c16-vllm-v0.30.0-sm89-v1/lib/python3.12/site-packages")
    hashes={k:sha_file(site/"vllm"/rel) for k,rel in [("compilation.py","config/compilation.py"),("qwen2.py","model_executor/models/qwen2.py")]}
    assert hashes==runtime["vllm_installed_source_sha256"]
    interfaces={}
    for rel,prior in runtime["cache_isolation_interfaces"].items():
        actual=sha_file(site/rel);assert actual==prior["sha256"];interfaces[rel]=actual
    versions={n:importlib.metadata.version(n) for n in runtime["versions"]}
    assert versions==runtime["versions"]
    inputs=json.load(open(V1/".private/inputs.json"));ir=json.load(open(OUT/"INPUT_RECEIPT.json"));rows=[]
    for row in ir["inputs"]:
        assert row["prompt_tokens"]==512
        key=row["source"]+"_512";ids=inputs[key];assert len(ids)==512 and all(type(x) is int for x in ids)
        assert canonical(ids)==row["token_ids_sha256"]
        rows.append(dict(source=row["source"],tokens=512,token_ids_sha256=canonical(ids),status="PASS"))
    assert len(inputs)==2
    (OUT/".private/inputs.json").write_text(json.dumps(inputs,separators=(",",":"))+"\n")
    reference=V1/".private/reference.json";assert sha_file(reference)==ir["reference"]["sha256"]
    (OUT/".private/reference.json").write_bytes(reference.read_bytes())
    receipt=dict(status="G0_PASS_REUSED_AUTHORITY_REVALIDATED",model_files=files,versions=versions,source_hashes=hashes,cache_interface_hashes=interfaces,input_checks=rows,reference_sha256=sha_file(reference),why_full_model_hash_needed="V1 did not record inode/mtime/ctime fingerprints; rehash only12 required local files to prove current unchanged bytes, not historical experiment audit.",tokenizer_retokenized=False,tokenizer_reuse_basis="All model/tokenizer bytes, library versions and accepted fixed IDs unchanged; V1 prefix-tokenizer validation inherited.",downloads=0,installs=0,NVML_init=0,CUDA_init=0,model_initializations=0,seconds=time.time()-start)
    (OUT/"G0_REVALIDATION.json").write_text(json.dumps(receipt,indent=2)+"\n")
    runtime["V2_revalidation"]="G0_REVALIDATION.json";(OUT/"SOURCE_AND_RUNTIME.json").write_text(json.dumps(runtime,indent=2)+"\n")
    print(json.dumps(dict(G0="PASS",files=len(files),inputs=rows,seconds=time.time()-start)),flush=True)
if __name__=="__main__":main()
