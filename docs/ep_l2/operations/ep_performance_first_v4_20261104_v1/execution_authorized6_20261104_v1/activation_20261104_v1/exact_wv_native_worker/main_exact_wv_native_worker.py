"""One exact Main-delegated Native point worker. No general model queue or Git publisher."""
from pathlib import Path
import json,hashlib,importlib.util,subprocess,sys,os,time,datetime
D=Path(__file__).resolve().parent;C=D.parent/"control";V=C.parent.parent
CASE="EP_PERF_PFV4_VECTOR4M_WV_ZERO_RO_1700_V1";REQUEST="EP_L2_VECTOR1700_WV_DECOMPOSITION_FRESH_V4_20261104"
CONTROLLER=V/"activation_20261104_v1/engineering_dispatcher_candidate_v1/finite_main_exact6_candidate.py"
CONTROLLER_SHA="c8b62fd7a0d0c83e9af186cdfcf2a694cd02f87c78eeb49361d78df088e17f2a"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def ref(p):return dict(path=str(p),sha256=sha(p))
def put(p,x):
 b=(json.dumps(x,sort_keys=True,indent=2)+"\n").encode();temp=p.with_name("."+p.name+"."+str(os.getpid()))
 with temp.open("wb")as f:f.write(b);f.flush();os.fsync(f.fileno())
 os.replace(temp,p)
def check(grant):
 assert grant["approved_by"]=="EP-MAIN"and grant["status"]=="MAIN_DELEGATES_EXACT_UNCONSUMED_WV_NATIVE_POINT"
 assert grant["cohort"]==CASE and grant["request"]==REQUEST and grant["max_new_starts"]==1
 assert grant["manifest_ref"]==ref(C/"EXACT_EXECUTION_MANIFEST.json")and grant["executor_ref"]==ref(CONTROLLER)
 assert sha(CONTROLLER)==CONTROLLER_SHA
 assert grant["parent_authorization_ref"]==ref(C/"USER_AUTHORIZATION.json")
 for r in [grant["consumer_adapter_ref"],grant["consumer_amendment_ref"]]:assert sha(r["path"])==r["sha256"]
 # Main's original dispatcher has relinquished this unconsumed exact point locally.
 # Its immutable loop skips terminal_hold points even after the W prerequisite closes.
 current=read(C/"RESULTS_CURRENT.json");row=next(x for x in current["points"]if x["cohort"]==CASE)
 assert row["consumed"]is False and row["controller_state"]["terminal_hold"]is True
 assert row["controller_state"]["reason"]in["B_W_FAILED_NO_WV_RELEASE","EXACT_MAIN_TECHNICAL_HOLD"]
 started=read(C/"EXECUTOR_STARTED.json");assert started["process"]==grant["original_dispatcher_process"]
 return True
def main():
 grant=read(D/"MAIN_EXACT_WV_WORKER_GRANT.json");check(grant)
 sp=importlib.util.spec_from_file_location("same_Main_pinned_finite_mechanics_for_one_point",CONTROLLER);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 ctx=m.Executor(C/"EXACT_EXECUTION_MANIFEST.json");p=next(p for p in ctx.points if p["cohort"]==CASE)
 reg,rows=ctx.rows();q=reg["registered_future_requests"][REQUEST];assert CASE not in rows and q["remaining"]==1 and len(q["consumed"])==1
 wcase="EP_PERF_PFV4_VECTOR4M_W_ONLY_1700_V1";assert rows[wcase]["state"]=="CLOSED_ACCEPTED"
 assert ctx.closed_view(wcase,rows[wcase])["two_restores_complete"]is True
 decision=ctx.decisions(reg,rows)[0][CASE];assert decision["status"]=="RELEASE"
 if "--run"not in sys.argv:print(json.dumps(dict(status="EXACT_WV_DELEGATION_AND_W_CLOSED_RELEASE_PASS_NO_START",grant_ref=ref(D/"MAIN_EXACT_WV_WORKER_GRANT.json"))));return
 with m.lock(D/"SINGLE_EXACT_WV_WORKER.lock",True):
  assert not(D/"WORKER_STARTED.json").exists(),"never restart this finite Native worker"
  put(D/"WORKER_STARTED.json",dict(process=m.pid_identity(os.getpid()),grant_ref=ref(D/"MAIN_EXACT_WV_WORKER_GRANT.json"),code_ref=ref(__file__),no_model_retry=True))
  began=time.monotonic()
  while True:
   reg,rows=ctx.rows();assert CASE not in rows,"no consume/refork retry"
   if ctx.start(p):break
   if ctx.states.get(CASE,{}).get("terminal_hold"):raise ValueError("preconsume Main review HOLD "+repr(ctx.states[CASE]))
   if time.monotonic()-began>3600:raise ValueError("bounded preconsume resource wait expired; no model started")
   put(D/"STATE.json",dict(status="WAIT_UNCONSUMED_RESOURCE_ADMISSION",cohort=CASE,states=ctx.states.get(CASE),utc=m.now()))
   time.sleep(10)
  put(D/"STATE.json",dict(status="SINGLE_APPROVED_NATIVE_WV_IN_PROGRESS",cohort=CASE,utc=m.now()))
  while ctx.running:
   ctx.poll();time.sleep(2)
  reg,rows=ctx.rows();row=rows.get(CASE);assert row and row.get("done_ref"),"consume/closure HOLD; no retry"
  assert row["state"]=="NATURAL_COMPLETE_PENDING_VALIDATION","Native terminal failure retained; no retry"
  adapter=grant["consumer_adapter_ref"]["path"];amend=grant["consumer_amendment_ref"]["path"]
  review=subprocess.run(["/usr/bin/python3","-B",adapter,"--cohort",CASE,"--amendment",amend],capture_output=True,text=True,timeout=300)
  (D/"CONSUMER_REVIEW_STDOUT.json").write_text(review.stdout);(D/"CONSUMER_REVIEW_STDERR.txt").write_text(review.stderr);assert review.returncode==0,review.stderr[-3000:]
  apply=subprocess.run(["/usr/bin/python3","-B",adapter,"--cohort",CASE,"--amendment",amend,"--apply"],capture_output=True,text=True,timeout=300)
  (D/"CONSUMER_APPLY_STDOUT.json").write_text(apply.stdout);(D/"CONSUMER_APPLY_STDERR.txt").write_text(apply.stderr);assert apply.returncode==0,apply.stderr[-3000:]
  with ctx.native("accept",CASE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)as proc:
   output,_=proc.communicate(timeout=600);(D/"NATIVE_ARCHIVE_AND_TWO_RESTORES.json").write_bytes(output);assert proc.returncode==0,output[-3000:]
  reg,rows=ctx.rows();assert rows[CASE]["state"]=="CLOSED_ACCEPTED";assert ctx.closed_view(CASE,rows[CASE])["two_restores_complete"]is True
  put(D/"WORKER_FINISHED.json",dict(status="EXACT_WV_CLOSED_ACCEPTED_ARCHIVED_TWO_RESTORES",cohort=CASE,accepted_point_ref=rows[CASE]["accepted_point_ref"],archive_receipt_ref=rows[CASE]["archive_receipt_ref"],no_extra_budget=True,no_retry=True,utc=m.now()))
if __name__=="__main__":
 try:main()
 except BaseException as e:
  if "--run"in sys.argv:put(D/"WORKER_HOLD.json",dict(status="MAIN_EXACT_WV_WORKER_REVIEW_HOLD",reason=repr(e),no_model_retry=True))
  raise
