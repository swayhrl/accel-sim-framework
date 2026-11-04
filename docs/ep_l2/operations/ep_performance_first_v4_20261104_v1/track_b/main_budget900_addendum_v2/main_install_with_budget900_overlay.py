"""Explicit Main-selected Host budget overlay wrapper. Frozen V1 package is read-only.
No registry/sharedNative writes or model launches; underlying Main materializer remains sole immutable implementation.
"""
from pathlib import Path
import argparse,json,hashlib,copy,importlib.util,sys
A=Path(__file__).resolve().parent;O=A.parent
DEFAULT_OVERLAY=A/'MAIN_SELECTED_HOST_LIMITS_OVERLAY.json'
DEFAULT_OVERLAY_SHA='54bedc875d9f1ae332648711469ad59612ce3b935878c01abae074d12a2ce63a'
BASES={'W_ONLY':dict(cohort='EP_PERF_PFV4_VECTOR4M_W_ONLY_1700_V1',path=str(O/'proposal/specs/W_ONLY.json'),sha256='7417e0eea9559d2c1ed89709a2fa10e0ad162a376d99188470a978a0a40ba8a6'),'WV_ZERO_RO':dict(cohort='EP_PERF_PFV4_VECTOR4M_WV_ZERO_RO_1700_V1',path=str(O/'proposal/specs/WV_ZERO_RO.json'),sha256='96322c016c1f8ec148151b61872b45cd7b6ed9f8c4c045c338d7fe211a5a24b9')}
LIMITS=dict(wall_seconds=900,RSS_bytes=2<<30,AS_bytes=10<<30,result_bytes=128<<20)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_bytes())
def need(v,m):
 if not v:raise ValueError(m)
def validate_overlay_data(d):
 need(d.get('schema')=='EP_PFV4_MAIN_SELECTED_VECTOR1700_HOST_LIMITS_OVERLAY_V2'and d.get('selected_by')=='EP-MAIN','wrong Main Host-limits overlay identity')
 need(d.get('scientific_start_authorization')is False and d.get('proposed_new_scientific_starts')==0,'overlay cannot grant scientific starts')
 need(d.get('scope_request')=='EP_L2_VECTOR1700_WV_DECOMPOSITION_FRESH_V4_20261104','wrong independent request scope')
 need(d.get('allowed_patch_fields')==['limits','estimated_peak_RAM_bytes']and d.get('allowed_limit_keys')==['wall_seconds','RSS_bytes','AS_bytes','result_bytes'],'Host field whitelist altered')
 need(type(d.get('points'))is list and len(d['points'])==2,'overlay requires exact two cohorts')
 need({p.get('cohort')for p in d['points']}=={b['cohort']for b in BASES.values()},'overlay cohort scope violation')
 rows={}
 for p in d['points']:
  need(set(p)=={'cohort','mode','base_spec_ref','Host_limits','estimated_peak_RAM_bytes'},'unauthorized overlay field: only Host limits/estimate permitted')
  need(p.get('mode')in BASES,'wrong overlay mode');b=BASES[p['mode']]
  need(p['cohort']==b['cohort'],'wrong mode/cohort binding')
  need(p['base_spec_ref']==dict(path=b['path'],sha256=b['sha256']),'wrong exact base spec identity')
  need(sha(b['path'])==b['sha256'],'frozen base spec SHA changed')
  need(type(p['Host_limits'])is dict and set(p['Host_limits'])==set(LIMITS)and all(type(v)is int for v in p['Host_limits'].values())and p['Host_limits']==LIMITS,'only selected wall900/RSS2GiB/AS10GiB/result128MiB permitted')
  need(type(p['estimated_peak_RAM_bytes'])is int and p['estimated_peak_RAM_bytes']==1<<30,'only selected estimated RAM1GiB permitted')
  base=read(b['path']);need(base['cohort']==p['cohort']and base['mode']==p['mode'],'base mode/cohort drift')
  need(base['limits']==dict(LIMITS,wall_seconds=86400),'old base Host limit identity drift')
  rows[p['cohort']]=p
 need(len(rows)==2,'duplicate overlay cohort')
 for k in ['original_delivery_ref','original_materializer_ref','original_engine_package_ref']:
  r=d[k];need(sha(r['path'])==r['sha256'],'frozen original delivery preimage drift '+k)
 need(d['original_materializer_ref']['path']==str(O/'main_install_materialize.py'),'wrong original materializer')
 for e in d['accepted_sameSource_DONE_evidence']:
  need(sha(e['DONE_ref']['path'])==e['DONE_ref']['sha256'],'accepted historical DONE drift')
  done=read(e['DONE_ref']['path']);need(done['source_identity']==read(BASES['W_ONLY']['path'])['source_identity']==e['source_identity'],'historical budget evidence different Source')
 return rows

