"""Revalidate retained F exit0 after a published E decoder correction; never rerun."""
from pathlib import Path
import sys,json,copy,time,subprocess,importlib.util
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c,runner
from validate import validate_summary
OLD=P.parent/'MS20261020_E2_MAIN61_CONV_QUALIFICATION_r1'
AID='E009_76e25c1e';OLDQ='73d2efae3c7fc445ae4179c720e87c149a2fc7a3fb9de686f62de78e9074a4f6'
def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(p),sha256=c.digest(p))
def prepare():
 coord=c.Coordinator();snap=coord.snapshot();assert snap['actual_starts']==10 and snap['controller']['state']=='STOPPED'
 original=c.OUTPUT/AID;failed=read(original/'run_status.json');assert failed['status']=='FAILED' and failed['exit_code']==0 and failed['execution_stage']=='TERMINAL_VALIDATION';assert failed['detail']=='ValueError: independent terminal parser failed'
 assert c.digest(original/'raw.log')==failed['raw_log_sha256']
 review=read(P/'ENGINEERING_REVIEW.json');assert review['hold']==snap['scientific_holds']['qualification:'+OLDQ]
 q=read(OLD/'convolutionSeparable_QUALIFICATION.json');q.update(schema='E2_MAIN61_SAME_SCIENTIFIC_SCOPE_DECODER_COMPAT_REVISION_V1',qualified_unix=time.time(),terminal_parser=ref(P/'parse_main_terminal.py'),decoder_engineering_review=ref(P/'ENGINEERING_REVIEW.json'),previous_qualification=dict(path=str(OLD/'convolutionSeparable_QUALIFICATION.json'),sha256=OLDQ),scope_note=q['scope_note']+' Decoder-only compatibility revision: verify commandlist lifecycle outside slice snapshots and use the complete final post-END snapshot at a potentially repeated native clock. All native11+7 and resource/data/slice closure rules retained. No experiment rerun and no science scope expansion.')
 qp=P/'convolutionSeparable_QUALIFICATION.json';c.write_json(qp,q);qid=coord.register_qualification(qp)
 spec=read(original/'input_spec.json');spec.pop('input_audit',None);spec.update(qualification_id=qid,parser=q['terminal_parser']);sp=P/'F_REVALIDATION_SPEC.json';c.write_json(sp,spec)
 audit=runner.inspect(spec,coord,launch_check=False);prior=failed['input_audit']
 allowed={'qualification_sha256','parser'}
 assert {k:v for k,v in audit.items() if k not in allowed}=={k:v for k,v in prior.items() if k not in allowed},'non-parser runtime/input scope changed'
 assert c.digest(original/'accel-sim.out')==q['source_identity']['binary_sha256']==c.digest(spec['binary'])
 native=runner.runtime_metrics(original/'raw.log',audit['effective_options']);summary=read(P/'F_READONLY_DECODER_SUMMARY.json')
 assert summary['raw_log_sha256']==failed['raw_log_sha256'];assert native==dict(cycle=summary['cycles'],insn=summary['instructions']);assert native['insn']==audit['expected_full_instructions']
 validation=validate_summary(summary,spec['identity']);assert validation['status']=='PASS'
 record=copy.deepcopy(failed);record.update(status='COMPLETE_VALID',detail='E2 accepted immutable original F exit0 through explicit offline decoder-only terminal revalidation; original parser failure receipt retained.',execution_stage='TERMINAL_REVALIDATION_NO_NATIVE_RESTART',qualification_id=qid,input_audit=audit,validation=validation,summary=summary,mechanism_metrics=summary['mechanism_metrics'],complete_input_verified=True,independent_acceptance='PASS',original_failed_receipt=ref(original/'run_status.json'),original_parser_log=ref(original/'parser.log'),decoder_engineering_review=ref(P/'ENGINEERING_REVIEW.json'),revalidated_unix=time.time(),new_application_starts=0)
 c.write_json(P/'F_REVALIDATED_RUN_STATUS.json',record);c.write_json(P/'F_REVALIDATION_PREFLIGHT.json',audit)
 resolution=dict(schema='E2_EXPLICIT_ENGINEERING_HOLD_RESOLUTION_V1',reviewed_by='E',qualification_id=OLDQ,status='RESOLVED_WITH_EXPLICIT_EVIDENCE',hold_at_unix=review['hold']['at_unix'],reason='Actual F native exit0. Published decoder rejected valid commandlist lifecycle record and same-clock post-drain snapshots. New parser explicitly validates both protocol constructs, passes11 offline rejection/regression checks, S summary identical and immutable F raw passes all original full-input/data/resource/64slice/epoch checks. This resolves only this new parser engineering hold; every prior main773 hold and failure remains. No native restart.',evidence=[ref(P/'ENGINEERING_REVIEW.json'),ref(P/'CONTROLS.log'),ref(P/'parse_main_terminal.py'),ref(qp),ref(P/'F_REVALIDATED_RUN_STATUS.json'),ref(original/'run_status.json'),ref(original/'raw.log')])
 c.write_json(P/'HOLD_RESOLUTION.json',resolution)
 print(json.dumps(dict(status='READONLY_FULL_F_REVALIDATION_PASS_CANONICAL_ACCEPTANCE_PENDING',qualification_id=qid,native=native)))
