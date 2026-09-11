#!/usr/bin/env python3
"""Prepare and run the C13 diagnostic matrix without mutating C12 inputs.

The tool writes only C13-derived configs, manifests, and fresh C13 output
directories.  It validates each completed arm before returning from replay.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
C12 = Path('/workspace/worktrees/accel-sim-vm-m4b-speculative')
CORE = Path('/workspace/worktrees/gpgpu-sim-vm-m4b-speculative')
BINARY = C12 / 'gpu-simulator/bin/release/accel-sim.out'
RUNTIME = CORE / 'lib/gcc-11.4.0/cuda-11080/release'
NEW_CORE = Path('/workspace/worktrees/gpgpu-sim-vm-m4b-c13-diagnostics')
NEW_BINARY = ROOT / 'gpu-simulator/bin/release/accel-sim.out'
NEW_RUNTIME = NEW_CORE / 'lib/gcc-11.4.0/cuda-11080/release'
OUT = Path('/workspace/vm-m4b-c13-diagnostics/results')
PACK = ROOT / 'docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C13_MINIMAL_DIAGNOSTICS'
CFG = ROOT / 'configs/vm_tlb/c13_diagnostics'
OP_PARSER = Path('/workspace/worktrees/accel-sim-vm-m4b-operator-aware/util/vm_tlb/analyze_c12_operator_aware.py')
EXPECTED = {
    'prefill': ('/workspace/m4c-c3-formal-20260905-v1/prefill-generic/traces/kernelslist.g',
                '/workspace/m4c-c3-formal-20260905-v1/prefill-generic/traces', 692,
                'a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f',
                '6ae0e18cc3bba29871002c4ff1877052489740163424723a845ead45c4a5f4b0'),
    'decode1': ('/workspace/m4c-c3-formal-20260905-v1/decode1-generic/traces/kernelslist.g',
                '/workspace/m4c-c3-formal-20260905-v1/decode1-generic/traces', 740,
                'b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc',
                '3dc77c1f348028ba7b8abfef3dc6c4cffa0c9678f003bc23bdc9158d62762b48'),
}
BINARY_SHA = '2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a'
CORE_SHA = '57bb71ecd015b6ec0ab32e45b0815e5beaf69172'
NEW_CORE_SHA = '4f5f2a2583d71e5aee0e5ff59b67e5e6cd7d5be0'
NEW_BINARY_SHA = '63c6011f20a22ff37afe0cef2958b67b32a9a6dcf0132d92ff28f62a8395cec4'
REGISTER = {
    'prefill': C12 / 'configs/vm_tlb/c5_registrations/C11_C5_PREFILL_V2_REGISTRATION.tsv',
    'decode1': C12 / 'configs/vm_tlb/c5_registrations/C11_C5_DECODE1_V2_REGISTRATION.tsv',
}
POINTS = {
    'C13-LAT-P8': ('prefill', 1, 8, 320, 8, 'FAIR_F7_GEOMETRY'),
    'C13-LAT-P9': ('prefill', 1, 8, 320, 9, 'FAIR_F7_GEOMETRY'),
    'C13-LAT-D11': ('decode1', 1, 8, 320, 11, 'FAIR_F7_GEOMETRY'),
    'C13-CAP-P320': ('prefill', 0, 0, 320, 0, 'DIAGNOSTIC_NON_EQUAL_BUDGET'),
    'C13-CAP-P768S10': ('prefill', 1, 8, 768, 10, 'DIAGNOSTIC_NON_EQUAL_BUDGET'),
}
SELECTIVE = {
    'C13-SEL-P10-CTRL-NEWBIN': ('prefill', 'ALL_C5_ELIGIBLE_WEIGHT', None),
    'C13-SEL-D10-CTRL-NEWBIN': ('decode1', 'ALL_C5_ELIGIBLE_WEIGHT', None),
    'C13-SEL-P10': ('prefill', 'EXCLUDE_EMBEDDING_OUTPUT_WEIGHT_RANGE', ROOT/'configs/vm_tlb/c13_diagnostics/selective/C13_PREFILL_EXCLUDE_EMBEDDING_OUTPUT_WEIGHT.tsv'),
    'C13-SEL-D10': ('decode1', 'EXCLUDE_EMBEDDING_OUTPUT_WEIGHT_RANGE', ROOT/'configs/vm_tlb/c13_diagnostics/selective/C13_DECODE1_EXCLUDE_EMBEDDING_OUTPUT_WEIGHT.tsv'),
}

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()

def fail(message: str) -> None: raise SystemExit('C13 FAIL: ' + message)

def source_config(roi: str, enabled: int) -> Path:
    return C12 / 'configs/vm_tlb/c5_configs' / (
        'C11_C5_%s_F7_Lseg10.config' % roi.upper() if enabled else
        'C11_C5_%s_F0.config' % roi.upper())

def config_text(exp: str, roi: str, enabled: int, n: int, exact: int, lseg: int, exclude: Path | None = None) -> str:
    base = source_config(roi, enabled).read_text()
    # MANUAL is essential: F7 only admits the historic 5/10/20 points, while
    # C13's L8/L9/L11 and non-equal-capacity observations are config-only.
    text = base + ('\n# C13 diagnostic override; frozen C12 input paths retained.\n'
                   '-gpgpu_vm_fair_arm 0\n'
                   '-gpgpu_vm_l2_tlb_entries %d\n'
                   '-gpgpu_vm_weight_segmentation_enable %d\n'
                   '-gpgpu_vm_weight_segment_entries %d\n'
                   '-gpgpu_vm_weight_segment_lookup_latency %d\n' %
                   (exact, enabled, n, lseg))
    if exclude is not None: text += '-gpgpu_vm_weight_segment_exclude_map %s\n' % exclude
    return text

def prepare() -> None:
    if sha(BINARY) != BINARY_SHA: fail('C12 binary SHA mismatch')
    if subprocess.check_output(['git','-C',str(CORE),'rev-parse','HEAD'], text=True).strip() != CORE_SHA:
        fail('C12 Core HEAD mismatch')
    rows = []
    for exp, (roi, enabled, n, exact, lseg, budget) in POINTS.items():
        trace, root, kernels, trace_sha, reg_sha = EXPECTED[roi]
        if sha(Path(trace)) != trace_sha or sha(REGISTER[roi]) != reg_sha: fail(exp + ' frozen input SHA mismatch')
        path = CFG / (exp + '.config')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(config_text(exp, roi, enabled, n, exact, lseg))
        rows.append({'exp_id':exp,'roi':roi,'config_path':str(path),'config_sha256':sha(path),
                     'trace_list':trace,'trace_root':root,'trace_sha256':trace_sha,
                     'registration_path':str(REGISTER[roi]),'registration_sha256':reg_sha,
                     'expected_kernels':str(kernels),'segment_enable':str(enabled),'segment_n':str(n),
                     'exact_l2_tlb_entries':str(exact),'lseg':'NONE' if not enabled else str(lseg),
                     'budget_class':budget,'binary_path':str(BINARY),'binary_sha256':BINARY_SHA,
                     'core_head':CORE_SHA,'output_dir':str(OUT / exp)})
    if sha(NEW_BINARY) != NEW_BINARY_SHA: fail('C13 binary SHA mismatch')
    if subprocess.check_output(['git','-C',str(NEW_CORE),'rev-parse','HEAD'], text=True).strip() != NEW_CORE_SHA:
        fail('C13 Core HEAD mismatch')
    for exp,(roi,policy,exclude) in SELECTIVE.items():
        trace,root,kernels,trace_sha,reg_sha=EXPECTED[roi]
        if exclude is not None and not exclude.is_file(): fail(exp+' exclusion artifact missing')
        path=CFG/(exp+'.config'); path.write_text(config_text(exp,roi,1,8,320,10,exclude))
        rows.append({'exp_id':exp,'roi':roi,'config_path':str(path),'config_sha256':sha(path),
                     'trace_list':trace,'trace_root':root,'trace_sha256':trace_sha,
                     'registration_path':str(REGISTER[roi]),'registration_sha256':reg_sha,
                     'expected_kernels':str(kernels),'segment_enable':'1','segment_n':'8',
                     'exact_l2_tlb_entries':'320','lseg':'10','budget_class':'DIAGNOSTIC_POLICY_CHANGE' if exclude else 'CONTROL_NOT_NEW_HYPOTHESIS',
                     'binary_path':str(NEW_BINARY),'binary_sha256':NEW_BINARY_SHA,'core_head':NEW_CORE_SHA,
                     'eligibility_policy':policy,'eligibility_artifact_sha256':sha(exclude) if exclude else 'NONE',
                     'core_path':str(NEW_CORE),'runtime_path':str(NEW_RUNTIME),'output_dir':str(OUT/exp)})
    PACK.mkdir(parents=True, exist_ok=True)
    fields=list(rows[0]) + ['eligibility_policy','eligibility_artifact_sha256','core_path','runtime_path']
    with (PACK/'C13_COMMAND_MANIFEST.tsv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
    print('C13_PREPARE_PASS\tpoints=%d' % len(rows))

def read_rows() -> dict[str,dict[str,str]]:
    path=PACK/'C13_COMMAND_MANIFEST.tsv'
    if not path.is_file(): fail('run --prepare first')
    with path.open(newline='') as f: return {r['exp_id']:r for r in csv.DictReader(f,delimiter='\t')}

COUNTER=re.compile(r'^([A-Za-z0-9_]+) = (-?[0-9]+(?:\.[0-9]+)?)\s*$')
def validate(row: dict[str,str], code: int) -> dict[str,object]:
    run=Path(row['output_dir']); log=run/'run.log'; errors=[]; vals={}
    lines=log.read_text(errors='strict').splitlines() if log.is_file() else []
    for line in lines:
        m=COUNTER.match(line)
        if m: vals[m.group(1)]=m.group(2)
    markers=sum(x.startswith('Processing kernel ') for x in lines)
    telemetry=sum(x.startswith('m4c_telemetry_schema =') for x in lines)
    required=('gpu_tot_sim_cycle','gpu_tot_sim_insn','gpu_tot_ipc','vm_l1_tlb_accesses','vm_l1_tlb_hits','vm_l1_tlb_misses','vm_l2_tlb_accesses','vm_l2_tlb_hits','vm_l2_tlb_misses','vm_pte_requests','vm_pte_responses','vm_pte_l2_only_responses','vm_pte_dram_responses','vm_object_attribution_conservation_pass','vm_weight_segmentation_enabled','vm_weight_segment_entries_configured','vm_weight_segment_lookup_latency_cycles','vm_weight_segment_mapping_mismatch_faults')
    if code != 0: errors.append('simulator_exit=%d' % code)
    if markers != int(row['expected_kernels']): errors.append('marker_count')
    if telemetry != int(row['expected_kernels']): errors.append('telemetry_count')
    if 'm4c_telemetry_schema = M4C_MEMORY_TELEMETRY_V1' not in lines: errors.append('telemetry_schema')
    if any(x not in vals for x in required): errors.append('missing_critical_counter')
    def iv(x): return int(vals[x])
    try:
        if iv('vm_l1_tlb_accesses') != iv('vm_l1_tlb_hits') + iv('vm_l1_tlb_misses'): errors.append('l1_conservation')
        if iv('vm_l2_tlb_accesses') != iv('vm_l2_tlb_hits') + iv('vm_l2_tlb_misses'): errors.append('l2_conservation')
        if iv('vm_pte_requests') != iv('vm_pte_responses') or iv('vm_pte_responses') != iv('vm_pte_l2_only_responses')+iv('vm_pte_dram_responses'): errors.append('pte_conservation')
        if iv('vm_object_attribution_conservation_pass') != 1: errors.append('object_conservation')
        if iv('vm_weight_segmentation_enabled') != int(row['segment_enable']): errors.append('segment_enable')
        if iv('vm_weight_segment_entries_configured') != int(row['segment_n']): errors.append('segment_entries')
        if iv('vm_weight_segment_lookup_latency_cycles') != (0 if row['lseg']=='NONE' else int(row['lseg'])): errors.append('segment_latency')
        if iv('vm_weight_segment_mapping_mismatch_faults') != 0: errors.append('segment_mapping_mismatch')
    except (KeyError,ValueError): errors.append('counter_parse')
    # Import the accepted parser solely for hardened per-kernel conservation.
    sys.path.insert(0,str(OP_PARSER.parent)); import analyze_c12_operator_aware as op
    raw=op.raw_kernels(log)
    if len(raw) != markers: errors.append('raw_marker_parse')
    if any(k.exact_occurrences['gpu_sim_cycle'] != 1 for k in raw): errors.append('kernel_cycle_missing_or_duplicate')
    if raw and sum(k.exact['gpu_sim_cycle'] for k in raw) != int(vals.get('gpu_tot_sim_cycle','-1')): errors.append('kernel_cycle_sum')
    active=[x for x in raw[-1].cumulative] if raw else []
    for name in active:
        prior=0
        for k in raw:
            if k.cumulative_occurrences[name] != 1 or name not in k.cumulative or k.cumulative[name] < prior:
                errors.append('vm_snapshot_continuity:'+name); break
            prior=k.cumulative[name]
        if name in vals and str(prior) != vals[name]: errors.append('vm_terminal:'+name)
    result={**row,'simulator_exit':str(code),'kernel_markers':str(markers),'telemetry_records':str(telemetry),
            'gpu_tot_sim_cycle':vals.get('gpu_tot_sim_cycle','NOT_EMITTED'),'gpu_tot_sim_insn':vals.get('gpu_tot_sim_insn','NOT_EMITTED'),'gpu_tot_ipc':vals.get('gpu_tot_ipc','NOT_EMITTED'),
            'raw_log_sha256':sha(log) if log.is_file() else 'MISSING','terminal_status':'PASS' if not errors else 'FAILED_DIAGNOSING','errors':errors}
    (run/'C13_ARM_VALIDATION.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    if errors: fail(row['exp_id']+' validation '+','.join(errors[:5]))
    print('C13_ARM_PASS\t%s\tcycles=%s' % (row['exp_id'],result['gpu_tot_sim_cycle']))
    return result

def execute(exp: str) -> None:
    row=read_rows().get(exp)
    if not row: fail('unknown exp '+exp)
    if sha(Path(row['binary_path'])) != row['binary_sha256'] or sha(Path(row['config_path'])) != row['config_sha256']: fail('provenance changed')
    run=Path(row['output_dir'])
    if run.exists(): fail('fresh-output policy refuses '+str(run))
    run.mkdir(parents=True); traces=run/'traces';traces.mkdir()
    target=traces/'kernelslist.g'; target.write_bytes(Path(row['trace_list']).read_bytes())
    if sha(target) != row['trace_sha256']: fail('copied trace SHA mismatch')
    for name in target.read_text().splitlines(): os.symlink(str(Path(row['trace_root'])/name),str(traces/name))
    command=['/usr/bin/time','-v',row['binary_path'],'-config',row['config_path'],'-trace',str(target)]
    with (run/'run.log').open('w') as log:
        core=Path(row.get('core_path') or CORE); runtime=Path(row.get('runtime_path') or RUNTIME)
        code=subprocess.run(command,cwd=run,env={**os.environ,'GPGPUSIM_ROOT':str(core),'LD_LIBRARY_PATH':str(runtime)},stdout=log,stderr=subprocess.STDOUT).returncode
    lines=(run/'run.log').read_text(errors='strict').splitlines()
    starts=[i for i,line in enumerate(lines) if line.lstrip().startswith('Command being timed:')]
    if starts: (run/'time-v.txt').write_text('\n'.join(lines[starts[-1]:])+'\n')
    validate(row,code)

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--execute');a=p.parse_args()
    if a.prepare == bool(a.execute): fail('select exactly one of --prepare or --execute')
    prepare() if a.prepare else execute(a.execute)
