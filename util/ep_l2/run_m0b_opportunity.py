#!/usr/bin/env python3
"""Run M0b observation controls on the reviewed speculative M0a+M1 parent."""
from __future__ import annotations
import argparse, gzip, hashlib, json, os, re, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORE = Path(os.environ.get("EP_L2_CORE", "/workspace/worktrees/gpgpu-sim-ep-l2-m0b"))
TRACE = Path("/workspace/worktrees/accel-sim-decoupled-l2/hw_run")
EXIT = "GPGPU-Sim: *** exit detected ***"
MATURE = "SPECULATIVE_PENDING_GATE"
ROSTER = {
 "convolutionSeparable": "decoupled-l2-pretraces/cudasdk/9.1/convolutionSeparable/__size_3072",
 "spmv": "decoupled-l2-extract/parboil.current.small8.stage/parboil/11.0/parboil-spmv/_i___data_large_input_Dubcova3_mtx_bin___data_large_input_vector_bin__o_Dubcova3_mtx_out",
 "vectorAdd_4M": "decoupled-l2-pretraces/cudasdk/9.1/vectorAdd/__size_4000000",
 "scan": "decoupled-l2-pretraces/cudasdk/9.1/scan/NO_ARGS",
 "sad": "decoupled-l2-extract/parboil.current.small8.stage/parboil/11.0/parboil-sad/_i___data_default_input_reference_bin___data_default_input_frame_bin__o_out_bin",
 "dwt2d": "decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/dwt2d-rodinia-3.1/__data_192_bmp__d_192x192__f__5__l_3",
 "cfd_097k": "decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/cfd-rodinia-3.1/__data_fvcorr_domn_097K",
}
CONTROLS = ("convolutionSeparable", "dwt2d", "sad")
MODES = {"M0A_ON_M0B_OFF_M1_STATIC": "OFF", "M0A_ON_M0B_ON_M1_STATIC": "ON"}

def sha(path):
 return subprocess.check_output(("git", "-C", str(path), "rev-parse", "HEAD"), text=True).strip()
def digest(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""): h.update(b)
 return h.hexdigest()
def active(path):
 return [x.strip() for x in path.read_text().splitlines() if x.strip() and not x.startswith("#")]
def write(path, obj): path.write_text(json.dumps(obj, indent=2, sort_keys=True)+"\n")
def terminal(log):
 cyc=ins=None; ok=False
 for line in log.read_text(errors="replace").splitlines():
  ok |= EXIT in line
  m=re.match(r"^gpu_tot_sim_cycle\s*=\s*(\d+)\s*$",line)
  if m: cyc=m.group(1)
  m=re.match(r"^gpu_tot_sim_insn\s*=\s*(\d+)\s*$",line)
  if m: ins=m.group(1)
 return ok,cyc,ins
def run(task,out,cmd,audit):
 name,mode=task; directory=out/mode/name; directory.mkdir(parents=True,exist_ok=True); log=directory/"raw.log"; start=time.time()
 env=os.environ.copy(); env.update({"CORE":str(CORE),"FRAME":str(ROOT),"CUDA_INSTALL_PATH":"/usr/local/cuda-11.8"})
 shell='set -eo pipefail; source "$CORE/setup_environment" release >/dev/null; source "$FRAME/gpu-simulator/setup_environment.sh" release >/dev/null; exec "$@"'
 with log.open("w") as f: p=subprocess.run(("bash","-lc",shell,"m0b-run",*cmd),cwd=directory,stdout=f,stderr=subprocess.STDOUT,env=env)
 ok,cyc,ins=terminal(log); status={"workload":name,"mode":mode,"exit_code":p.returncode,"normal_simulator_exit":ok,"terminal_gpu_tot_sim_cycle":cyc,"terminal_gpu_tot_sim_insn":ins,"wall_seconds":round(time.time()-start,3),"audit":audit}
 if p.returncode or not ok: status.update(status="FAILED"); write(directory/"run_status.json",status); return status
 for parser in ("parse_epl2_m0a.py","parse_epl2_b0.py"):
  q=subprocess.run((sys.executable,str(ROOT/"util/ep_l2"/parser),str(log),"--out",str(directory),"--framework-commit",audit["framework_sha"],"--core-commit",audit["core_sha"],*( ("--source-log",str(log)) if parser=="parse_epl2_b0.py" else ())),capture_output=True,text=True)
  (directory/(parser+".stdout")).write_text(q.stdout); (directory/(parser+".stderr")).write_text(q.stderr)
  if q.returncode: status.update(status="FAILED",detail=q.stderr.strip()); write(directory/"run_status.json",status); return status
 if mode.endswith("ON_M1_STATIC"):
  q=subprocess.run((sys.executable,str(ROOT/"util/ep_l2/parse_epl2_m0b.py"),str(log),"--out",str(directory),"--framework-commit",audit["framework_sha"],"--core-commit",audit["core_sha"]),capture_output=True,text=True)
  (directory/"m0b_parser.stdout").write_text(q.stdout); (directory/"m0b_parser.stderr").write_text(q.stderr)
  if q.returncode: status.update(status="FAILED",detail=q.stderr.strip()); write(directory/"run_status.json",status); return status
 packed=log.with_suffix(".log.gz")
 with log.open("rb") as src,gzip.open(packed,"wb") as dst: shutil.copyfileobj(src,dst)
 log.unlink(); status.update(status="COMPLETE_VALID",raw_log_gz=str(packed),raw_log_gz_sha256=digest(packed)); write(directory/"run_status.json",status); return status
