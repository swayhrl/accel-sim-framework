#!/usr/bin/env python3
"""M5.0BT exact trace capture.  Valid bundles are immutable; archives/transfers
are external resumable operations.  Dependencies are selected by WorkloadSpec."""
import argparse,csv,hashlib,json,os,re,shutil,subprocess,sys,tarfile,time
from dataclasses import dataclass
from pathlib import Path
PIN="0db04452ec1c47630e4b08002067d82c6811e243"; POLY_PIN="5584aaa7d0be810ff5eb0b61c49fb64ecc81ba4c"
WRAP_PIN="de9cf4293f418877aa9cdb6a2395338ca06674a6"; PARBOIL_PIN="4e0fc54866546efa44fe93af57c9cef62f6c8eb9"
ROOT=Path(__file__).resolve().parents[2]; MANIFEST=ROOT/"docs/dtc_l1/m5/trace/PAPER10_TRACE_CAPTURE_MANIFEST.tsv"
@dataclass(frozen=True)
class WorkloadSpec:
 workload_id:str; canonical_id:str; source_kind:str; source_commit:str; source_file:str; binary_name:str; checker_kind:str; dimensions:str; build_script:str; build_arguments:tuple; input_kind:str
P={"bicg":("BICG/bicg.cu","bicg","bicg","NX=NY=4096"),"atax":("ATAX/atax.cu","atax","atax","NX=NY=4096"),"gemv":("GEMVER/gemver.cu","gemver","gemv","N=4096"),"mvt":("MVT/mvt.cu","mvt","mvt","N=4096"),"syrk":("SYRK/syrk.cu","syrk","syrk","NI=NJ=1024"),"gesu":("GESUMMV/gesummv.cu","gesummv","gesu","N=4096"),"syr2k":("SYR2K/syr2k.cu","syr2k","syr2k","NI=NJ=1024"),"2mm":("2MM/2mm.cu","twomm","2mm","NI=NJ=NK=NL=1024"),"2dconv":("2DCONV/2DConvolution.cu","twodconv","conv2d","NI=NJ=4096")}
S={w:WorkloadSpec(w,"polybench_"+w,"polybench",POLY_PIN,x,b,c,d,"util/dtc_l1/build_m5_polybench_cuda_trace_sm70.sh",("--workload",b),"GENERATED_FROM_FROZEN_SOURCE_DIMENSIONS") for w,(x,b,c,d) in P.items()}
S["spmv"]=WorkloadSpec("spmv","parboil_spmv_medium_bcsstk18","spmv",WRAP_PIN,"main.cu","spmv","spmv","medium bcsstk18; 63 CTA expected","util/dtc_l1/build_m5_parboil_spmv_trace_sm70.sh",(),"FILE_BACKED_CANONICAL_INPUT")
W=tuple(S); FIELDS="workload canonical_id source_kind source_commit source_tree_sha source_file source_file_sha source_dependencies input_identity_kind input_hashes build_script build_script_sha build_command trace_capture_binary_sha checker_kind checker_reference_sha gpu_uuid_model_cc tracer_source_tree_sha tracer_tool_sha nvbit_archive_sha postprocess_sha trace_format kernel_invocation_count kernel_invocation_manifest_sha kernel_geometry_manifest_sha kernelslist_sha kernelslist_g_sha raw_trace_count grouped_trace_count raw_trace_set_sha256 traceg_set_sha256 trace_bundle_id status".split()
def run(a,**k): k.setdefault("stdout",subprocess.PIPE);k.setdefault("stderr",subprocess.PIPE);k.setdefault("text",True);k.setdefault("check",True);return subprocess.run(a,**k)
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def setsha(ps,root):return hashlib.sha256("".join(f"{sha(p)}  {p.relative_to(root)}\n" for p in sorted(ps)).encode()).hexdigest()
def git(p,*a):return run(["git","-C",str(p),*a]).stdout.strip()
def tree(p):
 # Git mode/object identity is authoritative for tracked regular files and
 # symlinks; do not dereference a tracked symlink whose target is a directory.
 return hashlib.sha256(git(p,"ls-files","-s").encode()).hexdigest()
def st(o,w,x):(o/"state").mkdir(exist_ok=True);(o/"state"/(w+".state")).write_text(x+"\n")
def req(p,name):
 if p is None or not p.exists():raise RuntimeError(f"{name} required by selected workload")
