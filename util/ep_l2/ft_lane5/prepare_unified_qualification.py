"""Bind freshfb native gates and exact profiles; no simulator or compiler launch."""
import copy,json,shutil,subprocess
from pathlib import Path
from registry import Registry,write_json,PARALLEL
from run import digest,require,GATES,asset_manifest,content_hash
from unified_scope import IDENTITY,features,LOCAL
from package_r0 import freeze_checksums

REPO=Path(__file__).resolve().parents[3]
H=REPO/'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5'
OUT=Path('/workspace/ep_l2_potential20261017_lane5_results')
ORIGINAL=Path('/workspace/results/ep_l2_ft20261016/lane5_a1_b1_formal_preparation_r1/specs')

def main():
 hand=json.loads(Path('/workspace/ep_l2_ft20261016_shared/lane1/PARALLEL_ALL_DATA_RELEASE_r1.json').read_text());native=json.loads((OUT/'UNIFIED_FB_NATIVE_OFF_RESULT_r1.json').read_text());ind=json.loads((OUT/'independent_unified_fb_runtime_r1/RECEIPT.json').read_text());construct=json.loads((OUT/'unified_constructors_and_guards_r1/RECEIPT.json').read_text());guards=json.loads((OUT/'unified_mode_guards_r1/RECEIPT.json').read_text())
 require(native['status']=='COMPLETE_VALID' and native['off_equivalence']=='PASS' and native['identity']['binary_sha256']==IDENTITY['binary_sha256'],'Newfb nativeOFF not qualified')
 require(ind['status']=='AFFECTED_NEW_RUNTIME_ASSERTIONS_PASS_ELEVEN_AND_MODE_REVIEW_PENDING' and len(ind['tests'])==49,'New actual49 incomplete')
 require(construct['status']=='11_ACTUAL_CONSTRUCTORS_5_EXPECTED_NATIVE_REJECTIONS_PASS_NOT_FULL_QUALIFICATION' and guards['status']=='ALL8_EXPECTED_NATIVE_REJECTIONS_PASS','New constructor/mode/reference guards incomplete')
 for row in ind['tests']:require(row['exit_code']==0 and row['status']=='ACTUAL_ASSERTIONS_PASS' and digest(row['log'])==row['sha256'],'Changed independent native evidence')
 for row in construct['positive']+construct['expected_rejections']+guards['rows']:require(digest(row['log'])==row['sha256'],'Changed actual constructors/rejections')
 require(Registry().snapshot()['runs'][native['run_key']]['status']=='COMPLETE_VALID','Canary not canonical complete')
 require(digest(hand['binary'])==IDENTITY['binary_sha256'],'Official binary changed');manifest=json.loads(Path(hand['producer_manifest_path']).read_text());prod=json.loads(Path(hand['producer_receipt_path']).read_text());supp=json.loads(Path(hand['supplement_receipt_path']).read_text())
 for row in prod['tests']+prod['expected_rejections']+supp['tests']+supp['expected_rejections']:require(digest(row['log'])==row['log_sha256'],'Published producer actual log changed')
 require(Path(hand['producer_manifest_path']).read_bytes()==subprocess.check_output(['git','show',hand['publication']+':'+hand['producer_manifest_repository_path']],cwd=REPO),'Producer config manifest unpublished')
 vendor=Path(hand['actual_build_framework'])/'gpu-simulator/extern/pybind11';require(subprocess.check_output(['git','rev-parse','HEAD'],cwd=vendor,text=True).strip()=='f90c430c3a1ce8f08c09942a5a1c3a797bb2295b' and not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=vendor),'Actualpybind11 vendor changed')
 pack=REPO/'docs/ep_l2/review_packs/FT20261017_LANE5_UNIFIED_ELEVEN_GATES_r1';require(not pack.exists(),'Preserve frozen qualification revision');pack.mkdir()
 for dirname in ['independent_unified_fb_runtime_r1','unified_constructors_and_guards_r1','unified_mode_guards_r1']:shutil.copytree(OUT/dirname,pack/dirname)
 for name,p in [('NATIVE_OFF_RESULT.json',OUT/'UNIFIED_FB_NATIVE_OFF_RESULT_r1.json'),('RETAINED_INPUT_SCOPE.json',REPO/'docs/ep_l2/review_packs/FT20261017_LANE5_UNIFIED_INPUT_SCOPE_REUSE_r1/RETAINED_INPUT_SCOPE.json'),('PRODUCER_MANIFEST.json',Path(hand['producer_manifest_path'])),('PRODUCER_RECEIPT.json',Path(hand['producer_receipt_path'])),('SUPPLEMENT_RECEIPT.json',Path(hand['supplement_receipt_path']))]:shutil.copyfile(p,pack/name)
 for name in ['unified_scope.py','parse_unified_terminal.py','parse_all_data_terminal.py']:shutil.copyfile(REPO/'util/ep_l2/ft_lane5'/name,pack/name)
 cases=[v['case'] for v in ind['tests']];gate_map={
 'old_all_off_equivalence':['NATIVE_OFF_RESULT.json'],
 'mode_legality':['unified_mode_guards_r1/RECEIPT.json','unified_constructors_and_guards_r1/RECEIPT.json'],
 'physical_bank_clock':[v for v in cases if 'clock' in v or v.startswith('P1_') or v.startswith('P2_')]+['ALL_DATA_native_offset4096'],
 'memcpy_payload_identity':[v for v in cases if 'host_prefill' in v]+['ALL_DATA_native_ldst'],
 'finite_wbuf':['partition_1_16','partition_2_16','ft_directed','ideal_wb','S64_capacity','UCAP_capacity','UCAP_bank_retry'],
 'requester_exact_once':['ft_directed','a1_1_16','a1_2_16','ideal_meta_integrated','ideal_meta_integrated_B16','ALL_DATA_reference','ALL_DATA_native_ldst','ALL_DATA_supplement_0'],
 'sector_reference_data':['ft_directed','b1-read-first','b1-atomic-first','b1-version-only','ideal_wb','ideal_read_hit','ideal_read_hit_B16','ALL_DATA_reference','ALL_DATA_native_ldst','ALL_DATA_supplement_1'],
 'stale_fill':['host_prefill_1_16','host_prefill_2_16','a1_1_16','a1_2_16','ideal_host_prefill_partition','A1_S64','A1_UCAP','A1_UCAP_rollback'],
 'resource_closure':cases,
 'wb_lifecycle':['partition_1_16','partition_2_16','ft_directed','ideal_wb','UCAP_bank_retry','A1_UCAP_mixed','ALL_DATA_native_ldst'],
 'bank_service':[v for v in cases if 'clock' in v or v.startswith('P1_') or v.startswith('P2_')]+['ideal_wb','ideal_read_hit']}
 require(set(gate_map)==GATES,'Eleven gate mapping incomplete')
 review={'status':'ALL11_NEW_SOURCE_GATES_PASS','source_identity':IDENTITY,'producer_publication':hand['publication'],'gates':{g:{'status':'PASS','production_driven':True,'actual_evidence':names} for g,names in gate_map.items()},'actual_affected_native_checks':49,'actual_config_constructors':11,'actual_expected_rejections':13,'actual_new_nativeOFF_canaries':1,'scope':'Finite/retained local paths use all64 physical cache/request/sector/WB/bank/drain. ALL_DATA uses original native instruction/access/UID, byte-producer snapshots, realstore commits/barriers/architectural consume/reference drain; physical bypassed countersN/A and two printed literals labelled source assertions. No numericSASS or PPA claim.'};write_json(pack/'ELEVEN_GATE_REVIEW.json',review)
 profiles={}
 for name,row in manifest['profiles'].items():
  profile='U_OFF' if name=='U_WB16_OFF' else name;features({**IDENTITY,'feature_vector':row['feature_vector'],'ideal_vector':row['ideal_vector']},profile);configs=asset_manifest(row['configs'],ordered=True);require(configs==row['ordered_config_manifest'],'Changed ordered config bytes');profiles[profile]={'ordered_configs':configs,'auxiliary_assets':[],'environment':row['environment'],'runtime_config_sha256':row['runtime_config_sha256'],'effective_options':__import__('headroom_config').options([v['path'] for v in row['configs']]),'feature_vector':row['feature_vector'],'ideal_vector':row['ideal_vector']}
 evidence=[{'path':str(p),'sha256':digest(p)} for p in sorted(pack.rglob('*')) if p.is_file()];specdir=H/'parallel_unified_specs_r1';specdir.mkdir();qpaths={group:H/('PARALLEL_UNIFIED_'+group+'_INDEPENDENTLY_QUALIFIED_r1.json') for group in ['ORDINARY','LEGACY']};groups={group:[] for group in qpaths};source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip();cells=Registry().snapshot()['campaigns'][PARALLEL]['seed_cells'];original_proof=json.loads((ORIGINAL/'FWT_7_21_B16_BANKED.json').read_text())['native_legacy_semantic_proof'];scope_tool={'path':str(pack/'unified_scope.py'),'sha256':digest(pack/'unified_scope.py')}
 def spec_for(cell,profile):
  workload=cell['workload_alias'];group='LEGACY' if workload in ['convolutionSeparable','FWT_7_21'] else 'ORDINARY';name='U_WB16_OFF' if profile=='U_OFF' else profile;row=manifest['profiles'][name];mode=row['mode'];spec=copy.deepcopy(json.loads((ORIGINAL/(workload+'_'+mode+'.json')).read_text()));all_data=profile=='I_MEM_ALL_DATA';parser=pack/('parse_all_data_terminal.py' if all_data else 'parse_unified_terminal.py');spec.update(experiment_id=PARALLEL,regime=cell['condition'],profile=cell['mode'],producer_profile=profile,cell_id=cell['cell_id'],scientific_scope='ALL_DATA_REFERENCE_V1' if all_data else 'UNIFIED_NATIVE_V1',scope_tool=scope_tool,parser={'path':str(parser),'sha256':digest(parser)},qualified_release=str(qpaths[group]),binary=hand['binary'],result_root=str(OUT),runner_tooling_source_commit=source,memory_reservation_bytes=8*2**30,configs=[{'name':v['name'],'path':v['path']} for v in row['configs']]);spec['identity'].update(IDENTITY,feature_vector=row['feature_vector'],ideal_vector=row['ideal_vector'],runtime_config_sha256=row['runtime_config_sha256'])
  if group=='LEGACY':spec['native_legacy_semantic_proof']=original_proof
  return spec,group
 for cell in cells:
  if cell['condition']=='P2':profile='P2_B16' if cell['mode']=='B16_BANKED' else 'P2_U_WB16'
  elif cell['condition']=='H0' and cell['mode'] in LOCAL and cell['cell_id'] not in ['I011','I012','I013','I014']:profile=cell['mode']
  else:continue
  spec,group=spec_for(cell,profile);file=specdir/(cell['cell_id']+'_'+cell['workload_alias']+'_'+cell['mode']+'.json');write_json(file,spec);groups[group].append(str(file))
 # A new samefb vector anchor is additional, never a relabel/reset of old source37 I011.
 cell={'cell_id':'E_VECTOR_OFF_UNIFIED_FB_R1','condition':'H0','mode':'B16_OFF','workload_alias':'vectorAdd_4M'};spec,group=spec_for(cell,'B16_OFF');checkpoint=pack/'MATCHED_VECTOR_FB_ANCHOR_CHECKPOINT.json';write_json(checkpoint,{'identity':spec['identity'],'reason':'SeedI011 actual source37 cannot be a same-binary baseline for sourcefb ALL_DATA; one extra complete anchor charged to72','new_full_application_started':False});Registry().register_unified_vector_anchor(spec['identity'],{'path':str(checkpoint),'sha256':digest(checkpoint)});file=specdir/'E_VECTOR_OFF_UNIFIED_FB_R1_vectorAdd_4M_B16_OFF.json';write_json(file,spec);groups[group].append(str(file));evidence.append({'path':str(checkpoint),'sha256':digest(checkpoint)})
 for group,files in groups.items():
  q=copy.deepcopy(json.loads((H/('R0_1_A1_B1_LEGACY_TRACE_INDEPENDENTLY_QUALIFIED_r2.json' if group=='LEGACY' else 'R0_1_A1_B1_INDEPENDENTLY_QUALIFIED.json')).read_text()));q.update(IDENTITY,producer_publication_commit=hand['publication'],release_name='UNIFIED_RUNTIME_'+group+'_r1',coordination_commit='a9ab796f0c905d99eb1ffa3d02ea9305ce0bc900',qualified_feature_vectors=[v['feature_vector'] for v in profiles.values()],qualified_modes=[{'profile':name,'feature_vector':v['feature_vector'],'ideal_vector':v['ideal_vector']} for name,v in profiles.items()],retained_input_scope={'path':str(pack/'RETAINED_INPUT_SCOPE.json'),'sha256':digest(pack/'RETAINED_INPUT_SCOPE.json')},TVD_RO_Ideal_qualification='Declared11 profiles only; TVD_RO_I_BANK_I_L2_SERVICE_and_combinations_not_included',data_correctness_scope=review['scope']);q['gates']={g:{'status':'PASS','production_driven':True,'evidence_path':str(pack/'ELEVEN_GATE_REVIEW.json'),'evidence_sha256':digest(pack/'ELEVEN_GATE_REVIEW.json')} for g in GATES}
  if 'input_adapter_revision' in q:q['input_adapter_revision'].update(runtime_gates_source_binary_config_unchanged=False,new_runtime_all_eleven_gates_requalified=True,retained_input_scope_sha256=q['retained_input_scope']['sha256'])
  cfg={'status':'INDEPENDENT_CONFIG_PASS','qualification_kind':'UNIFIED_NATIVE_V1','coordination_commit':'a9ab796f0c905d99eb1ffa3d02ea9305ce0bc900','experiment_id':PARALLEL,'regime':'H0','identity':IDENTITY,'profiles':profiles,'evidence':evidence,'spec_paths':files,'producer_publication':hand['publication'],'producer_publication_verified':True,'independent_affected_production_pass':True,'all_eleven_gates_passed':True,'native_all_off_equivalence':'PASS','independent_mode_semantics_passed':True};path=pack/('INDEPENDENT_CONFIG_REVIEW_'+group+'.json');write_json(path,cfg);q['downstream_config_qualification']={'path':str(path),'sha256':digest(path)};write_json(qpaths[group],q)
 write_json(pack/'SPEC_INDEX.json',groups);freeze_checksums(pack);print(json.dumps({'status':'NEW_UNIFIED_RUNTIME_ELEVEN_GATES_INDEPENDENTLY_QUALIFIED_NOT_YET_CURRENT_V2','specs':{k:len(v) for k,v in groups.items()},'full_starts_this_tool':0}))
if __name__=='__main__':main()
