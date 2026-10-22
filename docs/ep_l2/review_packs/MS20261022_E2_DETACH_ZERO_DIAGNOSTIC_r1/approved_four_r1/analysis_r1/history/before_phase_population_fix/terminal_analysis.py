#!/usr/bin/env python3
"""Read-only independent review of one centrally accepted approved-four endpoint.
No controller, registry writes, launches, retries, trace-body reads or acceptance API.
"""
import argparse,copy,hashlib,importlib.util,json,re,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
PACK=ROOT/'docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1'
APPROVED=PACK/'approved_four_r1';TOOLS=ROOT/'util/ep_l2/mechanism_e'
RESULTS=Path('/workspace/ep_l2_ms20261019_e_results');CAP=384*1024**2;META_CAP=16*1024**2
SCI='DETACH_OBSERVER_DIAGNOSTIC_POINT_V1'
WORKLOADS=('cfd_097k','dwt2d','vectorAdd_4M','convolutionSeparable')
EXPECTED_DECODER='647510163053d30773176578cf35c10e0aea0a1256af366feba520820d0e11d4'

def require(ok,message):
 if not ok:raise ValueError(message)
def unique(pairs):
 out={}
 for k,v in pairs:require(k not in out,'duplicate metadata JSON key '+k);out[k]=v
 return out