def bundle_required(b):
 t=b/"traces";return [b/"CAPTURE_RESULT.json",b/"application.stdout",b/"tracer.stderr",b/"correctness.log",b/"postprocess.stdout",b/"kernel_invocation_manifest.json",b/"kernel_geometry_manifest.json",t/"kernelslist",t/"kernelslist.g",t/"stats.csv",*sorted(t.glob("kernel-*.traceg"))]
def valid_bundle(b):
 b=Path(b); sums=b/"SHA256SUMS"
 if not (b/"CAPTURE_RESULT.json").is_file() or not sums.is_file():return False
 lines=sums.read_text(errors="replace").splitlines()
 if not lines:return False
 seen=set()
 for x in lines:
  m=re.fullmatch(r"([0-9a-f]{64})  ([^\0]+)",x)
  if not m:return False
  d,n=m.groups();q=Path(n)
  if q.is_absolute() or ".." in q.parts or n in seen or not (b/q).is_file() or sha(b/q)!=d:return False
  seen.add(n)
 if any(not q.is_file() or str(q.relative_to(b)) not in seen for q in bundle_required(b)):return False
 try:r=json.loads((b/"CAPTURE_RESULT.json").read_text());return bool(r["trace_bundle_id"]) and r["kernel_invocation_count"]>0 and bool(list((b/"traces").glob("kernel-*.traceg")))
 except (KeyError,TypeError,json.JSONDecodeError):return False
def paths(o,w):a=o/"archives"/(w+".tar.zst");return a,a.with_suffix(".archive.json")
def valid_archive(o,w):
 a,m=paths(o,w)
 try:x=json.loads(m.read_text());return a.is_file() and x["archive_sha256"]==sha(a) and x["archive_bytes"]==a.stat().st_size
 except (OSError,KeyError,json.JSONDecodeError):return False
def archive(o,b):
 if not valid_bundle(b):raise RuntimeError("invalid bundle before archive")
 a,m=paths(o,b.name);a.parent.mkdir(exist_ok=True)
 if valid_archive(o,b.name):return a
 if a.exists() or m.exists():raise RuntimeError("refuse ambiguous archive overwrite")
 if not shutil.which("zstd"):raise RuntimeError("zstd required for transfer-grade archive")
 tmp=a.with_name(a.name+f".partial.{os.getpid()}.{int(time.time())}")
 run(["tar","--zstd","-cf",str(tmp),"-C",str(b.parent),b.name]);os.replace(tmp,a)
 m.write_text(json.dumps({"workload":b.name,"trace_bundle_id":json.loads((b/"CAPTURE_RESULT.json").read_text())["trace_bundle_id"],"archive_path":str(a),"archive_sha256":sha(a),"archive_bytes":a.stat().st_size,"archive_format":"tar.zst","source_host":os.uname().nodename,"created_unix":int(time.time())},sort_keys=True,indent=2)+"\n");return a
def receipt(o,w):return o/"transfers"/(w+".transfer.json")
def transfer(o,w,dst):
 a,_=paths(o,w);r=receipt(o,w)
 if r.is_file():return
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(a,dst)
 if sha(a)!=sha(dst):raise RuntimeError("copyback SHA mismatch")
 r.parent.mkdir(exist_ok=True);r.write_text(json.dumps({"workload":w,"source_archive":str(a),"destination_archive":str(dst),"source_sha256":sha(a),"destination_sha256":sha(dst),"status":"TRANSFER_PASS","created_unix":int(time.time())},sort_keys=True,indent=2)+"\n")
