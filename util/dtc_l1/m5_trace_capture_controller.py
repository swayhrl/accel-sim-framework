#!/usr/bin/env python3
"""M5.0BT resumable V100 capture controller; PASS bundles are immutable."""
import argparse,csv,hashlib,json,os,re,shutil,subprocess,sys,time
from pathlib import Path
WORK=["bicg","atax","gemv","mvt","syrk","gesu","syr2k","spmv","2mm","2dconv"]; CHECK={**{w:w for w in WORK if w not in {"2dconv","spmv"}},"2dconv":"conv2d"}; PIN="0db04452ec1c47630e4b08002067d82c6811e243"
HEAD="thesis_id\tcanonical_id\tsource_commit_path_sha\ttrace_capture_binary_sha\targuments\tinput_hashes\tchecker_reference_sha\tcapture_app_correctness\tgpu_uuid_model_cc\tdriver_cuda\ttracer_source_tree_tool_nvbit_postprocess\ttrace_format\tkernel_inventory_sha\tkernel_invocations\traw_trace_count\tgrouped_trace_count\tkernelslist_sha\tkernelslist_g_sha\traw_trace_set_sha256\ttraceg_set_sha256\ttrace_bundle_id\tstatus\n"
def run(x,**kw): return subprocess.run(x,check=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,**kw)
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1048576),b""): h.update(b)
 return h.hexdigest()
