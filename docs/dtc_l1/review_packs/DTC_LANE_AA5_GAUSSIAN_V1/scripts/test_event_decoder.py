"""Synthetic decoder tests only. No Core, library, simulation or export qualification."""
from common import *
from event_snapshots import *
import copy

def render(records,cycle):return 'gpu_tot_sim_cycle = '+str(cycle)+'\nDTC_INVALIDATE_V1_SNAPSHOT_BEGIN version=1 sms=64 cycle='+str(cycle)+' no_event_cycle_sentinel='+str(SENTINEL)+'\n'+'\n'.join('DTC_INVALIDATE_V1_SUMMARY sm='+str(i)+' '+' '.join(k+'='+str(v) for k,v in row.items()) for i,row in records)+'\nDTC_INVALIDATE_V1_SNAPSHOT_END version=1 sms=64 cycle='+str(cycle)+'\n'
def main():
    records=[]
    for sm in range(64):
        r={k:0 for k in FIELDS}
        for k in ['first_request_cycle','last_request_cycle','first_ordinary_commit_cycle','last_ordinary_commit_cycle']:r[k]=SENTINEL
        records.append((sm,r))
    zero=render(records,0);assert snapshot(zero,1,0)['totals']['requests']==0
    live=copy.deepcopy(records);live[0][1].update(requests=4,idle=2,membar=1,config=1,ordinary_commits=3,changed=2,retained_at_event=1,reclaimed_at_event=1,no_op_requests=2,first_request_cycle=10,last_request_cycle=36,first_ordinary_commit_cycle=23,last_ordinary_commit_cycle=36)
    text=render(live,40);assert snapshot(text,1,40)['reclaimed_at_event']==1
    results=[]
    def reject(name,text,expected_cycle=40):
        try:snapshot(text,1,expected_cycle)
        except QualificationError as e:results.append(dict(case=name,expected='REJECT',observed='REJECT',reason=str(e)));return
        raise AssertionError(name+' accepted invalid snapshot')
    reject('missing_SM',render(live[:-1],40));reject('duplicate_SM',render(live+live[:1],40));reject('same_length_duplicate_SM',render(live[:-1]+live[:1],40));reject('truncated_field',text.replace('reclaimed_at_event=1 ','',1));reject('wrong_cycle_boundary',text,41)
    reject('missing_normal_frame',text.replace('DTC_INVALIDATE_V1_SNAPSHOT_BEGIN','PRIVATE_BEGIN',1));reject('truncated_normal_frame',text.replace('DTC_INVALIDATE_V1_SNAPSHOT_END','PRIVATE_END',1));reject('wrong_frame_boundary',text.replace('sms=64 cycle=40','sms=64 cycle=41',1))
    bad=copy.deepcopy(live);bad[0][1]['last_request_cycle']=41;reject('event_after_public_cycle',render(bad,40))
    bad=copy.deepcopy(live);bad[1][1]['first_request_cycle']=0;reject('missing_no_event_sentinel',render(bad,40))
    bad=copy.deepcopy(live);bad[0][1]['changed']=3;reject('mapping_balance_wrong',render(bad,40))
    bad=copy.deepcopy(live);bad[0][1]['idle']=3;reject('origin_balance_wrong',render(bad,40))
    wrapped=''.join(f'AA5_EXPORT_SNAPSHOT_BEGIN label={label} expected_cycle={cycle}\n'+body+f'AA5_EXPORT_SNAPSHOT_END label={label}\n' for label,cycle,body in [('initial',0,zero),('A',40,text),('B',40,text)])
    parsed=fixture_snapshots(wrapped,1);assert parsed['last_snapshot']['totals']['requests']==4 and parsed['last_snapshot']['reclaimed_at_event']==1
    assert sum(s['totals']['requests'] for s in parsed['snapshots'])==8 # deliberate counterexample; never used as final count
    assert snapshot('gpu_tot_sim_cycle = 40\n',0,40)['event_fields'].startswith('UNAVAILABLE')
    try:fixture_snapshots(wrapped.rsplit('AA5_EXPORT_SNAPSHOT_END',1)[0],1)
    except QualificationError:results.append(dict(case='truncated_last_snapshot_not_silently_use_previous',expected='REJECT',observed='REJECT'))
    else:raise AssertionError('truncated final wrapper accepted')
    write(PACK/'DECODER_CPU_TESTS.json',dict(status='PASS_SYNTHETIC_DECODER_ONLY_NOT_NORMAL_TERMINAL_EXPORT_GATE',cases=results,sentinel_case='PASS',last_snapshot_case='PASS_FINAL4_NOT_SUM8',K0_missing='UNAVAILABLE_NOT_ZERO',real_production_objects_executed=False,X2_qualified=False,simulator_starts=0,decoder_sha256=sha(PACK/'scripts/event_snapshots.py')))
    print('PASS synthetic decoder sentinel/64SM/cycle/origin/reclaim/last-snapshot/K0 rules and',len(results),'rejecting negatives; no X2 gate PASS.')

if __name__=='__main__':main()
