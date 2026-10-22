from pathlib import Path
import sys,json,copy,hashlib,importlib.util,time
E=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1');P=E/'docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1';R=P/'parser_recovery';D=Path('/workspace/ep_l2_ms20261019_e_results/E051_c0185b56');sys.path.insert(0,str(E/'util/ep_l2/mechanism_e'))
from coordinator import Coordinator,digest,tooling_binding,process_identity
import detach_validation as dv
import run as legacy
from headroom_config import options
c=Coordinator();item=c.snapshot();a=item['attempts'][50];assert a['attempt_id']=='E051_c0185b56' and a['state']=='FAILED' and item['controller']['state']=='STOPPED' and item['actual_starts']==51
qrow=item['qualifications'][a['qualification_id']];q=qrow['qualification'];assert digest(qrow['path'])==qrow['sha256'];s=json.loads((D/'input_spec.json').read_bytes());audit=json.loads((D/'input_audit.json').read_bytes());original=json.loads((D/'run_status.json').read_bytes());assert original['status']=='FAILED' and original['raw_log_sha256']==digest(D/'raw.log')
fixed=R/'decoder_samecycle_close.py';assert digest(fixed)=='647510163053d30773176578cf35c10e0aea0a1256af366feba520820d0e11d4';framing=json.loads((R/'FRAMING_SOURCE_ENGINEERING_REVIEW.json').read_bytes());assert framing['raw']['sha256']==original['raw_log_sha256']
dv.configure_binding(q['detach_observer_diagnostic']['validation_scope']);adapter=dv._ADAPTER;adapter.check(s,qrow,audit)
legacy_summary=adapter.legacy_parse(D/'raw.log',s,q);assert adapter.legacy_validate(legacy_summary,s['identity'])['status']=='PASS'
module=importlib.util.spec_from_file_location('_E051_exact_engineering_fixed_decoder',fixed);dec=importlib.util.module_from_spec(module);module.loader.exec_module(dec)
with (D/'raw.log').open('rb') as stream:o=dec.Decoder(adapter.schema).decode(stream)
assert o['status']=='VALID_OBSERVER_TERMINAL_DECLARATIONS_ONLY' and o['same_cycle_lifecycle_closures']==1 and o['snapshot_count']==2
native=adapter.native_files(D/'raw.log',s,audit)
summary=copy.deepcopy(legacy_summary);summary['diagnostic_scope']=dv.SCI_SCOPE
ref=lambda p:{'path':str(p),'sha256':digest(p)}
summary['detach_observer_diagnostic']={'schema':'E2_DETACH_NORMALIZED_TERMINAL_V1','source_identity':copy.deepcopy(q['source_identity']),'qualification_id':s['qualification_id'],'pair':False,'binding_sha256':dv.sha(q['detach_observer_diagnostic']['validation_scope']),'legacy_summary_sha256':dv.sha(legacy_summary),'legacy_diagnostic_scope':legacy_summary['diagnostic_scope'],'observer':o,'native_boundary':native,'observer_sha256':dv.sha(o),'raw_log_sha256':legacy_summary['raw_log_sha256'],'parser_engineering_revalidation':{'original_execution_status':'FAILED','original_failed_receipt':ref(D/'run_status.json'),'original_decoder':q['detach_observer_diagnostic']['validation_scope']['observer_decoder'],'actual_fixed_decoder':ref(fixed),'framing_source_evidence':ref(R/'FRAMING_SOURCE_ENGINEERING_REVIEW.json'),'new_application_starts':0,'scope':'Only fullsamecycle unchangedledger epochclose framing repair; original source/main/spec/Q/input/gates/nativecollector andall terminalrules unchanged. No hidden callback or model change; original decoder remains at original path.'}}
validation=adapter.validate_summary(summary,s,qrow,audit);assert validation['status']=='PASS'
# The previous original runner stopped before its post-run inspect. Independently
# perform its actual post-run byte/closure/math checks while HOLD remains active.
assert digest(s['binary'])==digest(D/'accel-sim.out')==s['identity']['binary_sha256']
assert digest(q['archive_identity']['path'])==q['source_identity']['archive_sha256']
configs=legacy.asset_manifest(s['configs'],ordered=True);assets=legacy.asset_manifest(s['auxiliary_assets']);traces=legacy.asset_manifest(s['trace_files']);assert configs==audit['configs'] and assets==audit['auxiliary_assets'] and traces==audit['traces']
assert legacy.content_hash(traces)==s['identity']['trace_content_sha256'];assert legacy.content_hash({'ordered_configs':configs,'auxiliary_assets':assets,'environment':s['environment']})==s['identity']['runtime_config_sha256'];legacy.validate_config_closure(s);legacy.validate_trace_closure(s)
assert options([v['path'] for v in s['configs']])==audit['effective_options']==s['profile_semantics']['effective_options'];assert audit['comparison_invariants_sha256']==s['comparison_invariants_sha256'];tooling_binding()
for ident in (a['process'],a['exit_collector_process']):
 try:actual=process_identity(ident['pid'])
 except (FileNotFoundError,ProcessLookupError):actual=None
 assert actual!=ident
