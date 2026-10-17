"""Normalize qualified local producer modes only after fresh eleven-gate closure."""
import argparse,copy,json,shutil,subprocess
from pathlib import Path
from registry import Registry,write_json,PARALLEL
from run import digest,require,GATES,asset_manifest,content_hash
from local_ideal_scope import IDENTITY,PROFILE_BITS
from qualify_r0_1 import check_directed_log
from package_r0 import freeze_checksums

REPO=Path(__file__).resolve().parents[3]
H=REPO/'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5'
OUT=Path('/workspace/ep_l2_potential20261017_lane5_results')
ORIGINAL=Path('/workspace/results/ep_l2_ft20261016/lane5_a1_b1_formal_preparation_r1/specs')


def main():
 h=json.loads(Path('/workspace/ep_l2_ft20261016_shared/lane1/PARALLEL_LOCAL_IDEALS_RELEASE_r1.json').read_text());pub=h['publication'];native=json.loads((OUT/'LOCAL_IDEAL_NATIVE_OFF_RESULT_r1.json').read_text());ind=json.loads((OUT/'independent_local_ideals_runtime_r1/RECEIPT.json').read_text());guards=json.loads((OUT/'local_mode_guards_r1/RECEIPT.json').read_text());effective=json.loads((OUT/'local_effective_replay_r1/RECEIPT.json').read_text())
 require(native['status']=='COMPLETE_VALID' and native['off_equivalence']=='PASS' and native['identity']['binary_sha256']==h['binary_sha256'],'New allOFF gate not passed')
 require(guards['status']=='ALL8_EXPECTED_NATIVE_REJECTIONS_PASS' and effective['status']=='ALL6_ACTUAL_NATIVE_PROFILE_CONSTRUCTORS_PASS','New mode/config gates incomplete')
 require(ind['status']=='AFFECTED_NEW_RUNTIME_ASSERTIONS_PASS_ELEVEN_AND_MODE_REVIEW_PENDING' and len(ind['tests'])==27,'Affected new-runtime checks incomplete')
 for row in ind['tests']:
  require(row['status']=='ACTUAL_ASSERTIONS_PASS' and row['exit_code']==0 and digest(row['log'])==row['sha256'],'Changed actual independent evidence')
  if not row['case'].startswith('ideal_'):
   case={'case':row['case'],'argv':row['command'][1:]}
   if 'clock' in row['case']:case['required_clock']={'offset':0 if row['case'].endswith('_0') else 4096}
   check_directed_log(case,Path(row['log']).read_text())
 for row in guards['rows']+effective['rows']:require(digest(row['log'])==row['sha256'],'Actual native constructor/guard evidence changed')
 require(Registry().snapshot()['runs'][native['run_key']]['status']=='COMPLETE_VALID','Native canary not canonical complete')
 raw=Path(h['producer_manifest_path']).read_bytes();require(raw==subprocess.check_output(['git','show',pub+':'+h['producer_manifest_repository_path']],cwd=REPO) and digest(h['binary'])==IDENTITY['binary_sha256'],'Producer manifest/runtime changed');manifest=json.loads(raw)
 pack=REPO/'docs/ep_l2/review_packs/FT20261017_LANE5_PARALLEL_LOCAL_IDEALS_ELEVEN_GATES_r1';require(not pack.exists(),'Preserve frozen independent revision');pack.mkdir()
 for dirname in ['independent_local_ideals_runtime_r1','local_mode_guards_r1','local_effective_replay_r1']:
  shutil.copytree(OUT/dirname,pack/dirname)
 for name,source in [('NATIVE_OFF_RESULT.json',OUT/'LOCAL_IDEAL_NATIVE_OFF_RESULT_r1.json'),('RETAINED_INPUT_SCOPE.json',OUT/'LOCAL_IDEAL_INPUT_SCOPE_REUSE_r1.json'),('LOCAL_IDEAL_PRODUCER_MANIFEST.json',Path(h['producer_manifest_path'])),('LOCAL_IDEAL_PRODUCER_RECEIPT.json',Path(h['producer_receipt_path'])),('AUTHOR_BUILD_RECEIPT.json',Path('/workspace/ep_l2_parallel_lane1/local_ideals_release_r4/AUTHOR_BUILD_RECEIPT.json'))]:shutil.copyfile(source,pack/name)
 for name in ['local_ideal_scope.py','parse_local_ideal_terminal.py']:shutil.copyfile(REPO/'util/ep_l2/ft_lane5'/name,pack/name)
 # This new source is reviewed from its actual assertions, not the old7b certificate.
 cases={r['case']:r for r in ind['tests']};selected={
  'old_all_off_equivalence':['NATIVE_OFF_RESULT.json'],
  'mode_legality':['local_mode_guards_r1/RECEIPT.json','local_effective_replay_r1/RECEIPT.json'],
  'physical_bank_clock':[n for n in cases if 'clock' in n],
  'memcpy_payload_identity':[n for n in cases if n.startswith('host_prefill')]+['ideal_host_prefill_reference','ideal_host_prefill_partition'],
  'finite_wbuf':['partition_1_16','partition_2_16','ft_directed','ideal_wb'],
  'requester_exact_once':['ft_directed','a1_1_16','a1_2_16','ideal_meta_integrated','ideal_meta_integrated_B16'],
  'sector_reference_data':['ft_directed','b1-read-first','b1-atomic-first','b1-version-only','ideal_wb','ideal_read_hit','ideal_read_hit_B16'],
  'stale_fill':['host_prefill_1_16','host_prefill_2_16','a1_1_16','a1_2_16','ideal_host_prefill_partition'],
  'resource_closure':list(cases),
  'wb_lifecycle':['partition_1_16','partition_2_16','ft_directed','ideal_wb'],
  'bank_service':[n for n in cases if 'clock' in n]+['ideal_wb','ideal_read_hit']}
 require(set(selected)==GATES,'Eleven gate mapping incomplete')
 review={'status':'ALL_ELEVEN_NEW_SOURCE_GATES_PASS','source_identity':IDENTITY,'producer_publication':pub,'gates':{g:{'status':'PASS','production_driven':True,'actual_evidence':names} for g,names in selected.items()},'new_actual_assertion_processes':27,'actual_constructor_profiles':6,'actual_invalid_modes':8,'new_full_application_canaries':1,'native_off_metrics':native['metrics'],'native_off_csv_hashes':native['seven_csv_sha256'],'retained_input_proof':'Explicit identical10 source trees/objects plus retained full body/opcode/legacy proofs; no report retagged. New host/reference cases independently executed.','scope':'Symbolic32B physical data and byte-reference localread semantics. I_WB pays dynamic extra backing and realcopy/bank/WAD/lower services; I_META lifts only3 metadata capacities; I_READ_HIT retainsROP/bank/response/dependency waits. NoALL_DATA, numericalSASS/ALU, strong-static orPPA qualification.'};write_json(pack/'ELEVEN_GATE_REVIEW.json',review)
 profiles={}
 for name,row in manifest['profiles'].items():
  name='U_OFF' if name=='U_WB16_OFF' else name
  configs=asset_manifest(row['configs'],ordered=True);require(configs==row['ordered_config_manifest'],'Official config bytes changed')
  profiles[name]={'ordered_configs':configs,'auxiliary_assets':[],'environment':row['environment'],'runtime_config_sha256':row['runtime_config_sha256'],'effective_options':__import__('headroom_config').options([v['path'] for v in row['configs']]),'feature_vector':row['feature_vector'],'ideal_vector':row['ideal_vector']}
  require(content_hash({'ordered_configs':configs,'auxiliary_assets':[],'environment':row['environment']})==row['runtime_config_sha256'],'Actual ordered config hash differs')
 shared_evidence=[{'path':str(p),'sha256':digest(p)} for p in sorted(pack.rglob('*')) if p.is_file()];specdir=H/'parallel_local_ideal_specs_r1';specdir.mkdir(exist_ok=False);scope_tool={'path':str(pack/'local_ideal_scope.py'),'sha256':digest(pack/'local_ideal_scope.py')};parser={'path':str(pack/'parse_local_ideal_terminal.py'),'sha256':digest(pack/'parse_local_ideal_terminal.py')};source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip();original_proof=json.loads((ORIGINAL/'FWT_7_21_B16_BANKED.json').read_text())['native_legacy_semantic_proof'];cells=Registry().snapshot()['campaigns'][PARALLEL]['seed_cells'];groups={'ORDINARY':[],'LEGACY':[]};paths={k:H/('PARALLEL_LOCAL_IDEALS_'+k+'_INDEPENDENTLY_QUALIFIED_r1.json') for k in groups}
 for cell in cells:
  if cell['condition']!='H0' or cell['mode'] not in PROFILE_BITS:continue
  profile=cell['mode'];workload=cell['workload_alias'];scope='LEGACY' if workload in ['convolutionSeparable','FWT_7_21'] else 'ORDINARY';mode='U_WB16' if profile=='U_OFF' else 'B16_BANKED';producer_name='U_WB16_OFF' if profile=='U_OFF' else profile;row=manifest['profiles'][producer_name];spec=copy.deepcopy(json.loads((ORIGINAL/(workload+'_'+mode+'.json')).read_text()));spec.update(experiment_id=PARALLEL,regime='H0',profile=profile,cell_id=cell['cell_id'],scientific_scope='LOCAL_IDEAL_NATIVE_V1',scope_tool=scope_tool,parser=parser,qualified_release=str(paths[scope]),binary=h['binary'],result_root=str(OUT),runner_tooling_source_commit=source,configs=[{'name':v['name'],'path':v['path']} for v in row['configs']])
  spec['identity'].update(IDENTITY,feature_vector=row['feature_vector'],ideal_vector=row['ideal_vector'],runtime_config_sha256=row['runtime_config_sha256'])
  if scope=='LEGACY':spec['native_legacy_semantic_proof']=original_proof
  file=specdir/(cell['cell_id']+'_'+workload+'_'+profile+'.json');write_json(file,spec);groups[scope].append(str(file))
 for scope,files in groups.items():
  q=copy.deepcopy(json.loads((H/('R0_1_A1_B1_LEGACY_TRACE_INDEPENDENTLY_QUALIFIED_r2.json' if scope=='LEGACY' else 'R0_1_A1_B1_INDEPENDENTLY_QUALIFIED.json')).read_text()));q.update(IDENTITY,producer_publication_commit=pub,release_name='LOCAL_IDEALS_'+scope+'_r1',qualified_feature_vectors=[r['feature_vector'] for r in profiles.values()],qualified_modes=[{'profile':n,'feature_vector':r['feature_vector'],'ideal_vector':r['ideal_vector']} for n,r in profiles.items()],retained_input_scope={'path':str(pack/'RETAINED_INPUT_SCOPE.json'),'sha256':digest(pack/'RETAINED_INPUT_SCOPE.json')})
  q.update(coordination_commit='a9ab796f0c905d99eb1ffa3d02ea9305ce0bc900',TVD_RO_Ideal_qualification='LOCAL_IDEALS_ONLY_TVD_RO_ALL_DATA_NOT_INCLUDED',data_correctness_scope='SYMBOLIC_SECTOR_AND_LOCAL_BYTE_REFERENCE_NOT_NUMERIC_SASS')
  if 'input_adapter_revision' in q:q['input_adapter_revision'].update(runtime_gates_source_binary_config_unchanged=False,new_runtime_all_eleven_gates_requalified=True,retained_input_scope_sha256=q['retained_input_scope']['sha256'])
  q['gates']={g:{'status':'PASS','production_driven':True,'evidence_path':str(pack/'ELEVEN_GATE_REVIEW.json'),'evidence_sha256':digest(pack/'ELEVEN_GATE_REVIEW.json')} for g in GATES}
  cfg={'status':'INDEPENDENT_CONFIG_PASS','qualification_kind':'LOCAL_IDEAL_NATIVE_V1','coordination_commit':'a9ab796f0c905d99eb1ffa3d02ea9305ce0bc900','experiment_id':PARALLEL,'regime':'H0','identity':IDENTITY,'profiles':profiles,'evidence':shared_evidence,'spec_paths':files,'producer_publication':pub,'producer_publication_verified':True,'independent_affected_production_pass':True,'all_eleven_gates_passed':True,'native_all_off_equivalence':'PASS','independent_mode_semantics_passed':True};cp=pack/('INDEPENDENT_CONFIG_REVIEW_'+scope+'.json');write_json(cp,cfg);q['downstream_config_qualification']={'path':str(cp),'sha256':digest(cp)};write_json(paths[scope],q)
 write_json(pack/'SPEC_INDEX.json',groups);freeze_checksums(pack);print(json.dumps({'status':'NEW_LOCAL_RUNTIME11_AND6_PROFILES_INDEPENDENTLY_QUALIFIED_PENDING_CURRENT_V2','scopes':{k:len(v) for k,v in groups.items()},'new_seed_apps':0,'canary_counted':1}))
if __name__=='__main__':main()
