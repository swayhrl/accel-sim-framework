#!/usr/bin/env python3
"""Main-only finite V3 exact10 executor candidate. No activation on import/default.
Reuses frozen V2 claim/poll/closed-view/resource/native archive mechanics;
new scope/authorization/stage/routing/concurrency/publication are explicit below."""
import argparse,contextlib,csv,hashlib,importlib.util,json,os,pathlib,shutil,subprocess,sys,time,uuid
P=pathlib.Path;J=P("/root/data/ep_l2_full_workload_performance_20261027_v1")
V=J/"research/performance_first_v3_20261104_v1";ACT=V/"activation_20261104_v1";CONTROL=ACT/"control"
PREV=J/"research/performance_first_v2_20261103_v1/activation_20261104_v1/agent_d_execution/finite_main_authorized18.py"
PREV_SHA="414826aa29620a4daf2cc73a230786bee072d58ac8c2217d7e0f9c834e9d7f33"
if hashlib.sha256(PREV.read_bytes()).hexdigest()!=PREV_SHA:raise ValueError("frozen host mechanics predecessor drift")
sys.path.insert(0,str(PREV.parent))
import finite_main_authorized18 as E
need,read,put,ref,exact,sha,now,lock,authority,pid_identity,same_live=map(lambda n:getattr(E,n),["need","read","put","ref","exact","sha","now","lock","authority","pid_identity","same_live"])
REQUESTS={"midtag":"EP_L2_MID_TAG_850MHZ_V1_20261104","vector1700":"EP_L2_VECTOR1700_WV_DECOMPOSITION_V1_20261104"}
BUDGETS={"midtag":8,"vector1700":2}
ROOTS={"midtag":J/"execution_midtag_v3_20261104_v1/midtag","vector1700":J/"execution_vector1700_decomposition_v3_20261104_v1/vector1700"}
TERMINAL=E.TERMINAL;M=1<<20
ADMISSION=E.ADMISSION;RESTORE=E.RESTORE;GITLOCK=E.GITLOCK;OWNERSHIP=E.OWNERSHIP
# Only this in-memory imported helper namespace is rebound. The old module file is unchanged.
E.REQUESTS=REQUESTS;E.BUDGETS=BUDGETS;E.ROOTS=ROOTS
GUARD=P(__file__).with_name("native_route_guard_v3.py")
GUARD_SHA="9df2bab0058b571466998f71bfa487a929b6718a0d7e56d347746e98d6208ca9"
def route_guard():
 need(sha(GUARD)==GUARD_SHA,"V3 routeguard drift")
 s=importlib.util.spec_from_file_location("ep_v3_executor_route_guard",GUARD);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sealed_command(fd,argv):
 head=os.pread(fd,64,0);path="/proc/self/fd/"+str(fd)
 if head.startswith(b"#!/bin/sh\n"):return ["/bin/sh",path,*argv]
 if head.startswith(b"#!/usr/bin/env python3\n")or head.startswith(b"#!/usr/bin/python3\n"):return ["/usr/bin/python3","-B",path,*argv]
 raise RuntimeError("unqualified sealed scoped-entry interpreter")
