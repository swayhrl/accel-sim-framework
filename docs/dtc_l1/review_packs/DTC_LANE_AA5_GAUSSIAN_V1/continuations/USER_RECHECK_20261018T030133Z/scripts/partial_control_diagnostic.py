from pathlib import Path
import sys,json,re
P=Path('/workspace/worktrees/accel-sim-iscas2027-dtc-lane-aa5-gaussian-convergence-174-v1/docs/dtc_l1/review_packs/DTC_LANE_AA5_GAUSSIAN_V1');sys.path.insert(0,str(P/'scripts'))
from strict_matrix import *
Q=ROOT/'user_recheck_20261018T030133Z';C=P/'continuations/USER_RECHECK_20261018T030133Z';run=ROOT/'attempts/K0_32x4_d0a29a82-c171-46e4-b077-d7ccfd2c4b7a'
assert json.loads((run/'RUN_TERMINAL.json').read_text())['returncode']==-15
text=(run/'simulator.stdout').read_text();old=BASELINES[32].read_text();expected=json.loads((P/'ORDERED_KERNELS.json').read_text())
def blocks(t):
 starts=list(re.finditer(r'^kernel_name = (\S+)[ \t]*$',t,re.M));return [(m[1],t[m.start():starts[i+1].start() if i+1<len(starts) else len(t)]) for i,m in enumerate(starts)]
a=blocks(text);b=blocks(old);rows=[];diff=[]
for i,((name,blk),(_,ref)) in enumerate(zip(a,b)):
 d=numeric(blk);rd=numeric(ref);x,y=comparable(d),comparable(rd)
 delta={k:[y.get(k),x.get(k)] for k in set(x)|set(y) if x.get(k)!=y.get(k)}
 if delta:diff.append(dict(ordinal=i+1,differences=delta))
 rows.append(dict(ordinal=i+1,name=name,expected=expected[i]['kernel'],active_instructions=d['gpu_sim_insn'],expected_active_instructions=expected[i]['active_instructions'],raw_cumulative_cycles=d['gpu_tot_sim_cycle'],reference_cumulative_cycles=rd['gpu_tot_sim_cycle'],public_counter_prefix_match=not delta))
spec=json.loads((C/'specs/K0_32x4.json').read_text());cfg=echo(text);configdiff={k:[v,cfg.get(k)] for k,v in spec['expected_full_default_and_config_echo'].items() if cfg.get(k)!=v}
first=json.loads((run/'RESOURCE_START.json').read_text());last=json.loads((run/'RESOURCE_FINAL.json').read_text())
body=dict(status='PARTIAL_PREFIX_DIAGNOSTIC_ONLY_NOT_FULL_CONTROL_PASS',completed_snapshot_count=len(rows),required_full_kernels=510,rows=rows,counter_differences=diff,config267_match=not configdiff,config_differences=configdiff,observed_embedded_Core='gpgpu-sim_git-commit-e32afdcf_modified_0.0.' in text,last_completed_raw_cycles=rows[-1]['raw_cumulative_cycles'],last_completed_active_thread_instructions=numeric(a[-1][1])['gpu_tot_sim_insn'],last_completed_CTA=numeric(a[-1][1])['gpu_tot_issued_cta'],required_full_CTAs=65790,required_full_instructions=283685120,full_K0_equivalence='NOT_ESTABLISHED_NO_NATURAL_TERMINAL_NO_510_COMPLETION',new_performance_accepted=False,resource=dict(pswpin_start=first['pswpin'],pswpin_end=last['pswpin'],pswpin_delta=last['pswpin']-first['pswpin'],pswpout_start=first['pswpout'],pswpout_end=last['pswpout'],pswpout_delta=last['pswpout']-first['pswpout'],page_bytes=os.sysconf('SC_PAGE_SIZE'),scope='HOST_GLOBAL_COUNTER_NOT_ATTRIBUTED_TO_AA5_PROCESS',own_rusage_major_faults=json.loads((run/'RUN_TERMINAL.json').read_text())['resource_usage']['ru_majflt']),input=input_check(spec),negative_K1_evidence='NONE_K1_NOT_RUN',stopped_cannot_reuse_UUID=True)
write(Q/'PARTIAL_CONTROL_DIAGNOSTIC.json',body);write(C/'PARTIAL_CONTROL_DIAGNOSTIC.json',body)
print(json.dumps({k:body[k] for k in ['status','completed_snapshot_count','counter_differences','config267_match','last_completed_raw_cycles','last_completed_active_thread_instructions','last_completed_CTA','resource']},indent=2))