def state(o,w,s): (o/"state").mkdir(exist_ok=True);(o/"state"/(w+".state")).write_text(s+"\n")
def setsha(ps): return hashlib.sha256("".join(sha(p)+"  "+p.name+"\n" for p in sorted(ps)).encode()).hexdigest()
def main():
 p=argparse.ArgumentParser();
 for n in ("polybench-src","spmv-wrapper","parboil-src","spmv-input-dir","spmv-reference","tracer-framework-src","nvbit-archive","out"): p.add_argument("--"+n,type=Path,required=True)
 p.add_argument("--workloads",default=",".join(WORK));p.add_argument("--resume",action="store_true");p.add_argument("--pilot-only",action="store_true");p.add_argument("--admit-full-wave",action="store_true");p.add_argument("--dry-run",action="store_true");a=p.parse_args(); o=a.out.resolve();o.mkdir(parents=True,exist_ok=True); root=Path(__file__).resolve().parents[2]
 ws=[x for x in a.workloads.split(",") if x]; assert ws and all(x in WORK for x in ws)
 if a.pilot_only: ws=["bicg"]
 if ws != ["bicg"] and not a.admit_full_wave: raise SystemExit("FAIL --admit-full-wave requires completed BICG storage gate")
 if run(["git","-C",str(a.tracer_framework_src),"rev-parse","HEAD"]).stdout.strip()!=PIN or run(["git","-C",str(a.tracer_framework_src),"status","--porcelain"]).stdout: raise SystemExit("FAIL clean pinned tracer Framework source required")
 if run(["git","-C",str(a.polybench_src),"rev-parse","HEAD"]).stdout.strip()!="5584aaa7d0be810ff5eb0b61c49fb64ecc81ba4c": raise SystemExit("FAIL PolyBench source commit")
 if run(["git","-C",str(a.spmv_wrapper),"rev-parse","HEAD"]).stdout.strip()!="de9cf4293f418877aa9cdb6a2395338ca06674a6": raise SystemExit("FAIL SpMV wrapper source commit")
 if run(["git","-C",str(a.parboil_src),"rev-parse","HEAD"]).stdout.strip()!="4e0fc54866546efa44fe93af57c9cef62f6c8eb9": raise SystemExit("FAIL Parboil source commit")
 if sha(a.spmv_input_dir/"bcsstk18.mtx")!="abbe1909f57d6fc17fc800446bac326bd0c5343305cf193b3aa1bc8f40c82ec9" or sha(a.spmv_input_dir/"vector.bin")!="d155de2b9615cae3c2bb8b60a9e82a7d26be7e80de772a5f1c0cb830d2e49061": raise SystemExit("FAIL canonical SpMV input identity")
 nvcc=os.environ.get("NVCC","/usr/local/cuda-11.8/bin/nvcc"); assert "release 11.8" in run([nvcc,"--version"]).stdout and os.environ.get("CUDA_VISIBLE_DEVICES")
 probe=o/"tools/m5_device_probe";probe.parent.mkdir(exist_ok=True);run([nvcc,"-arch=sm_70",str(root/"util/dtc_l1/m5_trace_capture_device_probe.cu"),"-o",str(probe)]); dev=run([str(probe)]).stdout.splitlines(); assert len(dev)==2 and "V100" in dev[1],"FAIL selected logical CUDA 0 is not V100"
 (o/"environment.txt").write_text(run(["nvidia-smi"]).stdout+run([nvcc,"--version"]).stdout+f"TRACER_SOURCE_COMMIT={PIN}\nNVBIT_ARCHIVE_SHA={sha(a.nvbit_archive)}\nSELECTED_DEVICE={dev[1]}\n")
 (o/"identity.tsv").write_text("item\tidentity\n"+"\n".join([f"polybench_commit\t{run(['git','-C',str(a.polybench_src),'rev-parse','HEAD']).stdout.strip()}",f"spmv_wrapper_commit\t{run(['git','-C',str(a.spmv_wrapper),'rev-parse','HEAD']).stdout.strip()}",f"parboil_commit\t{run(['git','-C',str(a.parboil_src),'rev-parse','HEAD']).stdout.strip()}",f"spmv_matrix_sha256\t{sha(a.spmv_input_dir/'bcsstk18.mtx')}",f"spmv_vector_sha256\t{sha(a.spmv_input_dir/'vector.bin')}"])+"\n")
 if a.dry_run: print("PASS static/preflight contract; CUDA probe build required on V100");return
 tr=a.tracer_framework_src/"util/tracer_nvbit";run(["make"],cwd=tr);tool=tr/"tracer_tool/tracer_tool.so";post=tr/"tracer_tool/traces-processing/post-traces-processing";assert tool.exists() and post.exists()
 b=o/"build";run([str(root/"util/dtc_l1/build_m5_polybench_cuda_trace_sm70.sh"),str(a.polybench_src),str(b/"polybench")]);run([str(root/"util/dtc_l1/build_m5_parboil_spmv_trace_sm70.sh"),str(a.spmv_wrapper),str(a.parboil_src),str(b/"spmv")]); result=o/"CAPTURE_RESULT_MANIFEST.tsv";result.write_text(HEAD) if not result.exists() else None
 bins={"bicg":"bicg","atax":"atax","gemv":"gemver","mvt":"mvt","syrk":"syrk","gesu":"gesummv","syr2k":"syr2k","2mm":"twomm","2dconv":"twodconv","spmv":"spmv"}
 for w in ws:
  if a.resume and (o/"bundles"/w/"CAPTURE_RESULT.json").exists():state(o,w,"PASS");continue
  state(o,w,"CAPTURING"); d=o/"attempts"/w/("attempt-"+str(int(time.time())));d.mkdir(parents=True)
  try:
   exe=b/("spmv" if w=="spmv" else "polybench")/bins[w];cmd=[str(exe)] if w!="spmv" else [str(exe),"-i",str(a.spmv_input_dir/"bcsstk18.mtx")+","+str(a.spmv_input_dir/"vector.bin"),"-o","result.bin"]
   capture_env={**os.environ,"LD_PRELOAD":str(tool)};capture_env.pop("DYNAMIC_KERNEL_RANGE",None)
   with open(d/"application.stdout","w") as so,open(d/"tracer.stderr","w") as se: subprocess.run(cmd,cwd=d,env=capture_env,stdout=so,stderr=se,check=True)
   if w=="spmv":run([sys.executable,str(root/"util/dtc_l1/verify_m5_parboil_spmv_output.py"),str(a.spmv_reference),str(d/"result.bin")],stdout=open(d/"correctness.log","w"))
   else:run([sys.executable,str(root/"util/dtc_l1/verify_m5_polybench_output.py"),CHECK[w],str(d/"application.stdout")],stdout=open(d/"correctness.log","w"))
   t=d/"traces";run([str(post),str(t/"kernelslist")],cwd=d,stdout=open(d/"postprocess.stdout","w"));raw=sorted(t.glob("kernel-*.trace"));grp=sorted(t.glob("kernel-*.traceg"));assert raw and grp and (t/"kernelslist.g").stat().st_size
   assert not re.search(r"(NVBit.*(?:fatal|assert)|cudaError|tracer.*fatal)",(d/"tracer.stderr").read_text(errors="replace"),re.I)
   inv=list(csv.DictReader((t/"stats.csv").open()));assert inv;(d/"kernel_inventory.json").write_text(json.dumps(inv,sort_keys=True,indent=2)); bundle=o/"bundles"/w;bundle.parent.mkdir(exist_ok=True);shutil.move(str(d),str(bundle));rawh=setsha(list(bundle.glob("traces/kernel-*.trace")));gh=setsha(list(bundle.glob("traces/kernel-*.traceg")));bid=hashlib.sha256((w+rawh+gh+sha(bundle/"traces/kernelslist.g")).encode()).hexdigest();rec={"TRACE_BUNDLE_ID":bid,"TRACE_CAPTURE_BINARY_SHA":sha(exe),"TRACEG_SET_SHA256":gh,"RAW_TRACE_SET_SHA256":rawh,"status":"PASS"};(bundle/"CAPTURE_RESULT.json").write_text(json.dumps(rec,sort_keys=True,indent=2));state(o,w,"PASS")
   with result.open("a") as f:f.write("\t".join([w,w,"identity.tsv",sha(exe)," ".join(cmd[1:]),"identity.tsv",sha(a.spmv_reference) if w=="spmv" else "N/A","PASS",dev[1],"environment.txt",f"{PIN};{sha(tool)};{sha(a.nvbit_archive)};{sha(post)}","NVBit-v1.8",sha(bundle/"kernel_inventory.json"),str(len(inv)),str(len(raw)),str(len(grp)),sha(bundle/"traces/kernelslist"),sha(bundle/"traces/kernelslist.g"),rawh,gh,bid,"PASS"])+"\n")
  except Exception as e:state(o,w,"RETRY_READY");(d/"controller.stderr").write_text(str(e)+"\n")
 if (o/"bundles/bicg/CAPTURE_RESULT.json").exists():
  z=o/"bundles/bicg";raw=sum(x.stat().st_size for x in z.rglob("*.trace"));grp=sum(x.stat().st_size for x in z.rglob("*.traceg"));arc=shutil.make_archive(str(o/"bicg-pilot"),"gztar",z);(o/"STORAGE_BUDGET.tsv").write_text(f"pilot\traw_bytes\tgrouped_bytes\tarchive_bytes\tprojected_10_raw_bytes\tfree_bytes\nBICG\t{raw}\t{grp}\t{Path(arc).stat().st_size}\t{raw*10}\t{shutil.disk_usage(o).free}\n")
if __name__=="__main__":main()
