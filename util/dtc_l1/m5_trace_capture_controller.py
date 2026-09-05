#!/usr/bin/env python3
"""M5.0BT exact-trace capture controller.  No PASS bundle is ever mutable."""
import argparse,csv,hashlib,json,os,shutil,subprocess,sys,tarfile,tempfile,time
from pathlib import Path
W=("bicg","atax","gemv","mvt","syrk","gesu","syr2k","spmv","2mm","2dconv")
C={**{x:x for x in W if x not in ("spmv","2dconv")},"2dconv":"conv2d"}; PIN="0db04452ec1c47630e4b08002067d82c6811e243"; RESERVE=3
FIELDS=("workload canonical_source source_tree_sha trace_build_script_sha trace_capture_binary_sha arguments input_hashes checker_reference_sha capture_app_correctness gpu_uuid_model_cc driver_cuda tracer_source_tree_sha tracer_tool_sha nvbit_archive_sha postprocess_sha trace_format kernel_inventory_sha kernel_invocations raw_trace_count grouped_trace_count kernelslist_sha kernelslist_g_sha raw_trace_set_sha256 traceg_set_sha256 trace_bundle_id status").split()
def run(args,**kw):
 kw.setdefault("stdout",subprocess.PIPE);kw.setdefault("stderr",subprocess.PIPE);kw.setdefault("text",True);kw.setdefault("check",True);return subprocess.run(args,**kw)
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def setsha(ps):return hashlib.sha256("".join(f"{sha(p)}  {p.name}\n" for p in sorted(ps)).encode()).hexdigest()
def git(p,*a):return run(["git","-C",str(p),*a]).stdout.strip()
def tree(p):
 return hashlib.sha256("".join(f"{sha(Path(p)/x)}  {x}\n" for x in sorted(git(p,"ls-files").splitlines())).encode()).hexdigest()
def write_state(o,w,s): (o/"state").mkdir(exist_ok=True);(o/"state"/(w+".state")).write_text(s+"\n")
def valid_bundle(p):
 m=p/"CAPTURE_RESULT.json"; sums=p/"SHA256SUMS"
 if not m.exists() or not sums.exists():return False
 return all(sha(p/name)==digest for digest,name in (x.split("  ",1) for x in sums.read_text().splitlines() if x))
def archive_bundle(bundle):
 if not valid_bundle(bundle):raise RuntimeError("invalid bundle before archive")
 out=bundle.with_suffix(".tar.gz")
 if out.exists():raise RuntimeError("refuse overwrite archive")
 with tarfile.open(out,"w:gz",format=tarfile.PAX_FORMAT) as t:
  for p in sorted(bundle.rglob("*")):t.add(p,arcname=f"{bundle.name}/{p.relative_to(bundle)}",recursive=False)
 meta={"trace_bundle_id":json.loads((bundle/"CAPTURE_RESULT.json").read_text())["trace_bundle_id"],"archive_sha256":sha(out),"archive_bytes":out.stat().st_size};(bundle/"ARCHIVE.json").write_text(json.dumps(meta,sort_keys=True,indent=2));return out,meta
def verify_transfer(src,dst):
 if sha(src)!=sha(dst):raise RuntimeError("transfer SHA mismatch")
 return {"source_sha256":sha(src),"destination_sha256":sha(dst),"status":"PASS"}
def storage_gate(o):
 b=o/"bundles/bicg"; f=o/"STORAGE_BUDGET.tsv"
 if not valid_bundle(b) or not f.exists():raise RuntimeError("BICG valid pilot and storage budget required")
 r=list(csv.DictReader(f.open(),delimiter="\t"));
 if len(r)!=1:raise RuntimeError("invalid storage budget")
 x=r[0]; raw=int(x["raw_bytes"]); archive=int(x["archive_bytes"]); free=shutil.disk_usage(o).free; projected=max(raw,archive)*10*RESERVE
 if raw<=0 or archive<=0 or free<projected:raise RuntimeError("unsafe projected heterogeneous trace storage")
 return {"projected_bytes":projected,"free_bytes":free,"status":"PASS"}
def inventory(t):
 raw=sorted(t.glob("kernel-*.trace"));grp=sorted(t.glob("kernel-*.traceg"));kl=t/"kernelslist";kg=t/"kernelslist.g";stats=t/"stats.csv"
 if not(raw and grp and kl.is_file() and kg.is_file() and stats.is_file()):raise RuntimeError("incomplete trace artifact set")
 inv=list(csv.DictReader(stats.open()))
 if not inv or any(not r.get("kernel mangled name") or not r.get("grid_dimX") or not r.get("block_dimX") for r in inv):raise RuntimeError("stats lacks kernel ABI/geometry")
 raw_names=[x.strip() for x in kl.read_text().splitlines() if x.startswith("kernel-")];grp_names=[x.strip().replace(".traceg",".trace") for x in kg.read_text().splitlines() if x.startswith("kernel-")]
 if len(raw_names)!=len(raw) or len(grp_names)!=len(grp) or set(raw_names)!=set(grp_names):raise RuntimeError("raw/grouped/kernelslist mapping mismatch")
 return inv,raw,grp
