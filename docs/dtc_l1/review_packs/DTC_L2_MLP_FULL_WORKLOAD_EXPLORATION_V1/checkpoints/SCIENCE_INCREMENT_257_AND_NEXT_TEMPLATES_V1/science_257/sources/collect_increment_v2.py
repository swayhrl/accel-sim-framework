"""Normal snapshot, only newly accepted raw opened beyond immutable198 anchor."""
import copy,datetime,hashlib,importlib.util,json,pathlib,sys
P=pathlib.Path;HERE=P(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from io_chain_audit import audit
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
OUT=A/'agents/E/results_increment_v2'
ANCHOR=A/'agents/E/results_increment_v1/20261027T145915Z'
TOOL=A/'docs-worktree/docs/dtc_l1/review_packs/DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_V1/agents/D'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,x):p.write_bytes((json.dumps(x,indent=2,sort_keys=True)+'\n').encode())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 OUT.mkdir(parents=True,exist_ok=True);stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');run=OUT/stamp;run.mkdir()
 base=load('increment_v2_report',TOOL/'report_v1/build_report.py');side=load('increment_v2_reasons',TOOL/'raw_reason_v1/raw_reason_sidecar.py');merger=load('increment_v2_merger',TOOL/'raw_reason_v1/merge_reason_report.py')
 previous_path=ANCHOR/'report.json';previous=read(previous_path);assert sha(previous_path)=='9d354efbde4f592ed278edb959e374b86a2001943092fd9996cf418e0922a117'
 older_path=A/'derived_reports/checkpoint_04/closed_raw_reasons.json';old_side=read(older_path);anchor_side=read(ANCHOR/'NEW_RAW_REASONS.json')
 old_side['rows']+=anchor_side['rows'];old_side['sources']+=anchor_side['sources'];assert len({x['cohort']for x in old_side['rows']})==198
 report=base.acquire(R,'fce10d92eb09bc8f562b84a5a84b202bbf1ea385')
 def cellmap(r):return{c['cohort']:c for profiles in r['table'].values()for cells in profiles.values()for c in cells.values()}
 oldcells=cellmap(previous);cells=cellmap(report);assert sum(c['accepted']for c in oldcells.values())==198
 new=[c for c,v in cells.items()if v['accepted']and not oldcells.get(c,{}).get('accepted')]
 allrows=[];sources={};errors=[];scope=read(TOOL/'report_v1/input_stream_scope.json');declared={r['input_digest']:r for r in scope['rows']}
 matrix=read(R/'control/MATRIX_CURRENT.json');points={p['cohort']:p for p in matrix['points']};io_rows=[]
 print(json.dumps({'stage':'snapshot','utc':report['utc'],'accepted':sum(c['accepted']for c in cells.values()),'new_raw_only':len(new)}),flush=True)
 for index,c in enumerate(new):
  point=points[c];rp=R/'analysis'/(c+'.RESULT.json');result=read(rp);proof=result['proof']
  identity=dict(cohort=c,input_digest=point['input_digest'],program=point['program'],suite=point['suite'],cell=point['cell'],profile=point['profile'],uuid=result['uuid'],state=result['state'],cycles=result['cycles'],result_path=str(rp),result_sha256=sha(rp))
  try:
   raw,closure=side.closed_source(R,P('/root/data/dtc_hash_downstream18_20261027_v1'),point,result,sources)
   io=audit(R,c,result);io_rows.append(dict(cohort=c,**io))
   scan=side.scan_raw(raw,proof);ss=declared.get(point['input_digest'],{})
   complete=len(scan['unique_kernel_uids'])==point['expected']['kernels']and scan['stream_ids']==ss.get('stream_ids')and ss.get('complete_header_coverage')is True and not scan['unbound_reason_lines']and not scan['unparsed_reason_lines']
   values=[f['reservation_fails']for f in scan['last_cumulative_frame_by_stream'].values()];total=sum(values)if values and all(v is not None for v in values)else None
   known=scan['sum_known_positive_reason_contributions'];match=known==total if known is not None and total is not None else None
   allrows.append(dict(identity,status='SIDECAR_EXTRACTED_CLOSED_ACCEPTED',source_closure=closure,closed_raw=scan,IO_extra_chain=io,
    complete_declared_stream_stats_coverage=complete,observed_last_frame_reservation_fail_total=total,known_reason_sum_matches_observed_reservation_fail_total=match,
    scope='VERIFIED_SINGLE_STREAM_DECLARED_TRACE'if complete and len(scan['stream_ids'])==1 else'PER_STREAM_LAST_FRAME_EVIDENCE_ONLY'))
  except(OSError,ValueError,KeyError,AssertionError)as error:
   allrows.append(dict(identity,status='SIDECAR_EVIDENCE_ERROR_NO_RECLASSIFICATION',error=repr(error)));errors.append(dict(cohort=c,error=repr(error)))
  if index%5==0:print(json.dumps({'stage':'new_raw','complete':index+1,'total':len(new),'errors':len(errors)}),flush=True)
 increment=dict(schema='DTC_L2_MLP_CLOSED_RAW_REASON_SIDECAR_V2',utc=report['utc'],root=str(R),rows=allrows,sources=list(sources.values()),model_starts=0,
  previous_checkpoint_path=str(previous_path),previous_checkpoint_sha256=sha(previous_path),reused_raw_rows=198,
  raw_policy='Only newly accepted cells since198 anchor opened; prior198 raw records reused by immutable RESULT/UUID identity')
 merged=copy.deepcopy(old_side);merged['rows']+=allrows;merged['utc']=report['utc'];merged['sources']+=list(sources.values());joined=merger.join_sidecar(report,merged)
 report['incremental_raw_reason_source']=dict(path=str(run/'NEW_RAW_REASONS.json'),anchor=str(previous_path),anchor_sha256=sha(previous_path))
 put(run/'NEW_RAW_REASONS.json',increment);put(run/'IO_CHAIN_AUDIT.json',io_rows);put(run/'report.json',report)
 summary=dict(schema='DTC_RESULTS_INCREMENT_V2_CAPTURE',utc=report['utc'],run_path=str(run),previous_checkpoint_path=str(previous_path),previous_checkpoint_sha256=sha(previous_path),previous_utc=previous['utc'],previous_accepted=198,current_accepted=sum(c['accepted']for c in cells.values()),newly_accepted=new,state_counts=report['state_counts'],raw_scanned_new_count=len(allrows),new_raw_evidence_errors=errors,raw_join=joined,
  source_hashes={name:sha(path)for name,path in {'base_generator':TOOL/'report_v1/build_report.py','reason_parser':TOOL/'raw_reason_v1/raw_reason_sidecar.py','merger':TOOL/'raw_reason_v1/merge_reason_report.py','io_audit':HERE/'io_chain_audit.py','collector':P(__file__)}.items()},
  anchor_reason_sha256=sha(ANCHOR/'NEW_RAW_REASONS.json'),older_reason_sha256=sha(older_path),files=dict(report_sha256=sha(run/'report.json'),new_raw_sha256=sha(run/'NEW_RAW_REASONS.json')),model_launches=0,production_changes=0,old_72_matrix_scanned=False)
 put(run/'CAPTURE.json',summary);put(OUT/'LATEST_CAPTURE.json',summary);print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