def gate(o):
 b=o/"bundles/bicg";f=o/"STORAGE_ADMISSION.json"
 if not valid_bundle(b) or not valid_archive(o,"bicg") or not f.is_file():raise RuntimeError("valid BICG bundle/archive and storage admission receipt required")
 try:x=json.loads(f.read_text())
 except json.JSONDecodeError as e:raise RuntimeError("invalid storage admission receipt") from e
 keys={"bicg_trace_bundle_id","bicg_archive_sha256","raw_bytes","grouped_bytes","archive_bytes","working_headroom_bytes","safety_factor","projected_bytes","free_bytes","data_volume","admission"}
 if keys-set(x) or x["admission"]!="PASS":raise RuntimeError("incomplete storage admission receipt")
 a,_=paths(o,"bicg");r=json.loads((b/"CAPTURE_RESULT.json").read_text())
 if x["bicg_trace_bundle_id"]!=r["trace_bundle_id"] or x["bicg_archive_sha256"]!=sha(a):raise RuntimeError("storage receipt not BICG-bound")
 raw,grp,arc,head=[int(x[k]) for k in ("raw_bytes","grouped_bytes","archive_bytes","working_headroom_bytes")];projected=(raw+grp+arc+head)*float(x["safety_factor"])
 if min(raw,grp,arc,head)<=0 or projected>int(x["projected_bytes"]) or shutil.disk_usage(o).free<projected:raise RuntimeError("unsafe projected heterogeneous trace storage")
 return {"projected_bytes":int(projected),"free_bytes":shutil.disk_usage(o).free,"status":"PASS"}
def token(line,suffix):
 for x in line.split():
  n=Path(x).name
  if n.startswith("kernel-") and n.endswith(suffix):return n
 return None
def inventory(t):
 raw=sorted(t.glob("kernel-*.trace"));grp=sorted(t.glob("kernel-*.traceg"));kl=t/"kernelslist";kg=t/"kernelslist.g";stats=t/"stats.csv"
 if not(raw and grp and kl.is_file() and kg.is_file() and stats.is_file()):raise RuntimeError("incomplete trace artifact set")
 rows=list(csv.DictReader(stats.open()))
 fields=("grid_dimX","grid_dimY","grid_dimZ","block_dimX","block_dimY","block_dimZ")
 if not rows or any(not x.get("kernel mangled name") or any(not x.get(k) for k in fields) for x in rows):raise RuntimeError("stats lacks source-supported kernel ABI/geometry")
 rn=[token(x,".trace") for x in kl.read_text().splitlines()];gn=[token(x,".traceg") for x in kg.read_text().splitlines()]
 if None in rn or None in gn or gn!=[x+"g" for x in rn] or len(rn)!=len(raw) or len(gn)!=len(grp) or len(rows)!=len(rn) or set(rn)!={x.name for x in raw} or set(gn)!={x.name for x in grp}:raise RuntimeError("ordered replay mapping mismatch")
 inv=[{"dynamic_invocation_index":i,"raw_trace":n,"grouped_trace":n+"g","kernel_mangled_name":r["kernel mangled name"],**{k:int(r[k]) for k in fields},"cta_count":int(r["grid_dimX"])*int(r["grid_dimY"])*int(r["grid_dimZ"])} for i,(n,r) in enumerate(zip(rn,rows))]
 geom=[{k:x[k] for k in ("dynamic_invocation_index","raw_trace","grouped_trace",*fields,"cta_count")} for x in inv];return inv,geom,raw,grp
def rows():return {x["thesis_id"]:x for x in csv.DictReader((z for z in MANIFEST.read_text().splitlines() if not z.startswith("#")),delimiter="\t")}
def specs(a):
 ws=[x for x in a.workloads.split(",") if x]
 if not ws or len(set(ws))!=len(ws) or any(x not in S for x in ws):raise RuntimeError("bad workload set")
 return [S["bicg"]] if a.pilot_only else [S[x] for x in ws]
