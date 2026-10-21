#!/usr/bin/env python3
"""CPU-only review of frozen certificates and accepted MAIN61 counters.

No trace body/database, executable, application launch, build or production edit.
Reads at most 64MiB; optional existing raw reads are bounded final tails only.
"""
import argparse
import csv
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import time

CORE = 'd010911e3174a3764791183cd108fe4664ba8731'
D = Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-d-analysis-v1')
DPACK = D/'docs/ep_l2/review_packs/MS20261021_D_PRIMARY_FOUR_SCIENCE_r1'
ROOT = Path('/workspace/ep_l2_ms20261019_e_results')
APACK = Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-a-core-v1/docs/ep_l2/review_packs/MS20261020_A2_FORMAL_WAD_PRODUCER_RELEASE_r1')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    a=parser.parse_args()
    start=time.monotonic()
    os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
    resource.setrlimit(resource.RLIMIT_AS,(256*1024**2,256*1024**2))
    resource.setrlimit(resource.RLIMIT_CPU,(30,30));signal.alarm(90)
    reads=[];checks=[];used=0
    sha=lambda b:hashlib.sha256(b).hexdigest()

    def check(name,condition):
        if not condition:raise AssertionError(name)
        checks.append(dict(name=name,status='PASS',scope='METADATA_SOURCE_ACCOUNTING_NOT_NEW_NATIVE_TEST'))

    def read(path,tail=False):
        nonlocal used
        path=Path(path)
        assert path.suffix not in ('.traceg','.trace','.sqlite3','.gz')
        size=path.stat().st_size
        with path.open('rb') as f:
            if tail:f.seek(max(0,size-2*1024**2))
            elif size>4*1024**2:raise ValueError('oversized metadata '+str(path))
            offset=f.tell();b=f.read()
        used+=len(b);assert used<64*1024**2
        reads.append(dict(path=str(path),offset=offset,bytes=len(b),sha256=sha(b),
                          scope='BOUNDED_FINAL_TAIL_NOT_FRESH_WHOLE_HASH' if tail else 'WHOLE_SMALL_FILE'))
        return b

    def js(path):return json.loads(read(path))
    r=js('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json')['mechanism_study_20261019_v1']
    candidates={}
    for work in ['convolutionSeparable','FWT_7_21','cfd_097k','dwt2d','vectorAdd_4M','sad','btree']:
        directory='convolutionSeparable_r1' if work=='convolutionSeparable' else work+'_v2_r1'
        c=js(ROOT/'D_OFFLINE_INPUT_ANALYSIS'/directory/'CANDIDATE.json')
        mb=read(c['manifest']);m=json.loads(mb)
        check(work+':exact_manifest',sha(mb)==c['manifest_sha256'])
        check(work+':full_epoch_model',m['epoch']=='whole_commandlist' and
              m['scope']=='TRACE_MODEL_CLOSED_WORLD' and not m['unresolved_opcodes'])
        rb=read(Path(c['manifest']).parent/'certified_ranges.csv')
        check(work+':range_hash',sha(rb)==m['artifacts']['certified_ranges.csv'])
        ranges=[]
        for row in csv.DictReader(io.StringIO(rb.decode())):
            first,last=int(row['first_line'],16),int(row['last_line_inclusive'],16)
            check(work+':aligned_ordered_range',first%128==last%128==0 and first<=last and
                  (not ranges or first>ranges[-1][1]))
            ranges.append((first,last))
        check(work+':range_line_count',sum((last-first)//128+1 for first,last in ranges)==c['counts'].get('CERTIFIED_RO_lines',0))
        cb=read(m['commandlist']);commands=[s.strip() for s in cb.decode().splitlines() if s.strip() and not s.lstrip().startswith('#')]
        check(work+':command_hash',sha(cb)==m['commandlist_sha256'])
        seen_kernel=False;host=[];kernels=[];initial=[]
        for command in commands:
            if command.startswith('kernel'):
                seen_kernel=True;kernels.append(command)
            elif command.startswith(('MemcpyHtoD,','MemcpyDtoH,')):
                kind,address,count=command.split(',');address=int(address,16);count=int(count)
                if kind=='MemcpyHtoD' and count:
                    if seen_kernel:host.append((address&~127,(address+count-1)&~127))
                    else:initial.append(dict(address=address,bytes=count))
            else:raise AssertionError('unknown command')
        check(work+':all_kernel_identities_in_order',kernels==[Path(k['path']).name for k in m['kernels']] and len(kernels)==m['kernel_count'])
        check(work+':all_later_host_updates_recorded',host==[tuple(x) for x in m['host_updates_excluded']])
        check(work+':host_updated_lines_excluded',all(last<hfirst or first>hlast for first,last in ranges for hfirst,hlast in host))
        atomic_ops=sum(k['opcodes'].get(op,0) for k in m['kernels'] for op in ['ATOM','ATOMG','RED'])
        assumption_match=any('alias' in x.lower() for x in m['assumptions'])
        check(work+':explicit_alias_closed_world_scope',assumption_match and m['address_domain']=='CANONICAL_GPU_GLOBAL_VA_NO_TRANSLATION_ALIAS')
        model_review=next((x for key,x in r['input_oracle_reviews'].items() if key.endswith('_'+work)),None)
        if model_review:check(work+':E_model_review_hash',sha(read(model_review['path']))==model_review['sha256'])
        candidates[work]=dict(manifest_sha256=c['manifest_sha256'],trace_sha256=c['trace_content_sha256'],
            command_sha256=m['commandlist_sha256'],range_sha256=m['artifacts']['certified_ranges.csv'],
            kernel_count=len(kernels),RO_lines=c['counts'].get('CERTIFIED_RO_lines',0),counts=c['counts'],
            initial_HtoD_prefix=initial,later_HtoD_excluded=host,
            certified_ranges_disjoint_from_later_HtoD=True,global_atomic_instruction_records=atomic_ops,
            alias_and_external_agent_assumptions=m['assumptions'],
            alias_status='CONDITIONAL_MODEL_ASSUMPTION_NOT_PHYSICAL_ALIAS_PROOF',
            qualification='INPUT_HOLD_OVERRIDES_MODEL' if work=='btree' else 'MODEL_BOUNDARIES_PASS_NOT_NEW_RUNTIME_PASS',
            E_artifact_review=model_review)

    endpoints=js(DPACK/'ACCEPTED_ENDPOINT_IDENTITIES.json')
    target=['E009_76e25c1e','E016_776b0d99','E018_67a874f4','E020_6fd11ee2','E033_f01f6993']
    workloads={};endpoint_identities=[]
    for attempt in target:
        e=next(e for e in endpoints if e['attempt_id']==attempt)
        fb=read(e['receipt_path']);f=json.loads(fb)
        check(attempt+':accepted_exact_receipt',sha(fb)==e['receipt_sha256'] and f['status']=='COMPLETE_VALID')
        check(attempt+':exact_main61',e['core']==CORE and e['profile']=='F')
        work=e['workload'];off=candidates[work]
        check(attempt+':exact_input_model',e['trace_sha256']==off['trace_sha256'])
        per=f['mechanism_metrics']['full_mechanism_records']['readonly'];check(attempt+':64_RO_slices',len(per)==64)
        check(attempt+':manifest_and_flags',all(v['summary']['manifest']==off['manifest_sha256'] and v['summary']['detach']==v['summary']['bypass']==1 for v in per.values()))
        check(attempt+':closed_exact_response_counts',all(v['summary']['accepted_ro']==v['summary']['responses'] and v['closure']['epoch_closed']==1 and v['closure']['ro_live']==v['closure']['shared_descriptor_used']==v['closure']['shared_line_used']==0 for v in per.values()))
        sums={key:sum(v['summary'][key] for v in per.values()) for key in ['accepted_global_reads','accepted_oracle_candidates','accepted_ro','transactions','merges','detached','lower_sectors','concurrent_duplicate_sectors','responses']}
        check(attempt+':admission_decomposition',sums['transactions']+sums['merges']==sums['accepted_ro'])
        check(attempt+':actual_detach_zero',sums['detached']==0)
        peaks={key:max(v['resource'][key] for v in per.values()) for key in ['peak_transactions','peak_shared_descriptors','peak_shared_lines']}
        peaks.update({key:max(v['lower_concurrency'][key] for v in per.values()) for key in ['peak_lower_transactions','peak_independent_lower_lines']})
        check(attempt+':independent_lower_scope',all(v['lower_concurrency']['peak_independent_lower_lines']<=v['lower_concurrency']['peak_lower_transactions'] for v in per.values()))
        avoid=sum(v['resource']['avoided_line_allocations'] for v in per.values())
        check(attempt+':M_counts_transactions_not_children',avoid==sums['transactions'])
        # Only existing completed accepted raw files; no full raw hash/rescan.
        raw=ROOT/attempt/'raw.log';tail=read(raw,True).decode(errors='strict');last={}
        for line in tail.splitlines():
            if line.startswith('EPL2B0V1|scope=application|'):
                fields=dict(p.split('=',1) for p in line.split('|')[1:] if '=' in p)
                last[int(fields['slice'])]=fields
        check(attempt+':all_final_Tag_MSHR_records_in_bounded_tail',len(last)==64)
        pressure={k:max(int(v[k]) for v in last.values()) for k in ['line_mshr_max','descriptor_max','c7d_reserved_max','c7d_reserved_set_max']}
        waits={k:{n:v[n] for n in ['distinct_requests_first_block','blocked_observations_over_slices','request_wait_cycle_sum','request_wait_max']} for k,v in f['mechanism_metrics']['bottleneck'].items() if k in ['TAG_SET_PENDING','LINE_MSHR_FULL','DESCRIPTOR_FULL','PER_LINE_CAP','BANK_COMPATIBLE_LANDING','DATA_SERVICE']}
        se=next(v for v in endpoints if v['workload']==work and v['profile']=='S')
        sb=read(se['receipt_path']);s=json.loads(sb);check(work+':S_anchor_hash',sha(sb)==se['receipt_sha256'])
        sw={k:{n:v[n] for n in ['distinct_requests_first_block','blocked_observations_over_slices','request_wait_cycle_sum','request_wait_max']} for k,v in s['mechanism_metrics']['bottleneck'].items() if k in ['TAG_SET_PENDING','LINE_MSHR_FULL','DESCRIPTOR_FULL']}
        workloads[work]=dict(attempt=attempt,accepted_summary=sums,avoided_line_allocations=avoid,
            peaks_per_slice_not_sum=peaks,actual_application_pressure_max_per_slice=pressure,
            F_nonexclusive_waits=waits,S_nonexclusive_waits=sw,
            raw_tail_only_full_file_identity_reused_from_E=e['raw_sha256'],
            no_application_sibling_parent_identity_count=True)
        endpoint_identities.append({k:e[k] for k in ['attempt_id','workload','receipt_path','receipt_sha256','binary','core','framework','trace_sha256','config_sha256','qualification_id','run_key','raw_sha256']})

    native=js(APACK/'NATIVE_EVIDENCE_MANIFEST.json');native_reuse=[]
    for name in ['new_combined_same_address','new_combined_host_update','new_combined_fallback']:
        case=next(c for c in native['tests'] if c['case']==name)
        b=read(case['raw_log']);check(name+':existing_native_raw_hash',sha(b)==case['raw_log_sha256'])
        check(name+':existing_native_terminal','PASS' in b.decode())
        native_reuse.append(case)
    sources={}
    repo='/workspace/worktrees/gpgpu-sim-ep-l2-ms20261019-c-ro-v1'
    for path in ['src/gpgpu-sim/ep-l2-ro-runtime.inc','src/gpgpu-sim/ep-l2-ro-transactions.h','tests/ep_l2/ms_ro_combined/test_combined.cc','tests/ep_l2/ms_ro_combined/native_fixture.h']:
        b=subprocess.check_output(['git','-C',repo,'show',CORE+':'+path]);sources[path]=dict(commit=CORE,sha256=sha(b),bytes=len(b))
    result=dict(schema='C_D_CANDIDATE_EPOCH_AND_FIVE_MAIN_F_PRESSURE_REVIEW_V1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        audited_MAIN_Core=CORE,candidates=candidates,MAIN_F=workloads,accepted_endpoint_identities=endpoint_identities,
        reused_native_evidence=native_reuse,source_identities=sources,
        SGEMM='EXPLORATORY_HOLD_NO_WHOLE_EPOCH_RO_CERTIFICATE; explicit valid empty fallback only after native input qualification',
        preserved_input_holds=r['input_scope_holds'],registry_snapshot=dict(actual_starts=r['actual_starts'],cap=r['maximum_actual_starts'],controller=r['controller']),
        validation_checks=checks,checks_pass=len(checks),bytes_read=used,read_audit=reads,
        elapsed_seconds=time.monotonic()-start,
        VmHWM_bytes=int(next(l for l in Path('/proc/self/status').read_text().splitlines() if l.startswith('VmHWM:')).split()[1])*1024,
        no_new_native_test=True,no_trace_DB_scan=True,no_build=True,no_application_start=True,no_production_semantics_or_capacity_change=True)
    with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(checks=len(checks),read_bytes=used,elapsed=result['elapsed_seconds'],VmHWM=result['VmHWM_bytes'],
        F={w:dict(RO=v['accepted_summary']['accepted_ro'],detach=v['accepted_summary']['detached'],
            independent=v['peaks_per_slice_not_sum']['peak_independent_lower_lines'],pressure=v['actual_application_pressure_max_per_slice']) for w,v in workloads.items()}),indent=2))


if __name__=='__main__':main()
