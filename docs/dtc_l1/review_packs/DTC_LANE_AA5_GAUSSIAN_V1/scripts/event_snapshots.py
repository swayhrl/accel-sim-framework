"""Independent decoder: exact 64-SM normal-stat snapshots, never sum snapshots."""
import re
SENTINEL=(1<<64)-1
FIELDS=['requests','idle','membar','config','unspecified','ordinary_commits','changed','retained_at_event','reclaimed_at_event','no_op_requests','first_request_cycle','last_request_cycle','first_ordinary_commit_cycle','last_ordinary_commit_cycle','pending_first_request','pending_last_request','event_records_omitted']
class QualificationError(ValueError):pass

def snapshot(text,K,expected_cycle=None):
    cycles=re.findall(r'^gpu_tot_sim_cycle\s*=\s*(\d+)\s*$',text,re.M)
    if len(cycles)!=1:raise QualificationError('PUBLIC_CYCLE_MISSING_OR_DUPLICATE')
    cycle=int(cycles[0])
    if expected_cycle is not None and cycle!=expected_cycle:raise QualificationError('PUBLIC_CYCLE_WRONG_BOUNDARY')
    begins=list(re.finditer(r'^DTC_INVALIDATE_V1_SNAPSHOT_BEGIN version=1 sms=(\d+) cycle=(\d+) no_event_cycle_sentinel=(\d+)\s*$',text,re.M))
    ends=list(re.finditer(r'^DTC_INVALIDATE_V1_SNAPSHOT_END version=1 sms=(\d+) cycle=(\d+)\s*$',text,re.M))
    lines=re.findall(r'^DTC_INVALIDATE_V1_SUMMARY(?:\s.*)?$',text,re.M)
    if K==0:
        if lines or begins or ends:raise QualificationError('UNEXPECTED_K0_EVENT_EXPORT')
        return dict(K=0,public_cycle=cycle,event_fields='UNAVAILABLE_K0_NOT_OUTPUT_NOT_OBSERVED_ZERO',per_SM='UNAVAILABLE',reclaimed_at_event='UNAVAILABLE')
    if len(begins)!=1 or len(ends)!=1:raise QualificationError('NORMAL_FRAME_MISSING_DUPLICATE_OR_TRUNCATED')
    begin,end=begins[0],ends[0]
    if begin.start()>=end.start() or tuple(map(int,begin.groups()))!=(64,cycle,SENTINEL) or tuple(map(int,end.groups()))!=(64,cycle):raise QualificationError('FRAME_POPULATION_CYCLE_OR_SENTINEL')
    inside=re.findall(r'^DTC_INVALIDATE_V1_SUMMARY(?:\s.*)?$',text[begin.end():end.start()],re.M)
    if inside!=lines:raise QualificationError('UNFRAMED_PRIVATE_OR_MIXED_SNAPSHOT_ROWS')
    if len(lines)!=64:raise QualificationError('SM_COUNT_MISSING_TRUNCATED_OR_DUPLICATE')
    records={}
    for line in lines:
        parts=line.split()[1:];record={}
        for token in parts:
            m=re.fullmatch(r'([a-z_]+)=(\d+)',token)
            if not m or m[1] in record:raise QualificationError('MALFORMED_OR_DUPLICATE_FIELD')
            record[m[1]]=int(m[2])
        if set(record)!=set(['sm']+FIELDS):raise QualificationError('SUMMARY_FIELDS_MISSING_OR_UNKNOWN')
        sm=record.pop('sm')
        if sm not in range(64) or sm in records:raise QualificationError('SM_ID_DUPLICATE_OR_OUT_OF_RANGE')
        if record['idle']+record['membar']+record['config']+record['unspecified']!=record['requests']:raise QualificationError('ORIGIN_BALANCE')
        if record['changed']!=record['retained_at_event']+record['reclaimed_at_event']:raise QualificationError('MAPPING_BALANCE')
        if record['no_op_requests']>record['requests']:raise QualificationError('NOOP_RANGE')
        for count,prefix in [('requests','request'),('ordinary_commits','ordinary_commit')]:
            first=record['first_'+prefix+'_cycle'];last=record['last_'+prefix+'_cycle']
            if record[count]==0:
                if first!=SENTINEL or last!=SENTINEL:raise QualificationError('NO_EVENT_SENTINEL')
            elif not (0<=first<=last<=cycle):raise QualificationError('EVENT_TIMESTAMP_OUTSIDE_SNAPSHOT')
        records[sm]=record
    if set(records)!=set(range(64)):raise QualificationError('SM_ID_SET')
    sums={key:sum(v[key] for v in records.values()) for key in FIELDS if not key.startswith(('first_','last_','pending_'))}
    return dict(K=1,public_cycle=cycle,per_SM=records,totals=sums,reclaimed_at_event=sums['reclaimed_at_event'],scope='ONE_COMPLETE_NORMAL_STAT_SNAPSHOT; count fields summed across SM only')

def fixture_snapshots(text,K):
    pattern=r'^AA5_EXPORT_SNAPSHOT_BEGIN label=(\S+) expected_cycle=(\d+)\n(.*?)^AA5_EXPORT_SNAPSHOT_END label=\1\s*$'
    matches=list(re.finditer(pattern,text,re.M|re.S));begins=re.findall(r'^AA5_EXPORT_SNAPSHOT_BEGIN ',text,re.M)
    if not matches or len(matches)!=len(begins):raise QualificationError('TRUNCATED_OR_MALFORMED_SNAPSHOT_WRAPPER')
    labels=[m[1] for m in matches]
    if len(set(labels))!=len(labels):raise QualificationError('DUPLICATE_SNAPSHOT_LABEL')
    snapshots=[dict(label=m[1],**snapshot(m[3],K,int(m[2]))) for m in matches]
    return dict(snapshots=snapshots,last_snapshot=snapshots[-1],snapshot_count=len(snapshots),aggregation='LAST_COMPLETE_SNAPSHOT_ONLY; never add repeated cumulative snapshots')
