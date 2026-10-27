"""Strict matched read-only increment: missing never0; no best-of suite GM."""
import collections,hashlib,json,math,pathlib
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/E/results_increment_v2')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def dump(p,v):p.write_bytes((json.dumps(v,indent=2,sort_keys=True)+'\n').encode())
def compare(a,b):return dict(P0=a,variant=b,delta=b-a if a is not None and b is not None else None,change_pct=(b/a-1)*100 if a is not None and b is not None and a!=0 else None)
def main():
    capture=read(A/'LATEST_CAPTURE.json');run=P(capture['run_path']);r=read(run/'report.json');old=read(capture['previous_checkpoint_path'])
    matrix=read(R/'control/MATRIX_CURRENT.json');points={p['cohort']:p for p in matrix['points']};new=set(capture['newly_accepted'])
    cache={};errors=[]
    def result(cell):
        path=P(cell['result_path'])
        if str(path)not in cache:
            assert sha(path)==cell['result_sha256'];cache[str(path)]=read(path)
        return cache[str(path)]
    def paired(d,profile):
        cells=r['table'][d];base=cells.get('P0',{}).get('DH',{});var=cells.get(profile,{}).get('DH',{})
        if not base.get('accepted')or not var.get('accepted'):return None
        a=result(base);b=result(var);pa=a['proof'];pb=b['proof'];err=[]
        for key in ['input_digest','cell','core_commit','framework_commit','binary_sha256']:
            if pa.get(key)!=pb.get(key):err.append('PAIR_'+key)
        if pa.get('input_digest')!=d:err.append('FROZEN_INPUT_IDENTITY')
        speca=read(R/'control/specs'/(base['cohort']+'.json'));specb=read(R/'control/specs'/(var['cohort']+'.json'))
        for key in ['input_digest','input_binding_sha256','core_commit','framework_commit','binary_sha256','library_sha256']:
            if speca.get(key)!=specb.get(key):err.append('CANONICAL_PAIR_'+key)
        if speca.get('cell')!='DH'or specb.get('cell')!='DH':err.append('DESIGN_IDENTITY')
        for v in [a,b]:
            proof=v['proof'];scope=points[var['cohort']]['expected']
            if dict(CTA=proof.get('CTA'),instructions=proof.get('instructions'),kernels=proof.get('kernel_count'))!=scope:err.append('FULL_POPULATION')
        oa=pa['effective_options'];ob=pb['effective_options'];targets={'-gpgpu_cache:dl2','-gpgpu_frfcfs_dram_sched_queue_size'}
        if set(oa)!=set(ob)or any(oa[k]!=ob[k]for k in oa if k not in targets):err.append('NON_TARGET_OPTIONS')
        if oa.get('-gpgpu_clock_domains')!=['1410.0:1410.0:1410.0:850.0']:err.append('DRAM850')
        if err:errors.append(dict(cohort=var['cohort'],errors=err));return None
        ca=base['counters']or{};cb=var['counters']or{}
        old_pair=old['comparisons'].get(d,{}).get(profile,{}).get('DH_speedup')
        sa=(base.get('L2_failure_reason_sidecar')or{}).get('positive_known_contributions')
        sb=(var.get('L2_failure_reason_sidecar')or{}).get('positive_known_contributions')
        reason_keys=sorted(set(sa or{})|set(sb or{}))
        changes={k:compare(ca.get(k),cb.get(k))for k in ['L2_read_sectors','L2_read_miss_sectors','DRAM_read_atoms','DRAM_read_bytes','L2_reservation_fail','gpu_stall_dramfull','avg_mrq_latency_last_printed']}
        reasons={k:compare((sa or{}).get(k),(sb or{}).get(k))for k in reason_keys}
        return dict(program=r['programs'][d]['program'],suite=r['programs'][d]['suite'],input_digest=d,profile=profile,
            baseline_cohort=base['cohort'],variant_cohort=var['cohort'],P0_cycles=a['cycles'],variant_cycles=b['cycles'],DH_speedup=a['cycles']/b['cycles'],
            variant_new_since_anchor=var['cohort']in new,newly_matched_since_anchor=old_pair is None,
            CH_variant_accepted=cells.get(profile,{}).get('CH',{}).get('accepted',False),
            relative_DTC_improvement=r['comparisons'][d][profile]['relative_DTC_improvement'],
            counter_changes=changes,raw_positive_reason_changes=reasons,raw_missing_reasons_remain_None=True,
            raw_reason_scope=(var.get('L2_failure_reason_sidecar')or{}).get('scope'),
            P0_result_path=base['result_path'],P0_result_sha256=base['result_sha256'],variant_result_path=var['result_path'],variant_result_sha256=var['result_sha256'],
            P0_raw_reason_evidence=base.get('L2_failure_reason_sidecar'),variant_raw_reason_evidence=var.get('L2_failure_reason_sidecar'),
            identity=dict(core_commit=pa['core_commit'],framework_commit=pa['framework_commit'],binary_sha256=pa['binary_sha256']),
            input_binding_sha256=speca.get('input_binding_sha256'),P0_uuid=a['uuid'],variant_uuid=b['uuid'],
            non_target_options_sha256=hashlib.sha256(json.dumps({k:v for k,v in oa.items()if k not in targets},sort_keys=True).encode()).hexdigest(),
            effective_option_count=len(oa),
            matched_full_input_population=points[var['cohort']]['expected'],all_non_target_effective_options_equal=True)
    pairs=[];coverage=[]
    for d,program in sorted(r['programs'].items(),key=lambda kv:(kv[1]['suite'],kv[1]['program'])):
        cells=r['table'][d];variants=[p for p in r['profiles']if p!='P0']
        row=dict(**program,CH_P0_accepted=cells['P0']['CH']['accepted'],DH_P0_accepted=cells['P0']['DH']['accepted'],
            accepted_DH_variants=[p for p in variants if cells.get(p,{}).get('DH',{}).get('accepted')],
            missing_DH_variants=[p for p in variants if not cells.get(p,{}).get('DH',{}).get('accepted')],
            new_accepted_cells=sum(v['cohort']in new for designs in cells.values()for v in designs.values()),
            states={p:cells[p]['DH']['state']for p in cells if'DH'in cells[p]})
        coverage.append(row)
        for profile in variants:
            value=paired(d,profile)
            if value:pairs.append(value)
    increments=[p for p in pairs if p['variant_new_since_anchor']or p['newly_matched_since_anchor']]
    focus=[p for p in pairs if p['program']in('ATAX','MVT','BICG')]
    stats={}
    for profile in r['profiles']:
        if profile=='P0':continue
        selected=[p for p in pairs if p['profile']==profile];v=[p['DH_speedup']for p in selected]
        stats[profile]=dict(n=len(v),expected_n=35,missing_n=35-len(v),GM=math.exp(math.fsum(math.log(x)for x in v)/len(v))if v else None,
            positive=sum(x>1 for x in v),neutral=sum(x==1 for x in v),negative=sum(x<1 for x in v),population=[p['input_digest']for p in selected])
    result=dict(schema='DTC_L2_MLP_RESULTS_INCREMENT_ANALYSIS_V2',utc=r['utc'],capture=capture,
        coverage=coverage,all_matched_DH_pairs=pairs,new_or_newly_matched_pairs=increments,focus_strided3=focus,
        partial_uniform_DH_statistics=stats,top_increment_positive=sorted([p for p in increments if p['DH_speedup']>1],key=lambda p:p['DH_speedup'],reverse=True)[:8],
        top_increment_negative=sorted([p for p in increments if p['DH_speedup']<1],key=lambda p:p['DH_speedup'])[:8],
        pair_identity_validation_errors=errors,full35_profile_count=sum(s['n']==35 for s in stats.values()),
        unaccepted_terminal_cells=[dict(program=r['programs'][d]['program'],profile=p,cell=cell,**v)for d,ps in r['table'].items()for p,ds in ps.items()for cell,v in ds.items()if not v['accepted']and('FAIL'in v['state']or'ENGINEERING'in v['state'])],
        scientific_boundaries=dict(CH_nonP0_missing_relative_is_None=True,no_missing_zero_imputation=True,no_per_program_best_GM=True,
            partial_suite_cannot_select_formal_uniform_profile=True,no_simulation_or_retries=True,raw_rejection_attempts_not_unique_requests_or_elapsed_cycles=True,
            last_printed_avg_mrq_not_weighted_whole_application_mean=True,FRFCFS_coupled_memory_partition_credits=True))
    assert not errors,errors
    dump(run/'ANALYSIS.json',result);dump(A/'LATEST_ANALYSIS.json',result)
    def short(p):return dict(program=p['program'],profile=p['profile'],speedup=p['DH_speedup'],DRAM_change_pct=p['counter_changes']['DRAM_read_atoms']['change_pct'])
    print(json.dumps(dict(utc=r['utc'],accepted=capture['current_accepted'],new=capture['current_accepted']-capture['previous_accepted'],
        matched_pairs=len(pairs),new_or_newly_matched=len(increments),focus=[short(p)for p in focus],
        top_positive=[short(p)for p in result['top_increment_positive'][:3]],top_negative=[short(p)for p in result['top_increment_negative'][:3]],
        stats={p:{k:v for k,v in s.items()if k!='population'}for p,s in stats.items()},errors=errors),indent=2))

if __name__=='__main__':main()