def main():
 ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("--out",type=Path,default=Path("/workspace/results/ep_l2_m0b")); ap.add_argument("--jobs",type=int,default=3); ap.add_argument("--only",choices=tuple(ROSTER)); args=ap.parse_args()
 base=CORE/"configs/tested-cfgs/SM7_QV100/gpgpusim.config"; trace_cfg=ROOT/"gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"; d512=ROOT/"tests/ep_l2/b0_banked_d512_850.config"; overlays={"OFF":ROOT/"tests/ep_l2/m0b_off.config","ON":ROOT/"tests/ep_l2/m0b_on.config"}; sim=ROOT/"gpu-simulator/bin/release/accel-sim.out"
 for p in (base,trace_cfg,d512,*overlays.values(),sim):
  if not p.is_file(): raise SystemExit("required asset missing: "+str(p))
 if active(overlays["OFF"]) != ["-gpgpu_ep_l2_m0a_stats 1","-gpgpu_ep_l2_m0b_stats 0"] or active(overlays["ON"]) != ["-gpgpu_ep_l2_m0a_stats 1","-gpgpu_ep_l2_m0b_stats 1"]: raise SystemExit("M0b one-bit overlay contract failed")
 audit={"schema_version":"EPL2M0BV1","semantic_base_id":"EP_L2_D512_CALIBRATED","maturity":MATURE,"promotion_dependencies":["M0A_FINAL_PASS","M1_FINAL_PASS","M0A_M1_INTEGRATED_PARENT_FINAL_PROMOTION"],"framework_sha":sha(ROOT),"core_sha":sha(CORE),"frequency_mhz":850,"primary_variant":"D512_B0_Banked","functional_features":{"unified_payload":False,"ro_pending_state":False,"tvd":False,"adaptive_policy":False},"m0a_stats_enabled":True,"m0b_stats_enabled_by_mode":{"M0A_ON_M0B_OFF_M1_STATIC":False,"M0A_ON_M0B_ON_M1_STATIC":True},"config_delta_evidence":"only -gpgpu_ep_l2_m0b_stats: 0 -> 1"}
 args.out.mkdir(parents=True,exist_ok=True); write(args.out/"campaign_manifest.json",audit)
 names=(args.only,) if args.only else tuple(ROSTER); tasks=[(n,"M0A_ON_M0B_ON_M1_STATIC") for n in names]+[(n,m) for n in CONTROLS if n in names for m in MODES]; tasks=list(dict.fromkeys(tasks)); commands={}
 for n,m in tasks:
  trace=TRACE/ROSTER[n]/"traces/kernelslist.g"
  if not trace.is_file(): raise SystemExit("missing frozen trace: "+str(trace))
  commands[n,m]=(str(sim),"-config",str(base),"-config",str(trace_cfg),"-config",str(d512),"-config",str(overlays[MODES[m]]),"-trace",str(trace))
 failed=[]
 with ThreadPoolExecutor(max_workers=max(1,args.jobs)) as pool:
  futures=[pool.submit(run,t,args.out,commands[t],audit) for t in tasks]
  for f in as_completed(futures):
   s=f.result(); print(s["status"],s["mode"],s["workload"],flush=True); failed += [s] if s["status"]!="COMPLETE_VALID" else []
 if failed: raise SystemExit("M0b campaign has failed cells")
if __name__ == "__main__": main()
