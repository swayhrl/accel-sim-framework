"""New normal snapshot + raw-reason reads only beyond checkpoint04 accepted set."""
import copy,datetime,hashlib,importlib.util,json,pathlib
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
OUT=A/'agents/E/results_increment_v1'
TOOL=A/'docs-worktree/docs/dtc_l1/review_packs/DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_V1/agents/D'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,x):p.write_bytes((json.dumps(x,indent=2,sort_keys=True)+'\n').encode())
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
    OUT.mkdir(parents=True,exist_ok=True);stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run=OUT/stamp;run.mkdir()
    base=load('readonly_increment_report',TOOL/'report_v1/build_report.py')
    side=load('readonly_increment_reasons',TOOL/'raw_reason_v1/raw_reason_sidecar.py')
    merger=load('readonly_increment_merger',TOOL/'raw_reason_v1/merge_reason_report.py')
    previous_path=A/'derived_reports/checkpoint_04/dashboard/report.json';previous=read(previous_path)
    old_side_path=A/'derived_reports/checkpoint_04/closed_raw_reasons.json';old_side=read(old_side_path)
    report=base.acquire(R,'fce10d92eb09bc8f562b84a5a84b202bbf1ea385')
    def cellmap(r):return{c['cohort']:c for profiles in r['table'].values()for cells in profiles.values()for c in cells.values()}
    oldcells=cellmap(previous);cells=cellmap(report)
    new=[c for c,v in cells.items()if v['accepted']and not oldcells.get(c,{}).get('accepted')]
    allrows=[];sources={};errors=[];scope=read(TOOL/'report_v1/input_stream_scope.json');declared={r['input_digest']:r for r in scope['rows']}
    matrix=read(R/'control/MATRIX_CURRENT.json');points={p['cohort']:p for p in matrix['points']}
    for c in new:
        point=points[c];result=read(R/'analysis'/(c+'.RESULT.json'));proof=result['proof']
        identity=dict(cohort=c,input_digest=point['input_digest'],program=point['program'],suite=point['suite'],cell=point['cell'],profile=point['profile'],
            uuid=result['uuid'],state=result['state'],cycles=result['cycles'],result_path=str(R/'analysis'/(c+'.RESULT.json')),result_sha256=sha(R/'analysis'/(c+'.RESULT.json')))
        try:
            raw,closure=side.closed_source(R,P('/root/data/dtc_hash_downstream18_20261027_v1'),point,result,sources)
            scan=side.scan_raw(raw,proof);ss=declared.get(point['input_digest'],{})
            complete=len(scan['unique_kernel_uids'])==point['expected']['kernels']and scan['stream_ids']==ss.get('stream_ids')and ss.get('complete_header_coverage')is True and not scan['unbound_reason_lines']and not scan['unparsed_reason_lines']
            values=[f['reservation_fails']for f in scan['last_cumulative_frame_by_stream'].values()]
            total=sum(values)if values and all(v is not None for v in values)else None
            known=scan['sum_known_positive_reason_contributions'];match=known==total if known is not None and total is not None else None
            allrows.append(dict(identity,status='SIDECAR_EXTRACTED_CLOSED_ACCEPTED',source_closure=closure,closed_raw=scan,
                complete_declared_stream_stats_coverage=complete,observed_last_frame_reservation_fail_total=total,
                known_reason_sum_matches_observed_reservation_fail_total=match,
                scope='VERIFIED_SINGLE_STREAM_DECLARED_TRACE'if complete and len(scan['stream_ids'])==1 else'PER_STREAM_LAST_FRAME_EVIDENCE_ONLY'))
        except(OSError,ValueError,KeyError,AssertionError)as ex:
            allrows.append(dict(identity,status='SIDECAR_EVIDENCE_ERROR_NO_RECLASSIFICATION',error=repr(ex)));errors.append(c)
    increment=dict(schema='DTC_L2_MLP_CLOSED_RAW_REASON_SIDECAR_V1',utc=report['utc'],root=str(R),rows=allrows,skipped=[],sources=list(sources.values()),
        model_starts=0,previous_checkpoint_path=str(previous_path),previous_checkpoint_sha256=sha(previous_path),
        previous_reason_path=str(old_side_path),previous_reason_sha256=sha(old_side_path),
        raw_policy='Only newly accepted cells since checkpoint04 are opened; old raw reason records reused by immutable result identity')
    merged=copy.deepcopy(old_side);merged['rows']+=allrows;merged['utc']=report['utc'];merged['sources']+=list(sources.values())
    joined=merger.join_sidecar(report,merged)
    report['incremental_raw_reason_source']=dict(path=str(run/'NEW_RAW_REASONS.json'),previous_sidecar=str(old_side_path),previous_sidecar_sha256=sha(old_side_path))
    put(run/'NEW_RAW_REASONS.json',increment);put(run/'report.json',report)
    summary=dict(schema='DTC_RESULTS_INCREMENT_V1_CAPTURE',utc=report['utc'],run_path=str(run),
        previous_checkpoint_path=str(previous_path),previous_checkpoint_sha256=sha(previous_path),previous_utc=previous['utc'],
        previous_accepted=sum(c['accepted']for c in oldcells.values()),current_accepted=sum(c['accepted']for c in cells.values()),
        newly_accepted=new,state_counts=report['state_counts'],raw_scanned_new_count=len(allrows),new_raw_evidence_errors=errors,
        raw_join=joined,source_hashes=dict(base_generator=sha(TOOL/'report_v1/build_report.py'),reason_parser=sha(TOOL/'raw_reason_v1/raw_reason_sidecar.py'),merger=sha(TOOL/'raw_reason_v1/merge_reason_report.py')),
        files=dict(report_sha256=sha(run/'report.json'),new_raw_sha256=sha(run/'NEW_RAW_REASONS.json')),
        model_launches=0,production_changes=0,old_72_matrix_scanned=False)
    put(run/'CAPTURE.json',summary);put(OUT/'LATEST_CAPTURE.json',summary)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
