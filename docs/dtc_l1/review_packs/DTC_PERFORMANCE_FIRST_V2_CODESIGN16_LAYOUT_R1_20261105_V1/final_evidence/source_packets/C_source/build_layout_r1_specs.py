"""Materialize exactly the approved fixed-Core Physical x OO-PIB16 namespace.
No science registration, native prepare, model launch, lease, owner or Goal actions.
"""
from pathlib import Path
import argparse,json,hashlib,copy,types
D=Path(__file__).resolve().parent
REQ='DTC_PERF_FIRST_V2_CODESIGN16_LAYOUT_R1_20261105_V1'
AUTHORITY='425ff55a5b57eb28d968bfc8f79eb5f5060e6ebe'
LOGICAL=Path('/root/data/dtc_perf_first_v2_codesign16_layout_r1_20261105_v1')
PROFILES={'PHYS768_OOPIB192_TAG64x8':768,'PHYS1024_OOPIB192_TAG64x8':1024}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def encoded(x):return (json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
def load(p):
 m=types.ModuleType('V2_COMBO_PRIVATE_CPU_MATERIALIZER');m.__file__=str(p);exec(compile(Path(p).read_bytes(),str(p),'exec'),m.__dict__);return m

def build(output_root,resource_fields_path,resource_fields_sha256,logical_root=LOGICAL):
 root=Path(output_root).resolve();logical=Path(logical_root);assert logical==LOGICAL;root.mkdir(parents=True,exist_ok=True)
 layout_path=logical/'control/LAUNCHER_LAYOUT.fixed.json';assert layout_path.exists();layout_ref={'path':str(layout_path),'sha256':sha(layout_path)}
 dep=read(D/'DEPENDENCY_PINS.json');assert dep['request']==REQ and dep['authority_commit']==AUTHORITY and dep['logical_root']==str(logical)
 for x in dep['files']:assert sha(x['path'])==x['sha256'],'DEPENDENCY_SHA:'+x['path']
 assert sha(resource_fields_path)==resource_fields_sha256
 fields=read(resource_fields_path);records=fields['points']if'points'in fields else fields['records'];assert fields['request']==REQ and len(records)==16 and ('budget'not in fields or fields['budget']==16)
 u=load(dep['utility_path']);cm=read(dep['candidate_matrix_path']);rows=cm['candidates'];assert len(rows)==16 and len({r['proposed_native_cohort']for r in rows})==16
 assert {r['profile']for r in rows}==set(PROFILES)and len({r['input_digest']for r in rows})==8
 assert {(r['program'],r['profile'])for r in rows}=={(r['program'],p)for r in rows for p in PROFILES}
 assert {x['cohort']for x in records}=={r['proposed_native_cohort']for r in rows}
 configs={};config_files={}
 for profile in PROFILES:
  row=next(r for r in rows if r['profile']==profile);configs[profile]=[];config_files[profile]=[]
  for i,x in enumerate(row['configs']):
   assert sha(x['path'])==x['sha256'];rel=Path('DTC/env')/('DH_'+profile)/('config-'+str(i)+'.config');h=u.write_exact(root/rel,Path(x['path']).read_bytes(),root);configs[profile].append({'path':str(logical/rel),'sha256':h});config_files[profile].append(root/rel)
 points=[];refs=[]
 for row in rows:
  profile=row['profile'];cohort=row['proposed_native_cohort'];physical=PROFILES[profile];digest=row['input_digest'];assert cohort=='E2-DTCPFV2R1-'+digest[:16]+'-DH-PHYS'+str(physical)+'-OOPIB192-V1'
  d=next(x for x in dep['selected']if x['program']==row['program']);assert sha(d['baseline_spec_path'])==d['baseline_spec_sha256'];base=read(d['baseline_spec_path']);assert base['expected_options']==row['DH_P0_reference']['effective_options']and len(base['expected_options'])==270
  rp=next(x for x in records if x['cohort']==cohort);assert rp['program']==row['program']and rp['input_digest']==digest and rp['profile']==profile and rp.get('structure_variant',profile)==profile and rp.get('cell','DH')=='DH'and rp.get('downstream_profile','P0')=='P0'
  assert all(type(v)is int and v>0 for v in rp['limits'].values());assert rp['limits']['max_process_tree_vms_bytes']>=rp['limits']['max_process_tree_rss_bytes'];assert type(rp['estimated_peak_model_RAM_bytes'])is int and rp['estimated_peak_model_RAM_bytes']>0
  s=copy.deepcopy(base);s.update(schema='DTC_PERFV2_CODESIGN16_LAYOUT_R1_SPEC_V1',cohort=cohort,request=REQ,cell='DH',profile=profile,structure_variant=profile,downstream_profile='P0',host_cpu=None,performance_scope='PERFV2_CODESIGN16_LAYOUT_R1_DH_ONLY_NEVER_ORIGINAL_OR_IR_R2',estimated_peak_model_RAM_bytes=rp['estimated_peak_model_RAM_bytes'],limits=dict(copy.deepcopy(base['limits']),**copy.deepcopy(rp['limits'])),configs=copy.deepcopy(configs[profile]),source_kind='FROZEN_FIXED8_WHOLE_DECLARED_TRACE_PERFORMANCE_ONLY',scientific_authority_commit=AUTHORITY,host_launcher_layout=copy.deepcopy(layout_ref),recovery_from_old_charged_cohort=row['recovery_from_old_charged_cohort'],recovery_from_old_charged_uuid=row['recovery_from_old_charged_uuid'],original_plan_id=row['plan_id'],frozen_candidate_matrix_sha256=dep['candidate_matrix_sha256'])
  s['expected_options']=copy.deepcopy(row['expected_effective_options']);delta={k:{'from':base['expected_options'][k],'to':s['expected_options'][k]}for k in base['expected_options']if base['expected_options'][k]!=s['expected_options'][k]}
  assert delta=={'-gpgpu_dtc_l1_physical_lines':{'from':['640'],'to':[str(physical)]},'-gpgpu_dtc_l1_oo_pib_entries':{'from':['128'],'to':['192']}}and len(s['expected_options'])==270
  parsed=u.supplied_options(config_files[profile]);assert all(s['expected_options'].get(k)==v for k,v in parsed.items())
  bind=Path(base['input_binding_path']);assert sha(bind)==base['input_binding_sha256']==row['input_binding']['sha256'];rel=Path('control/input_bindings')/(digest+'.json');u.write_exact(root/rel,bind.read_bytes(),root);s['input_binding_path']=str(logical/rel)
  argv=copy.deepcopy(base['native_simulator_argv']);pos=[i+1 for i,t in enumerate(argv)if t=='-config'];assert len(pos)==4
  for i,j in enumerate(pos):argv[j]=configs[profile][i]['path']
  s['native_simulator_argv']=argv
  assert s['expected']==base['expected']==row['expected']and s['original_environment']==base['original_environment']and s['runtime_files']==base['runtime_files']and argv[0]==base['native_simulator_argv'][0]
  assert s['core_commit']==cm['fixed_core']and s['framework_commit']==cm['fixed_framework']and s['binary_sha256']==row['binary_sha256']
  links=[u.runtime_link(root,x)for x in s['runtime_files']];rel=Path('control/specs')/(cohort+'.json');raw=encoded(s);h=u.write_exact(root/rel,raw,root);u.write_exact(root/'control'/(cohort+'_SPEC.json'),raw,root)
  points.append({'cohort':cohort,'plan_id':row['plan_id'],'program':row['program'],'suite':row['suite'],'input_digest':digest,'cell':'DH','profile':profile,'structure_variant':profile,'downstream_profile':'P0','host_cpu':None,'canonical_spec_path':str(logical/rel),'canonical_spec_sha256':h,'spec_sha256':h,'expected':s['expected'],'estimated_peak_model_RAM_bytes':s['estimated_peak_model_RAM_bytes'],'limits':s['limits']})
  refs.append({'cohort':cohort,'plan_id':row['plan_id'],'source_candidate_matrix_sha256':dep['candidate_matrix_sha256'],'source_baseline_spec':{'path':d['baseline_spec_path'],'sha256':d['baseline_spec_sha256']},'DH_P0_reference':d['DH_reference'],'CH_P0_reference':d['CH_reference'],'new_spec_sha256':h,'effective_option_delta':delta,'input_binding_sha256':s['input_binding_sha256'],'resource_fields_path':str(resource_fields_path),'resource_fields_sha256':resource_fields_sha256,'runtime_links':links,'configured_lower_create_queue_bound':192,'strict_runtime_not_claimed_by_builder':True})
 matrix={'schema':'DTC_PERFV2_CODESIGN16_LAYOUT_R1_MATRIX_V1','request':REQ,'authority_commit':AUTHORITY,'count':16,'points':points,'variant_counts':{p:sum(r['profile']==p for r in points)for p in PROFILES},'Tag_or_other_scientific_points':0,'extra_canary_or_P0_reruns':0,'builder_scientific_registrations':0,'model_starts_by_builder':0}
 u.write_exact(root/'control/MATRIX.fixed.json',encoded(matrix),root)
 p0refs=[d[k]for d in dep['selected']for k in ['CH_reference','DH_reference']]
 u.write_exact(root/'control/P0_REFERENCE_INDEX.json',encoded({'references':p0refs,'no_P0_reruns':True,'source_candidate_matrix_sha256':dep['candidate_matrix_sha256']}),root)
 u.write_exact(root/'control/SPEC_BUILD_REFERENCE_TABLE.json',encoded({'schema':'DTC_PERFV2_CODESIGN16_LAYOUT_R1_SPEC_BUILD_REFERENCE_TABLE_V1','request':REQ,'rows':refs,'resource_fields_path':str(resource_fields_path),'resource_fields_sha256':resource_fields_sha256,'source_dependency_sha256':sha(D/'DEPENDENCY_PINS.json'),'all_pass':True,'registrations':0,'model_starts':0}),root)
 return {'status':'CPU_MATERIALIZATION_PASS_NO_NATIVE_START','request':REQ,'points':16,'logical_root':str(logical),'physical_output_root':str(root),'matrix_sha256':sha(root/'control/MATRIX.fixed.json'),'specs':{r['cohort']:r['spec_sha256']for r in points},'science_registrations':0,'model_starts':0}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--output-root',required=True,type=Path);ap.add_argument('--resource-fields',required=True,type=Path);ap.add_argument('--resource-fields-sha256',required=True);ap.add_argument('--logical-root',default=LOGICAL,type=Path);a=ap.parse_args();print(json.dumps(build(a.output_root,a.resource_fields,a.resource_fields_sha256,a.logical_root),sort_keys=True))


