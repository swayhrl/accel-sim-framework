#!/usr/bin/env python3
"""Validate the evidence package; optionally exercise builder with an audit guard."""
import argparse
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def read_rows(name):
    with (ROOT/name).open() as f:
        return list(csv.DictReader(f, delimiter='\t'))


def exercise():
    forbidden = ['/workspace/dtc-service-closure-174-v1',
                 '/workspace/dtc-tag-pilot-174-v1',
                 '/workspace/dtc-t1c-holdout-174-v1']
    seen = dict(trace_body_opens=0, prior_raw_opens=0, writes_outside_pack=0,
                non_git_show_subprocesses=0, git_show_subprocesses=0)

    def guard(event, args):
        if event == 'open' and isinstance(args[0], (str,bytes,os.PathLike)):
            p = Path(os.fsdecode(args[0])).absolute()
            if p.name.endswith(('.traceg','.traceg.gz','.traceg.xz','.traceg.zst','.trace')):
                seen['trace_body_opens'] += 1
                raise RuntimeError('Trace body open prohibited: '+str(p))
            if any(p == Path(r) or Path(r) in p.parents for r in forbidden):
                seen['prior_raw_opens'] += 1
                raise RuntimeError('Prior raw read/write prohibited: '+str(p))
            mode, flags = args[1:3]
            writing = (isinstance(mode,str) and any(c in mode for c in 'wa+')) or (
                isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))
            if writing and ROOT not in p.parents:
                seen['writes_outside_pack'] += 1
                raise RuntimeError('Write outside pack prohibited: '+str(p))
        if event == 'subprocess.Popen':
            argv=args[1]
            if not (isinstance(argv,list) and len(argv)==5 and argv[0]=='git' and argv[1]=='-C' and argv[3]=='show'):
                seen['non_git_show_subprocesses'] += 1
                raise RuntimeError('Only immutable git show is allowed: '+repr(argv))
            seen['git_show_subprocesses'] += 1

    sys.addaudithook(guard)
    spec=importlib.util.spec_from_file_location('w_builder', ROOT/'scripts/build_readonly_pack.py')
    builder=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    builder.build()
    assert all(seen[k]==0 for k in ('trace_body_opens','prior_raw_opens','writes_outside_pack','non_git_show_subprocesses'))
    (ROOT/'CPU_AUDIT_GUARD.json').write_text(json.dumps(dict(status='PASS', **seen),indent=2)+'\n')


