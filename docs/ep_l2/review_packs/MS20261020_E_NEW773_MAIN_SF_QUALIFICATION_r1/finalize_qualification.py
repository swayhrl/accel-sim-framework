"""Finalize exact new producer only after actual new-source OFF completes; no launch."""
from pathlib import Path
import sys,json,time,subprocess,copy
sys.path.insert(0,'/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/util/ep_l2/mechanism_e')
import coordinator as c
import runner
import run as legacy
from headroom_config import options

def main():
 p=Path(__file__).resolve().parent;root=p.parents[3];coord=c.Coordinator();snap=coord.snapshot()
 c.require(snap['controller']['state']=='STOPPED','wait existing OFFcontroller to retire')
 source=snap['final_source_identity'];sha=source['binary_sha256'];c.require(sha=='773271ac70f009dddcd4c522f66dcd37967e4f57ce1e5082d3fc5aea61f2f9f5','only requested newproducer')
 record=snap['native_off_controls_by_binary'][sha];off=record['result'];c.require(off['status']=='COMPLETE_VALID' and c.digest(off['path'])==off['sha256'],'newsource actualOFF required')
 actual=json.loads(Path(off['path']).read_text());c.require(actual['source_identity']==source and actual['old_all_off_equivalence']=='PASS' and actual['actual_metrics']==dict(cycle=73873,insn=56000000),'newsource originalOFF native gate failed')
 off_cp=json.loads(Path(record['binding']['path']).read_text());c.require(actual['seven_csv_sha256']==off_cp['csv_sha256'],'allseven frozenCSV must match')
 intake=p.parent/'MS20261020_E_NEW773_INTAKE_r1';old=p.parent/'MS20261020_E_MAIN_SF_QUALIFICATION_r2'
 gate=dict(schema='E_NEW_SOURCE_ORIGINAL_OFF_ACTUAL_GATE_V1',gate='old_all_off_equivalence',status='PASS',production_driven=True,reviewed_by='E',qualified_unix=time.time(),source_identity=source,control_result=off,actual_qualification_control=actual,actual_full_start_spent=1,budget_bucket='contingency',old_failure_or_qualification_reaccepted=False,baseline_scope='Original FTmode0 fullVectorAdd4M73873/56000000,64sliceclosure,all7CSVbyteequivalent; independentnew773 raw, not E001 reusedasnewPASS; not aperformanceendpoint.')
 c.write_json(p/'NEW_SOURCE_ALL_OFF_GATE_PASS.json',gate)
 oldscopepath=p.parent/'MS20261020_E_MAIN_SF_QUALIFICATION_r1/RETAINED_COMPLETE_INPUT_SCOPE.json';oldscope=json.loads(oldscopepath.read_text());scope=copy.deepcopy(oldscope)
 scope.update(at_unix=time.time(),new_source_identity={k:source[k] for k in oldscope['new_source_identity']},previous_input_scope_chain=dict(path=str(oldscopepath),sha256=c.digest(oldscopepath)),new_producer_identity_review=dict(path=str(intake/'PRODUCER_IDENTITY_REVIEW.json'),sha256=c.digest(intake/'PRODUCER_IDENTITY_REVIEW.json')),new_native_execution=dict(path=str(c.OUTPUT/'E_INDEPENDENT_NEW773_AFFECTED_NATIVE_r1/RECEIPT.json'),sha256=c.digest(c.OUTPUT/'E_INDEPENDENT_NEW773_AFFECTED_NATIVE_r1/RECEIPT.json')),changed_input_interface_review='OnlyROlowerread origin allocator changes wid/sid/tpc inheritance; exact inputparser/ISA/addressmaskgenerator/sourceobjects unchanged. Historical byte/non-atomic proofs remain originalsource evidence. Actual newaffected native24 includes GPUepoch/ROsourceidentity/drain and realDRAM; hostprefill/reference unaffected evidence explicitly retained. No body rescan, numericalSASS claim, or binary performance inheritance.')
 for t in scope['source_trees']:
  if t['new_commit']=='c994c893e69a1214ee1a96a045d02cdc54eaebcf':t['new_commit']=source['core_source_commit']
  t['new']=subprocess.check_output(['git','rev-parse',t['new_commit']+':'+t['path']],cwd=t['repository'],text=True).strip();c.require(t['new']==t['old'],'inputgeneratorchanged')
 c.write_json(p/'RETAINED_COMPLETE_INPUT_SCOPE.json',scope)
 A=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-a-core-v1/docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/a/full_system_v2');release=json.loads((A/'RO_ORIGIN_RELEASE_r30.json').read_text())
 queues=[];reviews=[]
 for workload in ['convolutionSeparable','FWT_7_21']:
  q=json.loads((old/(workload+'_QUALIFICATION.json')).read_text())
  q.update(schema='E_NEW773_INDEPENDENT_11_PLUS_7_NATIVE_QUALIFICATION_V1',source_identity=source,binary_path=release['binary_path'],qualified_unix=time.time(),status='INDEPENDENTLY_QUALIFIED',supersedes_held_registration='NEW_SOURCE_ONLY; alloldqualifications/holds andE001/E002/E003 immutable, none reinstated',native_execution_receipt=scope['new_native_execution'],producer_fixture_scope=dict(current_test_source_core=source['core_source_commit'],main_producing_core=source['core_source_commit'],generated_banner_core='97fd7a3d872f572818afee1f99343368f89b7ed9',scope='ExactnewROarchive+4relinkedELFs; unaffectedELFs andsources explicitlyretained, not claimedallfresh.'))
  for name in q['gates']:
   path=p/'NEW_SOURCE_ALL_OFF_GATE_PASS.json' if name=='old_all_off_equivalence' else intake/'gates'/(name+'.json')
   c.require(json.loads(path.read_text())['status']=='PASS','gate notpassed')
   q['gates'][name]=dict(status='PASS',production_driven=True,evidence_path=str(path),evidence_sha256=c.digest(path))
  q['default_off_equivalence']=q['gates']['old_all_off_equivalence']
  q['producer_release']=dict(path=str(A/'RO_ORIGIN_RELEASE_r30.json'),sha256=c.digest(A/'RO_ORIGIN_RELEASE_r30.json'),publication_commit='156adbbb5ddcd49e8adb96939837372936ac451e',execution_evidence_publication='91f2eacf07476c69f47dd43a75055f355415bd3d',source_identity=source)
  q['build_log']=release['producing_build_receipt'];q['producer_test_manifest']=release['producer_test_manifest']
  q['input_scope_admission']['retained_input_scope']=dict(path=str(p/'RETAINED_COMPLETE_INPUT_SCOPE.json'),sha256=c.digest(p/'RETAINED_COMPLETE_INPUT_SCOPE.json'))
  q['unqualified_extra_joint_scope']=dict(path=str(intake/'VRW_SCOPE_REVIEW.json'),sha256=c.digest(intake/'VRW_SCOPE_REVIEW.json'))
  q['scope_note']='Exact official Core27/main773: E24 affectedactualnative cases plus reviewed source-disjoint retained native reference/hostprefill/WB tests. Newbinary originalOFF completed independently incl64closure and7CSV. Original11+7minimumgates allPASS; nooldbinaryOFF or performance inherited. Extra128Bsectorized VRW fixture remains FAILED/unqualified, B/Cexpectedpacket/UID/descriptor review pending; no reuse_seen change/no22packet benefitclaim. Existing requiredcombo source/assertions explicitlyreviewed and currentarchive actualexecuted; fullapplicationacceptance is separately pending. TRACE_MODEL_CLOSED_WORLD input-specificoracle, F fixedW/V/T/M includingzeroFWTcoverage fallback; no numericSASSdataexecutionclaim. Terminaldecoder bytes unchanged because productiondelta has no format change; parseronlyruntimeoptiongrammar fix exactEpublicationa1a68. Alloriginalboundaries preserve.'
  qp=p/(workload+'_QUALIFICATION.json');c.write_json(qp,q);qid=coord.register_qualification(qp)
  rows=[];keys=[]
  for profile in ['S','F']:
   spec=json.loads((old/(workload+'_'+profile+'_SPEC.json')).read_text())
   spec.update(binary=release['binary_path'],qualification_id=qid,input_scope_admission=q['input_scope_admission'])
   for k in ['core_source_commit','framework_source_commit','binary_sha256']:spec['identity'][k]=source[k]
   for asset in spec['auxiliary_assets']:
    if asset['name']=='current_input_scope_binding.json':asset['path']=str(p/'RETAINED_COMPLETE_INPUT_SCOPE.json')
   if workload=='convolutionSeparable':spec.update(budget_bucket='contingency',contingency_review='NecessarysameNEWbinaryConvS/F replacementafteroldE002parserfailure/E003SIGSEGV; eachnewactualstartchargedoriginal8contingency, old2actualmainfailures retained. Remainingplannedmainconditions and40/32+8/cutoffs unchanged; no crossbinaryanchor.')
   configs=legacy.asset_manifest(spec['configs'],ordered=True);assets=legacy.asset_manifest(spec['auxiliary_assets']);traces=legacy.asset_manifest(spec['trace_files'])
   spec['identity']['runtime_config_sha256']=legacy.content_hash(dict(ordered_configs=configs,auxiliary_assets=assets,environment=spec['environment']))
   # Same frozen H0 nonresearch options/configs and matching perinput auxiliaries.
   effective=options([a['path'] for a in spec['configs']]);assert effective==spec['profile_semantics']['effective_options']
   changes=spec['profile_semantics']['comparison_variable_options']
   invariant=dict(source=source,trace=spec['identity']['trace_content_sha256'],epoch=spec['identity']['epoch_range'],termination=spec['identity']['termination_contract'],environment=spec['environment'],auxiliary_assets=assets,nonresearch_options={k:v for k,v in effective.items() if k not in changes},comparison_variable_options=sorted(changes))
   spec['comparison_invariants_sha256']=legacy.content_hash(invariant)
   # Explicit fullbyte/nonatomic/native-mask audits using retainedsource chain.
   atomic=legacy.validate_atomic_input_scope(spec,spec['input_scope_admission'],traces)
   originalclient=json.loads((c.SHARED/'CLIENT_CONTRACT.json').read_text())
   legacy.validate_native_legacy_semantic_proof(spec,spec['input_scope_admission'],traces,binding=originalclient['native_legacy_semantic_proof'])
   sp=p/(workload+'_'+profile+'_SPEC.json');c.write_json(sp,spec)
   audit=runner.inspect(spec,coord);c.write_json(p/(workload+'_'+profile+'_PREFLIGHT.json'),dict(audit,complete_atomic_scope=atomic,retained_native_legacy_proof='CURRENT_SOURCE_CHAIN_VERIFIED'))
   rows.append(dict(path=str(sp),sha256=c.digest(sp)));keys.append(c.run_key(spec['identity']))
  pairid='V2_MAIN_'+workload+'_S_F_NEW773'
  queue=dict(campaign_id=c.CAMPAIGN,authority_commit=c.AUTHORITY,prepared_by='E',input_and_profile_freeze_unix=1792433922.9336863,specs=rows,pairs=[dict(pair_id=pairid,left_run_key=keys[0],right_run_key=keys[1],mechanism='TRADITIONAL_STATIC_WB16_VS_COMBINED_W_V_T_M_FIXED1168_SAME773')])
  queuepath=p/(workload+'_QUEUE.json');c.write_json(queuepath,queue);queues.append(dict(path=str(queuepath),sha256=c.digest(queuepath),workload=workload,pair_id=pairid))
  reviews.append(dict(workload=workload,qualification_id=qid,qualification_sha256=c.digest(qp),path=str(qp)))
 receipt=dict(schema='E_NEW773_ORIGINAL18_GATES_PASS_FORMAL_TWO_PAIR_READY_V1',qualified_by='E',at_unix=time.time(),source_identity=source,qualifications=reviews,queues=queues,actual_starts=coord.snapshot()['actual_starts'],accepted_pairs=len(coord.snapshot()['accepted_pairs']),historical_attempts_preserved=True,newsourceOFF=off,oldbinary_anchors_reused=False,unqualified_extra_joint_scope=q['unqualified_extra_joint_scope'],E_source_publication=json.loads((c.HANDOFF/'CLIENT_CONTRACT.json').read_text())['source_publication_commit'])
 c.write_json(p/'RECEIPT.json',receipt)
 with coord.locked() as (data,item):
  item['official_producer_current']['E_independent_qualification']=True
  item['independent_native_current']['scientific_acceptance']='ORIGINAL11_PLUS7_MINIMUM_NATIVE_GATES_ACCEPTED_NEW_SOURCE_OFF_ACTUAL_PASS_EXTRA_R35_JOINT_SCENARIO_EXCLUDED'
  item['unqualified_extra_joint_scenarios']=dict(r35=q['unqualified_extra_joint_scope'])
 c.write_json(c.HANDOFF/'events/E_NEW773_18GATES_AND_CONV_FWT_READY_r1.json',receipt)
 print(json.dumps(dict(status='INDEPENDENT_NEW773_18_GATES_PASS',qualifications=reviews,actual_starts=receipt['actual_starts'])))
if __name__=='__main__':main()