def validate_manifest(m):
 need(m["schema"]=="EP_MAIN_PFV3_AUTHORIZED10_EXECUTION_MANIFEST_V1"and P(m["control_root"])==CONTROL,"V3 control/schema")
 need(m["new_model_start_ceiling"]==10 and m["authorized_max_concurrent_models"]==10 and m["automatic_retry"]is False and m["refund"]is False,"exact10 cap10 no retry/refund")
 auth=exact(m["user_authorization_ref"]);need(auth["explicit_user_approval"]is True and auth["total_new_start_budget"]==10 and auth["global_EP_model_cap"]==10 and auth["temporary_qualified_cap2_allowed"]is True and auth["old_budgets_reusable"]is False,"fresh exact authorization")
 a={z["name"]:z for z in auth["families"]};need(set(m["groups"])==set(REQUESTS),"two canonical groups")
 points=m["points"];need(len(points)==10 and len({p["cohort"]for p in points})==10,"unique exact10")
 for g,qid in REQUESTS.items():
  z=m["groups"][g];need(z["request_id"]==qid and z["budget"]==BUDGETS[g]and P(z["data_root"])==ROOTS[g],"scope/root/budget")
  expected=set(a[g]["allowed_cohorts"]);need({p["cohort"]for p in points if p["group"]==g}==expected,"exact family cohorts")
  need(sha(z["native_entry_ref"]["path"])==z["native_entry_ref"]["sha256"],"new scoped Native bytes")
  for p in points:
   if p["group"]!=g:continue
   s=exact(p["spec_ref"]);need(P(p["spec_ref"]["path"])==ROOTS[g]/"cases"/p["cohort"]/"control/FROZEN_SPEC.json","formal frozen spec path")
   need(s["cohort"]==p["cohort"]and s["source_identity"]==a[g]["Source5"]and s["science_request_id"]==qid,"exact Source5/scope")
   need(len(s["expected_effective_options"])==282,"effective282")
   need(s["mode"]in(["S","WV_ZERO_RO"]if g=="midtag"else["W_ONLY","WV_ZERO_RO"]),"qualified exact modes")
   need(s["expected_effective_options"]["-dram_latency"]=="100","no new latency")
   need(s["expected_effective_options"]["-gpgpu_clock_domains"]==("1132.0:1132.0:1132.0:850.0"if g=="midtag"else"1132.0:1132.0:1132.0:1700.0"),"exact clocks")
   need(s["geometry"]in[dict(line_bytes=128,sets=32,slices=64,ways=16),dict(line_bytes=128,sets=64,slices=64,ways=8)]if g=="midtag"else s["geometry"]==dict(line_bytes=128,sets=32,slices=64,ways=8),"exact Tag geometry")
 need(P(m["global_admission_lock"])==ADMISSION and P(m["runtime_global_restore_lock"])==RESTORE,"shared crossfamily lock")
 need(P(m["accept_serial_lock"])not in[ADMISSION,RESTORE],"outer accept lock must not self-deadlock child")
 pub=m["publication"];need(P(pub["repo"])==V/"review"and pub["branch"]=="hrl/ep-l2-performance-first-v3-20261104-v1","one Main branch")
 rel=P(pub["relative_directory"]);need(not rel.is_absolute()and".."not in rel.parts and str(rel).startswith("docs/ep_l2/operations/ep_performance_first_v3_20261104_v1/"),"own docs subtree")
 return True
def stage_decisions(points,rows,views,technical=()):
 """GEMM releases only after every FWT point is accepted, full archived and restored twice."""
 held=set(technical);fwt=[p["cohort"]for p in points if p["group"]=="midtag"and"_FWT_"in p["cohort"]]
 need(len(fwt)==4,"exact FWT stage4")
 good=all(rows.get(c,{}).get("state")=="CLOSED_ACCEPTED"and views.get(c,{}).get("accepted")and views.get(c,{}).get("archived")for c in fwt)
 bad=any(rows.get(c,{}).get("state")=="CLOSED_UNACCEPTED"or c in held for c in fwt)
 out={}
 for p in points:
  c=p["cohort"]
  if c in held:out[c]=dict(status="HOLD",reason="MAIN_EXACT_TECHNICAL_HOLD");continue
  if c in rows:out[c]=dict(status="CONSUMED",reason="NEVER_RETRY");continue
  if p["group"]=="midtag"and"_GEMM_"in c and not good:
   out[c]=dict(status="HOLD"if bad else"WAIT",reason="FWT_STAGE_FAILED_NO_GEMM_RELEASE"if bad else"WAIT_FWT4_CLOSED_ACCEPTED_ARCHIVE_TWO_RESTORES")
  else:out[c]=dict(status="RELEASE",reason="APPROVED_EXACT_INITIAL_OR_FWT_STAGE_COMPLETE")
 return out
