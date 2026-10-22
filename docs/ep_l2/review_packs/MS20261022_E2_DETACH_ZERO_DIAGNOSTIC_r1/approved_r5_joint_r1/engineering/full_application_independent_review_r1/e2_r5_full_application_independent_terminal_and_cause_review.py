#!/usr/bin/env python3
"""Read-only source-bound review of an already accepted r5 endpoint; one raw pass.
No launches, retries, registry/CLIENT writes, polling or qualification mutations.
"""
import argparse,copy,hashlib,json,re,sys
from collections import defaultdict
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1');TOOLS=ROOT/'util/ep_l2/mechanism_e';APP=ROOT/'docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1/approved_r5_joint_r1';RESULTS=Path('/workspace/ep_l2_ms20261019_e_results');SCI='TAGPRESSURE_OBSERVER_DIAGNOSTIC_POINT_V1';CAP=384*2**20;META=CAP
MANIFEST_SHA='25d1b8cf8b80d53bfe677f58d5273f35115cf40599660b1c0038a9be7ed58b69'

def require(ok,m):
 if not ok:raise ValueError(m)
def unique(pairs):
 d={}
 for k,v in pairs:require(k not in d,'duplicate JSON key '+str(k));d[k]=v
 return d
def canon(v):return json.dumps(json.loads(json.dumps(v,allow_nan=False)),sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def csha(v):return hashlib.sha256(canon(v)).hexdigest()
def metadata(p):
 p=Path(p);require(p.is_file() and p.stat().st_size<=META,'bounded metadata absent/oversized '+str(p));return json.loads(p.read_bytes(),object_pairs_hook=unique)
def ref(p):
 p=Path(p);require(p.is_file()and p.stat().st_size<=META,'bounded source/ref absent/oversized '+str(p));return {'path':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def read(r):require(ref(r['path'])['sha256']==r['sha256'],'source/ref changed '+r['path']);return metadata(r['path'])
def uint(v):require(type(v)is int and 0<=v<2**64,'invalid uint64');return v

def accepted(item,aid,spec,qref):
 matches=[a for a in item['attempts']if a['attempt_id']==aid];require(len(matches)==1,'exact charged attempt missing/duplicate');a=matches[0];e=item['accepted_results'].get(aid);require(isinstance(e,dict),'CURRENT central accepted result pointer absent')
 require(a['actual_start'] is True and a['state']=='COMPLETE_VALID','not actual COMPLETE_VALID endpoint');require(a['scientific_scope']==e['scientific_scope']==SCI,'wrong scientific scope')
 require(a['condition_id']==spec['condition_id']and a['identity']==e['identity']==spec['identity'],'wrong approved condition/source/input identity');require(a['qualification_id']==e['qualification_id']==spec['qualification_id']==qref['sha256'],'wrong exact qualification')
 require(a['run_key']==e['run_key']==csha(spec['identity']),'wrong canonical run key');qrow=item['qualifications'].get(spec['qualification_id']);require(qrow and qrow['path']==qref['path']and qrow['sha256']==qref['sha256']and qrow['qualification']==read(qref),'registered Q differs')
 require('qualification:'+spec['qualification_id']not in item.get('scientific_holds',{}),'active exact Q HOLD');return a,e,qrow

def sum_sparse(records,name):
 d=defaultdict(int)
 for r in records:
  rows=r['route_joint']if name=='route_joint'else r['histograms'][name]
  for row in rows:
   key=tuple(row[:-1]);d[key]+=uint(row[-1]);uint(d[key])
 return [list(k)+[v]for k,v in sorted(d.items())]

def panel(record,wire,*,phase=False):
 """Only aggregate source-emitted joints along disjoint dimensions; never multiply marginals."""
 c=record['counters'];h=record['histograms'];J=record['route_joint'];covered=uint(c['covered']);route=defaultdict(int)
 for row in J:
  require(len(row)==10,'exact joint10');key=tuple(row[2:-1]);route[key]+=uint(row[-1])
 route_rows=[list(k)+[v]for k,v in sorted(route.items())]
 require(sum(v[-1]for v in route_rows)==covered,'route projection lost heads')
 byraw={label:sum(v[-1]for v in h['heads_raw_reserved']if v[0]==i)for i,label in enumerate(wire['raw_labels'])}
 r16={label:sum(v[-1]for v in h['heads_raw_reserved']if v[:2]==[i,16])for i,label in enumerate(wire['raw_labels'])}
 def jointfilter(raws):return [r for r in route_rows if r[0]in raws]
 return {'domain':'FRONTEND_HEAD_CYCLE_SAME_TARGET_SET','scope':'DISJOINT_PHYSICAL_EVENT_PHASE_NOT_REQUESTER_VICTIM_CAUSE'if phase else'GLOBAL_CUMULATIVE',
 'denominators':{'covered_head_cycle_exposures':covered,'target_set_way_exposures':16*covered,'live_RO_way_exposures':sum(uint(r[-1])for r in h['ways_raw_reserved_predmask']),'structural_eligible_way_exposures':sum(uint(r[-1])for r in h['ways_raw_reserved_predmask']if r[2]==5),'RO_observed_head_cycle_exposures':c['ro_observed'],'route_joint_head_cycle_exposures':sum(r[-1]for r in route_rows),'unique_requests_or_victims':'UNKNOWN_NOT_A_HEAD_OR_WAY_EXPOSURE_DOMAIN'},
 'counts':c,'coverage':{'observed_heads':c['observed_heads'],'covered_probed_heads':covered,'skipped_heads':c['probe_skipped'],'absent_cycles':c['head_absent_cycles'],'skipped_raw_set_requester_eligibility':'NA_NOT_OBSERVED_DO_NOT_FILL_ZERO','skips':{k:c[k]for k in ('skip_tvd','skip_ideal','skip_disabled','skip_other')},'RO_runtime_population':{'observed':c['ro_observed'],'NA':c['ro_na']}},
 'raw_counts':byraw,'all16_RESERVED_raw_counts':r16,
 'raw_new_tag_demand_MISS_or_FAIL':{'head_exposures':byraw['MISS']+byraw['RESERVATION_FAIL'],'all16_reserved_head_exposures':r16['MISS']+r16['RESERVATION_FAIL'],'definition':'Source raw MISS/RESERVATION_FAIL new-tag demand classification; not all accesses/unique requests or eventual successful allocation.'},
 'same_tag_outcomes':{'raw_labels':['HIT','HIT_RESERVED','SECTOR_MISS'],'head_exposures':sum(byraw[k]for k in ('HIT','HIT_RESERVED','SECTOR_MISS')),'all16_reserved_head_exposures':sum(r16[k]for k in ('HIT','HIT_RESERVED','SECTOR_MISS')),'interpretation':'A matching-tag outcome can coexist with16 RESERVED ways; it is not a newTag RESERVATION_FAIL.'},
 'same_head_route_joint':{'columns':wire['route_joint_columns'][2:],'rows':route_rows,'dropped_dimensions':'sum disjoint physical slice and phase dimensions only','requester_labels':wire['requester_labels'],'eligibility_labels':wire['eligibility_state_labels'],'route_labels':wire['route_labels'],'early_labels':wire['early_labels'],'frontend_admit_scope':'Same recorded frontend preview head-cycle route/admit; not eventual request completion or actual commit-domain count.'},
 'new_tag_demand_same_head_joint':jointfilter((2,3)),
 'r16_matching_tag_same_head_joint':[r for r in route_rows if r[0]in(0,1,4)and r[1]==16],
 'histograms_exact_source':h,
 'histogram_semantics':'Each histogram remains its explicitly emitted dimensions/raw×reserved conditional denominator; eligible-count, reason mask, way predicate and way class are not cross-joined with requester/route or each other. Only head_route_joint proves its full tuple.',
 'phase_old_RO':'UNKNOWN_NOT_EMITTED_DO_NOT_APPORTION'if phase else'NA_USE_AUTHORITATIVE_GLOBAL_MODEL_RO',
 'phase_live_detached_residual':'NA_NOT_A_PHASE_LOCAL_POPULATION'if phase else'NA_USE_OLD212_CUMULATIVE_SUCCESS_MINUS_RETIRE'}

def causes(new,old,summary,wire):
 G=new['global_record'];out={'global':panel(G,wire),'physical_phases':{},'old212_global_counters':old['global_counters'],'old212_commit_and_lifecycle':{k:old['global_counters'][k]for k in ('ft_access_attempts','commit_raw_probe_reached','raw_tag_fail_commit','relieve_calls','relieve_T_disabled','relieve_no_eligible','relieve_eligible_selected','detach_calls','detach_success','detached_retired','trigger_accepted_after_detach','trigger_denied_after_detach','commit_accepted','commit_denied')},'facts':[]}
 fields=old['schema_counter_fields'];oldphases=[r for r in new['old212_scope_projection']if r['record']=='PHASE'];phases=new['phase_records']
 for pid in range(len(G['kernel_catalog'])+2):
  rows=[phases[str(sid)+':'+str(pid)]for sid in range(64)];require(len(rows)==64,'phase64 absent');counts={k:sum(r['counters'][k]for r in rows)for k in G['counters']};hs={k:sum_sparse(rows,k)for k in G['histograms']};joint=sum_sparse(rows,'route_joint');record={'counters':counts,'histograms':hs,'route_joint':joint}
  pp=panel(record,wire,phase=True);pp.update(phase=pid,kernel_uid=rows[0]['kernel_uid'],kernel_scope=rows[0]['kernel_scope']);oldrows=[r for r in oldphases if r['phase']==pid];require(len(oldrows)==64,'old212 phase64 absent');pp['old212_event_counters']={k:sum(r['counters'][k]for r in oldrows)for k in fields};out['physical_phases'][str(pid)]=pp
 for k in G['counters']:require(sum(p['counts'][k]for p in out['physical_phases'].values())==G['counters'][k],'phase scalar rollup '+k)
 for k in fields:require(sum(p['old212_event_counters'][k]for p in out['physical_phases'].values())==old['global_counters'][k],'phase old212 event rollup '+k)
 ro=summary['mechanism_metrics']['full_mechanism_records']['readonly'];require({int(k)for k in ro}==set(range(64)),'oldRO64 missing');out['authoritative_oldmodel_RO_global']={f:sum((ro[str(s)]if str(s)in ro else ro[s])['summary'][f]for s in range(64))for f in ('accepted_global_reads','accepted_oracle_candidates','accepted_ro','transactions','merges','responses','detached')}
 pressure=out['global']['raw_counts']['RESERVATION_FAIL'];c=old['global_counters'];out['facts'].append({'code':'DETACH_NONZERO'if c['detach_success']else'DETACH_ZERO','measured_detach_success':c['detach_success'],'retired':c['detached_retired'],'statement':'Victim detach/retirement, immediate trigger acceptance and eventual request completion remain separate domains; nonzero and negative scientific outcomes are both valid.'})
 if pressure==0:out['facts'].append({'code':'NO_RAW_ALL_RESERVED_FAILURE_IN_COVERED_HEADS','count':0,'covered_denominator':G['counters']['covered'],'statement':'No raw RESERVATION_FAIL at covered frontend heads. Skipped upstream paths remain NA; this does not prove globally sufficient Tags or no unobserved pressure.'})
 if c['raw_tag_fail_commit']==0:out['facts'].append({'code':'NO_ACTUAL_COMMIT_TAG_FAIL','count':0,'commit_probe_denominator':c['commit_raw_probe_reached'],'statement':'Actual commit probes never returned Tag failure; inspect relief counters separately, without identifying commit invocations with frontend head-cycle exposures.'})
 out['interpretation_limits']=['All sums combine same fields over disjoint physical scopes only; no product of marginal percentages or invented joint.','A16 RESERVED count alone is not a newTag failure; matching HIT/HIT_RESERVED/SECTOR_MISS are kept distinct.','RO way eligibility is structural; route/requester admission joints do not establish later retry/critical path or counterfactual benefit.','No requester/victim causal kernel attribution from physical event phase. Cross-phase detach minus retirement is not a local population and must not be required nonnegative.','Old main61/r4 dynamic reasons are not backfilled; original failures/HOLD/negative results and input limits remain.','Current diagnostic F points do not create new S anchors, S/F pairs or cross-binary speedups.']
 return out

def review(aid):
 require(re.fullmatch(r'E\d{3}_[0-9a-f]{8}',aid)is not None,'bad attempt id');mf=APP/'FINAL_MANIFEST.json';require(ref(mf)['sha256']==MANIFEST_SHA,'exact final manifest changed');manifest=metadata(mf);scope=manifest['validation_scope']
 sys.path.insert(0,str(TOOLS));from coordinator import Coordinator,tooling_binding
 import tagpressure_validation as tv
 tooling_binding();coord=Coordinator();before=coord.snapshot();matches=[a for a in before['attempts']if a['attempt_id']==aid];require(len(matches)==1,'not actual registered attempt');a=matches[0];cid=a.get('condition_id');require(cid in manifest['conditions'],'not approved exact4 condition');cond=manifest['conditions'][cid];spec=read(cond['spec_ref']);q=read(cond['qualification']);require(ref(cond['qualification']['path'])['sha256']==spec['qualification_id'],'exact Qsha differs');a,e,qrow=accepted(before,aid,spec,cond['qualification']);require(qrow['qualification']==q,'exact Qbody differs')
 result=Path(a['result_directory']).resolve();require(result.parent==RESULTS and result.name==aid,'wrong original-owned resultdir');require(Path(e['path']).resolve()==result/'run_status.json','accepted pointer not exact status');require(ref(e['path'])['sha256']==e['sha256']==a['receipt_sha256'],'accepted status bytes changed');status=metadata(e['path']);require(status['status']=='COMPLETE_VALID'and status['independent_acceptance']=='PASS'and status['complete_input_verified']is True and status['validation']['status']=='PASS','actual terminal not complete independently accepted')
 require(status['attempt_id']==aid and status['identity']==spec['identity']and status['qualification_id']==spec['qualification_id']and status['exit_code']==0,'actual terminal source/input/normalexit differs');actualspec=metadata(result/'input_spec.json');audit=metadata(result/'input_audit.json');stored=copy.deepcopy(actualspec);stored.pop('input_audit',None);require(stored==spec and actualspec['input_audit']==audit==status['input_audit'],'frozen actualspec/inputaudit differs');summary=metadata(result/'terminal_summary.json');require(canon(summary)==canon(status['summary']),'accepted summary changed');contract=q['terminal_acceptance_required'];require(summary['instructions']==contract['expected_instructions']==audit['expected_full_instructions']==q['detach_observer_diagnostic']['expected_full_instructions'],'full instruction denominator not closed')
 require(q['source_identity']==manifest['source_identity']==scope['source_identity'],'source/main/archive/release scope differs');require(len(q['gates'])==20,'not exact20 independently signed source/input gates')
 for name,g in q['gates'].items():require(g['status']=='PASS'and g['production_driven']is True and ref(g['evidence_path'])['sha256']==g['evidence_sha256'],'exact gate changed '+name)
 adapter=tv.Adapter(scope);adapter.check(spec,qrow,audit);raw=result/'raw.log';require(raw.is_file()and raw.stat().st_size<=CAP,'missing/overcap completed raw');pre=raw.stat();feed=adapter.decoder.Feed(expected_slices=list(range(64)),registered_slice_count=64,expected_kernels=q['detach_observer_diagnostic']['expected_kernel_uids'],expected_flags={'T':True,'M':True,'ro_runtime':True},source_binding=manifest['source_identity'],old212_decoder_sha256=tv.OLD647)
 with raw.open('rb')as stream:old=adapter.fixed.Decoder(adapter.compat_schema).decode(adapter.decoder.TappingReader(stream,feed))
 new=feed.finish(old);post=raw.stat();require((pre.st_dev,pre.st_ino,pre.st_size,pre.st_mtime_ns)==(post.st_dev,post.st_ino,post.st_size,post.st_mtime_ns),'raw mutated during independent singlepass');require(old.get('status')=='VALID_OBSERVER_TERMINAL_DECLARATIONS_ONLY'and new.get('status')=='VALID_R5_OBSERVER_DECLARATIONS_ONLY','independent full64/source-bound observer decode failed '+str(new.get('reason')));require(new['raw_log_sha256']==status['raw_log_sha256']==summary['raw_log_sha256'],'independent same-raw SHA differs');d=summary['tagpressure_observer_diagnostic'];require(canon(old)==canon(d['r4_compat_observer'])and canon(new)==canon(d['r5_observer']),'independent decoded evidence differs from accepted exact summary')
 native=adapter.native_files(raw,spec,audit);require(native['documents']['NATIVE_EXIT']==status['native_exit_evidence']and ref(result/'NATIVE_EXIT.json')['sha256']==status['native_exit_receipt_sha256'],'true durable accepted normal exit docs differ');require(native['documents']['NATIVE_EXIT']['native_process']==a['process'],'native PID/startticks/boot ownership differs from charged attempt');validation=adapter.validate_summary(summary,spec,qrow,audit);require(validation['status']=='PASS','independent fullmodel/ROC1/drain/durable validation failed')
 life=summary['mechanism_metrics']['commandlist_lifecycle'];require(life['complete']is True and life['commands']==life['begin']==life['end']==contract['command_count']and life['final_snapshot_after_epoch_end']is True,'wholecommandlist not closed');require(new['global_record']['kernel_catalog']==contract['kernel_uids']==q['detach_observer_diagnostic']['expected_kernel_uids']and len(contract['kernel_uids'])<=16,'full ordered kernel catalog differs');cause=causes(new,old,summary,adapter.schema)
 after=coord.snapshot();aa,ee,qq=accepted(after,aid,spec,cond['qualification']);require(aa==a and ee==e and qq==qrow,'accepted endpoint changed during review');require(ref(mf)['sha256']==MANIFEST_SHA and read(cond['spec_ref'])==spec and ref(cond['qualification']['path'])['sha256']==spec['qualification_id']and ref(e['path'])['sha256']==e['sha256'],'final immutable inputs changed')
 return {'schema':'E2_R5_INDEPENDENT_FULL_APPLICATION_TERMINAL_AND_CAUSE_REVIEW_V1','status':'INDEPENDENT_REVIEW_OF_EXISTING_CURRENT_ACCEPTED_DIAGNOSTIC_POINT_PASS','attempt_id':aid,'workload':spec['identity']['workload'],'condition_id':cid,'scientific_scope':SCI,'pair':False,'source_identity':manifest['source_identity'],'identity':spec['identity'],'qualification_id':spec['qualification_id'],'instructions':summary['instructions'],'cycles':summary['cycles'],'kernel_uids':contract['kernel_uids'],'command_count':life['commands'],'evidence':{'final_manifest':ref(mf),'spec':cond['spec_ref'],'Q':cond['qualification'],'central_current_accepted_pointer':e,'run_status':ref(e['path']),'input_audit':ref(result/'input_audit.json'),'terminal_summary':ref(result/'terminal_summary.json'),'native4docs':native['refs'],'raw':{'path':str(raw),'sha256':new['raw_log_sha256'],'bytes':new['input_bytes'],'independent_raw_passes':1,'r5_substream_bytes':new['r5_bytes'],'r5_substream_sha256':new['r5_stream_sha256']},'parser_refs':{k:scope[k]for k in tv.REF_KEYS}},'observer_independent_decode':{'old212_status':old['status'],'newr5_status':new['status'],'registered_count':new['registered_slice_count'],'selected64':new['selected_slices']==list(range(64)),'global_closed':new['global_closure_declared']and new['global_epoch_closed_declared'],'snapshots':new['snapshot_count'],'old212_normalized_sha256':csha(old),'r5_normalized_sha256':csha(new)},'original_adapter_independent_validation':validation,'cause':cause,'scope_of_model_identity_check':'Exact accepted model summary revalidated by unchanged original fullmodel validator plus new source-bound adapter; original pre/post-run inspector exact input/source/config/main verification preserved by accepted inputaudit/status equality. This tool independently decodes old212+r5 and rawSHA once, validates actual durable ownership/exit/docs; it does not reread large trace/main/archive bodies or call Adapter.parse for another raw scan. Build archive/source identity is independently bound by true producer/native/source proofs checked by Adapter.','acceptance_authority':'Original sole E Coordinator accepted this exact paid endpoint. This read-only review inserts no registry acceptance and creates no pair.','actions':{'native_runs':0,'application_starts':0,'registry_CLIENT_source_Q_mutations':0,'independent_raw_passes':1}}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--attempt',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();require(out.is_relative_to(Path('/tmp'))and not out.exists(),'new unused /tmp output only');out.parent.mkdir(parents=True,exist_ok=True)
 try:r=review(a.attempt);code=0
 except Exception as e:r={'schema':'E2_R5_INDEPENDENT_FULL_APPLICATION_TERMINAL_AND_CAUSE_REVIEW_V1','status':'REVIEW_FAILED_CLOSED','attempt_id':a.attempt,'error':type(e).__name__+': '+str(e),'acceptance_granted':False,'no_polling_or_retry':True};code=1
 data=json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False)+'\n';require(len(data.encode())<=64*2**20,'review artifact exceeds64MiB bounded cap');out.write_text(data);return code
if __name__=='__main__':raise SystemExit(main())
