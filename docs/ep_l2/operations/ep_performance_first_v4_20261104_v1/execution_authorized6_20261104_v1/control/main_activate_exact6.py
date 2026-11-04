"""EP-MAIN exact approved6 activation; no model launch. Owned metadata only, CAS Native+registry."""
from pathlib import Path
import json,hashlib,os,fcntl,uuid,copy,datetime,sys,importlib.util,subprocess
C=Path(__file__).resolve().parent;V=C.parent.parent;N=Path("/root/data/ep_l2_dtc_l1_native_v2")
REG=N/"control/science_authority/NATIVE_SCIENCE_REGISTRY.json";EPOCH=N/"control/CURRENT_SCIENCE_EPOCH.json"
def need(x,m):
 if not x:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_bytes())
def put(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(x,sort_keys=True,indent=2)+"\n").encode();t=p.with_name("."+p.name+"."+str(uuid.uuid4()))
 with t.open("xb")as f:f.write(b);f.flush();os.fsync(f.fileno())
 os.replace(t,p);fd=os.open(p.parent,os.O_RDONLY);os.fsync(fd);os.close(fd);return ref(p)
def module(p):
 sp=importlib.util.spec_from_file_location("main_activation_check_"+str(uuid.uuid4()).replace("-",""),p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def merge(old,extra):
 d={r["path"]:r for r in old}
 for r in extra:
  need(sha(r["path"])==r["sha256"],"added resource pin drift "+r["path"])
  need(r["path"]not in d or d[r["path"]]["sha256"]==r["sha256"],"conflicting added graph pin")
  d[r["path"]]=r
 return list(d.values())
def main():
 overlay=read(C/"MAIN_CURRENT_FOREIGN_RESOURCE_BINDING.json");need(overlay["approved_by"]=="EP-MAIN","resource wiring not reviewed")
 parent=read(C/"USER_AUTHORIZATION.json");need(parent["explicit_user_approval"]and parent["approved_total_launches"]==6 and not parent["old_budgets_reusable"],"exact6 auth")
 families={f["name"]:f for f in parent["families"]};need(set(families)=={"A1","B","A3"}and all(f["approved_launches"]==2 for f in families.values()),"exact independent budgets")
 native=N/"bin/native";pre=C/"NATIVE_PREIMAGE_WITH_DTC_PHYS768.sh";candidate=C/"GLOBAL_NATIVE_EXACT6_WITH_FOREIGN_PRESERVED.sh"
 need(candidate.read_bytes().endswith(pre.read_bytes()),"foreign byte preservation")
 need(native.read_bytes()==pre.read_bytes(),"Native preimage moved; no overwrite")
 contract=C/"SHARED_ROUTE_CONTRACT_V4_EXACT6.json";put(contract,dict(schema="EP_MAIN_V3_SHARED_ROUTE_CONTRACT_V1",installed_baseline_ref=ref(candidate),reviewed_foreign_insertions=[],Main_authorization_ref=ref(C/"USER_AUTHORIZATION.json"),current_foreign_preimage_ref=ref(pre)))
 groups={};points=[]
 for g in ["A1","B","A3"]:
  f=families[g]
  rt=V/("track_b/private_runtime"if g=="B"else f"track_a/resource_admission_followup_v2/{g}/runtime")
  root=V/("track_b/private_execution/vector1700"if g=="B"else f"track_a/resource_admission_followup_v2/{g}/execution")
  rr=overlay["groups"][g];extras=rr["owned_resource_refs"]
  for item in extras:need(sha(item["path"])==item["sha256"],"resource identity drift")
  if g!="B":
   put(root/"control/USER_AUTHORIZATION.json",read(C/(g+"_USER_AUTHORIZATION.json")))
  authref=ref(root/"control/USER_AUTHORIZATION.json")
  hbase=root/("control/HOST_QUALIFICATION.json"if g=="B"else"control/HOST_DELTA_QUALIFICATION_CANDIDATE.json")
  host=read(hbase);host["modules"]=merge(host["modules"],extras);host["Main_scientific_authorization_ref"]=authref;host["Main_current_foreign_resource_binding_ref"]=ref(C/"MAIN_CURRENT_FOREIGN_RESOURCE_BINDING.json")
  hp=root/"control/HOST_QUALIFICATION_MAIN_V4.json";put(hp,host)
  admitted={};specs=[]
  for cohort in f["allowed_cohorts"]:
   sp=root/"cases"/cohort/"control/FROZEN_SPEC.json";s=read(sp);before=copy.deepcopy(s)
   need(s["source_identity"]==f["Source5"]and s["science_request_id"]==f["request"],"Source/scope")
   need(s["native_boot_id"]==Path("/proc/sys/kernel/random/boot_id").read_text().strip()and s["native_mount_namespace"]==os.readlink("/proc/self/ns/mnt"),"domain changed")
   s.update(status="USER_APPROVED_MAIN_BOUND_FRESH_V4",launch_permission=True,scientific_scope_activated=True,Main_scientific_launch_authorization=authref,parent_scientific_authorization_ref=ref(C/"USER_AUTHORIZATION.json"),host_qualification_ref=ref(hp),resource_module_ref=rr["resource_module_ref"])
   for r in extras:s["pinned_files"][r["path"]]=r["sha256"]
   s["pinned_files"][str(hp)]=sha(hp)
   allowed={"status","launch_permission","scientific_scope_activated","Main_scientific_launch_authorization","parent_scientific_authorization_ref","host_qualification_ref","resource_module_ref","pinned_files"}
   need({k:x for k,x in s.items()if k not in allowed}=={k:x for k,x in before.items()if k not in allowed},"protected Spec field changed")
   for p,h in s["pinned_files"].items():need(sha(p)==h,"runtime dependency drift "+p)
   check_code="import sys,json;sys.path.insert(0,sys.argv[1]);import ep_perf_native_wv_modes_draft as e;e.validate_spec_contract(json.load(sys.stdin));print(1)"
   z=subprocess.run(["/usr/bin/python3","-B","-c",check_code,str(rt)],input=json.dumps(s),text=True,capture_output=True,timeout=60);need(z.returncode==0,"full43 final Spec failed "+z.stderr[-2000:])
   put(sp,s);admitted[cohort]=sha(sp);specs.append(s)
   points.append(dict(group=g,cohort=cohort,mode=s["mode"],spec_ref=ref(sp)))
  routepath=root/("control/NATIVE_ENTRY_ROUTE_V3.json"if g=="B"else"control/NATIVE_ENTRY_ROUTE_V4.json")
  route=read(routepath);route.update(status="MAIN_INSTALLED_ADDITIVE_NATIVE_EP_PERF_ROUTE",approved_by="EP-MAIN",scientific_scope_activated=True,install_authorization=True,Main_user_authorization_ref=authref,global_shared_native_ref=dict(path=str(native),sha256=sha(candidate)),shared_route_contract_ref=ref(contract))
  route["owned_runtime_pins"]=merge(route["owned_runtime_pins"],extras+[ref(hp),authref]);put(routepath,route)
  entry=route["entry_ref"];s=specs[0]
  row=dict(request=f["request"],owner="EP-MAIN",project="EP_L2",budget=2,remaining=2,consumed={},admitted_specs=admitted,runtime_versions={s["host_engine_ref"]["sha256"]:dict(engine_ref=s["host_engine_ref"],common_ref=s["host_common_ref"])},authorization_ref=authref,parent_authorization_ref=ref(C/"USER_AUTHORIZATION.json"),source_identity=s["source_identity"],allowed_cohorts=f["allowed_cohorts"],native_entry_ref=entry,native_qualification_ref=ref(routepath),state="ARMED",resource_group_id=f["request"],reserved_write_bytes=0,source_keep=True,automatic_retry=False,refund=False,global_model_concurrency_authorized=10,global_model_concurrency_qualified=10,registered_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
  groups[g]=dict(request_id=f["request"],budget=2,data_root=str(root),runtime_root=str(rt),native_entry_ref=entry,route_ref=ref(routepath),registry_row=row)
  claims=root/"control/DISPATCH_CLAIMS.json"
  if claims.exists():need(read(claims)==dict(claims={}),"existing own claims")
  else:put(claims,dict(claims={}))
 payload=dict(schema="EP_MAIN_PFV4_EXACT6_ACTIVATION_PAYLOAD_V1",user_authorization_ref=ref(C/"USER_AUTHORIZATION.json"),groups=groups,points=points,global_native_candidate_ref=ref(candidate),resource_binding_ref=ref(C/"MAIN_CURRENT_FOREIGN_RESOURCE_BINDING.json"),scientific_starts=0)
 put(C/"EXACT6_ACTIVATION_PAYLOAD.json",payload)
 admission=Path("/root/data/ep_l2_full_workload_performance_20261027_v1/execution_performance_first_20261103_v1/control/ADMISSION.lock")
 with admission.open("a+b")as al,(N/"control/science_authority/REGISTRY_UPDATE.lock").open("a+b")as l,(N/"control/science_authority/NATIVE_ROUTE_UPDATE.lock").open("a+b")as nl:
  fcntl.flock(al,fcntl.LOCK_EX);fcntl.flock(l,fcntl.LOCK_EX);fcntl.flock(nl,fcntl.LOCK_EX)
  registry=read(REG);epoch=read(EPOCH);need(sha(REG)==epoch["native_registry_sha256"],"authority unstable");before=copy.deepcopy(registry)
  need(native.read_bytes()==pre.read_bytes(),"Native CAS changed")
  need(all(q["request_id"]not in registry["registered_future_requests"]for q in groups.values()),"already registered no repeat")
  for p in [REG,EPOCH]:
   dest=N/"control/science_authority/request_history"/(p.stem+"."+sha(p)+".json")
   if not dest.exists():dest.write_bytes(p.read_bytes())
  tmp=native.with_name(".native.EP_PFV4_"+str(uuid.uuid4()))
  with tmp.open("xb")as f:f.write(candidate.read_bytes());f.flush();os.fsync(f.fileno())
  tmp.chmod(native.stat().st_mode&0o777);need(native.read_bytes()==pre.read_bytes(),"Native CAS changed before replace");os.replace(tmp,native);fd=os.open(native.parent,os.O_RDONLY);os.fsync(fd);os.close(fd)
  for g,q in groups.items():registry["registered_future_requests"][q["request_id"]]=q["registry_row"]
  need(all(registry["registered_future_requests"][k]==x for k,x in before["registered_future_requests"].items()),"foreign/old row changed")
  need({k:x for k,x in registry.items()if k not in["registered_future_requests","new_scientific_budget_remaining"]}=={k:x for k,x in before.items()if k not in["registered_future_requests","new_scientific_budget_remaining"]},"old top/history changed")
  registry["new_scientific_budget_remaining"]=sum(q["remaining"]if"remaining"in q else max(0,q.get("budget",0)-(q.get("consumed",0)if type(q.get("consumed",0))is int else len(q.get("consumed",{}))))for q in registry["registered_future_requests"].values())
  put(REG,registry);epoch["native_registry_sha256"]=sha(REG);epoch["new_budget_remaining"]=registry["new_scientific_budget_remaining"];epoch["request_revision"]=dict(request_id=[x["request_id"]for x in groups.values()],operation="EP_MAIN_PFV4_REGISTER_EXACT3_FAMILIES_6_STARTS_AND_INSTALL_NATIVE",utc=datetime.datetime.now(datetime.timezone.utc).isoformat());put(EPOCH,epoch)
  put(C/"MAIN_FORMAL_NATIVE_INSTALLATION_RECEIPT.json",dict(schema="EP_MAIN_PFV4_FORMAL_EXACT6_INSTALLATION_V1",status="THREE_REQUESTS_BUDGET2_EACH_REGISTERED_NATIVE_AND_FINAL_SPECS_ARMED",payload_ref=ref(C/"EXACT6_ACTIVATION_PAYLOAD.json"),registry_ref=ref(REG),epoch_ref=ref(EPOCH),native_ref=ref(native),foreign_and_old_registry_rows_preserved=True,foreign_native_bytes_preserved=True,scientific_starts=0))
 print(json.dumps(dict(status="EXACT6_REGISTERED_ARMED_NO_START",payload_ref=ref(C/"EXACT6_ACTIVATION_PAYLOAD.json"))))
if __name__=="__main__":main()
