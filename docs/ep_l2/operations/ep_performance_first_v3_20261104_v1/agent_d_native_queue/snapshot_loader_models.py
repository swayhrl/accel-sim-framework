"""Read-only exact loader/model/claim join; never starts or modifies peers."""
import datetime,hashlib,json,os
from pathlib import Path
import safe_native_candidate as c
O=Path(__file__).parent
D=Path("/root/data/dtc_stage_iia_remaining48_20261104_v1")
REG=Path("/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 cp=D/"control/POOL_DISPATCH_RESERVATIONS.json";cb=cp.read_bytes();rb=REG.read_bytes()
 claims=json.loads(cb)["claims"];q=json.loads(rb)["registered_future_requests"]["DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1"]
 matches=[];wrappers=[];unmatched=[];errors=[];join=[]
 for pp in Path("/proc").iterdir():
  if not pp.name.isdigit():continue
  try:
   argv=[x.decode(errors="replace")for x in(pp/"cmdline").read_bytes().split(b"\0")if x]
   kind=c.classify_simulator_argv(argv)
   if kind=="NOT_MODEL":continue
   parts=(pp/"stat").read_text().rsplit(")",1)[1].split()
   status={x.split(":",1)[0]:x.split(":",1)[1].strip()for x in(pp/"status").read_text().splitlines()if ":"in x}
   row=dict(pid=int(pp.name),start_ticks=int(parts[19]),state=parts[0],exe=os.readlink(pp/"exe"),
    argv=argv,RSS_bytes=int(status.get("VmRSS","0 kB").split()[0])*1024,
    CPU_affinity=sorted(os.sched_getaffinity(int(pp.name))),kind=kind)
   if kind=="WRAPPER_NOT_MODEL":wrappers.append(row);continue
   matches.append(row)
  except (OSError,ValueError,IndexError):continue
 for cohort,claim in claims.items():
  try:
   cr=q["consumed"][cohort];sp=D/"control"/(cohort+"_SPEC.json")
   assert sha(sp)==q["admitted_specs"][cohort]
   spec=json.loads(sp.read_text());ip=Path(cr["intent"]);assert sha(ip)==cr["intent_sha256"]
   intent=json.loads(ip.read_text());assert intent["uuid"]==cr["uuid"]
   out=D/"DTC/run/results"/cr["uuid"];ident=json.loads((out/"NATIVE_SIMULATOR_PID_AND_MAPS.json").read_text())
   expected=spec["native_simulator_argv"];models=[z for z in matches if z["argv"][-len(expected):]==expected]
   assert len(models)==1,(cohort,"expected one exact argv model",len(models))
   z=models[0];assert z["pid"]==ident["pid"]and z["start_ticks"]==ident["start_ticks"]
   maps=(Path("/proc")/str(z["pid"])/"maps").read_text();elf=expected[0]
   assert any(line.split()[-1]==elf for line in maps.splitlines()if line.split())
   join.append(dict(cohort=cohort,uuid=cr["uuid"],input_digest=spec["input_digest"],program=spec["program"],
    profile=spec["profile"],pid=z["pid"],start_ticks=z["start_ticks"],RSS_bytes=z["RSS_bytes"],
    estimate_bytes=spec["estimated_peak_model_RAM_bytes"],
    additional_RAM_bytes=max(0,spec["estimated_peak_model_RAM_bytes"]-z["RSS_bytes"]),
    CPU_affinity=z["CPU_affinity"],matched_actual_argv_config_input=True,
    model_PID_generation_and_map_verified=True,
    existing_claim_observed_model=claim.get("observed_model"),
    claim_flag_not_a_live_process_test=True))
  except Exception as e:errors.append(dict(cohort=cohort,error=repr(e)))
 joined={(x["pid"],x["start_ticks"])for x in join}
 unmatched=[z for z in matches if(z["pid"],z["start_ticks"])not in joined]
 stable=(sha(cp)==hashlib.sha256(cb).hexdigest())
 result=dict(schema="EP_V3_READONLY_LOADER_AWARE_DTC48_MODEL_JOIN_V1",utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
  status="PASS_READONLY_JOIN_NOT_FULL_ADMISSION"if not errors and stable else"HOLD_MAPPING_OR_DRIFT",
  registered_claims=len(claims),actual_model_count=len(matches),matched_DTC48_models=len(join),
  strace_wrappers_excluded=len(wrappers),models=matches,claim_joins=join,unmatched_models=unmatched,errors=errors,
  claims_sha256=hashlib.sha256(cb).hexdigest(),claims_unchanged_while_read=stable,
  actual_model_RSS_sum_bytes=sum(x["RSS_bytes"]for x in join),
  future_model_RAM_growth_sum_bytes=sum(x["additional_RAM_bytes"]for x in join),
  note="Observed_model=false claim metadata is not proof of no live model. PID and loader argv checked independently.",
  no_foreign_mutation=True,full_foreign_resource_adapter_qualified=False)
 (O/"LOADER_AWARE_FOREIGN_PROCESS_JOIN.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps({k:result[k]for k in["status","actual_model_count","matched_DTC48_models","strace_wrappers_excluded","actual_model_RSS_sum_bytes","future_model_RAM_growth_sum_bytes","errors"]}))
if __name__=="__main__":main()