def pin_sources(a):
 want=((a.polybench_src,"5584aaa7d0be810ff5eb0b61c49fb64ecc81ba4c"),(a.spmv_wrapper,"de9cf4293f418877aa9cdb6a2395338ca06674a6"),(a.parboil_src,"4e0fc54866546efa44fe93af57c9cef62f6c8eb9"),(a.tracer_framework_src,PIN))
 for p,h in want:
  if git(p,"rev-parse","HEAD")!=h or git(p,"status","--porcelain"):raise RuntimeError(f"dirty/wrong source identity: {p}")
 return {str(p):tree(p) for p,_ in want}
def build_tracer(a,o,nvcc):
 scratch=o/"scratch-tracer";shutil.rmtree(scratch,ignore_errors=True);shutil.copytree(a.tracer_framework_src/"util/tracer_nvbit",scratch,ignore=shutil.ignore_patterns("nvbit_release","*.o","*.so","post-traces-processing"))
 with tarfile.open(a.nvbit_archive) as t:t.extractall(scratch/"nvbit_release")
 # archives may contain one top-level directory; normalize to expected core/.
 children=list((scratch/"nvbit_release").iterdir());
 if not (scratch/"nvbit_release/core").exists() and len(children)==1 and children[0].is_dir():shutil.move(str(children[0]),str(scratch/"tmp"));shutil.rmtree(scratch/"nvbit_release");shutil.move(str(scratch/"tmp"),str(scratch/"nvbit_release"))
 if not (scratch/"nvbit_release/core/libnvbit.a").exists():raise RuntimeError("NVBit archive lacks required core/libnvbit.a")
 env={**os.environ,"NVCC":str(nvcc),"PATH":str(Path(nvcc).parent)+":"+os.environ["PATH"]};run(["make"],cwd=scratch,env=env)
 tool=scratch/"tracer_tool/tracer_tool.so";post=scratch/"tracer_tool/traces-processing/post-traces-processing"
 if not tool.exists() or not post.exists():raise RuntimeError("tracer build incomplete")
 return tool,post,{"tracer_source_tree_sha":tree(a.tracer_framework_src),"tracer_tool_sha":sha(tool),"nvbit_archive_sha":sha(a.nvbit_archive),"nvbit_root_sha":tree(scratch) if (scratch/".git").exists() else sha(scratch/"nvbit_release/core/libnvbit.a"),"postprocess_sha":sha(post),"nvcc":run([str(nvcc),"--version"]).stdout,"ptxas":run([str(Path(nvcc).parent/"ptxas"),"--version"]).stdout,"cc":run([os.environ.get("CC","gcc"),"--version"]).stdout,"cxx":run([os.environ.get("CXX","g++"),"--version"]).stdout}
