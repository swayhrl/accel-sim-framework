"""V3 minimal CPU revalidation using V2 SHA plus unchanged inode,size,mtime,ctime."""
import json,hashlib,time,importlib.metadata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"docs/ai_workload_research/runs/QWEN_DECODE_MEMORY_COMPUTE_ATTRIBUTION_109_V10"
V2=Path('/home/huangrulin/workspace/worktrees/accel-sim-aiarch-bf16-batch-performance-and-numeric-study-109-v8/docs/ai_workload_research/runs/QWEN_BF16_BATCH_PERFORMANCE_NUMERIC_STUDY_109_V8')
def sha_file(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1024**2),b""):h.update(chunk)
    return h.hexdigest()
def canonical(v):return hashlib.sha256(json.dumps(v,separators=(",",":")).encode()).hexdigest()
def main():
    start=time.time();prior=json.load(open(OUT/".private/V2_G0_REVALIDATION.json"));runtime=json.load(open(OUT/"SOURCE_AND_RUNTIME.json"));files=[];hashed=0
    for f in prior["model_files"]:
        p=Path(f["path"]);s=p.stat()
        same=(s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(f["inode"],f["size"],f["mtime_ns"],f["ctime_ns"])
        if same:mode="REUSED_V2_FULL_SHA_UNCHANGED_STAT"
        else:
            h=sha_file(p);assert h==f["sha256"],str(p);mode="V3_BOUNDED_REHASH_PASS";hashed+=s.st_size
        after=p.stat();assert (s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
        files.append(dict(path=str(p),expected_sha256=f["sha256"],mode=mode,inode=s.st_ino,size=s.st_size,mtime_ns=s.st_mtime_ns,ctime_ns=s.st_ctime_ns))
    site=Path("/data/c16/envs/c16-vllm-v0.30.0-sm89-v1/lib/python3.12/site-packages")
    hashes={k:sha_file(site/"vllm"/rel) for k,rel in [("compilation.py","config/compilation.py"),("qwen2.py","model_executor/models/qwen2.py")]}
    assert hashes==runtime["vllm_installed_source_sha256"]
    for rel,value in runtime["cache_isolation_interfaces"].items():assert sha_file(site/rel)==value["sha256"]
    versions={name:importlib.metadata.version(name) for name in runtime["versions"]};assert versions==runtime["versions"]
    inp=json.load(open(V2/".private/inputs.json"));ir=json.load(open(OUT/"INPUT_RECEIPT.json"));checks=[]
    assert len(inp)==2
    for row in ir["inputs"]:
        ids=inp[row["source"]+"_512"];assert len(ids)==512 and all(type(v)is int for v in ids)
        assert canonical(ids)==row["token_ids_sha256"]
        checks.append(dict(source=row["source"],tokens=512,token_ids_sha256=canonical(ids),status="PASS"))
    (OUT/".private/inputs.json").write_text(json.dumps(inp,separators=(",",":"))+"\n")
    ref=V2/".private/reference.json";assert sha_file(ref)==ir["reference"]["sha256"]
    (OUT/".private/reference.json").write_bytes(ref.read_bytes())
    result=dict(status="G0_PASS_REUSED_V2_IDENTITY",model_files=files,new_model_hash_bytes=hashed,asset_stat_reuse_assumption="Ordinary filesystem change detection by exact inode,size,mtime_ns,ctime_ns against V2 SHA-qualified files; no new full-stream SHA claim for unchanged files.",versions=versions,source_hashes=hashes,input_checks=checks,reference_sha256=sha_file(ref),NVML_init=0,CUDA_init=0,model_initializations=0,seconds=time.time()-start)
    (OUT/"G0_REVALIDATION.json").write_text(json.dumps(result,indent=2)+"\n")
    runtime["V5_revalidation"]="G0_REVALIDATION.json";(OUT/"SOURCE_AND_RUNTIME.json").write_text(json.dumps(runtime,indent=2)+"\n")
    print(json.dumps(dict(G0="PASS",files=len(files),new_model_hash_bytes=hashed,seconds=time.time()-start)),flush=True)
if __name__=="__main__":main()
