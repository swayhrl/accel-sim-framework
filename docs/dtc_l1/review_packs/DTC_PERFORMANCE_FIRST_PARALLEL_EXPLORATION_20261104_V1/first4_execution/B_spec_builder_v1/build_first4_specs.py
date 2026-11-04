"""Materialize exact first4 specification/configuration files, never register or launch.
Root may invoke with --output-root /root/data/... only after independent gates.
CPU qualification invokes only a new sandbox under this package.
"""
from pathlib import Path,PurePosixPath
import argparse,json,hashlib,copy,shlex,os
D=Path(__file__).resolve().parent
REQ='DTC_PERF_FIRST_PHYS768_FIRST4_20261104_V1'
VAR='PHYS768_TAG64x8'
NAMES=['2DCONV','GEMM','MVT','BICG']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def encoded(v):return (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def read(p):return json.loads(Path(p).read_bytes())
def within(p,root):return p.resolve().is_relative_to(root.resolve())
def ensure_parent(parent,root):
 rel=Path(parent).relative_to(root);cur=root
 for part in rel.parts:
  assert part not in ['..',''];cur=cur/part
  if cur.exists()or cur.is_symlink():assert cur.is_dir()and within(cur,root),'SYMLINK_PARENT_OUTSIDE_OUTPUT_ROOT'
  else:
   assert within(cur.parent,root),'PARENT_OUTSIDE_OUTPUT_ROOT';cur.mkdir()
def write_exact(p,b,root):
 p=Path(p);ensure_parent(p.parent,root)
 assert within(p.parent,root),'SYMLINK_PARENT_OUTSIDE_OUTPUT_ROOT'
 if p.exists()or p.is_symlink():
  assert p.is_file()and p.read_bytes()==b,'EXISTING_OUTPUT_DIFFERS_NO_OVERWRITE:'+str(p)
 else:
  with p.open('xb')as f:f.write(b)
 return hashlib.sha256(b).hexdigest()
def runtime_link(root,record):
 rel=PurePosixPath(record['target']);assert not rel.is_absolute()and'..'not in rel.parts
 dst=root/str(rel);src=Path(record['actual_realpath']);assert sha(src)==record['sha256']
 if dst.exists()or dst.is_symlink():assert dst.resolve()==src.resolve()and sha(dst)==record['sha256']
 else:
  ensure_parent(dst.parent,root);assert within(dst.parent,root),'RUNTIME_PARENT_OUTSIDE_OUTPUT_ROOT';dst.symlink_to(src)
 return {'target':str(dst.relative_to(root)),'actual_realpath':str(src),'sha256':record['sha256']}
def supplied_options(configs):
 # Exact continuation-aware pure-text parser used by frozen A packet.
 tokens=[]
 for p in configs:tokens+=shlex.split(Path(p).read_text(),comments=True)
 out={};i=0
 while i<len(tokens):
  assert tokens[i].startswith('-'),'NON_OPTION_CONFIG_TOKEN';key=tokens[i];i+=1;vals=[]
  while i<len(tokens)and not tokens[i].startswith('-'):vals.append(tokens[i]);i+=1
  out[key]=[word for val in vals for word in val.split()]
 return out

def build(output_root,logical_root):
 output_root=Path(output_root).resolve();logical_root=Path(logical_root);output_root.mkdir(parents=True,exist_ok=True)
 deps=read(D/'DEPENDENCY_PINS.json')
 for x in deps['files']:assert sha(x['path'])==x['sha256'],'DEPENDENCY_SHA_MISMATCH:'+x['path']
 assert str(logical_root)==deps['logical_root']and deps['request']==REQ
 auth=read(deps['authority_path']);v=next(v for v in read(deps['variant_path'])['variants']if v['variant']==VAR);res=read(deps['resource_fields_path']);assert res['request']==REQ and res['budget']==4
 assert v['delta']=={'-gpgpu_dtc_l1_physical_lines':{'from':['640'],'to':['768']}}and not v['status'].startswith('CPU_PROGRESS_NEGATIVE')
 points=[];refs=[];checks=[];config_logical=[];config_physical=[];shared_env=Path('DTC/env/DH_'+VAR)
 for i,x in enumerate(v['configs']):
  src=Path(x['path']);assert sha(src)==x['sha256'];rel=shared_env/('config-'+str(i)+'.config');h=write_exact(output_root/rel,src.read_bytes(),output_root);config_logical.append({'path':str(logical_root/rel),'sha256':h});config_physical.append(output_root/rel)
 parsed=supplied_options(config_physical);assert parsed==v['effective_supplied_options']
 p0refs=[]
 for name in NAMES:
  d=next(x for x in deps['selected']if x['program']==name);base=read(d['baseline_spec_path']);assert sha(d['baseline_spec_path'])==d['baseline_spec_sha256'];dr=d['DH_reference'];cr=d['CH_reference'];digest=dr['input_digest'];rp=next(x for x in res['points']if x['program']==name);assert rp['input_digest']==digest and rp['variant']==VAR
  original=Path(dr['source_RESULT_path']);rv=read(original);assert original.parents[1]/'control/specs'/(rv['cohort']+'.json')==Path(d['baseline_spec_path']);assert dr['source_profile']=='P0'and dr['source_cell']=='DH'and base['expected_options']==dr['effective_options'];assert len(base['expected_options'])==270
  cohort='E2-DTCPF4-'+digest[:16]+'-DH-PHYS768-V1';s=copy.deepcopy(base);s.update(schema='DTC_PERFFIRST_FIRST4_SPEC_V1',cohort=cohort,request=REQ,cell='DH',profile=VAR,structure_variant=VAR,downstream_profile='P0',host_cpu=None,performance_scope='PERFFIRST_FIRST4_DH_ONLY_NEVER_ORIGINAL_OR_IR_R2',estimated_peak_model_RAM_bytes=rp['estimated_peak_model_RAM_bytes'],limits=copy.deepcopy(rp['limits']),configs=copy.deepcopy(config_logical),source_kind='FROZEN_FIRST8_WHOLE_DECLARED_TRACE_PERFORMANCE_ONLY')
  s['expected_options']['-gpgpu_dtc_l1_physical_lines']=['768'];dif={k:{'from':base['expected_options'].get(k),'to':s['expected_options'].get(k)}for k in set(base['expected_options'])|set(s['expected_options'])if base['expected_options'].get(k)!=s['expected_options'].get(k)};assert dif==v['delta'];assert all(s['expected_options'].get(k)==vv for k,vv in parsed.items())
  binding=Path(base['input_binding_path']);assert sha(binding)==base['input_binding_sha256']==dr['input_binding']['sha256'];brel=Path('control/input_bindings')/(digest+'.json');write_exact(output_root/brel,binding.read_bytes(),output_root);s['input_binding_path']=str(logical_root/brel)
  argv=copy.deepcopy(base['native_simulator_argv']);positions=[i+1 for i,x in enumerate(argv)if x=='-config'];assert len(positions)==4
  for i,pos in enumerate(positions):argv[pos]=config_logical[i]['path']
  s['native_simulator_argv']=argv;assert argv[0]==base['native_simulator_argv'][0]and s['expected']==base['expected']==dr['expected'];assert s['original_environment']==base['original_environment']and s['runtime_files']==base['runtime_files'];assert s['core_commit']==auth['build']['core']and s['framework_commit']==auth['build']['framework']and s['binary_sha256']==auth['build']['binary_sha256'];assert all(type(x)is int and x>0 for x in s['limits'].values())and s['limits']['max_process_tree_vms_bytes']>=s['limits']['max_process_tree_rss_bytes']
  links=[runtime_link(output_root,x)for x in s['runtime_files']]
  rel=Path('control/specs')/(cohort+'.json');raw=encoded(s);h=write_exact(output_root/rel,raw,output_root);write_exact(output_root/'control'/(cohort+'_SPEC.json'),raw,output_root)
  point={'cohort':cohort,'input_digest':digest,'program':name,'suite':base['suite'],'cell':'DH','profile':VAR,'structure_variant':VAR,'downstream_profile':'P0','host_cpu':None,'canonical_spec_path':str(logical_root/rel),'canonical_spec_sha256':h,'spec_sha256':h,'expected':s['expected'],'estimated_peak_model_RAM_bytes':s['estimated_peak_model_RAM_bytes'],'limits':s['limits']};points.append(point);p0refs.extend([cr,dr]);refs.append({'program':name,'cohort':cohort,'new_spec_sha256':h,'new_spec_logical_path':str(logical_root/rel),'baseline_spec_path':d['baseline_spec_path'],'baseline_spec_sha256':d['baseline_spec_sha256'],'baseline_DH_RESULT_path':dr['source_RESULT_path'],'baseline_DH_RESULT_sha256':dr['source_RESULT_sha256'],'baseline_CH_RESULT_path':cr['source_RESULT_path'],'baseline_CH_RESULT_sha256':cr['source_RESULT_sha256'],'full_effective_option_n':len(s['expected_options']),'effective_option_delta':dif,'configs':config_logical,'input_binding_source':str(binding),'input_binding_sha256':s['input_binding_sha256'],'expected':s['expected'],'runtime_files_preserved_n':len(s['runtime_files']),'runtime_links':links,'resource_fields_source':deps['resource_fields_path'],'resources_exact_copy':True,'native_API_contract':'perf4_native.canonical fields DH/profile=structure,downstreamP0,host_cpuNone; strict runtime call not invoked'});checks.append({'program':name,'option270_onlyPhysicalDelta':True,'config4_exact_A_SHA':True,'inputbinding_exactSHA':True,'expected_binary_libraries_environment_preserved':True,'resource_A_fields_exact':True,'cohort_API_fields_valid':True,'no_model_started':True})
 assert len(points)==4 and{p['program']for p in points}==set(NAMES)and all(p['structure_variant']==VAR for p in points)
 matrix={'schema':'DTC_PERFFIRST_FIRST4_MATRIX_V1','request':REQ,'points':points,'count':4,'Tag_HOLD_or_other_variants_admitted':False,'model_starts_by_builder':0};write_exact(output_root/'control/MATRIX.json',encoded(matrix),output_root);write_exact(output_root/'control/P0_REFERENCE_INDEX.json',encoded({'references':p0refs,'same_P0_legal_reuse_only':True,'no_P0_reruns':True}),output_root);write_exact(output_root/'control/SPEC_BUILD_REFERENCE_TABLE.json',encoded({'schema':'DTC_PERFFIRST_FIRST4_SPEC_BUILD_REFERENCES_V1','source_dependency_manifest_sha256':sha(D/'DEPENDENCY_PINS.json'),'logical_root':str(logical_root),'output_root':str(output_root),'rows':refs,'checks':checks,'all_pass':True,'registration_or_dispatch':False}),output_root)
 return {'status':'FIRST4_SPEC_CONFIG_CPU_BUILD_PASS_NO_START','output_root':str(output_root),'logical_root':str(logical_root),'point_n':4,'spec_sha256':{p['cohort']:p['spec_sha256']for p in points},'matrix_sha256':sha(output_root/'control/MATRIX.json'),'source_dependency_manifest_sha256':sha(D/'DEPENDENCY_PINS.json'),'new_models':0,'registrations':0}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--output-root',required=True,type=Path);ap.add_argument('--logical-root',default='/root/data/dtc_perf_first_parallel_exploration_20261104_v1',type=Path);args=ap.parse_args();print(json.dumps(build(args.output_root,args.logical_root),sort_keys=True))