def canon(x):return json.dumps(json.loads(json.dumps(x,allow_nan=False)),sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def csha(x):return hashlib.sha256(canon(x)).hexdigest()
def metadata(path):
 p=Path(path);require(p.is_file() and p.stat().st_size<=META_CAP,'small metadata absent/oversized '+str(p));return json.loads(p.read_text(),object_pairs_hook=unique)
def smallsha(path):
 p=Path(path);require(p.is_file() and p.stat().st_size<=META_CAP,'small hash absent/oversized '+str(p));return hashlib.sha256(p.read_bytes()).hexdigest()
def mref(path):return {'path':str(path),'sha256':smallsha(path),'bytes':Path(path).stat().st_size}
def load_code(path,name):
 s=importlib.util.spec_from_file_location(name,str(path));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def require_accepted(item,attempt_id,spec,qpath):
 """Authoritative central metadata prerequisites. Never infer from process exit."""
 rows=[a for a in item['attempts'] if a['attempt_id']==attempt_id];require(len(rows)==1,'exact attempt absent/duplicate');a=rows[0]
 require(a.get('state')=='COMPLETE_VALID' and a.get('actual_start') is True,'Coordinator attempt is not real COMPLETE_VALID')
 entry=item['accepted_results'].get(attempt_id);require(isinstance(entry,dict),'accepted_results exact pointer missing')
 require(entry.get('scientific_scope')==SCI and a.get('scientific_scope')==SCI,'central diagnostic scope differs')
 require(a['identity']==entry['identity']==spec['identity'],'central identity differs from approved spec')
 require(a['qualification_id']==entry['qualification_id']==spec['qualification_id'],'central qualification differs')
 require(entry['run_key']==a['run_key']==csha(spec['identity']),'central run key differs')
 qrow=item['qualifications'].get(spec['qualification_id']);require(isinstance(qrow,dict),'registered perinput Q absent')
 require(Path(qrow['path']).resolve()==Path(qpath).resolve() and qrow['sha256']==spec['qualification_id'],'registered Q path/hash differs')
 require('qualification:'+spec['qualification_id'] not in item.get('scientific_holds',{}),'qualification has active hold')
 return a,entry,qrow

class DecodingReader:
 """One bounded raw pass, digest plus numeric-only final PHASE capture.
 The fixed independently-bound decoder alone judges frame validity.
 """
 def __init__(self,stream):self.stream=stream;self.raw_sha=hashlib.sha256();self.phases={};self.bytes=0
 def readline(self,limit):
  line=self.stream.readline(limit);self.raw_sha.update(line);self.bytes+=len(line)
  require(self.bytes<=CAP,'raw exceeds approved384MiB endpoint cap')
  if line.startswith(b'EPL2DETACH_DIAG_V1|'):
   r=json.loads(line.split(b'|',1)[1],object_pairs_hook=unique)
   if r.get('record')=='PHASE':self.phases[(r['slice'],r['phase'])]=r
  return line

def readonly_totals(summary):
 ro=summary['mechanism_metrics']['full_mechanism_records']['readonly'];require({int(k) for k in ro}==set(range(64)),'old readonly scope missing64 slices')
 fields=('accepted_global_reads','accepted_oracle_candidates','accepted_ro','transactions','merges','responses','detached')
 rows={str(i):(ro[str(i)] if str(i) in ro else ro[i])['summary'] for i in range(64)}
 return {'global':{f:sum(rows[str(i)][f] for i in range(64)) for f in fields},'slices':{k:{f:v[f] for f in fields} for k,v in rows.items()},'domain_note':'Sum each same-field measure over64 disjoint physical slices. Accepted requests, transaction creations, merged requesters, responses and frontend head-cycle exposures are different domains; no equality forced.'}

def phase_projection(phases,observer,project):
 catalog={int(k):v for k,v in observer['phase_catalog'].items()};out={}
 require(set(phases)=={(sid,p) for sid in range(64) for p in catalog},'numeric finalphase tap missing exact validated memberships')
 for p,uid in sorted(catalog.items()):
  rows={str(sid):phases[(sid,p)]['counters'] for sid in range(64)}
  counts={f:sum(rows[str(sid)][f] for sid in range(64)) for f in observer['schema_counter_fields']}
  panel=project.panels(counts);require(not panel['errors'],'invalid phase numeric values')
  out[str(p)]={'phase':p,'kernel_uid':uid,'kernel_scope':phases[(0,p)]['kernel_scope'],'global_samephase_counters':counts,'global_panels':panel,'slice_counters':rows,'oldaccepted_RO_perphase':'UNKNOWN_NOT_EMITTED_DO_NOT_APPORTION','metadata_not_summed':True}
 for f in observer['schema_counter_fields']:
  require(sum(row['global_samephase_counters'][f] for row in out.values())==observer['global_counters'][f],'numeric phase rollup differs '+f)
 return {'rows':out,'semantics':'Disjoint physical active-kernel state buckets (0 unassigned,1 overlapunknown,>=2 active kernel UID), never requester/victim causal ownership. PHASE live_detached/closed/flags are parentcumulative metadata, not summed. Source fullphase count<=18 includes<=16 kernels.'}

def causal_observations(c,old):
 """Conditional measured facts only; no SGEMM-specific universal cause."""
 def need(k):require(type(c.get(k)) is int and 0<=c[k]<2**64,'missing/invalid measured counter '+k);return c[k]
 facts=[]
 def add(code,keys,text):facts.append({'code':code,'measured':{k:need(k) for k in keys},'statement':text})
 if need('detach_success')>0:add('NONZERO_DETACH',['detach_success','detached_retired','trigger_accepted_after_detach','trigger_denied_after_detach'],'Successful victim detaches measured; victim retirement and immediate triggering-call acceptance/denial remain separate. Nonzero is a legal result.')
 else:add('ZERO_DETACH',['detach_success'],'Zero detach in this new source/condition only; inspect conditional stage distributions rather than infer globally sufficient Tags.')
 if need('ro_admits')==0 and old['transactions']==0:add('NO_TRANSACTION_CREATION',['ro_admits','ro_merges','certified_resident_hits','candidate_deferred_or_native'],'No RO transaction creations in observer and authoritative oldmodel domains. Candidate heads/residenthits/requester merges remain distinct.')
 if need('raw_reservation_fail')==0:add('NO_COVERED_RAW_TAG_PRESSURE',['raw_reservation_fail','observed_heads','probe_skipped'],'No all-reserved raw Tag outcome at covered/probed frontend heads. Upstream-skipped paths are unobserved, not global Tag sufficiency.')
 for key,code,text in [('pressure_no_live_ro','NO_SAME_SET_LIVE_RO','Pressure heads with no same-set live RO victim.'),('pressure_live_ro_no_eligible','LIVE_BUT_NO_ELIGIBLE','Pressure heads with same-set liveRO but no eligible victim; ordered way reasons do not provide perhead causal shares.'),('way_reuse_seen','STICKY_REUSE_WAY_EXPOSURES','Exclusive firstreason reused-way exposures; never unique victims or count of blocked heads.'),('way_no_missing','NO_MISSING_WAY_EXPOSURES','Exclusive firstreason no-missing-requiredsector way exposures; separate from stickyreuse precedence.'),('eligible_prod_probe_not_reached','ELIGIBLE_NOT_REACHED','Actual conditional eligible shadow-pressure subset did not reach production probe.'),('eligible_relief_not_consulted','ELIGIBLE_NOT_CONSULTED','Actual conditional eligible subset reached production probe but relief not consulted; distinct from noeligible.'),('eligible_frontend_denied','ELIGIBLE_FRONTEND_DENIED','Eligible frontend denied subset, not assumed eventualcommit linkage.'),('trigger_denied_after_detach','DETACHED_VICTIM_TRIGGER_DENIED','Victim detach succeeded before triggering invocation later denied; not failed victimdetach and no laterretry measurement.')]:
  if need(key)>0:add(code,[key],text)
 return facts

def review(attempt_id,spec_path,qpath):
 require(re.fullmatch(r'E\d{3}_[0-9a-f]{8}',attempt_id) is not None,'bad actual attemptid')
 spec=metadata(spec_path);q=metadata(qpath);w=spec['identity']['workload'];require(w in WORKLOADS,'not approvedfour workload')
 require(Path(spec_path).resolve()==(APPROVED/'specs'/(w+'_F_SPEC.json')).resolve(),'not final approvedspec path')
 require(Path(qpath).resolve()==(APPROVED/'qualifications'/(w+'_F_QUALIFICATION.json')).resolve(),'not final perinput Q path')
 require(q['status']=='INDEPENDENTLY_QUALIFIED' and q['source_identity']['core_source_commit']=='9243f769620653f2a9d4df5599e9581e9dae6067' and q['source_identity']['binary_sha256']=='d99ac88d60a596b123765009420a85eea1463c01e88807a8876ae946e380fd13' and q['source_identity']['framework_source_commit']=='9dd1ee57a83d83b56b7874bc7c716185ab52c8f7','not exact independentr4 Q')
 bindings=metadata(Path(__file__).parent/'TOOL_BINDINGS.json')
 for t in bindings['tools']:require(smallsha(t['path'])==t['sha256'],'independentreview dependency changed '+t['path'])
 require(len(q['gates'])==19,'missing original18 plus observer gate')
 for name,g in q['gates'].items():require(g['status']=='PASS' and g['production_driven'] is True and smallsha(g['evidence_path'])==g['evidence_sha256'],'changed/nonpassing exactsource gate '+name)
 scope=q['detach_observer_diagnostic']['validation_scope'];require(scope['observer_decoder']['sha256']==EXPECTED_DECODER and Path(scope['observer_decoder']['path']).resolve()==(PACK/'parser_recovery/decoder_samecycle_close.py').resolve(),'not fixed samecycle decoder')
 require(smallsha(qpath)==spec['qualification_id'],'approvedspec Qsha differs')
 sys.path.insert(0,str(TOOLS));from coordinator import Coordinator
 import detach_validation as dv
 coord=Coordinator();before=coord.snapshot();a,entry,qrow=require_accepted(before,attempt_id,spec,qpath)
 require(qrow['qualification']==q and qrow['sha256']==smallsha(qpath),'registered Q body/file mismatch')
 result=Path(a['result_directory']).resolve();require(result.parent==RESULTS and result.name==attempt_id,'unowned result directory')
 require(Path(entry['path']).resolve()==result/'run_status.json','acceptedresults not exact originalrunstatus')
 require(smallsha(entry['path'])==entry['sha256']==a['receipt_sha256'],'accepted runstatus changed')
 status=metadata(entry['path']);require(status['status']=='COMPLETE_VALID' and status['independent_acceptance']=='PASS' and status['complete_input_verified'] is True and status['validation']['status']=='PASS','actual terminal not independent completeinput accepted')
 require(status['attempt_id']==attempt_id and status['identity']==spec['identity'] and status['qualification_id']==spec['qualification_id'],'runstatus identity differs')
 actualspec=metadata(result/'input_spec.json');audit=metadata(result/'input_audit.json');stored=copy.deepcopy(actualspec);stored.pop('input_audit',None)
 require(stored==spec and actualspec['input_audit']==audit==status['input_audit'],'postrunaccepted/inputspec/audit metadata differs')
 summary=metadata(result/'terminal_summary.json');require(canon(status['summary'])==canon(summary),'accepted runstatus terminalsummary differs')
 require(status['exit_code']==0 and summary['instructions']==audit['expected_full_instructions']==q['detach_observer_diagnostic']['expected_full_instructions'],'native/fullinstructions incomplete')
 adapter=dv.Adapter(scope);adapter.check(spec,qrow,audit)
 raw=result/'raw.log';require(raw.is_file() and raw.stat().st_size<=CAP,'raw absent/oversized')
 Decoder=adapter.decoder_factory
 with raw.open('rb') as stream:
  tap=DecodingReader(stream);decoded=Decoder(adapter.schema).decode(tap)
 require(decoded.get('status')=='VALID_OBSERVER_TERMINAL_DECLARATIONS_ONLY','independent fixeddecoder failed: '+str(decoded.get('reason')))
 require(tap.raw_sha.hexdigest()==status['raw_log_sha256']==summary['raw_log_sha256'],'singlepass rawSHA differs')
 require(canon(decoded)==canon(summary['detach_observer_diagnostic']['observer']),'independent decode differs from accepted exactsummary')
 native=adapter.native_files(raw,spec,audit);require(native['documents']['NATIVE_EXIT']==status['native_exit_evidence'] and smallsha(result/'NATIVE_EXIT.json')==status['native_exit_receipt_sha256'],'native accepted exit evidence differs')
 require(native['documents']['NATIVE_EXIT']['native_process']==a['process'],'actual native identity differs from central chargedattempt')
 validation=adapter.validate_summary(summary,spec,qrow,audit);require(validation['status']=='PASS','original full64/ROC1/durable validation failed')
 contract=q['terminal_acceptance_required'];catalog={int(k):v for k,v in decoded['phase_catalog'].items()};uids=sorted(v for k,v in catalog.items() if k>=2)
 require(uids==sorted(contract['kernel_uids']) and len(uids)<=16,'full kernel catalog mismatch')
 life=summary['mechanism_metrics']['commandlist_lifecycle'];require(life['complete'] is True and life['commands']==life['begin']==life['end']==contract['command_count'] and life['final_snapshot_after_epoch_end'] is True,'wholecommandlist/kernel closeout incomplete')
 sys.path.insert(0,str(PACK/'analysis_r4'));project=load_code(PACK/'analysis_r4/project.py','_e_four_numeric_project');old=readonly_totals(summary);panels=project.panels(decoded['global_counters']);require(not panels['errors'],'global numerical projection invalid')
 phases=phase_projection(tap.phases,decoded,project);after=coord.snapshot();aa,ee,qq=require_accepted(after,attempt_id,spec,qpath);require(aa==a and ee==entry and qq==qrow,'accepted endpoint/Q changed during read-only review');require(smallsha(qpath)==spec['qualification_id'] and metadata(spec_path)==spec and smallsha(entry['path'])==entry['sha256'],'immutable source/spec/Q/receipt changed during review')
 out={'schema':'E2_APPROVED_FOUR_INDEPENDENT_TERMINAL_AND_CAUSE_REVIEW_V1','status':'INDEPENDENT_REVIEW_OF_EXISTING_CENTRAL_ACCEPTANCE_PASS','attempt_id':attempt_id,'workload':w,'pair':False,'scientific_scope':SCI,'source_identity':q['source_identity'],'identity':spec['identity'],'qualification_id':spec['qualification_id'],'evidence':{'approvedspec':mref(spec_path),'Q':mref(qpath),'central_accepted_pointer':entry,'runstatus':mref(result/'run_status.json'),'inputaudit':mref(result/'input_audit.json'),'summary':mref(result/'terminal_summary.json'),'raw':{'path':str(raw),'sha256':tap.raw_sha.hexdigest(),'bytes':tap.bytes,'passes':1},'native4docs':native['refs'],'fixedobserverdecoder':scope['observer_decoder'],'schema':scope['observer_schema'],'numeric_tool':mref(PACK/'analysis_r4/project.py')},'acceptance_authority':'Original unique E Coordinator alreadyaccepted thisexact endpoint; this tool is an independent read-only review, never inserts an acceptedrecord or changes status.','postrun_complete_input_evidence':'CentralCOMPLETE_VALID+complete_input_verified and exact inputaudit/runstatus/inputspec equality preserve originalrunner postrun inspect(spec,launch_check=False)==audit result. Large trace/source/main identities are not rehashed again by this tool.','fullinstructions':summary['instructions'],'cycles':summary['cycles'],'fullkernel_uids':uids,'command_count':life['commands'],'actual_fixeddecoder':{'status':decoded['status'],'snapshot_count':decoded['snapshot_count'],'final_cycle':decoded['final_cycle'],'same_cycle_lifecycle_closures':decoded.get('same_cycle_lifecycle_closures',0),'schema_fields':len(decoded['schema_counter_fields'])},'original_adapter_validation':validation,'authoritative_oldmodel_RO':old,'observer_global':panels,'observer_slice_counters':decoded['slice_counters'],'phase_projection':phases,'conditional_measured_facts':causal_observations(decoded['global_counters'],old['global']),'interpretation_limits':['Headcycle, wayexposure, transaction, mergedrequester, responses, packets and sectors are distinct; never sumdifferent populations or force acceptedrequests=headexposures.','Actual eligible joints/firstcallcapacity checked/unobserved/lineNA retained. Notconsulted is not pass/fail or noeligible; lineNA is subset of unobserved.','Samples capped64 examples; no criticalpath, laterretry or victimcausalkernel attribution.','Valid nonzerodetach preserved; triggerdeniedafterdetach is legal and doesnot invalidate victim success.','No oldmain61 dynamic backfill, oldS/newF speedup or newSbaseline/pair.','Allscientific input/model limitations and historical negative/failed/HOLD results remain.']}
 return out

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--attempt',required=True);ap.add_argument('--spec',type=Path,required=True);ap.add_argument('--qualification',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
 require(args.out.resolve().is_relative_to(Path('/tmp')) and not args.out.exists(),'new review output must be an unused /tmp path; never overwrite evidence or central files')
 args.out.parent.mkdir(parents=True,exist_ok=True)
 try:r=review(args.attempt,args.spec,args.qualification)
 except Exception as e:r={'schema':'E2_APPROVED_FOUR_INDEPENDENT_TERMINAL_AND_CAUSE_REVIEW_V1','status':'REVIEW_FAILED_CLOSED','attempt_id':args.attempt,'error':type(e).__name__+': '+str(e),'acceptance_granted':False};code=1
 else:code=0
 b=json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False)+'\n';require(len(b.encode())<=32*1024**2,'review artifact exceeds32MiB cap');args.out.write_text(b);return code
if __name__=='__main__':raise SystemExit(main())
