"""Read-only config/input handoff, no lease, compiler, trace-body scan or simulator."""
import datetime,hashlib,json,pathlib
P=pathlib.Path
ROOT=P('/workspace/worktrees/accel-sim-ep-l2-ms20261019-a-core-v1')
A=ROOT/'docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/a'
PREP=A/'full_system_v2/PREPARED_APPLICATION_CONFIGS_r1'
REG=P('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json')
BOOK=P('/workspace/ep_l2_ms20261019_a_common_v1')

def sha(path):
 h=hashlib.sha256()
 with P(path).open('rb') as f:
  for block in iter(lambda:f.read(4*2**20),b''):h.update(block)
 return h.hexdigest()

def load(path,digest=None):
 if digest:assert sha(path)==digest,str(path)
 return json.loads(P(path).read_text())

def options(path):
 result={}
 for raw in P(path).read_text().splitlines():
  fields=raw.split('#',1)[0].strip().split(None,1)
  if len(fields)==2:result[fields[0]]=fields[1]
 return result

def main():
 data=load(REG);ledger=data['mechanism_study_20261019_v1'];prep=load(PREP/'MATRIX.json')
 release=load(A/'RELEASE.json');matrixrow=ledger['full_system_matrix'];matrix=load(matrixrow['path'],matrixrow['sha256'])
 assert matrix==matrixrow['matrix'] and len(matrix['conditions'])==32
 assert sha(release['binary_path'])==release['source_identity']['binary_sha256']
 aliases={'WV_T_ONLY':'WV_T','WV_M_ONLY':'WV_M','STATIC_WB64':'S_WB64','F_FIXED64_DIRTY_RO':'F_FIXED_V64'}
 join={(row['workload'],row['profile']):row for row in matrix['conditions']};assert len(join)==32
 rows=[];seen=set();inputs={}
 for row in prep['conditions']:
  inp=row['input_identity'];matches=[(key,val) for key,val in ledger['input_selections'].items() if val['selection']['full_input_identity']['trace_content_sha256']==inp['trace_content_sha256']];assert len(matches)==1
  sid,selectionrow=matches[0];selection=load(selectionrow['path'],selectionrow['sha256']);assert selection==selectionrow['selection'] and sid==row['selection_id']
  selected=selection['full_input_identity'];profile=aliases.get(row['profile'],row['profile']);cell=join[(selected['workload'],profile)];assert cell['condition_id'] not in seen;seen.add(cell['condition_id'])
  assert sha(inp['commandlist'])==inp['commandlist_sha256']
  declared_command=selected['runtime_independent_input_source']['entry_trace_path'];assert P(declared_command).resolve()==P(inp['commandlist']).resolve()
  review=ledger['input_oracle_reviews'][sid];load(review['path'],review['sha256']);assert review['path']==inp['input_review_path'] and review['sha256']==inp['input_review_sha256']
  manifest=load(inp['manifest_path'],inp['manifest_sha256']);assert sha(inp['ranges_path'])==inp['ranges_sha256']
  assert manifest['commandlist_sha256']==inp['commandlist_sha256']
  assert manifest['artifacts']['certified_ranges.csv']==inp['ranges_sha256']
  if sid not in inputs:
   inputs[sid]=dict(workload=selected['workload'],registration=dict(path=selectionrow['path'],sha256=selectionrow['sha256']),trace_content_sha256=selected['trace_content_sha256'],expected_full_instructions=selected['expected_full_instructions'],commandlist=dict(path=inp['commandlist'],sha256=inp['commandlist_sha256']),oracle_review=review,oracle_manifest=dict(path=inp['manifest_path'],sha256=inp['manifest_sha256']),oracle_ranges=dict(path=inp['ranges_path'],sha256=inp['ranges_sha256']),model_certified_lines=inp['certified_model_lines'],E_fresh_trace_identity_and_runtime_qualification_required=True,trace_body_rehashed_by_A=False,identical_pair_oracle_auxiliary_assets=[dict(name='ep_l2_input_ro_ranges.csv',path=inp['ranges_path'],sha256=inp['ranges_sha256']),dict(name='ep_l2_input_ro_manifest.json',path=inp['manifest_path'],sha256=inp['manifest_sha256'])])
  item=dict(condition_id=cell['condition_id'],matrix_group=cell['group'],workload=selected['workload'],selection_id=sid,canonical_profile=profile,A_prepared_profile=row['profile'],ordinal_in_prepared_matrix=row['ordinal'],fixed_research_switches={k:cell[k] for k in ['W','V','T','M']},anchor_condition_id=cell['anchor_condition_id'],scientific_qualification=False,application_start_authorization=False)
  if row.get('overlay'):
   path=PREP/row['overlay'];assert sha(path)==row['overlay_sha256'];opts=options(path);assert opts==row['effective_overlay_options']
   assert all(name.startswith('-gpgpu_ep_l2_') for name in opts)
   assert all(row['mechanism'][name]==cell[name] for name in ['W','V','T','M'])
   for key,value in [('Tags',1024),('payload',1168),('WAD_TVD',128),('D',512),('per_address',32),('banks',4),('P',1)]:assert row['physical_budget'][key]==value
   if cell['T'] or cell['M']:
    assert opts['-gpgpu_ep_l2_ro_ranges']==inp['ranges_path'] and opts['-gpgpu_ep_l2_ro_ranges_sha256']==inp['ranges_sha256']
    assert opts['-gpgpu_ep_l2_ro_manifest']==inp['manifest_path'] and opts['-gpgpu_ep_l2_ro_manifest_sha256']==inp['manifest_sha256']
   if profile=='S_WB64':assert opts['-gpgpu_ep_l2_static_s64']=='1' and opts['-gpgpu_ep_l2_wbuf_entries']=='16' and row['static_partition']=='1024resident/80landing/64WB; legacy wbuf_entries16 anchor'
   if profile=='F':assert all(row['mechanism'][name]==1 for name in ['W','V','T','M'])
   item.update(status='PRODUCER_OVERLAY_BOUND_PENDING_E_PROFILE_AND_INPUT_QUALIFICATION',overlay=dict(path=str(path),sha256=row['overlay_sha256']),overlay_options=opts,static_partition=row['static_partition'],ordered_full_runtime_config_sha256=None,all_H0_noresearch_configs_and_environment_owned_by_E=True)
  else:item.update(status='UNSUPPORTED_DO_NOT_START',reason=row['status'],overlay=None)
  rows.append(item)
 assert len(rows)==32 and len(inputs)==7 and sum(row['overlay'] is not None for row in rows)==29
 assert sum(row['status']=='UNSUPPORTED_DO_NOT_START' for row in rows)==3
 report=dict(schema='A_FINAL_PROFILE_INPUT_BINDINGS_R24',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='PREPARATION_ONLY_EXACT_OVERLAY_INPUT_RUNTIME_BINDINGS_NOT_QUALIFICATION_OR_ADMISSION',official_producer_publication='75707624b980df5e3bbb809c76a31cf1b34501a1',official_release=dict(path=str(A/'RELEASE.json'),sha256=sha(A/'RELEASE.json')),runtime_source_identity=release['source_identity'],binary_path=release['binary_path'],prepared_matrix=dict(path=str(PREP/'MATRIX.json'),sha256=sha(PREP/'MATRIX.json')),canonical_D_matrix=dict(path=matrixrow['path'],sha256=matrixrow['sha256'],publication=matrixrow['D_publication']),native_producer_manifest=release['producer_test_manifest'],alias_map_from_A_profiles_to_D_canonical_profiles=aliases,conditions=rows,inputs=inputs,planned_conditions=32,available_overlays=29,unsupported_conditions=3,original_T0=ledger['t0_unix'],total_full_start_budget=40,planned_plus_reserve=[32,8],actual_full_starts_snapshot=ledger['actual_starts'],shared_registry_mutations=0,new_CPP_native_or_application_runs=0,tool_sha256=sha(__file__),integration_notes=['E runner.inspect compares whole effective_options to per-qualification profile; different input-specific oracle paths/hashes require appropriate per-input qualified profile binding. Do not silently reuse Conv F effective_options forFWT orotherinputs.','E comparison invariants include auxiliary_assets unchanged. Keep identical reviewed oracle asset bundle in each same-input S/F comparison, evenS doesnotactivateRO; append same frozenH0requiredassets. Existing validate_config_closure permits unusedextraevidenceassets, allwithin growthbudget.','This artifact is NOT a complete ordered runtimeconfig digest: E must use originalH0nonresearchbase/trace/hardwareconfigs/environment, no nativefixtureconfig substitution. E computes orderedconfig+aux+environment digest and current admission.','E retains fresh fulltracecontent/input qualification responsibility. A reads only commandlists/ranges/manifests/reviewmetadata, no fulltracebodyhash scan.','FWT fixedF toggles remainON with genuine0 modelcertifiedlines, so0activation isvalid. No borrowedConv certificate or per-inputbestsubset.','STATIC_WB64 label maps to frozen D S_WB64, fixedtotal1168=1024+80+64. F_FIXED_V64 remainsunsupported full dirtyRO comparator, never substituteS_WB64.'])
 out=BOOK/'FINAL_PROFILE_INPUT_BINDINGS_r24.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(rows),'conditions;29bound3unsupported;7exactinputmatches')
if __name__=='__main__':main()