def main():
 p=argparse.ArgumentParser();
 for x in ("polybench-src","spmv-wrapper","parboil-src","spmv-input-dir","spmv-reference","tracer-framework-src","nvbit-archive","out"):p.add_argument("--"+x,type=Path,required=True)
 p.add_argument("--workloads",default=",".join(W));p.add_argument("--resume",action="store_true");p.add_argument("--pilot-only",action="store_true");p.add_argument("--admit-full-wave",action="store_true");a=p.parse_args();o=a.out.resolve();o.mkdir(parents=True,exist_ok=True);ws=[x for x in a.workloads.split(",") if x in W];
 if not ws:raise SystemExit("bad workload set")
 if a.pilot_only:ws=["bicg"]
 pin_sources(a)
 if len(ws)>1:storage_gate(o) if a.admit_full_wave else (_ for _ in ()).throw(RuntimeError("full wave requires storage gate"))
 nvcc=Path(os.environ.get("NVCC","/usr/local/cuda-11.8/bin/nvcc"));
 if "release 11.8" not in run([str(nvcc),"--version"]).stdout:raise RuntimeError("CUDA 11.8 required")
 # Device probe is built/run only after all offline source and admission checks pass.
 tool,post,prov=build_tracer(a,o,nvcc);(o/"environment.json").write_text(json.dumps(prov,sort_keys=True,indent=2))
 root=Path(__file__).resolve().parents[2];probe=o/"tools/device_probe";probe.parent.mkdir(exist_ok=True);run([str(nvcc),"-arch=sm_70",str(root/"util/dtc_l1/m5_trace_capture_device_probe.cu"),"-o",str(probe)]);device=run([str(probe)]).stdout.splitlines()
 if len(device)!=2 or "V100" not in device[1]:raise RuntimeError("selected CUDA-visible logical device 0 is not V100")
 result=o/"CAPTURE_RESULT_MANIFEST.tsv";result.write_text("\t".join(FIELDS)+"\n") if not result.exists() else None
 src={"bicg":"BICG/bicg.cu","atax":"ATAX/atax.cu","gemv":"GEMVER/gemver.cu","mvt":"MVT/mvt.cu","syrk":"SYRK/syrk.cu","gesu":"GESUMMV/gesummv.cu","syr2k":"SYR2K/syr2k.cu","2mm":"2MM/2mm.cu","2dconv":"2DCONV/2DConvolution.cu"};bin={"gemv":"gemver","2mm":"twomm","2dconv":"twodconv"}
 # Requested rows build independently: a SpMV failure cannot block a BICG pilot.
 for w in ws:
  b=o/"bundles"/w
  if b.exists():
   if a.resume and valid_bundle(b):write_state(o,w,"PASS");continue
   raise RuntimeError(f"immutable PASS/invalid existing bundle: {b}")
  write_state(o,w,"CAPTURING");d=o/"attempts"/w/("attempt-"+str(int(time.time())));d.mkdir(parents=True)
  try:
   exe=d/(bin.get(w,w)); buildscript=root/("util/dtc_l1/build_m5_parboil_spmv_trace_sm70.sh" if w=="spmv" else "util/dtc_l1/build_m5_polybench_cuda_trace_sm70.sh")
   if w=="spmv":run([str(buildscript),str(a.spmv_wrapper),str(a.parboil_src),str(d/"build")]);exe=d/"build/spmv";cmd=[str(exe),"-i",str(a.spmv_input_dir/"bcsstk18.mtx")+","+str(a.spmv_input_dir/"vector.bin"),"-o","result.bin"]
   else:run([str(nvcc),"-arch=sm_70","-O2","-cudart","shared",str(a.polybench_src/"CUDA"/src[w]),"-o",str(exe)]);cmd=[str(exe)]
   env={**os.environ,"LD_PRELOAD":str(tool)};env.pop("DYNAMIC_KERNEL_RANGE",None)
   with open(d/"application.stdout","w") as so,open(d/"tracer.stderr","w") as se:run(cmd,cwd=d,env=env,stdout=so,stderr=se)
   if w=="spmv":run([sys.executable,str(root/"util/dtc_l1/verify_m5_parboil_spmv_output.py"),str(a.spmv_reference),str(d/"result.bin")],stdout=open(d/"correctness.log","w"))
   else:run([sys.executable,str(root/"util/dtc_l1/verify_m5_polybench_output.py"),C[w],str(d/"application.stdout")],stdout=open(d/"correctness.log","w"))
   t=d/"traces";run([str(post),str(t/"kernelslist")],cwd=d,stdout=open(d/"postprocess.stdout","w"));inv,raw,grp=inventory(t);(d/"kernel_inventory.json").write_text(json.dumps(inv,sort_keys=True,indent=2));err=(d/"tracer.stderr").read_text(errors="replace")
   if any(x in err.lower() for x in ("cudaerror","nvbit fatal","tracer fatal","assertion")):raise RuntimeError("explicit tracer/CUDA error")
   b.parent.mkdir(exist_ok=True);shutil.move(str(d),str(b));rawh=setsha(list(b.glob("traces/kernel-*.trace")));gh=setsha(list(b.glob("traces/kernel-*.traceg")));bid=hashlib.sha256((w+rawh+gh+sha(b/"traces/kernelslist.g")).encode()).hexdigest();rec={"trace_bundle_id":bid,"trace_capture_binary_sha":sha(exe),"kernel_inventory":inv,"device":device[1],"provenance":prov,"raw_trace_set_sha256":rawh,"traceg_set_sha256":gh};(b/"CAPTURE_RESULT.json").write_text(json.dumps(rec,sort_keys=True,indent=2));files=[p for p in b.rglob("*") if p.is_file() and p.name!="SHA256SUMS"];(b/"SHA256SUMS").write_text("".join(f"{sha(p)}  {p.relative_to(b)}\n" for p in sorted(files)))
   vals=[w,w,git(a.polybench_src,"rev-parse","HEAD"),tree(a.polybench_src),sha(buildscript),sha(exe)," ".join(cmd[1:]),"N/A",sha(a.spmv_reference) if w=="spmv" else "N/A","PASS",device[1],"environment.json",prov["tracer_source_tree_sha"],prov["tracer_tool_sha"],prov["nvbit_archive_sha"],prov["postprocess_sha"],"NVBit-v1.8",sha(b/"kernel_inventory.json"),str(len(inv)),str(len(raw)),str(len(grp)),sha(b/"traces/kernelslist"),sha(b/"traces/kernelslist.g"),rawh,gh,bid,"PASS"]
   with result.open("a") as f:f.write("\t".join(vals)+"\n")
   write_state(o,w,"PASS");archive_bundle(b)
  except Exception as e:write_state(o,w,"RETRY_READY");(d/"controller.stderr").write_text(str(e)+"\n")
if __name__=="__main__":main()
