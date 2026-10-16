#!/usr/bin/env python3
"""Strict new-input receipt; original collector and original attempts unchanged."""
import hashlib
import json
from pathlib import Path
import re
from collect_service_closure_attempts import collect, sha
from collect_service_closure_matched import effective_options

BUNDLE='6e59d31e018befcdd8d9244e6c90d09ab8dd51c665c77785857b690f051ed585'
MEMBERS=['6295eb13625bbc8f25a712917b1b92a02ffcd2e1faba542e555f7845a1288722', '3c67f85abf952be8a0d109497baabaf97a53d15d4f40e9d1ba2d74ddb1fdc481']


def review(run):
    run=Path(run); row=collect(run)
    if row['status']=='RUNNING': return row
    spec=json.loads((run/'SPEC.json').read_text()); start=json.loads((run/'RUN_START.json').read_text())
    text=(run/'simulator.stdout').read_text(errors='replace')
    metrics=dict(re.findall(r'^\s*(\w+)\s*=\s*(\d+)\s*$',text,re.M))
    checks=json.loads(row['scientific_checks']); options=effective_options(spec,run)
    def echo(name):
        values=re.findall(r'^'+re.escape(name)+r'\s+(\S+)',text,re.M)
        return values[-1] if values else None
    checks.update(stored_spec_equals_start=spec==start['spec'],
        bundle_identity=spec['input_bundle_sha256']==BUNDLE,
        admitted_identity=sha(Path(spec['admission_receipt']))==spec['admission_receipt_sha256'],
        trace_list_terminal=sha(Path(spec['trace_list']))==spec['trace_list_sha256'],
        member_terminal=len(spec['members'])==2 and [m['sha256'] for m in spec['members']]==MEMBERS and
            all(Path(m['path']).stat().st_size==m['bytes'] and sha(Path(m['path']))==m['sha256'] for m in spec['members']),
        ordered_full_kernels=re.findall(r'^kernel_name\s*=\s*(\S+)',text,re.M)==spec['expected_kernel_names'],
        per_kernel_instructions=[int(v) for v in re.findall(r'^gpu_sim_insn\s*=\s*(\d+)',text,re.M)]==[217350912,227116937],
        common_64sm=echo('-gpgpu_n_clusters')=='64' and echo('-gpgpu_n_cores_per_cluster')=='1',
        common_clocks=echo('-gpgpu_clock_domains')=='1410.0:1410.0:1410.0:850.0',
        common_lower_cap=echo('-gpgpu_dtc_l1_lower_outstanding_cap')=='32768',
        common_network=echo('-network_mode')=='2',
        full_roi=all(options.get(k,['0'])==['0'] for k in ['-gpgpu_max_cycle','-gpgpu_max_insn','-gpgpu_max_cta','-gpgpu_max_completed_cta']),
        no_stderr_errors=not any(v in (run/'simulator.stderr').read_text(errors='replace').lower() for v in ['assertion','segmentation fault','unsupported','fatal','error']),
        mode=echo('-gpgpu_dtc_l1_mode')==str(spec['expected_mode']))
    gate=json.loads(Path(spec['admission_receipt']).read_text())
    checks['admission_gate']=gate['status']=='DERIVED_INPUT_ADMITTED_FOR_BTRE_E_LIST_CONTRACT' and gate['bundle_sha256']==BUNDLE and all(gate['checks'].values())
    n=lambda name:int(metrics.get('DTC_L1_'+name,'-1'))
    checks['lower_terminal_drained']=n('lower_outstanding')==0
    if not spec['finite_service']:
        checks['base_mode']='DTC_L1_mode = PAPER_BASE' in text
        checks['base_admit_retire']=int(metrics.get('DTC_L1_pib_admits','-1'))==int(metrics.get('DTC_L1_pib_retires','-2'))>0
        checks['conventional_credit_balance']=n('lower_requests_acquired')==n('lower_requests_released')>0
        checks['conventional_cap_statistic']=n('lower_outstanding_cap')==32768
        checks['baseline_finite_absent']=not any(k.startswith('DTC_SERVICE_V1_') for k in metrics)
    else:
        key='-gpgpu_dtc_l1_'+spec['dtc_mode']+'_pib_entries'
        checks['active_depth']=echo(key)==str(spec['expected_active_pib'])
        checks['physical_pool']=echo('-gpgpu_dtc_l1_physical_lines')=='640'
        checks['logical_tags']=echo('-gpgpu_dtc_l1_logical_sets')=='32' and echo('-gpgpu_dtc_l1_logical_ways')=='4'
    row['scientific_checks']=json.dumps(checks,sort_keys=True)
    row['status']='PASS_CHECKED_SCOPE' if all(checks.values()) else 'FAIL_PRESERVED'
    return dict(schema='BTREE_E_LIST_DERIVED_STRICT_V1',input_bundle_sha256=BUNDLE,
        collector_sha256=sha(Path(__file__)),base_collector_sha256=sha(Path(__file__).with_name('collect_service_closure_attempts.py')),
        terminal_review=row,scientific_promotion='CONDITIONAL_E_LIST_DERIVED_INPUT_ONLY_NOT_CAPTURE_OR_NATIVE_EQUIVALENCE',
        input_interpretation='BTREE_FIXED_PC1C40_CONDITIONAL_FULL_E_LIST_TO_P_LIST_V1',
        aggregation='NONE_NO_OLD_INPUT_DENOMINATORS_NO_GM12')
