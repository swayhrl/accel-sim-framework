"""Exact B resource activation supplement around sealed 900sec preparation.
Read-only by default. No algorithms, Source/options, limits or monitor changes.
"""
from pathlib import Path
import argparse,contextlib,copy,hashlib,importlib.util,io,json,sys
A=Path(__file__).resolve().parent;O=A.parent;B900=O/'main_budget900_addendum_v2'
REQUEST='EP_L2_VECTOR1700_WV_DECOMPOSITION_FRESH_V4_20261104';ROOT=O/'private_execution/vector1700'
DEFAULT_SUPPLEMENT=A/'RESOURCE_ACTIVATION_SUPPLEMENT.json'
DEFAULT_SUPPLEMENT_SHA='b2546f763686bd01e70fdc57377eddf565a6295f1ef250344919b629535c4ef6'
B900_SCRIPT_SHA='1c4fefd5bccae407764b81dec4348762db9e583f4f6f8261a471df9e1918b983'
SELECTED_900={'W_ONLY':dict(path=str(B900/'specs/W_ONLY.json'),sha256='25f89fd1a8eeff1c9bae2875dbffa2c0ce3b24b5062943cc5dbe166419e713dc'),'WV_ZERO_RO':dict(path=str(B900/'specs/WV_ZERO_RO.json'),sha256='be801dd04f13e2a9aaab591fdf7ac8788fb5d373412b787d470a6dc2933de4a1')}
def need(v,m):
 if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_bytes())
def module(n,p):sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def pinned(r):need(set(r)>={'path','sha256'} and sha(r['path'])==r['sha256'],'resource supplement dependency drift '+r.get('path','?'));return r

def load_900():
 need(sha(B900/'main_install_with_budget900_overlay.py')==B900_SCRIPT_SHA,'sealed900 materializer changed')
 return module('sealed_900_overlay_pure_functions',B900/'main_install_with_budget900_overlay.py')

def validate_supplement_data(d):
 need(d.get('schema')=='EP_PFV4_B_EXACT_RESOURCE_ACTIVATION_SUPPLEMENT_V3'and d.get('selected_by')=='EP-MAIN','wrong resource supplement identity')
 need(d.get('request')==REQUEST and d.get('root')==str(ROOT),'wrong resource request/root')
 need(d.get('allowed_spec_changes')==['resource_module_ref','pinned_files additions only'],'resource field whitelist altered')
 need(d.get('scientific_start_authorization')is False,'resource supplement cannot grant science')
 need(d.get('selected_900_spec_refs')==SELECTED_900,'wrong exact selected900 base SpecSHA')
 for r in SELECTED_900.values():pinned(r)
 pinned(d['base_overlay_ref']);need(d['base_overlay_ref']==ref(B900/'MAIN_SELECTED_HOST_LIMITS_OVERLAY.json'),'wrong exact900 overlay binding')
 pinned(d['original_materializer_ref']);need(d['original_materializer_ref']==ref(O/'main_install_materialize.py'),'wrong frozen materializer')
 pinned(d['original_runtime_package_ref']);need(d['original_runtime_package_ref']==ref(O/'IMMUTABLE_RUNTIME_PACKAGE.json'),'original runtime package drift')
 need(d['resource_module_ref']['path']==str(A/'resources_vector1700_v4_main_qualified.py'),'wrong exact B adapter path')
 for r in d['resource_pin_additions']:pinned(r)
 bypath={r['path']:r['sha256']for r in d['resource_pin_additions']};need(len(bypath)==len(d['resource_pin_additions']),'duplicate resource graph pin')
 for k in ['resource_module_ref','Main_qualified_helper_ref']:
  pinned(d[k]);need(bypath.get(d[k]['path'])==d[k]['sha256'],'required resource module absent from owned pins')
 need(d['Main_qualified_helper_ref']['path']=='/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v4_20261104_v1/main/qualified_resources_v4/resources_v4.py','wrong Main qualified helper location')
 return bypath

def load_supplement(p=DEFAULT_SUPPLEMENT,expected_sha=None):
 expected_sha=DEFAULT_SUPPLEMENT_SHA if expected_sha is None else expected_sha
 need(sha(p)==expected_sha,'resource supplement SHA mismatch');d=read(p);validate_supplement_data(d);return d

def resource_candidate(base,d,supplement_ref):
 mode=base['mode'];need(mode in SELECTED_900 and base==read(SELECTED_900[mode]['path']),'resource overlay input is not exact selected900 candidate')
 s=copy.deepcopy(base);s['resource_module_ref']=copy.deepcopy(d['resource_module_ref'])
 additions=[*d['resource_pin_additions'],supplement_ref]
 for r in additions:
  need(r['path']not in s['pinned_files']or s['pinned_files'][r['path']]==r['sha256'],'resource supplement cannot replace an existing pin')
  s['pinned_files'][r['path']]=r['sha256']
 need({k:v for k,v in s.items()if k not in ['resource_module_ref','pinned_files']}=={k:v for k,v in base.items()if k not in ['resource_module_ref','pinned_files']},'resource supplement changed protected field')
 return s

