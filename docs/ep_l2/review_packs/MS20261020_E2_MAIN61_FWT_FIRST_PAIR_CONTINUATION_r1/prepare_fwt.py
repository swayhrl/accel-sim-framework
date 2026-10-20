"""Post-accepted-Conv decision: qualify original FWT S/F, no native replay/build."""
from pathlib import Path
import sys,json,time,copy
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c,runner
import run as legacy
from headroom_config import options
OLD=P.parent/'MS20261020_E_NEW773_MAIN_SF_QUALIFICATION_r1'
CONV=P.parent/'MS20261020_E2_MAIN61_CONV_QUALIFICATION_r1'
COMPAT=P.parent/'MS20261020_E2_MAIN61_TERMINAL_COMPAT_r1'
def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(p),sha256=c.digest(p))
def main():
 coord=c.Coordinator();snap=coord.snapshot();pair=snap['accepted_pairs']['V2_MAIN_convolutionSeparable_S_F_MAIN61'];assert pair['status']=='CURRENT_ACCEPTED' and snap['actual_starts']==10 and snap['controller']['state']=='STOPPED'
 for endpoint in pair['endpoints'].values():assert c.digest(endpoint['path'])==endpoint['sha256'];coord.require_no_hold(snap,endpoint['qualification_id'])
 source=snap['final_source_identity'];q=read(COMPAT/'convolutionSeparable_QUALIFICATION.json');previous=read(OLD/'FWT_7_21_QUALIFICATION.json')
 q.update(schema='E2_MAIN61_FWT_INDEPENDENT_11_PLUS7_QUALIFICATION_V1',qualified_unix=time.time(),supported_profiles=previous['supported_profiles'],input_selection_id=previous['input_selection_id'],input_scope_admission=copy.deepcopy(previous['input_scope_admission']),first_trusted_same_binary_Conv=ref(COMPAT/'FIRST_TRUSTED_PAIR.json'),previous_input_qualification_scope=ref(OLD/'FWT_7_21_QUALIFICATION.json'),scope_note='Exact main61 same as first CURRENT_ACCEPTED Conv pair. Reuse the exact source-specific original OFF and original11+7 native gates, current E17/26 and explicit unchanged-source/input proof; no new native test/build/OFF. Full preregistered FWT7_21 S/F, fixed W/V/T/M and1168 slots; F T/M stay ON despite valid zero-certified-line coverage, using tested fallback. Complete19-kernel input and791609344 instructions must close independently. Conv performance is not inherited as FWT data; extra joint fixture/Btree/SGEMM boundaries unchanged.')
 q['supported_profiles']={k:q['supported_profiles'][k] for k in ['S','F']};q['input_scope_admission']['retained_input_scope']=ref(CONV/'RETAINED_COMPLETE_INPUT_SCOPE.json')
 qp=P/'FWT_7_21_QUALIFICATION.json';c.write_json(qp,q);qid=coord.register_qualification(qp);rows=[];keys=[]
 for profile in ['S','F']:
  spec=read(OLD/('FWT_7_21_'+profile+'_SPEC.json'));spec.update(binary=q['binary_path'],qualification_id=qid,input_scope_admission=q['input_scope_admission'],parser=q['terminal_parser'])
  for k in ['core_source_commit','framework_source_commit','binary_sha256']:spec['identity'][k]=source[k]
  for asset in spec['auxiliary_assets']:
   if asset['name']=='current_input_scope_binding.json':asset['path']=str(CONV/'RETAINED_COMPLETE_INPUT_SCOPE.json')
  configs=legacy.asset_manifest(spec['configs'],ordered=True);assets=legacy.asset_manifest(spec['auxiliary_assets']);traces=legacy.asset_manifest(spec['trace_files'])
  spec['identity']['runtime_config_sha256']=legacy.content_hash(dict(ordered_configs=configs,auxiliary_assets=assets,environment=spec['environment']))
  effective=options([x['path'] for x in spec['configs']]);assert effective==spec['profile_semantics']['effective_options']==q['supported_profiles'][profile]['effective_options']
  changes=spec['profile_semantics']['comparison_variable_options'];invariant=dict(source=source,trace=spec['identity']['trace_content_sha256'],epoch=spec['identity']['epoch_range'],termination=spec['identity']['termination_contract'],environment=spec['environment'],auxiliary_assets=assets,nonresearch_options={k:v for k,v in effective.items() if k not in changes},comparison_variable_options=sorted(changes))
  spec['comparison_invariants_sha256']=legacy.content_hash(invariant)
  atomic=legacy.validate_atomic_input_scope(spec,spec['input_scope_admission'],traces);originalclient=read(c.SHARED/'CLIENT_CONTRACT.json');legacy.validate_native_legacy_semantic_proof(spec,spec['input_scope_admission'],traces,binding=originalclient['native_legacy_semantic_proof'])
  sp=P/('FWT_7_21_'+profile+'_SPEC.json');c.write_json(sp,spec);audit=runner.inspect(spec,coord);assert audit['expected_full_instructions']==791609344;c.write_json(P/('FWT_7_21_'+profile+'_PREFLIGHT.json'),dict(audit,complete_atomic_scope=atomic));rows.append(ref(sp));keys.append(c.run_key(spec['identity']))
 queue=dict(campaign_id=c.CAMPAIGN,authority_commit=c.AUTHORITY,prepared_by='E',input_and_profile_freeze_unix=1792433922.9336863,specs=rows,pairs=[dict(pair_id='V2_MAIN_FWT_7_21_S_F_MAIN61',left_run_key=keys[0],right_run_key=keys[1],mechanism='PREREGISTERED_S_VS_FIXED_W_V_T_M_SAME_MAIN61_ZERO_RO_COVERAGE_FALLBACK')]);c.write_json(P/'FWT_7_21_QUEUE.json',queue)
 decision=dict(schema='E2_POST_FIRST_TRUSTED_PAIR_FWT_CONTINUATION_DECISION_V1',at_unix=time.time(),reviewed_by='E2',trigger_pair=pair,status='CONTINUE_ORIGINAL_PREREGISTERED_FWT_S_F_ONLY',reason='Trusted same-main Conv pair closes both endpoints; original D order next is FWT. Continue for preregistered workload coverage, independent of small Conv speedup; no favorable-input substitution, no unsupported controls or joint fixture promotion.',source_identity=source,actual_starts_before=10,maximum_actual_starts=40,remaining_start_capacity_before=30,contingency_used=8,contingency_remaining=0,new_starts_budget_bucket='seven_workload_common_S_F',planned_FWT_starts=2,expected_actual_starts_after=12,expected_remaining_after=28,new_OFF_or_native_or_build=0,qualification=ref(qp),qualification_id=qid,queue=ref(P/'FWT_7_21_QUEUE.json'),main_matrix_automatic_dispatch=False,retained_boundaries=dict(Btree='HOLD',SGEMM='D_CANDIDATE_ONLY',extra_joint_fixture='UNQUALIFIED'))
 c.write_json(P/'DECISION.json',decision)
 clientpath=c.HANDOFF/'CLIENT_CONTRACT.json';client=read(clientpath);client['current_qualifications'].append(dict(path=str(qp),qualification_id=qid,qualification_sha256=qid,workload='FWT_7_21'));client.update(terminal_adapter_qualified_scope='EXACT_MAIN61_CONV_AND_FWT_S_F; EXTRA_JOINT_AND_OTHER_PROFILES_NOT_UPGRADED',producer_release_status='MAIN61_CONV_PAIR_CURRENT_ACCEPTED_FWT_ORIGINAL_PLANNED_SF_READY');c.write_json(clientpath,client);c.write_json(P/'CLIENT_FWT_QUALIFIED.json',client)
 print(json.dumps(dict(status=decision['status'],qualification_id=qid,planned_starts=2)))
if __name__=='__main__':main()