def accept():
 coord=c.Coordinator();record=read(P/'F_REVALIDATED_RUN_STATUS.json');qid=record['qualification_id'];head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 for f in ['parse_main_terminal.py','ENGINEERING_REVIEW.json','convolutionSeparable_QUALIFICATION.json','F_REVALIDATED_RUN_STATUS.json','HOLD_RESOLUTION.json','revalidate.py']:
  assert subprocess.check_output(['git','show',head+':'+(P/f).relative_to(ROOT).as_posix()],cwd=ROOT)==(P/f).read_bytes()
 assert c.digest(c.OUTPUT/AID/'raw.log')==record['raw_log_sha256'];assert c.digest(record['original_failed_receipt']['path'])==record['original_failed_receipt']['sha256']
 coord.resolve_scientific_hold(OLDQ,P/'HOLD_RESOLUTION.json')
 with coord.locked() as (data,item):
  assert item['actual_starts']==10 and item['controller']['state']=='STOPPED';coord.require_no_hold(item,qid);coord.require_no_hold(item,OLDQ)
  a=next(a for a in item['attempts'] if a['attempt_id']==AID);assert a['state']=='FAILED' and a['actual_start'] and a['run_key']==record['run_key'] and a['identity']==record['identity']
  try:live=c.process_identity(a['process']['pid'])==a['process']
  except (FileNotFoundError,ProcessLookupError):live=False
  assert not live and record['validation']['status']=='PASS'
  old_attempt=copy.deepcopy(a);run=data['runs'][a['run_key']];old_run=copy.deepcopy(run)
  assert c.digest(a['receipt_path'])==a['receipt_sha256']==record['original_failed_receipt']['sha256']
  assert record['source_identity']==item['final_source_identity']==item['qualifications'][qid]['qualification']['source_identity']
  item.setdefault('terminal_revalidation_history',[]).append(dict(at_unix=time.time(),publication=head,reason='Explicit retained-native parser engineering revalidation; no new start',original_attempt=old_attempt,original_run=old_run,accepted_terminal=ref(P/'F_REVALIDATED_RUN_STATUS.json'),review=ref(P/'ENGINEERING_REVIEW.json')))
  a.setdefault('state_history',[]).append(dict(state='FAILED',receipt_path=a['receipt_path'],receipt_sha256=a['receipt_sha256'],reason='Original parser failure retained immutable'))
  a.update(state='COMPLETE_VALID',terminal_revalidation_acceptance=ref(P/'F_REVALIDATED_RUN_STATUS.json'),terminal_revalidation_qualification_id=qid,original_receipt_is_preserved_parser_failure=True)
  run.setdefault('status_history',[]).append(dict(status=run['status'],detail=run.get('detail'),result_receipt_sha256=run.get('result_receipt_sha256')))
  run.update(status='COMPLETE_VALID',detail=record['detail'],result_receipt_sha256=c.digest(P/'F_REVALIDATED_RUN_STATUS.json'),original_failed_receipt=record['original_failed_receipt'])
  item['accepted_results'][AID]=dict(**ref(P/'F_REVALIDATED_RUN_STATUS.json'),run_key=a['run_key'],identity=a['identity'],qualification_id=qid)
  item['official_producer_current']['current_scientific_status']='MAIN61_CONV_S_F_INDEPENDENT_TERMINALS_VALID_AFTER_EXPLICIT_DECODER_REVALIDATION'
 pair=runner.accept_pair(coord,'E010_1108e4d2',AID,'V2_MAIN_convolutionSeparable_S_F_MAIN61','TRADITIONAL_STATIC_WB16_VS_FIXED_W_V_T_M_1168_SAME_MAIN61')
 c.write_json(P/'FIRST_TRUSTED_PAIR.json',pair)
 clientpath=c.HANDOFF/'CLIENT_CONTRACT.json';client=read(clientpath);client.update(terminal_adapter=str(P/'parse_main_terminal.py'),terminal_adapter_sha256=c.digest(P/'parse_main_terminal.py'),terminal_adapter_source_publication=head,producer_release_status='MAIN61_FIRST_CONV_S_F_CURRENT_ACCEPTED',terminal_adapter_qualified_scope='EXACT_MAIN61_CONV_S_F_RETAINED_NATIVE_VALIDATED; OTHER_INPUTS_AND_EXTRA_JOINT_NOT_UPGRADED')
 client['current_qualifications'].append(dict(path=str(P/'convolutionSeparable_QUALIFICATION.json'),qualification_id=qid,qualification_sha256=qid,workload='convolutionSeparable',revision='DECODER_ENGINEERING_ONLY'))
 c.write_json(clientpath,client);c.write_json(P/'CLIENT_AFTER_ACCEPTANCE.json',client)
 c.write_json(P/'CANONICAL_RECONCILIATION.json',dict(status='FIRST_TRUSTED_SAME_MAIN61_PAIR_CURRENT_ACCEPTED',at_unix=time.time(),publication=head,pair=pair,actual_starts=coord.snapshot()['actual_starts'],new_native_runs=0,original_failed_receipt=record['original_failed_receipt'],original_raw_sha256=record['raw_log_sha256'],new_hold_resolution=ref(P/'HOLD_RESOLUTION.json'),original_main773_holds_preserved=True))
 print(json.dumps(pair))
if __name__=='__main__':{'prepare':prepare,'accept':accept}[sys.argv[1]]()