def main(argv=None):
 args=list(sys.argv[1:]if argv is None else argv);ap=argparse.ArgumentParser(add_help=False);ap.add_argument('--resource-supplement',default=str(DEFAULT_SUPPLEMENT));ap.add_argument('--resource-supplement-sha256',default=DEFAULT_SUPPLEMENT_SHA);ap.add_argument('--validate-resource-only',action='store_true');a,rest=ap.parse_known_args(args)
 d=load_supplement(a.resource_supplement,a.resource_supplement_sha256);suppref=ref(a.resource_supplement);m900=load_900();overlay,rows=m900.load_overlay();overlayref=ref(B900/'MAIN_SELECTED_HOST_LIMITS_OVERLAY.json')
 candidates={c:resource_candidate(m900.apply_overlay(read(row['base_spec_ref']['path']),row),d,suppref)for c,row in rows.items()}
 adapter=module('exact_Main_B_resource_adapter',d['resource_module_ref']['path']);snap=adapter.snapshot()
 need(snap.get('current_request')==REQUEST and snap.get('resource_admission_is_not_science_permission')is True,'real snapshot wrong resource binding')
 summary=dict(current_request=snap['current_request'],current_scope_registered=snap.get('current_scope_registered'),global_EP_active_count=snap.get('global_EP_consumed_active_count'),foreign_metadata_errors=snap.get('foreign_metadata_errors',[]),resource_admission_is_not_science_permission=snap['resource_admission_is_not_science_permission'])
 if a.validate_resource_only:print(json.dumps(dict(status='EXACT_RESOURCE_GRAPH_AND_REAL_READONLY_SNAPSHOT_PASS',resource_supplement_ref=suppref,real_snapshot=summary,scientific_starts=0,final_spec_writes=0)));return
 if '--materialize'in rest:
  need('--main-install-binding'in rest,'Main install binding absent');bp=rest[rest.index('--main-install-binding')+1];bind=read(bp);need(bind.get('Main_selected_Host_limits_overlay_ref')==overlayref and bind.get('Main_resource_activation_supplement_ref')==suppref,'Main exact900/resource installation binding absent')
 m=module('frozen_main_materializer_with_900_and_resource_activation',O/'main_install_materialize.py');oldread=m.read;oldput=m.put
 specpaths={str(Path(row['base_spec_ref']['path'])):c for c,row in rows.items()};resource_refs=[*d['resource_pin_additions'],suppref]
 qualification_ref=ref(A/'READONLY_RESOURCE_SNAPSHOT_RECEIPT.json');resource_refs_with_receipt=[*resource_refs,qualification_ref]
 def merge_refs(base,extra):
  items={r['path']:r for r in base}
  for r in extra:
   need(r['path']not in items or items[r['path']]['sha256']==r['sha256'],'cannot replace original owned pin');items[r['path']]=r
  return list(items.values())
 def supplemented_read(p):
  key=str(Path(p))
  if key in specpaths:return copy.deepcopy(candidates[specpaths[key]])
  v=oldread(p)
  if key==str(O/'proposal/HOST_INTEGRATION_BINDING_CANDIDATE.json'):
   v=copy.deepcopy(v);v['modules']=merge_refs(v['modules'],resource_refs_with_receipt);v['evidence_refs']['Main_resource_activation']=suppref;v['evidence_refs']['real_readonly_resource_snapshot']=qualification_ref
  if key==str(O/'routing_stage_delta/SYNTHETIC_PRIVATE_ROUTE_NO_SCIENCE_AUTHORITY.json'):
   v=copy.deepcopy(v);v['owned_runtime_pins']=merge_refs(v['owned_runtime_pins'],resource_refs_with_receipt);v['resource_qualification_ref']=qualification_ref;v['Main_resource_activation_supplement_ref']=suppref
  return v
 def checked_put(p,v):
  p=Path(p)
  if p.name=='FROZEN_SPEC.json':
   c=v.get('cohort');need(c in candidates,'resource final Spec outside exact cohorts');base=candidates[c]
   final_binding_fields={'status','launch_permission','scientific_scope_activated','Main_scientific_launch_authorization','parent_scientific_authorization_ref','host_qualification_ref'}
   need({k:x for k,x in v.items()if k not in final_binding_fields}=={k:x for k,x in base.items()if k not in final_binding_fields},'final Spec changed outside exact900/resource/binding fields')
   need(v['limits']==m900.LIMITS and v['estimated_peak_RAM_bytes']==1<<30,'selected900 Host limits lost')
   need(v['resource_module_ref']==d['resource_module_ref'],'new Main resource adapter missing before final Spec write')
   for r in resource_refs:need(v['pinned_files'].get(r['path'])==r['sha256'],'resource graph incomplete before final Spec write')
  if p.name=='HOST_QUALIFICATION.json':
   need(all(r in v['modules']for r in resource_refs_with_receipt),'new resource graph absent from final Host qualification')
  if p.name=='NATIVE_ENTRY_ROUTE_V3.json':
   need(all(r in v['owned_runtime_pins']for r in resource_refs_with_receipt)and v['resource_qualification_ref']==qualification_ref,'new resource graph absent from final Native route')
  if p.name=='MAIN_ATOMIC_ACTIVATION_PAYLOAD.json':
   v=copy.deepcopy(v);v['Main_selected_Host_limits_overlay_ref']=overlayref;v['Main_resource_activation_supplement_ref']=suppref;v['Main_selected_Host_limits_base_spec_refs']={c:rows[c]['base_spec_ref']for c in sorted(rows)};v['Host_limits_profile']='MAIN_SELECTED_900SEC_RSS2G_AS10G_RESULT128M_EST_RAM1G';v['old24h_candidates_selected']=False;v['old_resource_adapter_selected']=False
  return oldput(p,v)
 m.read=supplemented_read;m.put=checked_put;previous=sys.argv;capture=io.StringIO()
 try:
  sys.argv=[str(O/'main_install_materialize.py'),*rest]
  with contextlib.redirect_stdout(capture):m.main()
 finally:sys.argv=previous
 result=json.loads(capture.getvalue());result.update(Main_selected_Host_limits_overlay_ref=overlayref,Main_resource_activation_supplement_ref=suppref,real_readonly_snapshot=summary,selected_resource_module_ref=d['resource_module_ref'],old_resource_adapter_selected=False);print(json.dumps(result))
if __name__=='__main__':main()