def sources(a,ss):
 req(a.tracer_framework_src,"tracer framework source");req(a.nvbit_archive,"NVBit archive");want=[("tracer",a.tracer_framework_src,PIN)]
 if any(x.source_kind=="polybench" for x in ss):want.append(("polybench",a.polybench_src,POLY_PIN))
 if any(x.source_kind=="spmv" for x in ss):want += [("spmv wrapper",a.spmv_wrapper,WRAP_PIN),("parboil",a.parboil_src,PARBOIL_PIN)];req(a.spmv_input_dir,"SpMV input directory");req(a.spmv_reference,"SpMV reference")
 for n,p,h in want:
  req(p,n)
  if git(p,"rev-parse","HEAD")!=h or git(p,"status","--porcelain"):raise RuntimeError(f"dirty/wrong source identity: {n}")
 out={n:{"commit":h,"tree":tree(p)} for n,p,h in want};rs=rows()
 for s in ss:
  if s.source_kind=="polybench":
   q=a.polybench_src/"CUDA"/s.source_file
   if not q.is_file() or sha(q)!=rs[s.workload_id]["source_sha256"]:raise RuntimeError(f"PolyBench source hash mismatch: {q}")
  else:
   for q in ("main.cu","jds_kernels.cu","gpu_info.cc","file.cc","convert_dataset.c","mmio.c"):req(a.spmv_wrapper/q,"SpMV wrapper source")
   for q in ("common/src/parboil_cuda.c","common/include/parboil.h"):req(a.parboil_src/q,"Parboil source")
   if sha(a.spmv_input_dir/"bcsstk18.mtx")!="abbe1909f57d6fc17fc800446bac326bd0c5343305cf193b3aa1bc8f40c82ec9" or sha(a.spmv_input_dir/"vector.bin")!="d155de2b9615cae3c2bb8b60a9e82a7d26be7e80de772a5f1c0cb830d2e49061":raise RuntimeError("canonical SpMV input hash mismatch")
 return out
def tracer(a,o,nvcc):
 d=o/"scratch-tracer";shutil.rmtree(d,ignore_errors=True);shutil.copytree(a.tracer_framework_src/"util/tracer_nvbit",d,ignore=shutil.ignore_patterns("nvbit_release","*.o","*.so","post-traces-processing"))
 with tarfile.open(a.nvbit_archive) as t:t.extractall(d/"nvbit_release")
 kids=list((d/"nvbit_release").iterdir())
 if not (d/"nvbit_release/core").exists() and len(kids)==1 and kids[0].is_dir():shutil.move(str(kids[0]),str(d/"tmp"));shutil.rmtree(d/"nvbit_release");shutil.move(str(d/"tmp"),str(d/"nvbit_release"))
 if not (d/"nvbit_release/core/libnvbit.a").exists():raise RuntimeError("NVBit archive lacks required core/libnvbit.a")
 env={**os.environ,"NVCC":str(nvcc),"PATH":str(nvcc.parent)+":"+os.environ["PATH"]}
 # The root Makefile also builds unrelated legacy demonstration tools. Build
 # only the trace tool and its postprocessor that this controller consumes.
 run(["make","-C","tracer_tool"],cwd=d,env=env)
 run(["make","-C","tracer_tool/traces-processing"],cwd=d,env=env)
 tool=d/"tracer_tool/tracer_tool.so";post=d/"tracer_tool/traces-processing/post-traces-processing"
 if not tool.exists() or not post.exists():raise RuntimeError("tracer build incomplete")
 return tool,post,{"tracer_source_tree_sha":tree(a.tracer_framework_src),"tracer_tool_sha":sha(tool),"nvbit_archive_sha":sha(a.nvbit_archive),"postprocess_sha":sha(post)}
def record(a,s,src,script,cmd,exe,inv,t,raw,grp,prov,device):
 q=(a.polybench_src/"CUDA"/s.source_file) if s.source_kind=="polybench" else a.spmv_wrapper/s.source_file
 if s.source_kind=="polybench":inp={"dimension_source_path":str(q.relative_to(a.polybench_src)),"dimension_source_sha256":sha(q),"dimensions":s.dimensions,"generator":"frozen CUDA source dimensions"};source=src["polybench"];deps={"polybench":source}
 else:
  inp={"matrix_sha256":sha(a.spmv_input_dir/"bcsstk18.mtx"),"vector_sha256":sha(a.spmv_input_dir/"vector.bin"),"reference_sha256":sha(a.spmv_reference)};source=src["spmv wrapper"]
  wf=("main.cu","jds_kernels.cu","gpu_info.cc","file.cc","convert_dataset.c","mmio.c");pf=("common/src/parboil_cuda.c","common/include/parboil.h")
  deps={"spmv_wrapper":{**source,"files":{x:sha(a.spmv_wrapper/x) for x in wf}},"parboil":{**src["parboil"],"files":{x:sha(a.parboil_src/x) for x in pf}}}
 rh=setsha(raw,t);gh=setsha(grp,t);bid=hashlib.sha256((s.workload_id+rh+gh+sha(t/"kernelslist.g")).encode()).hexdigest();d=t.parent
 return {"trace_bundle_id":bid,"workload":s.workload_id,"canonical_id":s.canonical_id,"source_kind":s.source_kind,"source_commit":s.source_commit,"source_tree_sha":source["tree"],"source_file":s.source_file,"source_file_sha":sha(q),"source_dependencies":deps,"input_identity_kind":s.input_kind,"input_hashes":inp,"build_script":s.build_script,"build_script_sha":sha(script),"build_command":cmd,"trace_capture_binary_sha":sha(exe),"checker_kind":s.checker_kind,"checker_reference_sha":inp.get("reference_sha256","N/A"),"gpu_uuid_model_cc":device,"tracer_source_tree_sha":prov["tracer_source_tree_sha"],"tracer_tool_sha":prov["tracer_tool_sha"],"nvbit_archive_sha":prov["nvbit_archive_sha"],"postprocess_sha":prov["postprocess_sha"],"trace_format":"NVBit-v1.8","kernel_invocation_count":len(inv),"kernel_invocation_manifest_sha":sha(d/"kernel_invocation_manifest.json"),"kernel_geometry_manifest_sha":sha(d/"kernel_geometry_manifest.json"),"kernelslist_sha":sha(t/"kernelslist"),"kernelslist_g_sha":sha(t/"kernelslist.g"),"raw_trace_count":len(raw),"grouped_trace_count":len(grp),"raw_trace_set_sha256":rh,"traceg_set_sha256":gh}
