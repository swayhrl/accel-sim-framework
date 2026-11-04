from pathlib import Path
import json,hashlib,sys,importlib.util,datetime
C=Path(__file__).resolve().parent;V=C.parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def put(p,o):p.write_text(json.dumps(o,sort_keys=True,indent=2)+"\n")
helper=Path(sys.argv[1]);expected=sys.argv[2];pins=[Path(x)for x in sys.argv[3:]]
assert sha(helper)==expected and helper in pins
assert all(p.is_relative_to(V/"track_b")for p in pins)
source_refs=[ref(p)for p in pins];snapshots={};groups={}
for f in json.loads((C/"USER_AUTHORIZATION.json").read_bytes())["families"]:
 g=f["name"];request=f["request"];ap=C/("resources_current_"+g+".py")
 code='from pathlib import Path\nimport hashlib,importlib.util\nREQUEST='+repr(request)+'\nHELPER=Path('+repr(str(helper))+')\nHELPER_SHA='+repr(expected)+'''
def helper():
 if hashlib.sha256(HELPER.read_bytes()).hexdigest()!=HELPER_SHA:raise ValueError("current strict foreign resource helper drift")
 s=importlib.util.spec_from_file_location("Main_current_strict_foreign_resources",HELPER);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def snapshot():return helper().snapshot(REQUEST)
def admit(s,own_pending_additional_RAM,own_remaining_writes,policy=None):
 if s.get("current_request")!=REQUEST:raise ValueError("cross-scope current resource snapshot")
 return helper().admit(s,own_pending_additional_RAM,own_remaining_writes,policy=policy)
def forecast(input_id,history,policy=None):return helper().forecast(input_id,history,policy=policy)
'''
 ap.write_text(code);sp=importlib.util.spec_from_file_location("root_independent_resource_delta_"+g,ap);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 snap=m.snapshot();assert snap["current_request"]==request and snap["current_scope_registered"]is False and not snap["foreign_metadata_errors"],snap["foreign_metadata_errors"]
 assert len(snap["PHYS4_accounting"]["models"])==4
 try:m.admit(snap,1<<30,256<<20,policy=dict(max_global_EP_models=10,requested_host_cpu=2))
 except ValueError as e:assert "V4_REQUEST_NOT_REGISTERED"in str(e)
 else:raise ValueError("unregistered admission accepted")
 rp=C/("ACTUAL_PRE_ACTIVATION_RESOURCE_"+g+".json");put(rp,snap);snapshots[g]=ref(rp)
 groups[g]=dict(request=request,resource_module_ref=ref(ap),owned_resource_refs=source_refs+[ref(ap)])
review=dict(schema="EP_MAIN_PFV4_CURRENT_FOREIGN_MAPPING_BINDING_V1",approved_by="EP-MAIN",status="EXACT_PHYS4_LIVE_RESOURCE_AND_FOREIGN_GENERATION_MAPPING_ACCEPTED",groups=groups,actual_snapshot_refs=snapshots,original_V4_maps_math_caps_and_5GiB_floor_preserved=True,scope_Source_options_limits_monitor_unchanged=True,no_foreign_writes=True,no_model_starts=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
put(C/"MAIN_CURRENT_FOREIGN_RESOURCE_BINDING.json",review)
print(json.dumps(dict(status=review["status"],binding_ref=ref(C/"MAIN_CURRENT_FOREIGN_RESOURCE_BINDING.json"),no_model_starts=True)))