def concurrency_capacity(active,local,cap):
 need(type(cap)is int and cap in[2,10],"only qualified temporary2 or approved10")
 need(type(active)is int and active>=0 and type(local)is int and local>=0,"actual counts")
 return active<cap and local<cap
class Executor(E.Executor):
 def __init__(self,manifest):
  self.manifest_path=P(manifest);self.m=read(manifest);validate_manifest(self.m)
  self.C=CONTROL;self.states={};self.running={};self.pending_accept=[];self.started=time.monotonic()
  self.lastpublish=0;self.lastresource={};self.fatal=[];self.session=str(uuid.uuid4());self.points=self.m["points"]
  self.bypoint={p["cohort"]:p for p in self.points};self.specs={p["cohort"]:exact(p["spec_ref"])for p in self.points};self.phase_cache={};self.failures={}
 def effective_cap(self):
  q=read(self.C/"MAIN_MODEL_CONCURRENCY_POLICY.json")
  need(q["approved_by"]=="EP-MAIN"and E.same_ref(q["manifest_ref"],ref(self.manifest_path)),"Main exact concurrency policy")
  cap=q["max_concurrent_models"];need(cap in[2,10],"no unqualified cap")
  qr=exact(q["resource_qualification_ref"]);need(qr["status"]=="PASS"and cap in qr["qualified_global_EP_caps"],"resource adapter cap qualification")
  return cap
 def native(self,op,c,**kwargs):
  need(c in self.bypoint and op in["prepare","inspect","run-native","accept"],"exact scoped native operation")
  g=self.bypoint[c]["group"];r=self.m["groups"][g]["native_entry_ref"]
  fd,proof=route_guard().sealed_entry(ROOTS[g]/"control/NATIVE_ENTRY_ROUTE_V3.json")
  try:
   need(E.same_ref(proof["entry_ref"],r)and c in proof["exact_cohorts"],"wrong Main-installed scoped route")
   put(self.C/"ROUTE_INVOCATIONS"/(c+"."+op+"."+str(uuid.uuid4())+".json"),dict(**proof,cohort=c,operation=op,scientific_consumption_here=False))
   return subprocess.Popen(sealed_command(fd,["experiment",op,c,"--project","EP_L2"]),pass_fds=(fd,),**kwargs)
  finally:os.close(fd)
 def priorities(self,p):
  return (10 if"_FWT_"in p["cohort"]else 15 if p["group"]=="vector1700"else 30,p["cohort"])
 def decisions(self,reg,rows):
  views={};errors={}
  for g in REQUESTS:
   try:
    for p in self.points:
     if p["group"]==g:views[p["cohort"]]=self.closed_view(p["cohort"],rows.get(p["cohort"],{}))
   except Exception as e:errors[g]=repr(e)
  local_held=set(self.technical_holds())|{c for c,x in self.states.items()if x.get("terminal_hold")}
  out=stage_decisions(self.points,rows,views,local_held)
  for p in self.points:
   if p["group"]in errors and p["cohort"]not in rows:out[p["cohort"]]=dict(status="HOLD",reason="LOCAL_FAMILY_EVIDENCE_HOLD",detail=errors[p["group"]])
  return out,views,{},errors
 def emit_stage_receipts(self,decisions,views,refs,rows,only_group=None):
  if only_group=="vector1700":return
  fwt=[p for p in self.points if p["group"]=="midtag"and"_FWT_"in p["cohort"]]
  if not all(views.get(p["cohort"],{}).get("accepted")and views[p["cohort"]]["archived"]for p in fwt):return
  self.immutable(ROOTS["midtag"]/"control/FWT4_ACCEPTED_STAGE_REVIEW.json",dict(
    schema="EP_MAIN_PFV3_MIDTAG_FWT4_ACCEPTED_STAGE_REVIEW_V1",status="MAIN_REVIEWED_FWT4_CLOSED_ACCEPTED_ARCHIVED_TWO_RESTORES",
    approved_by="EP-MAIN",request_id=REQUESTS["midtag"],accepted_point_refs={p["cohort"]:rows[p["cohort"]]["accepted_point_ref"]for p in fwt},
    archive_receipt_refs={p["cohort"]:rows[p["cohort"]]["archive_receipt_ref"]for p in fwt},controller_manifest_ref=ref(self.manifest_path)))
 def available_cpu(self):
  # C's fresh loader-aware snapshot includes pending peer CPU claims, not only live processes.
  g=next(iter(REQUESTS));p=next(p for p in self.points if p["group"]==g)
  src='from ep_perf_common_v2 import *;s=read(ROOT/"cases"/sys.argv[1]/"control/FROZEN_SPEC.json");r=module(s["resource_module_ref"],"ep_v3_controller_fresh_cpu_snapshot");print(json.dumps(r.snapshot()))'
  result=self.group_call(g,src,[p["cohort"]])
  need(result.returncode==0,"fresh CPU resource mapping HOLD "+result.stderr[-2000:])
  snap=json.loads(result.stdout);need("occupied_model_or_claim_cpus"in snap,"missing exact CPU claims/liveness population")
  occupied=set(snap["occupied_model_or_claim_cpus"])|{r["cpu"]for r in self.running.values()}
  allowed=set(os.sched_getaffinity(0))
  return next((c for c in self.m.get("host_cpu_candidates",sorted(allowed))if c in allowed and c not in occupied),None)
 def start(self,p):
  c=p["cohort"];g=p["group"]
  if time.monotonic()<self.lastresource.get(c,0)+30:return False
  self.lastresource[c]=time.monotonic();cpu=self.available_cpu()
  if cpu is None:return False
  with lock(ADMISSION):
   reg,rows=self.rows();need(c not in rows,"consumed never refork")
   need(c not in self.technical_holds(),"exact Main technical hold")
   decisions,views,refs,errors=self.decisions(reg,rows)
   if decisions[c]["status"]!="RELEASE":return False
   active=sum(v.get("state")in["CONSUMED_BEFORE_FORK","RUNNING"]for qid,q in reg["registered_future_requests"].items()if qid.startswith("EP_")and isinstance(q.get("consumed"),dict)for v in q["consumed"].values())
   if not concurrency_capacity(active,len(self.running),self.effective_cap()):return False
   nas=E.nas_capacity_gate(self.specs[c]);put(self.C/"NAS_ADMISSION"/(c+"."+str(uuid.uuid4())+".json"),dict(**nas,cohort=c,spec_ref=p["spec_ref"]))
   self.claim(p,cpu)
   check=self.group_call(g,'from ep_perf_native_wv_modes_draft import *;s=spec_for(sys.argv[1]);resource_gate(s,dispatch_binding(sys.argv[1]))',[c])
   if check.returncode:
    self.release_unconsumed_claim(p);message=(check.stdout+check.stderr)[-6000:]
    resource="RESOURCE_ADMISSION_HOLD:"in message
    self.states[c]=dict(status="RESOURCE_ADMISSION_HOLD"if resource else"PRECONSUME_LOCAL_QUALIFICATION_HOLD",terminal_hold=not resource,reason=message,utc=now())
    return False
   path=self.C/"native_logs"/(c+"."+str(uuid.uuid4())+".run.log");path.parent.mkdir(exist_ok=True)
   f=path.open("xb")
   try:proc=self.native("run-native",c,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
   except BaseException:f.close();self.release_unconsumed_claim(p);raise
   self.running[c]=dict(process=proc,log=f,cpu=cpu,launcher=pid_identity(proc.pid),log_path=str(path),started_monotonic=time.monotonic())
   self.states[c]=dict(status="NATIVE_IN_PROGRESS",cpu=cpu,native_frontend_pid=proc.pid,utc=now())
   self.event("SINGLE_MAIN_NATIVE_STARTED",cohort=c,pid=proc.pid);return True
 def accept_one(self):
  if not self.pending_accept:return
  c=self.pending_accept.pop(0)
  with lock(self.m["accept_serial_lock"]):
   path=self.C/"native_logs"/(c+".accept.log")
   try:
    with path.open("xb")as f:
     p=self.native("accept",c,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL);rc=p.wait()
   except Exception as e:
    self.states[c]=dict(status="LOCAL_ACCEPTANCE_REVIEW_HOLD",terminal_hold=True,reason=repr(e),utc=now())
    raise
   _,rows=self.rows();row=rows[c];self.states[c]=dict(status=row["state"],accept_returncode=rc,utc=now())
   if row["state"]not in TERMINAL:self.states[c].update(terminal_hold=True,reason="bounded acceptance reviewHOLD; no model retry")
   self.event("ACCEPT_ARCHIVE_TWO_RESTORES_FINISHED",cohort=c,state=row["state"],returncode=rc)
 def check_activation(self):
  a=read(self.C/"MAIN_EXECUTOR_ACTIVATION.json")
  need(a["status"]=="MAIN_REVIEWED_V3_EXACT10_ACTIVATION"and a["approved_by"]=="EP-MAIN","Main explicit activation")
  need(E.same_ref(a["manifest_ref"],ref(self.manifest_path))and E.same_ref(a["executor_ref"],ref(__file__)),"exact Main manifest/executor")
  need(a["no_retry"]is True and a["no_refund"]is True,"no retry/refund")
  for old in a.get("prior_executor_started_refs",[]):
   prev=exact(old);need(not same_live(prev["process"]),"previous EP Main executor still live")
  reg,rows=self.rows();need(not rows,"fresh V3 activation cannot retry consumed points")
  for g,qid in REQUESTS.items():
   q=reg["registered_future_requests"][qid]
   need(q["budget"]==q["remaining"]==BUDGETS[g]and not q["consumed"],"fresh exact8/2 budget")
   need(q["admitted_specs"]=={p["cohort"]:p["spec_ref"]["sha256"]for p in self.points if p["group"]==g},"registered exact frozen specs")
   need(E.same_ref(q["native_entry_ref"],self.m["groups"][g]["native_entry_ref"]),"registered Native entry")
   need(not read(ROOTS[g]/"control/DISPATCH_CLAIMS.json")["claims"],"fresh scope claims not empty")
   route_guard().validate_current(ROOTS[g]/"control/NATIVE_ENTRY_ROUTE_V3.json")
  self.effective_cap()
 def summary(self,decisions=None):
  reg,rows=self.rows();out=[]
  for p in self.points:
   c=p["cohort"];s=self.specs[c];r=rows.get(c,{})
   v=dict(cohort=c,group=p["group"],mode=s["mode"],profile=s["profile"],source_identity=s["source_identity"],input_identity_sha256=s["input_identity_sha256"],spec_ref=p["spec_ref"],
    state=r.get("state",self.states.get(c,{}).get("status","NOT_STARTED")),consumed=c in rows,controller_state=self.states.get(c),family_decision=(decisions or{}).get(c))
   for k in["done_ref","accepted_point_ref","archive_receipt_ref","validation_ref"]:v[k]=r.get(k)
   if r.get("state")=="CLOSED_ACCEPTED":
    pt=exact(r["accepted_point_ref"]);v.update({k:pt[k]for k in["cycles","instructions","CTA","kernel_count","hardware_drained"]})
    try:v["mechanism_metrics_ref"]=self.metrics(p,pt,r)
    except Exception as e:v["small_metrics_status"]=dict(status="UNKNOWN",reason=repr(e))
   if r.get("done_ref"):
    done=exact(r["done_ref"]);v.update({k:done.get(k)for k in["elapsed_seconds","peak_process_tree_RSS_bytes","peak_hot_bytes","stop_reason"]})
   out.append(v)
  result=dict(schema="EP_MAIN_PFV3_FINITE_EXACT10_RESULTS_V1",utc=now(),session=self.session,points=out,
   budgets={g:{k:reg["registered_future_requests"][q].get(k)for k in["budget","remaining","state"]}for g,q in REQUESTS.items()},
   active_native_frontends=len(self.running),max_global_EP_models=self.effective_cap(),authorized_global_EP_models=10,
   new_model_start_ceiling=10,no_consumed_retry=True,no_refund=True,Source_keep=True,raw_polling=False,combined_GM=False,family_failures=self.failures)
  put(self.C/"RESULTS_CURRENT.json",result)
  with(self.C/"RESULTS_CURRENT.csv").open("w",newline="")as f:
   cols=["cohort","group","mode","profile","state","consumed","cycles","instructions","CTA","kernel_count","hardware_drained","elapsed_seconds","peak_process_tree_RSS_bytes","peak_hot_bytes","stop_reason"]
   w=csv.DictWriter(f,cols,extrasaction="ignore");w.writeheader();w.writerows(out)
  return result
 def publish(self,final=False):
  p=self.m["publication"];repo=P(p["repo"]);rel=p["relative_directory"];dst=repo/rel
  with lock(GITLOCK):
   need(subprocess.check_output(["git","-C",str(repo),"branch","--show-current"],text=True).strip()==p["branch"],"Main publication branch")
   need(not subprocess.check_output(["git","-C",str(repo),"diff","--cached","--name-only"],text=True).strip(),"foreign staged work")
   dst.mkdir(parents=True,exist_ok=True)
   for name in["RESULTS_CURRENT.json","RESULTS_CURRENT.csv","EXECUTOR_STARTED.json","EXECUTOR_FINISHED.json","SUMMARY_ARCHIVE_RECEIPT.json"]:
    if(self.C/name).exists():shutil.copy2(self.C/name,dst/name)
   for sub in["MECHANISM_METRICS"]:
    (dst/sub).mkdir(exist_ok=True)
    for src in(self.C/sub).glob("*.json"):need(src.stat().st_size<=16*M,"small summary bound");shutil.copy2(src,dst/sub/src.name)
   put(dst/"EXECUTION_SCOPE.json",dict(manifest_ref=ref(self.manifest_path),executor_ref=ref(__file__),approved10=10,budgets=BUDGETS,final=final,utc=now(),single_Main_writer=True))
   subprocess.run(["git","-C",str(repo),"add","--sparse","--",rel],check=True)
   subprocess.run(["git","-C",str(repo),"add","--sparse","-f","--",str(P(rel)/"RESULTS_CURRENT.csv")],check=True)
   changed=subprocess.check_output(["git","-C",str(repo),"diff","--cached","--name-only"],text=True).splitlines()
   need(all(x.startswith(rel+"/")for x in changed),"publication escape")
   if changed:subprocess.run(["git","-C",str(repo),"commit","-m","EP V3 exact10 "+("finite closeout"if final else"accepted progress")],check=True)
   subprocess.run(["git","-C",str(repo),"push","origin",p["branch"]],check=True)
   head=subprocess.check_output(["git","-C",str(repo),"rev-parse","HEAD"],text=True).strip()
   remote=subprocess.check_output(["git","-C",str(repo),"ls-remote","origin","refs/heads/"+p["branch"]],text=True).split()[0]
   need(head==remote,"remote readback");put(self.C/"REMOTE_PUBLICATION_RECEIPT.json",dict(utc=now(),HEAD=head,remote_HEAD=remote,final=final));self.lastpublish=time.monotonic()
 def run(self):
  self.check_activation()
  with lock(self.C/"SINGLE_MAIN_V3_EXECUTOR.lock",True),lock(OWNERSHIP,True):
   need(not(self.C/"EXECUTOR_STARTED.json").exists(),"no automatic controller resume/re-fork")
   put(self.C/"EXECUTOR_STARTED.json",dict(schema="EP_MAIN_PFV3_EXACT10_EXECUTOR_START_V1",utc=now(),session=self.session,process=pid_identity(os.getpid()),code_ref=ref(__file__),manifest_ref=ref(self.manifest_path),no_consumed_retry=True))
   self.event("SINGLE_MAIN_V3_EXECUTOR_STARTED");self.summary()
   try:self.publish()
   except Exception as e:self.event("PUBLICATION_LOCAL_HOLD",reason=repr(e))
   while True:
    try:self.poll()
    except Exception as e:self.event("LOCAL_POLL_HOLD_NO_KILL",reason=repr(e))
    try:self.accept_one()
    except Exception as e:self.event("LOCAL_ACCEPT_HOLD_NO_MODEL_RETRY",reason=repr(e))
    reg,rows=self.rows();decisions,views,refs,errors=self.decisions(reg,rows);self.failures=errors
    try:self.emit_stage_receipts(decisions,views,refs,rows)
    except Exception as e:
     self.failures["midtag_stage"]=repr(e)
     for p in self.points:
      if p["group"]=="midtag"and"_GEMM_"in p["cohort"]and p["cohort"]not in rows:decisions[p["cohort"]]=dict(status="HOLD",reason="LOCAL_STAGE_RECEIPT_HOLD",detail=repr(e))
    for p in sorted(self.points,key=self.priorities):
     c=p["cohort"]
     if c in rows or c in self.running:continue
     dec=decisions[c]
     if dec["status"]=="HOLD":
      self.states[c]=dict(status="LOCAL_FAMILY_HOLD_NOT_CONSUMED",terminal_hold=True,reason=dec["reason"],utc=now());continue
     if dec["status"]!="RELEASE"or self.states.get(c,{}).get("terminal_hold"):continue
     if len(self.running)>=self.effective_cap():break
     try:self.start(p)
     except Exception as e:self.states[c]=dict(status="LOCAL_PRELAUNCH_QUALIFICATION_HOLD",terminal_hold=True,reason=repr(e),utc=now());self.event("LOCAL_PRELAUNCH_HOLD",cohort=c,reason=repr(e))
    self.summary(decisions)
    if time.monotonic()-self.lastpublish>=1800:
     try:self.publish()
     except Exception as e:self.event("PERIODIC_PUBLICATION_LOCAL_HOLD",reason=repr(e))
    _,rows=self.rows();settled=all(rows.get(p["cohort"],{}).get("state")in TERMINAL or self.states.get(p["cohort"],{}).get("terminal_hold")for p in self.points)
    if settled and not self.running and not self.pending_accept:break
    if time.monotonic()-self.started>self.m.get("admission_wait_and_execution_wall_seconds",7*86400)and not self.running:break
    time.sleep(10)
   self.summary(decisions)
   try:self.archive_summary()
   except Exception as e:self.event("SUMMARY_ARCHIVE_LOCAL_HOLD",reason=repr(e))
   _,rows=self.rows()
   put(self.C/"EXECUTOR_FINISHED.json",dict(utc=now(),session=self.session,status="V3_EXACT10_TERMINAL_OR_LOCAL_REVIEW_HOLD",consumed=len(rows),
    accepted=sum(r["state"]=="CLOSED_ACCEPTED"for r in rows.values()),unaccepted=sum(r["state"]=="CLOSED_UNACCEPTED"for r in rows.values()),
    unconsumed_cohorts=[p["cohort"]for p in self.points if p["cohort"]not in rows],all_consumed_terminal=all(r["state"]in TERMINAL for r in rows.values()),
    no_retry=True,no_refund=True))
   try:self.publish(final=True)
   except Exception as e:self.event("FINAL_PUBLICATION_LOCAL_HOLD",reason=repr(e))
def main(argv=None):
 ap=argparse.ArgumentParser();ap.add_argument("--manifest",required=True);g=ap.add_mutually_exclusive_group();g.add_argument("--prepare",action="store_true");g.add_argument("--run",action="store_true");a=ap.parse_args(argv)
 if a.run:Executor(a.manifest).run()
 else:validate_manifest(read(a.manifest));print("PASS_PASSIVE_V3_EXACT10_NO_START")
if __name__=="__main__":main()
