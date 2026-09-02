#!/usr/bin/env python3
"""Route-E post-bootstrap gate; host_preflight.py must pass first."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, importlib.metadata as md, json, os, shutil, subprocess, sys
from pathlib import Path
PINS={"torch":"2.6.0","transformers":"4.51.3","accelerate":"1.6.0","safetensors":"0.5.3","huggingface_hub":"0.30.2"}
NVBIT_SHA="dba61708b702ff4562343716bb8b38a2d14aae5991b9719aece097afe505467f"
WRAPPERS={"run_llama_tp4_rank0.sh":"cc38edf0eda9b4498ce639145618770f44e417563799be26b1ac50af29380829","rank0_nvbit_exec.sh":"02d34b01c44d9b11abe281addba7b2bda7488175305c42f9b246c5525ff8bbba","llama_tp_workload.py":"a713f79c39bd0c9038d89f3960e561b258361effb2012fa358586e60cd8a48a1","run_m4a_c.sh":"3f4112cc71ccb86ae876235665c9a662185a39e8139ac4a44a91ba850d69fb6b"}
def command(*argv):
    try:
        result=subprocess.run(argv,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT); return result.returncode,result.stdout
    except FileNotFoundError:return 127,f"command not found: {argv[0]}\n"
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--framework-root",type=Path); parser.add_argument("--work-root",type=Path); parser.add_argument("--minimum-free-gib",type=int,default=500); parser.add_argument("--required-gpu-count",type=int,default=4); parser.add_argument("--self-test",action="store_true"); args=parser.parse_args()
    if args.self_test:
        assert PINS["torch"]=="2.6.0" and len(NVBIT_SHA)==64 and len(WRAPPERS)==4; print("PASS capture-ready preflight static self-test"); return 0
    if not args.framework_root or not args.work_root: parser.error("--framework-root and --work-root are required unless --self-test")
    root,work=args.framework_root.resolve(),args.work_root.resolve(); work.mkdir(parents=True,exist_ok=True); errors=[]
    if args.required_gpu_count!=4: errors.append("Route E requires required-gpu-count=4")
    if sys.version_info[:2] != (3, 10): errors.append(f"Python lock mismatch: {sys.version_info.major}.{sys.version_info.minor} != 3.10")
    for tool in ("python3","nvcc","nvidia-smi","sha256sum","tar"):
        if not shutil.which(tool): errors.append(f"missing command: {tool}")
    versions={}
    for package,pin in PINS.items():
        try: versions[package]=md.version(package)
        except md.PackageNotFoundError: versions[package]="MISSING"
        if versions[package]!=pin: errors.append(f"package pin mismatch: {package}={versions[package]} != {pin}")
    tracer=root/"util/tracer_nvbit/tracer_tool/tracer_tool.so"; post=root/"util/tracer_nvbit/tracer_tool/traces-processing/post-traces-processing"
    for artifact in (tracer,post):
        if not artifact.is_file(): errors.append(f"missing built artifact: {artifact}")
    marker=work/"bootstrap"/"nvbit-1.7.6.sha256"
    if not marker.is_file() or marker.read_text().strip().split()[0] != NVBIT_SHA: errors.append("missing/mismatched checksum-verified NVBit bootstrap marker")
    wrapper_actual={}
    for name, expected in WRAPPERS.items():
        path=root/"util/llm_trace_capture"/name
        wrapper_actual[name]=hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "MISSING"
        if wrapper_actual[name] != expected: errors.append(f"wrapper digest mismatch: {name}")
    free_gib=shutil.disk_usage(work).free//1024**3
    if free_gib<args.minimum_free_gib: errors.append(f"free disk {free_gib} GiB < {args.minimum_free_gib} GiB")
    rc,gpus=command("nvidia-smi","--query-gpu=compute_cap","--format=csv,noheader")
    if rc or len([x for x in gpus.splitlines() if x.strip()])!=4 or any(x.strip()!="8.6" for x in gpus.splitlines() if x.strip()): errors.append("four visible SM86 GPUs unavailable")
    revision=os.environ.get("M4A_MODEL_REVISION",""); token_set=bool(os.environ.get("HF_TOKEN"))
    if len(revision)!=40: errors.append("M4A_MODEL_REVISION immutable SHA is not set")
    _,nvcc=command("nvcc","--version")
    report={"schema_version":"m4a-route-e-capture-ready-v1","timestamp_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"status":"PASS" if not errors else "BLOCKED","errors":errors,"python":sys.version,"packages":versions,"wrapper_sha256":wrapper_actual,"nvcc":nvcc,"nvbit_sha256":NVBIT_SHA,"tracer":str(tracer),"postprocessor":str(post),"free_gib":free_gib,"hf_token_present":token_set,"model_revision_set":len(revision)==40}
    out=work/"capture-ready-preflight.json"; out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(f"{report['status']} report={out}")
    for error in errors:print(f"error: {error}")
    return 0 if not errors else 1
if __name__=="__main__":raise SystemExit(main())