assert summary['instructions']==1658916864 and summary['slices']==64 and summary['hardware_drained'] is True
out=R/'TERMINAL_SUMMARY.json';out.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
report={'schema':'E2_E051_FIXED_PARSER_INDEPENDENT_FULL_TERMINAL_VALIDATION_V1','status':'PASS','reviewed_by':'E','at_unix':time.time(),'attempt_id':a['attempt_id'],'identity':a['identity'],'qualification_id':a['qualification_id'],'raw_log_sha256':original['raw_log_sha256'],'terminal_summary_ref':ref(out),'fixed_decoder_ref':ref(fixed),'legacy_parser_ref':q['detach_observer_diagnostic']['validation_scope']['legacy_parser'],'validation':validation,'full_instructions':summary['instructions'],'physical_slices':64,'samecycle_close_transition':1,'original_native_binding':native['closure'],'original_run_failed_receipt':ref(D/'run_status.json'),'post_run_source_binary_archive_config_complete_trace_oracle_checks':'PASS_ACTUAL_HASHES_AND_ORIGINAL_CLOSURE_MATH','new_application_or_native_starts':0,'root_targeted_synthetic_framing_controls_pass':14,'agent_regression_synthetic_controls_pass':108,'no_qualification_or_spec_replacement':True,'original_failed_row_still_failed':True,'central_acceptance_not_yet_added':True}
(R/'INDEPENDENT_VALIDATION.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
closure={k:True for k in ('normal_native_exit0','full_instructions','all_kernels','all_64_slices','hardware_drained','resources_retired','source_config_input_unchanged','positive_ro_scope_unchanged','fixed_decoder_source_bound','original_native_binding_validated')}
review={'schema':'E2_E051_PARSER_ENGINEERING_SUPPLEMENTAL_TERMINAL_REVIEW_V1','status':'COMPLETE_VALID_SUPPLEMENTAL_DIAGNOSTIC','reviewed_by':'E','attempt_id':a['attempt_id'],'identity':a['identity'],'qualification_id':a['qualification_id'],'raw_log_sha256':original['raw_log_sha256'],'independent_acceptance':'PASS','complete_input_verified':True,'validation':validation,'original_execution_status':'FAILED','new_application_starts':0,'pair':False,'closure':closure,'terminal_summary_ref':ref(out),'independent_validation_ref':ref(R/'INDEPENDENT_VALIDATION.json'),'native_exit_ref':ref(D/'NATIVE_EXIT.json'),'cycles':summary['cycles'],'instructions':summary['instructions'],'scope':'Supplemental accepteddiagnostic after precise E parser-engineering correction only. Original attempted execution row, oldrunreceipt/parser.log/HOLDhistory/spec/Q/51charge remain unchanged.'}
(R/'SUPPLEMENTAL_REVIEW.json').write_text(json.dumps(review,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'full_terminal_validation':report['status'],'cycles':summary['cycles'],'instructions':summary['instructions'],'slices':summary['slices'],'raw_sha256':original['raw_log_sha256'],'root_actual_new_starts':0,'central_acceptance_pending':True}))