def load_overlay(p=DEFAULT_OVERLAY,expected_sha=DEFAULT_OVERLAY_SHA):
 need(isinstance(expected_sha,str)and len(expected_sha)==64 and sha(p)==expected_sha,'overlay SHA mismatch')
 d=read(p);return d,validate_overlay_data(d)

def apply_overlay(base,row):
 mode=row['mode'];b=BASES[mode]
 need(base==read(b['path'])and sha(b['path'])==b['sha256'],'overlay input differs from exact frozen base')
 out=copy.deepcopy(base);out['limits']=copy.deepcopy(row['Host_limits']);out['estimated_peak_RAM_bytes']=row['estimated_peak_RAM_bytes']
 need({k:v for k,v in out.items()if k not in ['limits','estimated_peak_RAM_bytes']}=={k:v for k,v in base.items()if k not in ['limits','estimated_peak_RAM_bytes']},'non-Host field changed')
 return out

def main(argv=None):
 args=list(sys.argv[1:]if argv is None else argv);ap=argparse.ArgumentParser(add_help=False);ap.add_argument('--limits-overlay',default=str(DEFAULT_OVERLAY));ap.add_argument('--limits-overlay-sha256',default=DEFAULT_OVERLAY_SHA);ap.add_argument('--validate-overlay-only',action='store_true');a,rest=ap.parse_known_args(args)
 d,rows=load_overlay(a.limits_overlay,a.limits_overlay_sha256);overlay_ref=ref(a.limits_overlay);candidates={c:apply_overlay(read(row['base_spec_ref']['path']),row)for c,row in rows.items()}
 if a.validate_overlay_only:
  print(json.dumps(dict(status='MAIN_SELECTED_900SEC_OVERLAY_VALIDATED_NO_WRITES',overlay_ref=overlay_ref,cohorts=sorted(rows),Host_limits=LIMITS,estimated_peak_RAM_bytes=1<<30,scientific_starts=0)));return
 if '--materialize'in rest:
  need('--main-install-binding'in rest,'Main installation binding required');bindingpath=rest[rest.index('--main-install-binding')+1];need(read(bindingpath).get('Main_selected_Host_limits_overlay_ref')==overlay_ref,'Main exact installation binding must include selected overlay SHA')
 sp=importlib.util.spec_from_file_location('frozen_v1_materializer_under_main_host_limits_overlay',O/'main_install_materialize.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);oldread=m.read;oldput=m.put
 paths={str(Path(row['base_spec_ref']['path'])):c for c,row in rows.items()}
 def overlay_read(p):
  k=str(Path(p))
  return copy.deepcopy(candidates[paths[k]])if k in paths else oldread(p)
 def checked_put(p,value):
  p=Path(p)
  if p.name=='FROZEN_SPEC.json':
   c=value.get('cohort');need(c in candidates,'materializer outside exact overlay cohorts');base=candidates[c]
   final_binding_fields={'status','launch_permission','scientific_scope_activated','Main_scientific_launch_authorization','parent_scientific_authorization_ref','host_qualification_ref'}
   need({k:v for k,v in value.items()if k not in final_binding_fields}=={k:v for k,v in base.items()if k not in final_binding_fields},'materializer changed nonbinding/non-Host scientific field')
   need(value['limits']==LIMITS and value['estimated_peak_RAM_bytes']==1<<30,'selected Host limits absent before immutable spec write')
  if p.name=='MAIN_ATOMIC_ACTIVATION_PAYLOAD.json':
   value=copy.deepcopy(value);value['Main_selected_Host_limits_overlay_ref']=overlay_ref;value['Main_selected_Host_limits_base_spec_refs']={c:rows[c]['base_spec_ref']for c in sorted(rows)};value['Host_limits_profile']='MAIN_SELECTED_900SEC_RSS2G_AS10G_RESULT128M_EST_RAM1G';value['old24h_candidates_selected']=False
  return oldput(p,value)
 m.read=overlay_read;m.put=checked_put
 # Whole overlay and base SHA/scope/field whitelist already checked, before original schema/spec-write/consume logic.
 previous=sys.argv
 try:sys.argv=[str(O/'main_install_materialize.py'),*rest];return m.main()
 finally:sys.argv=previous
if __name__=='__main__':main()
