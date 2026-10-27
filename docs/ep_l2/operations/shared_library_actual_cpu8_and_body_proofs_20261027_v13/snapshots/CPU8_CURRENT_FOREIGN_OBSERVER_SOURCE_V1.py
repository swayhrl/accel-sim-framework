"""Read-only current registered active RAM planning observer. No Root grant, leases, body, GPU or registry writes."""
import pathlib,json,hashlib,time,os,importlib.util
V=pathlib.Path("/root/share/mnt164/huangrulin/traces/receipts/rtx4080_specialist_adaptation_20261026_v1/sm70_r8_owned_descendant_closure_prepare_20261027_v1/production_keeper_v5/tools/versions/100bbf41b45927ec490c63c4e01ffaf64f522321b202e129303bab8cfac6a228")
def ref(p):
 b=p.read_bytes()
 if len(b)>8*1024**2:raise RuntimeError("Metadata cap8MiB")
 return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def one():
 q=json.loads((V/"PROFILE.json").read_bytes());rp=pathlib.Path(q["native_registry"]);raw=rp.read_bytes();registry=json.loads(raw)
 rm=load("existing_root_accounting",V/"resources.py");observed,reserved,active=rm.Resources(q)._platform()
 assert rp.read_bytes()==raw and observed==registry
 procrows={}
 for p in pathlib.Path("/proc").glob("[0-9]*/stat"):
  try:
   f=p.read_text().rsplit(")",1)[1].split();procrows[int(p.parent.name)]=(int(f[1]),f[19],f[0])
  except (FileNotFoundError,ProcessLookupError):pass
 evidence=[];additional=0
 for a in active:
  pid=a["pid"];cohort=a["cohort"];before=(pathlib.Path("/proc")/str(pid)/"stat").read_text().rsplit(")",1)[1].split();assert int(before[19])==a["start_ticks"]
  matches=[]
  for rid,r in registry["registered_future_requests"].items():
   for k,c in (r.get("consumed",{}).items() if isinstance(r.get("consumed"),dict) else []):
    if k==cohort or isinstance(c,dict)and c.get("cohort")==cohort:matches.append((rid,r))
  assert len(matches)==1
  rid,r=matches[0];memory=r.get("per_cohort_memory",{}).get(cohort,{})
  estimated=memory.get("estimated_peak_model_RAM_bytes",r.get("estimated_peak_model_RAM_bytes"))
  if estimated is None:estimated=r.get("live_RAM_guard_override_profile",{}).get("initial_future_RAM_reservation_bytes")
  declared_cap=memory.get("max_process_tree_rss_bytes",r.get("max_process_tree_rss_bytes"))
  limits=(pathlib.Path("/proc")/str(pid)/"limits").read_text()
  address=next(l for l in limits.splitlines() if l.startswith("Max address space")).split()
  assert address[3].isdigit() and address[4].isdigit();AS_cap=min(int(address[3]),int(address[4]))
  tree={pid};change=True
  while change:
   change=False
   for child,(parent,ticks,state) in procrows.items():
    if parent in tree and child not in tree:tree.add(child);change=True
  pss=0;members=[]
  for member in sorted(tree):
   mp=pathlib.Path("/proc")/str(member);expected=procrows[member]
   try:st=(mp/"stat").read_text().rsplit(")",1)[1].split()
   except (FileNotFoundError,ProcessLookupError):
    members.append(dict(pid=member,start_ticks=expected[1],Pss_bytes=0,credit_basis="disappeared_zero_credit"));continue
   if st[19]!=expected[1]or int(st[1])!=expected[0]:raise RuntimeError("PSS_PID_TICKS_PPID_DRIFT_HOLD")
   try:
    roll=(mp/"smaps_rollup").read_text();val=int(next(l.split()[1]for l in roll.splitlines()if l.startswith("Pss:")))*1024
   except (FileNotFoundError,ProcessLookupError):val=0
   try:post=(mp/"stat").read_text().rsplit(")",1)[1].split()
   except (FileNotFoundError,ProcessLookupError):val=0;post=st
   if post[19]!=st[19]or post[1]!=st[1]:raise RuntimeError("PSS_POST_IDENTITY_DRIFT_HOLD")
   if post[0]in ("Z","X","x"):val=0
   pss+=val;members.append(dict(pid=member,start_ticks=st[19],ppid=int(st[1]),Pss_bytes=val,credit_basis="same_PID_ticks_ppid_pre_post_or_zero"))
  after=(pathlib.Path("/proc")/str(pid)/"stat").read_text().rsplit(")",1)[1].split();assert before[19]==after[19]and before[1]==after[1]
  if estimated is not None:
   assert type(estimated)is int and estimated>0
   planning=max(estimated+2*1024**3,pss+2*1024**3)
   if declared_cap is not None:planning=min(planning,declared_cap)
   basis="Explicit registered model peak or registered runtime initial future reservation plus2GiB overhead; at least2GiB above actual current PSS unless declared tree cap reached. This is a planning commitment, not a guaranteed future hard RSS bound."
  else:
   assert len(tree)==1,"Unknown active tree without registered RAM planning profile"
   planning=AS_cap
   basis="No explicit model peak in this registered cohort; full actual finite kernel RLIMIT_AS used as conservative planning ceiling."
  pending=max(0,planning-pss);additional+=pending
  evidence.append(dict(pid=pid,start_ticks=after[19],cohort=cohort,request_id=rid,members=members,actual_current_Pss_bytes=pss,registered_memory_fields=memory,registered_planning_RAM_bytes=estimated,actual_RLIMIT_AS_bytes=AS_cap,planning_total_bytes=planning,additional_current_planning_commitment_bytes=pending,basis=basis))
 assert rp.read_bytes()==raw
 future_RAM=0
 for r in registry["registered_future_requests"].values():
  if type(r.get("estimated_peak_model_RAM_bytes"))is int:future_RAM+=r["estimated_peak_model_RAM_bytes"]
  for mem in r.get("per_cohort_memory",{}).values():
   if type(mem.get("estimated_peak_model_RAM_bytes"))is int:future_RAM+=mem["estimated_peak_model_RAM_bytes"]
 return dict(schema="ROOT_CURRENT_FOREIGN_ACTIVE_RAM_OBSERVATION_V1",unix=time.time(),registry_ref=dict(path=str(rp),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()),legacy_binding_ref=ref(V/"legacy_foreign_binding.json"),R5_resources_ref=ref(V/"resources.py"),R5_profile_ref=ref(V/"PROFILE.json"),active_foreign_proofs=active,current_RAM_planning_rows=evidence,additional_active_RAM_commitments_bytes=additional,registered_foreign_future_Native_ceiling_bytes=reserved,registered_foreign_explicit_RAM_model_declarations_bytes=future_RAM,foreign_future_ceilings_committed_by_this_scope=False,unknown_active_cohort_count=0,registered_history_or_budgets_modified=False,all_possible_simultaneous_future_max_allocations_guaranteed=False)
def observe():
 for attempt in range(3):
  try:return one()
  except (FileNotFoundError,ProcessLookupError,AssertionError):
   if attempt==2:raise
 raise RuntimeError("Current metadata snapshot failed")
if __name__=="__main__":
 d=observe();print(json.dumps(dict(schema=d["schema"],unix=d["unix"],registry_ref=d["registry_ref"],active_count=len(d["active_foreign_proofs"]),additional_active_RAM_commitments_bytes=d["additional_active_RAM_commitments_bytes"],registered_foreign_future_Native_ceiling_bytes=d["registered_foreign_future_Native_ceiling_bytes"])))
