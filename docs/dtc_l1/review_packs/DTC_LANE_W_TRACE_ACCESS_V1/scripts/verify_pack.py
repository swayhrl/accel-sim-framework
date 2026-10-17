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
    return dict(status='PASS', body_proof_members=523, scope_rows=527,
                access_counts_reconciled=True, unavailable_fields_preserved=True,
                trace_payloads_in_pack=0, new_simulation_attempts=0)


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
