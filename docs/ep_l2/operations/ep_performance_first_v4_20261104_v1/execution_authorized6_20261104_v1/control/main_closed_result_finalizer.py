"""Main metadata finalizer for exact authorized6. No model/Native/claim/GPU/Trace operations."""
from pathlib import Path
import json,hashlib,subprocess,os,time,datetime,fcntl,copy
C=Path(__file__).resolve().parent;V=C.parent.parent;N=Path("/root/data/ep_l2_dtc_l1_native_v2")
REG=N/"control/science_authority/NATIVE_SCIENCE_REGISTRY.json";EPOCH=N/"control/CURRENT_SCIENCE_EPOCH.json"
REPORTER=V/"activation_20261104_v1/closed_result_report_candidate_v2/closed_result_report.py";REPORTER_SHA="07670e2d84fe9579f139adcde92aab2af6edcf231479b6daf7fb899b0466ff13"
NAS=Path("/root/share/mnt164/huangrulin/host174_storage_recovery/ep_l2_performance_first_v4_20261104_v1/execution_authorized6_20261104_v1/closed_summaries")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_bytes())
def put(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(x,sort_keys=True,indent=2)+"\n").encode();t=p.with_name("."+p.name+"."+str(os.getpid()))
 with t.open("wb")as f:f.write(b);f.flush();os.fsync(f.fileno())
 os.replace(t,p)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 assert sha(REPORTER)==REPORTER_SHA
 assert sha(C/"main_publish_execution_metadata.py")=='f56f1c126de70cb97497399495bb8b82ce9bb7c6cbf6036b31667e8c4ae934f3'
 manifest=read(C/"EXACT_EXECUTION_MANIFEST.json");requests=[x["request_id"]for x in manifest["groups"].values()]
 assert len(requests)==3 and manifest["new_model_start_ceiling"]==6
 lock=(C/"SINGLE_MAIN_METADATA_FINALIZER.lock").open("a+b");fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert not(C/"METADATA_FINALIZER_STARTED.json").exists()
 stat=Path("/proc/self/stat").read_text().rsplit(")",1)[1].split()
 put(C/"METADATA_FINALIZER_STARTED.json",dict(pid=os.getpid(),start_ticks=int(stat[19]),code_ref=ref(__file__),reporter_ref=ref(REPORTER),manifest_ref=ref(C/"EXACT_EXECUTION_MANIFEST.json"),models_started=0))
 NAS.mkdir(parents=True,exist_ok=True);last=None;began=time.monotonic()
 while time.monotonic()-began<12*3600:
  z=subprocess.run(["/usr/bin/python3","-B",str(REPORTER),"--once"],capture_output=True,text=True,timeout=120)
  if z.returncode:
   put(C/"METADATA_FINALIZER_ATTENTION.json",dict(status="READONLY_REPORTER_HOLD",stderr=z.stderr[-2000:],no_models_or_budget_change=True,utc=now()));time.sleep(30);continue
  report=json.loads(z.stdout);finger=hashlib.sha256(json.dumps(dict(points=report["points"],comparisons=report["comparisons"]),sort_keys=True).encode()).hexdigest()
  if finger!=last:
   put(C/"PERFORMANCE_CURRENT.json",report);(C/"PERFORMANCE_CURRENT.md").write_text(report["markdown_candidate"])
   history=C/"CLOSED_SUMMARY_HISTORY"/(str(time.time_ns())+".json");put(history,report)
   put(NAS/history.name,report);put(NAS/"PERFORMANCE_CURRENT.json",report);(NAS/"PERFORMANCE_CURRENT.md").write_text(report["markdown_candidate"]);last=finger
  with (N/"control/science_authority/REGISTRY_UPDATE.lock").open("rb")as f:
   fcntl.flock(f,fcntl.LOCK_SH);r=read(REG);ep=read(EPOCH);assert sha(REG)==ep["native_registry_sha256"]
  scopes={qid:r["registered_future_requests"][qid]for qid in requests}
  terminal=all(q["budget"]==2 and q["remaining"]==0 and len(q["consumed"])==2 and all(row["state"]in["CLOSED_ACCEPTED","CLOSED_UNACCEPTED"]for row in q["consumed"].values())for q in scopes.values())
  accepted={c for q in scopes.values()for c,row in q["consumed"].items()if row["state"]=="CLOSED_ACCEPTED"}
  qualified={p["cohort"]for p in report["points"]if p["status"]=="QUALIFIED_CLOSED_METADATA"}
  if terminal and accepted<=qualified and(C/"EXECUTOR_FINISHED.json").exists():
   closure=dict(schema="EP_MAIN_PFV4_EXACT6_SCOPE_CLOSURE_V1",utc=now(),manifest_ref=ref(C/"EXACT_EXECUTION_MANIFEST.json"),results_ref=ref(C/"PERFORMANCE_CURRENT.json"),approved=6,consumed=6,remaining=0,accepted=len(accepted),unaccepted=6-len(accepted),all_accepted_full_SHA_two_restores=True,old_scope_and_foreign_rows_unchanged=True,no_retry_or_refund=True,Source_KEEP=True)
   put(C/"FINAL_SCOPE_CLOSURE.json",closure)
   with (N/"control/science_authority/REGISTRY_UPDATE.lock").open("a+b")as f:
    fcntl.flock(f,fcntl.LOCK_EX);r=read(REG);ep=read(EPOCH);assert sha(REG)==ep["native_registry_sha256"];before=copy.deepcopy(r)
    for qid in requests:
     q=r["registered_future_requests"][qid];assert q["remaining"]==0 and len(q["consumed"])==2 and all(x["state"]in["CLOSED_ACCEPTED","CLOSED_UNACCEPTED"]for x in q["consumed"].values())
     q["state"]="CLOSED_COMPLETED"if all(x["state"]=="CLOSED_ACCEPTED"for x in q["consumed"].values())else"CLOSED_WITH_TECHNICAL_FAILURES"
     q["Main_scope_closure_ref"]=ref(C/"FINAL_SCOPE_CLOSURE.json")
    assert all(r["registered_future_requests"][k]==v for k,v in before["registered_future_requests"].items()if k not in requests)
    for p in [REG,EPOCH]:
     h=N/"control/science_authority/request_history"/(p.stem+"."+sha(p)+".json")
     if not h.exists():h.write_bytes(p.read_bytes())
    put(REG,r);ep["native_registry_sha256"]=sha(REG);ep["request_revision"]=dict(request_id=requests,operation="MAIN_CLOSE_EXACT6_COMPLETED_SCOPES_NO_REFUND",utc=now());put(EPOCH,ep)
   put(NAS/"FINAL_SCOPE_CLOSURE.json",closure);put(C/"METADATA_FINALIZER_FINISHED.json",dict(status="EXACT6_TERMINAL_REPORT_AND_SCOPE_CLOSURE_SAVED_TRUE164",utc=now(),closure_ref=ref(C/"FINAL_SCOPE_CLOSURE.json"),NAS=str(NAS)))
   z=subprocess.run(["/usr/bin/python3","-B",str(C/"main_publish_execution_metadata.py"),"--final"],capture_output=True,text=True,timeout=900)
   (C/"FINAL_GIT_PUBLICATION_STDOUT.json").write_text(z.stdout);(C/"FINAL_GIT_PUBLICATION_STDERR.txt").write_text(z.stderr)
   if z.returncode:put(C/"METADATA_FINALIZER_ATTENTION.json",dict(status="FINAL_REMOTE_PUBLICATION_HOLD_TRUE164_RESULTS_RETAINED",stderr=z.stderr[-2000:],utc=now()))
   else:put(NAS/"REMOTE_FINAL_PUBLICATION_RECEIPT.json",read(C/"REMOTE_FINAL_PUBLICATION_RECEIPT.json"))
   return
  worker=V/"activation_20261104_v1/exact_wv_native_worker/WORKER_HOLD.json"
  if worker.exists():put(C/"METADATA_FINALIZER_ATTENTION.json",dict(status="EXACT_WV_WORKER_REQUIRES_MAIN_REVIEW_NO_RETRY",worker_hold_ref=ref(worker),utc=now()))
  time.sleep(30)
 put(C/"METADATA_FINALIZER_ATTENTION.json",dict(status="BOUNDED_METADATA_SUPERVISION_EXPIRED_NO_TASKS_KILLED",utc=now()))
if __name__=="__main__":
 try:main()
 except BaseException as e:put(C/"METADATA_FINALIZER_EXCEPTION.json",dict(reason=repr(e),no_model_restart=True,utc=now()));raise
