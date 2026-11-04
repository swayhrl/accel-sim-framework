"""New private contract tests only. Never reruns production bf4 CPU/parser."""
import itertools, json
from dataclasses import replace
from quota_commit_contract import Row,Op,QuotaCommit,RoundRobinHeads

results=[]
def record(name,detail):results.append(dict(name=name,status='PASS',detail=detail))
def op(q,i,kind,**kw):
    r=q.rows[i]
    return Op(i,kind,r.incarnation,r.payload_generation,
              new_payload_id=1000+i,new_payload_generation=99,**kw)
def finish(q,ops):
    before=q.visible();p=q.prepare(ops,q.revision);assert q.visible()==before
    c=q.commit();return p,c

# Hard quota and single atomic count write with two attempted row grants.
q=QuotaCommit([Row('CLEAN',1,i,1) for i in range(63)]+[Row() for i in range(65)],64)
p,c=finish(q,[op(q,63,'clean_install'),op(q,64,'clean_install')])
assert p['results']==['PREPARED','BACKPRESSURE_QUOTA'] and q.count==64 and q.acks==1
assert q.metrics['count_writes']==1 and q.cycle==2
record('cap64_two_competing_increments',dict(count=q.count,grants=q.acks,charged_contract_cycles=q.cycle))

q=QuotaCommit([Row('CLEAN',7,1,3)],1)
p,c=finish(q,[op(q,0,'clean_install')])
assert p['net_delta']==0 and q.count==1 and q.rows[0].incarnation==8
assert q.metrics['count_writes']==1 and q.metrics['row_writes']==1
record('clean_replacement_folded_net0',dict(net_delta=0,row_writes=1,count_writes=1))

q=QuotaCommit([Row('CLEAN',1,1,1),Row()],1)
p,c=finish(q,[op(q,0,'reclaim'),op(q,1,'clean_install')])
assert p['accepted']==[0,1] and p['net_delta']==0 and q.count==1 and q.acks==2
record('reclaim_then_install_atomic_signed_sum',dict(delta_terms=[-1,1],net_delta=0,commits=2,charged_contract_cycles=q.cycle))

q=QuotaCommit([Row(),Row('CLEAN',1,1,1)],1)
p,c=finish(q,[op(q,0,'clean_install'),op(q,1,'reclaim')])
assert p['results']==['BACKPRESSURE_QUOTA','PREPARED'] and q.count==0
p,c=finish(q,[op(q,0,'clean_install')]);assert q.count==1 and q.cycle==4
record('prefix_order_bubble_is_charged',dict(no_later_decrement_lookahead=True,charged_contract_cycles=4))

q=QuotaCommit([Row('CLEAN',1,i,1) for i in range(2)],2)
p,c=finish(q,[op(q,0,'reclaim'),op(q,1,'reclaim')]);assert p['net_delta']==-2 and q.count==0
record('two_decrements_need_signed_reducer',dict(net_delta=-2,minimum_signed_delta_bits=3))

q=QuotaCommit([Row('CLEAN',1,0,1),Row('WB_INFLIGHT',2,1,3)],1)
p,c=finish(q,[op(q,0,'reclaim'),op(q,1,'wb_done')])
assert q.count==0 and q.rows[1].state=='WB_COMPLETE' and q.acks==2
record('zero_delta_wb_completion_competes_for_real_row_port',dict(row_writes=2,count_delta=-1))

q=QuotaCommit([Row(),Row()],0)
p,c=finish(q,[op(q,0,'dirty_install'),op(q,1,'dirty_install')]);assert q.count==0 and q.acks==2
p,c=finish(q,[op(q,0,'wb_accept'),op(q,1,'wb_accept')]);assert q.count==0
p,c=finish(q,[op(q,0,'wb_done'),op(q,1,'wb_done')]);assert q.count==0
record('cap0_mandatory_wb_and_completed_retention_preserved',dict(wb_complete_rows=2,clean_count=0))

q=QuotaCommit([Row()],1);before=q.visible();q.prepare([op(q,0,'clean_install')],q.revision)
for i in range(3):
    assert q.commit(False)['status']=='BACKPRESSURE_DOWNSTREAM' and q.visible()==before
assert q.commit()['committed']==1 and q.cycle==5 and q.acks==1
record('downstream_hold_has_no_partial_visibility_or_ack',dict(held_commit_beats=3,charged_contract_cycles=5))

