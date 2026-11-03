"""Read-only Stage II-A first16 pairing. Never dispatches, registers or changes source evidence."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,math,pathlib,statistics
HERE=pathlib.Path(__file__).resolve().parent
METRICS=('S_CH','S_DH','R','I','R_P0')
QUAL_FLAGS=('strict_pass','actual_input_verified','actual_build_verified','actual_effective_options_verified','natural_exit_verified','true164_archive_verified','native_restore_verified')
SOURCE_KINDS=('RESULT','SPEC','STRICT','ARCHIVE_RECEIPT','NATIVE_RESTORE')
def canonical(d):return json.dumps(d,sort_keys=True,separators=(',',':')).encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def read_pinned(ref):
 p=pathlib.Path(ref['path']);b=p.read_bytes()
 if digest(b)!=ref['sha256']:raise ValueError('SOURCE_SHA_MISMATCH:'+str(p))
 return json.loads(b)
def load_statistics(base=HERE):
 path=base/'contract/qualification_tools/paired_statistics.py'
 pins=json.loads((base/'CONTRACT_SOURCE_PINS.json').read_text())
 pin=next(x for x in pins if x['local_path']=='contract/qualification_tools/paired_statistics.py')
 if digest(path.read_bytes())!=pin['sha256']:raise ValueError('FIXED_STATISTICS_SOURCE_DRIFT')
 spec=importlib.util.spec_from_file_location('fixed_stage_iia_statistics',path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def validate_new(row,expected,old):
 if row.get('accepted') is not True:raise ValueError('NOT_ACCEPTED')
 fields={'program':expected['program'],'input_digest':expected['input_digest'],'design':'CH','profile':expected['profile'],'cohort':expected['cohort'],'source_role':'STAGEII_AUTHORIZED_CH','request':expected['request'],'input_binding_sha':expected['input_binding']['sha256'],'roi_fingerprint':expected['expected_roi_fingerprint'],'downstream_fingerprint':expected['downstream_fingerprint'],'build_fingerprint':old['build_fingerprint']}
 for k,v in fields.items():
  if row.get(k)!=v:raise ValueError('NEW_CH_IDENTITY_MISMATCH:'+k)
 if row.get('build')!=old['build']:raise ValueError('NEW_CH_BUILD_OBJECT_MISMATCH')
 if row.get('effective_options')!=expected['effective_options']:raise ValueError('NEW_CH_EFFECTIVE_OPTIONS_MISMATCH')
 if row.get('config_sha256')!=[x['sha256'] for x in expected['configs']]:raise ValueError('NEW_CH_CONFIG_BYTES_MISMATCH')
 if row.get('expected_ROI')!=expected['expected']:raise ValueError('NEW_CH_ROI_MISMATCH')
 if any(row.get('qualification',{}).get(k) is not True for k in QUAL_FLAGS):raise ValueError('NEW_CH_QUALIFICATION_INCOMPLETE')
 refs=row.get('sources',{})
 if set(refs)!=set(SOURCE_KINDS):raise ValueError('NEW_CH_SOURCE_REFS_INCOMPLETE')
 for kind,ref in refs.items():
  if not isinstance(ref.get('sha256'),str) or len(ref['sha256'])!=64 or any(x not in '0123456789abcdef' for x in ref['sha256']):raise ValueError('NEW_CH_SOURCE_SHA_MISSING:'+kind)
 if refs['RESULT']['sha256']!=row.get('RESULT_sha256'):raise ValueError('NEW_CH_RESULT_SHA_DISAGREES')
 return row

def evaluate(contract,baselines,observations):
 st=load_statistics();expected=contract['expected_inputs'];wanted={(x['input_digest'],x['profile']):x for x in contract['expected_CH']}
 if len(wanted)!=16 or len(expected)!=8 or len(set(expected))!=8:raise ValueError('FIXED_FIRST16_CONTRACT_SHAPE')
 b={(r['input_digest'],r['design'],r['profile']):r for r in baselines['references']}
 if len(b)!=32 or any(x not in expected for x,_,_ in b):raise ValueError('BASELINE_REFERENCE_SCOPE')
 seen={};extra=[]
 for row in observations:
  key=(row.get('input_digest'),row.get('profile'))
  if key not in wanted:extra.append({'input_digest':row.get('input_digest'),'profile':row.get('profile'),'status':'OUTSIDE_FIRST16_REJECTED'});continue
  if key in seen:raise ValueError('DUPLICATE_FIRST16_RESULT_IDENTITY')
  seen[key]=row
 metrics={f:{m:{} for m in METRICS} for f in ['F128','F256']};out=[]
 for key,e in wanted.items():
  d,f=key;ch0=b[d,'CH','P0'];dh0=b[d,'DH','P0'];dhf=b[d,'DH',f];new=seen.get(key)
  row={'program':e['program'],'suite':e['suite'],'input_digest':d,'profile':f,'cohort':e['cohort'],'CH_P0':ch0['cycles'],'CH_F':None,'DH_P0':dh0['cycles'],'DH_F':dhf['cycles'],'source_refs':{'CH_P0':{'path':ch0['RESULT_path'],'sha256':ch0['RESULT_sha256']},'DH_P0':{'path':dh0['RESULT_path'],'sha256':dh0['RESULT_sha256']},'DH_F':{'path':dhf['RESULT_path'],'sha256':dhf['RESULT_sha256']}},'DH_self_response_known':dh0['cycles']/dhf['cycles'],'status':'NOT_OBSERVED','metrics':{m:None for m in METRICS}}
  if new:
   row['observed_status']=new.get('status');row['source_refs']['CH_F']=new.get('sources',{}).get('RESULT')
   if new.get('accepted') is True:
    try:
     validate_new(new,e,ch0);values=st.quadruple(ch0,new,dh0,dhf)
     row.update(CH_F=new['cycles'],status='ACCEPTED_MATCHED_QUADRUPLE',metrics=values)
     for m,v in values.items():metrics[f][m][d]=v
    except (ValueError,KeyError,TypeError) as exc:row.update(status='REJECTED_IDENTITY_OR_QUALIFICATION',reason=str(exc))
   else:row.update(status=new.get('status','NOT_ACCEPTED'),reason=new.get('reason','pending/negative is not performance; no imputation'))
  out.append(row)
 agg={f:{m:st.summarize(v,expected) for m,v in measures.items()} for f,measures in metrics.items()}
 common=sorted(set(metrics['F128']['I'])&set(metrics['F256']['I']))
 same={f:{m:st.summarize({d:metrics[f][m][d] for d in common},expected) for m in METRICS} for f in ['F128','F256']}
 direct={'CH_F128_over_F256':{},'DH_F128_over_F256':{},'I_F256_over_F128':{}}
 by={(r['input_digest'],r['profile']):r for r in out}
 for d in common:
  a,z=by[d,'F128'],by[d,'F256'];direct['CH_F128_over_F256'][d]=a['CH_F']/z['CH_F'];direct['DH_F128_over_F256'][d]=a['DH_F']/z['DH_F'];direct['I_F256_over_F128'][d]=z['metrics']['I']/a['metrics']['I']
 return {'schema':'DTC_STAGEIIA_FIRST16_READONLY_ANALYSIS_V1','scientific_population':'FIRST8_PREDECLARED_SUBSET_NOT_35_OR_CORE32','fixed_plan_commit':contract['fixed_plan_commit'],'expected_programs':contract['programs'],'expected_inputs':expected,'rows':out,'per_profile_available_paired':agg,'common_F128_F256_population':common,'common_F128_F256_metrics':same,'direct_F_comparison':{k:st.summarize(v,expected) for k,v in direct.items()},'out_of_scope_rejected':extra,'no_best_per_program_selection':True,'no_missing_imputation':True,'no_IR_R2_EP_PQ_PS_substitution':True,'CH_DH_equal_downstream_not_equal_L1_area':True,'new_models_started':0,'registrations':0}

def verify_original_sources(base):
 for row in base['references']:
  b=pathlib.Path(row['RESULT_path']).read_bytes()
  if digest(b)!=row['RESULT_sha256']:raise ValueError('ORIGINAL_RESULT_DRIFT')
  if digest(pathlib.Path(row['spec_path']).read_bytes())!=row['spec_sha256']:raise ValueError('ORIGINAL_SPEC_DRIFT')
  if digest(pathlib.Path(row['input_binding_path']).read_bytes())!=row['input_binding_sha']:raise ValueError('ORIGINAL_INPUT_BINDING_DRIFT')
  result=json.loads(b)
  if result.get('cycles')!=row['cycles'] or result.get('proof',{}).get('performance_accepted') is not True:raise ValueError('ORIGINAL_ACCEPTANCE_DRIFT')

def load_root_index(path,sha256):
 b=pathlib.Path(path).read_bytes()
 if digest(b)!=sha256:raise ValueError('ROOT_RESULT_INDEX_SHA_MISMATCH')
 index=json.loads(b)
 if index.get('schema')!='DTC_STAGEIIA_FIRST16_ANALYSIS_OBSERVATIONS_V1':raise ValueError('ROOT_RESULT_INDEX_SCHEMA')
 if index.get('request')!='DTC_STAGE_IIA_FIRST16_CH_MATCH_20261104_V1':raise ValueError('ROOT_RESULT_INDEX_REQUEST')
 for row in index['observations']:
  if row.get('accepted') is not True:continue
  data={kind:read_pinned(ref) for kind,ref in row.get('sources',{}).items()}
  result=data['RESULT'];spec=data['SPEC'];proof=result.get('proof',{})
  for k,v in [('cohort',row['cohort']),('uuid',row['uuid']),('cycles',row['cycles'])]:
   if result.get(k)!=v:raise ValueError('ROOT_RESULT_SOURCE_DISAGREES:'+k)
  if proof.get('performance_accepted') is not True or proof.get('cycles')!=row['cycles']:raise ValueError('ROOT_RESULT_NOT_PERFORMANCE_ACCEPTED')
  for k,v in [('input_digest',row['input_digest']),('cell','CH'),('effective_options',row['effective_options'])]+[(k,row['build'][k]) for k in ['core_commit','framework_commit','binary_sha256']]:
   if proof.get(k)!=v:raise ValueError('ROOT_STRICT_PROOF_SOURCE_DISAGREES:'+k)
  actual_profile=proof.get('profile',proof.get('downstream_profile'))
  if actual_profile!=row['profile']:raise ValueError('ROOT_STRICT_PROFILE_SOURCE_DISAGREES')
  for k,v in [('cohort',row['cohort']),('input_digest',row['input_digest']),('cell','CH'),('profile',row['profile']),('request',row['request']),('input_binding_sha256',row['input_binding_sha']),('expected',row['expected_ROI']),('expected_options',row['effective_options'])]:
   if spec.get(k)!=v:raise ValueError('ROOT_SPEC_SOURCE_DISAGREES:'+k)
  # Root is responsible for defining strict/archival semantics in this SHA-pinned qualified index.
  # Consumer never declares acceptance from raw printed cycles or a source filename.
 return index['observations']

def markdown(report):
 lines=['# Stage II-A first16 matched CH/DH results','','Population: predeclared first8 subset; no full35/core32 GM claim. Ratios>1 indicate improvement for S_CH/S_DH/I, lower DTC cycles for R.','', '| Program | F | CH P0 | CH F | DH P0 | DH F | S_CH | S_DH | R | I | Status |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|']
 for r in report['rows']:
  fmt=lambda x:'MISSING' if x is None else f'{x:.6f}' if isinstance(x,float) else str(x)
  lines.append('| '+' | '.join([r['program'],r['profile']]+[fmt(r[k]) for k in ['CH_P0','CH_F','DH_P0','DH_F']]+[fmt(r['metrics'][k]) for k in ['S_CH','S_DH','R','I']]+[r['status']])+' |')
 lines+=['','F128/F256 direct comparison uses only the common accepted input population; see JSON for exact digests, each metric GM, missing IDs, positive/zero/negative counts. New CH missing/negative rows remain visible. No IR/R2/EP/PQ/PS replacement, no source result mutation.','']
 return '\n'.join(lines)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--contract',type=pathlib.Path,default=HERE/'ANALYSIS_CONTRACT.json');ap.add_argument('--baselines',type=pathlib.Path,default=HERE/'BASELINE_REFERENCES.json');ap.add_argument('--root-index',type=pathlib.Path);ap.add_argument('--root-index-sha256');ap.add_argument('--output-dir',type=pathlib.Path,required=True);a=ap.parse_args()
 contract=json.loads(a.contract.read_text());base=json.loads(a.baselines.read_text());verify_original_sources(base)
 if bool(a.root_index)!=bool(a.root_index_sha256):raise ValueError('ROOT_INDEX_AND_SHA_REQUIRED_TOGETHER')
 obs=load_root_index(a.root_index,a.root_index_sha256) if a.root_index else []
 report=evaluate(contract,base,obs);report['new_source_input_index']=({'path':str(a.root_index),'sha256':a.root_index_sha256} if a.root_index else None)
 out=a.output_dir.resolve();allowed=HERE.resolve()
 if out!=allowed and allowed not in out.parents:raise ValueError('OUTPUT_MUST_STAY_IN_AGENT_B_DIRECTORY')
 out.mkdir(parents=True,exist_ok=True)
 for name,data in [('RESULTS.json',(json.dumps(report,indent=2)+'\n').encode()),('RESULTS.md',markdown(report).encode())]:
  p=out/name
  if p.exists() and p.read_bytes()!=data:raise ValueError('IMMUTABLE_OUTPUT_EXISTS_USE_NEW_SNAPSHOT_DIRECTORY')
  p.write_bytes(data)
 print(json.dumps({'rows':len(report['rows']),'accepted_quads':sum(r['status']=='ACCEPTED_MATCHED_QUADRUPLE' for r in report['rows']),'common_both_F':len(report['common_F128_F256_population']),'output':str(out)}))
if __name__=='__main__':main()