def sums(d):(d/"SHA256SUMS").write_text("".join(f"{sha(p)}  {p.relative_to(d)}\n" for p in sorted(x for x in d.rglob("*") if x.is_file() and x.name!="SHA256SUMS")))
def global_manifest(o):
 rs=[]
 for b in sorted((o/"bundles").glob("*")) if (o/"bundles").exists() else []:
  if not valid_bundle(b):raise RuntimeError(f"global result manifest refuses invalid bundle: {b}")
  if valid_archive(o,b.name):r=json.loads((b/"CAPTURE_RESULT.json").read_text());r["status"]="ARCHIVE_PASS";rs.append(r)
 (o/"CAPTURE_RESULT_MANIFEST.tsv").write_text("\t".join(FIELDS)+"\n"+"".join("\t".join(json.dumps(r.get(k,""),sort_keys=True) if isinstance(r.get(k),dict) else str(r.get(k,"")) for k in FIELDS)+"\n" for r in rs))
def main():
 p=argparse.ArgumentParser()
 for x in ("tracer-framework-src","nvbit-archive","out"):p.add_argument("--"+x,type=Path,required=True)
 for x in ("polybench-src","spmv-wrapper","parboil-src","spmv-input-dir","spmv-reference","transfer-destination"):p.add_argument("--"+x,type=Path)
 p.add_argument("--workloads",default=",".join(W));p.add_argument("--resume",action="store_true");p.add_argument("--pilot-only",action="store_true");a=p.parse_args();o=a.out.resolve();o.mkdir(parents=True,exist_ok=True);ss=specs(a);src=sources(a,ss)
 # Archive/copyback recovery is intentionally GPU-free and never re-captures.
 if a.resume and all((o/"bundles"/s.workload_id).exists() and valid_bundle(o/"bundles"/s.workload_id) for s in ss):
  for s in ss:
   w=s.workload_id;b=o/"bundles"/w;st(o,w,"CAPTURE_BUNDLE_PASS")
   if not valid_archive(o,w):st(o,w,"ARCHIVE_PENDING");archive(o,b);st(o,w,"ARCHIVE_PASS")
   if a.transfer_destination and not receipt(o,w).is_file():st(o,w,"TRANSFER_PENDING");transfer(o,w,a.transfer_destination/(w+".tar.zst"));st(o,w,"TRANSFER_PASS")
  global_manifest(o);return
 if any(s.workload_id!="bicg" for s in ss):gate(o)
 nvcc=Path(os.environ.get("NVCC","/usr/local/cuda-11.8/bin/nvcc"))
 if "release 11.8" not in run([str(nvcc),"--version"]).stdout:raise RuntimeError("CUDA 11.8 required")
 tool,post,prov=tracer(a,o,nvcc);(o/"environment.json").write_text(json.dumps(prov,sort_keys=True,indent=2)+"\n");probe=o/"tools/device_probe";probe.parent.mkdir(exist_ok=True);run([str(nvcc),"-arch=sm_70",str(ROOT/"util/dtc_l1/m5_trace_capture_device_probe.cu"),"-lcuda","-o",str(probe)]);dev=run([str(probe)]).stdout.splitlines()
 if len(dev)!=2 or "V100" not in dev[1]:raise RuntimeError("selected CUDA-visible logical device 0 is not V100")
 for s in ss:
  w=s.workload_id;b=o/"bundles"/w
  if b.exists() and valid_bundle(b):
   st(o,w,"CAPTURE_BUNDLE_PASS")
   if not valid_archive(o,w):st(o,w,"ARCHIVE_PENDING");archive(o,b);st(o,w,"ARCHIVE_PASS")
   if a.transfer_destination and not receipt(o,w).is_file():st(o,w,"TRANSFER_PENDING");transfer(o,w,a.transfer_destination/(w+".tar.zst"));st(o,w,"TRANSFER_PASS")
   continue
  if b.exists():raise RuntimeError(f"invalid immutable bundle exists: {b}")
  st(o,w,"CAPTURING");d=o/"attempts"/w/("attempt-"+str(int(time.time())));d.mkdir(parents=True)
  try:
   script=ROOT/s.build_script
   if s.source_kind=="spmv":run([str(script),str(a.spmv_wrapper),str(a.parboil_src),str(d/"build")]);exe=d/"build/spmv";cmd=[str(exe),"-i",str(a.spmv_input_dir/"bcsstk18.mtx")+","+str(a.spmv_input_dir/"vector.bin"),"-o","result.bin"]
   else:run([str(script),str(a.polybench_src),str(d/"build"),*s.build_arguments]);exe=d/"build"/s.binary_name;cmd=[str(exe)]
   env={**os.environ,"LD_PRELOAD":str(tool)};env.pop("DYNAMIC_KERNEL_RANGE",None)
   with (d/"application.stdout").open("w") as so,(d/"tracer.stderr").open("w") as se:run(cmd,cwd=d,env=env,stdout=so,stderr=se)
   if s.source_kind=="spmv":run([sys.executable,str(ROOT/"util/dtc_l1/verify_m5_parboil_spmv_output.py"),str(a.spmv_reference),str(d/"result.bin")],stdout=(d/"correctness.log").open("w"))
   else:run([sys.executable,str(ROOT/"util/dtc_l1/verify_m5_polybench_output.py"),s.checker_kind,str(d/"application.stdout")],stdout=(d/"correctness.log").open("w"))
   t=d/"traces";run([str(post),str(t/"kernelslist")],cwd=d,stdout=(d/"postprocess.stdout").open("w"));inv,geom,raw,grp=inventory(t);(d/"kernel_invocation_manifest.json").write_text(json.dumps(inv,sort_keys=True,indent=2)+"\n");(d/"kernel_geometry_manifest.json").write_text(json.dumps(geom,sort_keys=True,indent=2)+"\n")
   if any(x in (d/"tracer.stderr").read_text(errors="replace").lower() for x in ("cudaerror","nvbit fatal","tracer fatal","assertion")):raise RuntimeError("explicit tracer/CUDA error")
   r=record(a,s,src,script," ".join(cmd),exe,inv,t,raw,grp,prov,dev[1]);(d/"CAPTURE_RESULT.json").write_text(json.dumps(r,sort_keys=True,indent=2)+"\n");sums(d)
   if not valid_bundle(d):raise RuntimeError("internal bundle validation failed")
   st(o,w,"BUNDLE_READY_TEMP");b.parent.mkdir(exist_ok=True);os.replace(d,b);st(o,w,"CAPTURE_BUNDLE_PASS");st(o,w,"ARCHIVE_PENDING");archive(o,b);st(o,w,"ARCHIVE_PASS")
   if a.transfer_destination:st(o,w,"TRANSFER_PENDING");transfer(o,w,a.transfer_destination/(w+".tar.zst"));st(o,w,"TRANSFER_PASS")
  except Exception as e:st(o,w,"RETRY_READY");(o/"controller-errors.log").open("a").write(f"{w}: {e}\n");raise
 global_manifest(o)
if __name__=="__main__":main()