def verify():
    body=read_rows('inputs/KERNEL_BODY_AUDIT.tsv')
    access=read_rows('ACCESS_CLASS_COUNTS.tsv')
    scope=read_rows('TRACE_SCOPE_SHA256.tsv')
    assert len(body)==523 and len(scope)==527
    for workload,n,inst in [('Gaussian',510,283685120),('GEMM',1,739246080),
                            ('DWT2D',10,148684429),('BICG',2,145666048)]:
        br=[r for r in body if r['workload'].lower()==workload.lower()]
        sr=[r for r in scope if r['workload']==workload and r['kind']=='trace_member']
        assert len(br)==len(sr)==n
        assert sum(int(r['active_thread_instructions']) for r in br)==inst
        assert {r['path']:r['sha256'] for r in br}=={r['path']:r['sha256'] for r in sr}
        ar=[r for r in access if r['workload']==workload]
        keys={c for r in br for c in json.loads(r['memory_paths'])}
        for c in keys:
            expected=sum(json.loads(r['memory_paths']).get(c,0) for r in br)
            assert sum(int(r['count']) for r in ar if r['ordinal']!='ALL' and r['access_class']==c)==expected
            assert [int(r['count']) for r in ar if r['ordinal']=='ALL' and r['access_class']==c]==[expected]
        for cls in ['ATOMIC','BYPASS_GLOBAL_LOAD','FENCE']:
            assert [r['count'] for r in ar if r['ordinal']=='ALL' and r['access_class']==cls]==['0']
        assert all(r['pc']=='UNAVAILABLE' for r in ar)
    for r in read_rows('CROSS_KERNEL_ALIAS_AND_REUSE.tsv'):
        for k in ('prior_read_current_read_lines','previous_kernel_write_current_read_lines','reusable_distinct_lines','byte_conflicts'):
            assert r[k]=='UNAVAILABLE'
    for r in read_rows('WRITE_READ_RISK.tsv'):
        for k in ('read_pc','write_pc','same_line_read_write_candidates','byte_overlap_candidates',
                  'same_warp_write_then_read','actual_old_mapping_exposure'):
            assert r[k]=='UNAVAILABLE'
    assert not list(ROOT.rglob('*.traceg*'))
    check=json.loads((ROOT/'CPU_READONLY_CHECKS.json').read_text())
    assert not check['full_access_semantics_complete'] and check['new_simulation_attempts']==0
    preflight=json.loads((ROOT/'CPU_ACCESS_SEMANTICS_PREFLIGHT.json').read_text())
    assert preflight['status']=='PASS_SYNTHETIC_CPU_LEGALITY_ONLY' and len(preflight['passed'])==6
    assert preflight['analyzer_sha256']==hashlib.sha256((ROOT/'scripts/access_semantics.py').read_bytes()).hexdigest()
    assert preflight['test_sha256']==hashlib.sha256((ROOT/'scripts/preflight_access_semantics.py').read_bytes()).hexdigest()
    assert preflight['original_trace_body_opens']==preflight['native_or_simulator_executions']==0
    for receipt_name,source_name,test_name,hash_key in [
        ('CPU_STREAM_PREFLIGHT.json','stream_access_scan.py','preflight_stream_access.py','runner_sha256'),
        ('CPU_CROSS_KERNEL_PREFLIGHT.json','cross_kernel_reuse.py','preflight_cross_kernel.py','reducer_sha256')]:
        receipt=json.loads((ROOT/receipt_name).read_text())
        assert receipt['status'].startswith('PASS_SYNTHETIC_')
        assert receipt[hash_key]==hashlib.sha256((ROOT/'scripts'/source_name).read_bytes()).hexdigest()
        assert receipt['test_sha256']==hashlib.sha256((ROOT/'scripts'/test_name).read_bytes()).hexdigest()
        assert receipt['original_trace_body_opens']==receipt['native_or_simulator_executions']==0
    scan_admission=json.loads((ROOT/'SCAN_ADMISSION.json').read_text())
    assert scan_admission['decision']=='REFUSE_BEFORE_BODY_OPEN'
    assert not scan_admission['scan_requested'] and scan_admission['body_opens_at_admission']==0
    assert scan_admission['runner_sha256']==hashlib.sha256((ROOT/'scripts/stream_access_scan.py').read_bytes()).hexdigest()
    v_commit='26abd496417d9392245052e54fbd9ba27c6ffd96'
    provenance=read_rows('PROVENANCE_SHA256.tsv')
    for original,copy in [('K1_SEMANTIC_CONTRACT.md','LANE_V_K1_SEMANTIC_CONTRACT.md'),
                          ('SOURCE_EVENT_MAP.md','LANE_V_SOURCE_EVENT_MAP.md')]:
        matches=[r for r in provenance if r['commit']==v_commit and r['path'].endswith('/'+original)]
        assert len(matches)==1
        assert matches[0]['sha256']==hashlib.sha256((ROOT/'inputs'/copy).read_bytes()).hexdigest()
    events=read_rows('SOURCE_DEFINED_INVALIDATE.tsv')
    assert {'INV_CONFIG_CHANGE','INV_CLUSTER_IDLE','INV_REGULAR_MEMBAR','KERNEL_DONE_NOT_INVALIDATE'}<={r['event_id'] for r in events}
    audit=json.loads((ROOT/'COMPLETION_AUDIT.json').read_text())
    assert audit['status']=='BOUNDED_REVIEW_REQUIREMENTS_MET'
    assert audit['K1_contract_known'] and not audit['K1_performance_extrapolation_permitted']
    assert not audit['full_original_body_scan_complete'] and not audit['auto_resume_or_background_scan']
    return dict(status='PASS', body_proof_members=523, scope_rows=527,
                access_counts_reconciled=True, unavailable_fields_preserved=True,
                trace_payloads_in_pack=0, new_simulation_attempts=0,
                synthetic_cpu_preflight_groups=6,analyzer_identity_matches_preflight=True,
                stream_and_cross_kernel_synthetic_checks=True,body_scan_admission='REFUSED',
                K1_contract_pinned=True,user_authorized_bounded_closure=True)


def manifest():
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name!='FILES_SHA256.tsv')
    with (ROOT/'FILES_SHA256.tsv').open('w') as f:
        f.write('path\tbytes\tsha256\n')
        for p in files:
            data=p.read_bytes()
            f.write(f'{p.relative_to(ROOT)}\t{len(data)}\t{hashlib.sha256(data).hexdigest()}\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--exercise-builder',action='store_true')
    parser.add_argument('--seal',action='store_true')
    args=parser.parse_args()
    if args.exercise_builder:
        exercise()
    result=verify()
    if args.seal:
        (ROOT/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
        manifest()
    else:
        for r in read_rows('FILES_SHA256.tsv'):
            data=(ROOT/r['path']).read_bytes()
            assert len(data)==int(r['bytes']) and hashlib.sha256(data).hexdigest()==r['sha256']
    print(json.dumps(result))