q=QuotaCommit([Row('CLEAN',1,1,1,1)],1);before=q.visible()
p=q.prepare([op(q,0,'reclaim')],q.revision);assert not p['accepted'] and q.visible()==before
q=QuotaCommit([Row()],1);bad=replace(op(q,0,'clean_install'),expected_incarnation=9)
p=q.prepare([bad],q.revision);assert p['results']==['STALE_IDENTITY'] and q.count==0
q=QuotaCommit([Row()],1);p=q.prepare([op(q,0,'clean_install')],q.revision);q.revision+=1;before=q.visible()
assert q.commit()['status']=='STALE_COMMIT_REVISION' and q.visible()==before
record('pins_incarnation_and_commit_revision_refuse_before_mutation',dict(checks=3))

q=QuotaCommit([Row(),Row(),Row()],3);before=q.visible()
p=q.prepare([op(q,i,'clean_install') for i in range(3)],q.revision)
assert p['status']=='BACKPRESSURE_ROW_PORT_BOUND' and q.visible()==before and q.pending is None
q=QuotaCommit([Row()],1);before=q.visible()
p=q.prepare([op(q,0,'clean_install'),op(q,0,'dirty_install')],q.revision)
assert p['results']==['PREPARED','BACKPRESSURE_SAME_ROW'] and q.visible()==before
q.commit();assert q.acks==1
record('port_bound_and_same_row_collision_explicit',dict(max_row_lanes=2,no_oversubscription=True))

q=QuotaCommit([Row()],1);before=q.visible()
p=q.prepare([op(q,0,'dirty_install',resources_reserved=False)],q.revision)
assert not p['accepted'] and q.visible()==before
rr=RoundRobinHeads();heads=list(range(6));picks=[rr.select(heads,2) for i in range(3)]
assert [i for pair in picks for i,j in pair]==list(range(6))
record('reservation_and_round_robin_attempt_fairness',dict(reservation_refusal_no_mutation=True,all6_heads_attempted_in_3_read_beats=True,unbounded_downstream_progress_not_claimed=True))

cleanup=[]
for lanes in [1,2]:
    q=QuotaCommit([Row('CLEAN',1,i,1) for i in range(128)],128,lanes=lanes)
    for first in range(0,128,lanes):finish(q,[op(q,i,'reclaim') for i in range(first,first+lanes)])
    assert q.count==0 and q.cycle==256//lanes
    cleanup.append(dict(lanes=lanes,rows=128,charged_contract_cycles=q.cycle))
record('cleanup_charged_per_read_commit_batch',cleanup)

# Exhaustive small-state arithmetic/atomicity, not empirical hardware timing.
states=['EMPTY','CLEAN','WB_STAGED','WB_INFLIGHT','WB_COMPLETE']
kinds=['clean_install','dirty_install','reclaim','wb_accept','wb_done','read_begin','read_end']
cases=0
for a,b in itertools.product(states,repeat=2):
    rows=[Row(a,1,0,1),Row(b,1,1,1)]
    for cap in range(sum(r.state=='CLEAN' for r in rows),3):
        for ka,kb in itertools.product(kinds,repeat=2):
            q=QuotaCommit(rows,cap);before=q.visible()
            p=q.prepare([op(q,0,ka),op(q,1,kb)],q.revision)
            assert q.visible()==before
            c=q.commit()
            assert q.count==sum(r.state=='CLEAN' for r in q.rows) and 0<=q.count<=cap
            assert q.revision==q.acks==len(p['accepted'])
            assert q.metrics['row_reads']<=2 and q.metrics['row_writes']<=2
            assert q.metrics['count_writes']==bool(p['accepted'])
            cases+=1
record('exhaustive_two_row_state_operation_pairs',dict(cases=cases,oracle='count equals cardinality, cap bounded, READ no mutation, exact commit acks/revision, lane bounds'))
print(json.dumps(dict(schema='EP_PFV4_NEW_PRIVATE_QUOTA_HARDWARE_CONTRACT_CPU_RECEIPT_V1',status='PASS_NEW_PRIVATE_CONTRACT_ONLY',directed_case_groups=len(results)-1,exhaustive_cases=cases,results=results,production_CPU_parser_reruns=0,production_source_changed=False,ELF_executed=False,models_started=0,science_budget_registered=0,physical_timing_or_PPA_measured=False,production_integration_qualified=False),indent=2,sort_keys=True))
