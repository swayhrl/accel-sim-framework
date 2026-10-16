#!/usr/bin/env python3
"""Freeze necessary R2 rows after the R1 gate, without launching them."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--specs-dir', required=True)
    ap.add_argument('--plan', required=True)
    args = ap.parse_args()
    fw = Path(__file__).resolve().parents[2]
    base = fw / 'docs/dtc_l1/iscas2027/service_closure_174_v1'
    gate = json.loads((base / 'review_pack/r1/GATE.json').read_text())
    assert gate['gate'] == 'R1_PASS_FOR_FIXED_PILOT_QUALIFICATION'
    runtime = Path('/workspace/dtc-service-closure-174-v1/build-r1-a1/accel-sim.out')
    assert sha(runtime) == gate['binary_sha256']
    canonical = Path('/tmp/dtc-sg1-canonical-core6582b9d1-r2/accel-sim.out')
    assert sha(canonical) == '4fcac62cd7bdccc5a49cc77950ffc45c60d5fce7c4ee44bba877e1fef2d07ef9'
    with (fw / 'docs/dtc_l1/iscas2027/tc80/TC80_WORKLOAD_AUTHORITY.tsv').open() as f:
        authority = list(csv.DictReader(f, delimiter='\t'))
    with (fw / 'docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MEMBERS.tsv').open() as f:
        members = list(csv.DictReader(f, delimiter='\t'))
    specs = Path(args.specs_dir).resolve()
    specs.mkdir(exist_ok=False)
    cfg = base / 'config'
    trace_cfg = Path('/workspace/worktrees/accel-sim-decoupled-l1-fast64/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config')
    framework = subprocess.check_output(['git', '-C', str(fw), 'rev-parse', 'HEAD'], text=True).strip()
    pilots = ['BICG', 'Btree', '2DConvolution', 'Hotspot1']
    primary_order = [('BICG','IO'),('BICG','OO'),('Btree','IO'),('Btree','OO'),
                     ('Btree','TRAD96'),('BICG','TRAD96'),('2DConvolution','IO'),
                     ('Hotspot1','OO'),('2DConvolution','OO'),('Hotspot1','IO'),
                     ('2DConvolution','TRAD96'),('Hotspot1','TRAD96')]
    plan = []
    for a in authority:
        name = a['workload']
        arms = ['IO', 'OO', 'TRAD96'] + (['WAIT128', 'IO128'] if name in pilots else [])
        for arm in arms:
            finite = arm in ['IO','OO','IO128']
            mode = 'IO' if arm == 'IO128' else arm
            phase = 'PILOT' if name in pilots and arm in ['IO','OO','TRAD96'] else 'CONTROL' if arm in ['IO128','WAIT128'] else 'COHORT'
            config_paths = [fw / f'configs/dtc_l1/fast64/FAST64_{mode if finite else "BASE"}.config',
                            cfg / ('FINITE_MATCHED128.config' if arm == 'IO128' else
                                   'FINITE_PRIMARY_COMMON.config' if finite else
                                   'TRAD96_P256_M512.config' if arm == 'TRAD96' else 'WAIT128.config'), trace_cfg]
            binary = runtime if finite else canonical
            spec = dict(label=f'R2_{phase}_{arm}_{name}', workload=name, arm=arm, phase=phase,
                        classification='FINITE_SERVICE_PAIRED_SIMULATION_NOT_NATIVE_DTC_SPEEDUP',
                        core=gate['core'] if finite else '6582b9d171330d88b17e8d5294c97704229e3823',
                        build_framework=gate['build_framework'], orchestrator_framework=framework,
                        runtime=str(binary), runtime_sha256=sha(binary),
                        finite_service=finite, dtc_mode=mode.lower() if finite else 'base',
                        trace_list=a['trace_list'], trace_list_sha256=a['trace_list_sha256'],
                        expected_instructions=int(a['instructions']),
                        configs=[dict(path=str(p), sha256=sha(p)) for p in config_paths],
                        members=[dict(path=str(Path(m['trace_root']) / m['member']), sha256=m['sha256'], bytes=int(m['bytes']))
                                 for m in members if m['workload'].lower() == name.lower()])
            if not finite:
                spec.update(expected_dl1='N:32:128:24,L:T:m:L:L,A:512:8,16:0,32' if arm == 'TRAD96' else 'N:32:128:4,L:T:m:L:L,A:512:8,16:0,32',
                            expected_mshr=512 if arm == 'TRAD96' else 32,
                            expected_pib=256 if arm == 'TRAD96' else 128)
            path = specs / (spec['label'] + '.json')
            path.write_text(json.dumps(spec, indent=2) + '\n')
            if phase == 'PILOT':
                priority = primary_order.index((name, arm))
            else:
                priority = 20 + int(a['ordinal']) * 3 + ['IO','OO','TRAD96'].index(arm) if phase == 'COHORT' else 100 + int(a['ordinal'])
            plan.append(dict(label=spec['label'], workload=name, arm=arm, phase=phase, priority=priority,
                             heavy=name in ['GESUMMV','GEMM','MRI-Q'], spec_path=str(path), spec_sha256=sha(path),
                             launch_gate='R1' if phase=='PILOT' else 'ANY_VALID_PILOT_SAME_ARM' if phase=='COHORT' else 'VALID_IO_AND_OO_PILOT',
                             action='NECESSARY_PREREGISTERED_NOT_YET_LAUNCHED'))
    assert len(plan) == 44
    with Path(args.plan).open('x') as f:
        w = csv.DictWriter(f, fieldnames=list(plan[0]), delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(sorted(plan, key=lambda r:(r['priority'],r['label'])))
    print(json.dumps(dict(rows=len(plan), pilot=12, primary_and_enhanced_cohort=24, controls=8)))


if __name__ == '__main__':
    main()
