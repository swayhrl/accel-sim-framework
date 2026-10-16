#!/usr/bin/env python3
"""Read-only R0 receipts; never launch a simulator or modify an old attempt."""
import argparse
import csv
import hashlib
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def rows(path):
    with Path(path).open() as f:
        return list(csv.DictReader(f, delimiter='\t'))


def table(path, data):
    assert data
    with Path(path).open('w') as f:
        w = csv.DictWriter(f, fieldnames=list(data[0]), delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(data)


def member_receipt(r):
    p = Path(r['trace_root']) / r['member']
    actual = sha(p) if p.is_file() else 'MISSING'
    header = {}
    if p.is_file():
        with p.open() as f:
            for line in f:
                if line.startswith('#traces format'):
                    break
                if line.startswith('-') and ' = ' in line:
                    k, v = line.strip().split(' = ', 1)
                    header[k[1:]] = v
    return dict(workload=r['workload'], ordinal=r['ordinal'], member=r['member'],
                path=str(p), bytes=p.stat().st_size if p.exists() else -1,
                expected_sha256=r['sha256'], actual_sha256=actual,
                identity='PASS' if actual == r['sha256'] and p.stat().st_size == int(r['bytes']) else 'FAIL',
                kernel=header.get('kernel name', 'UNKNOWN'),
                grid=header.get('grid dim', 'UNKNOWN'), block=header.get('block dim', 'UNKNOWN'),
                shared_bytes=header.get('shmem', 'UNKNOWN'), registers=header.get('nregs', 'UNKNOWN'),
                binary_version=header.get('binary version', 'UNKNOWN'),
                input_shape='NOT_ESTABLISHED_BY_TRACE_HEADER',
                coverage='HEADER_ONLY_NOT_DYNAMIC_CTA_OR_STEADY_INTERVAL_PROOF')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[2]
    gen = root / 'docs/dtc_l1/fast64/generated'
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=False)
    members = rows(gen / 'FAST64_PAYLOAD_MEMBERS.tsv')
    with ThreadPoolExecutor(max_workers=4) as pool:
        audited = list(pool.map(member_receipt, members))
    table(out / 'PAYLOAD_MEMBERS.tsv', audited)
    payloads = []
    for r in rows(gen / 'FAST64_PAYLOAD_MANIFEST.tsv'):
        selected = [a for a in audited if a['workload'] == r['workload']]
        list_path = Path(r['trace_root']) / 'kernelslist.g'
        ordered = ''.join(f"{int(a['ordinal']):08d}\t{a['member']}\t{a['actual_sha256']}\n" for a in selected)
        actual_set = hashlib.sha256(ordered.encode()).hexdigest()
        actual_list = sha(list_path)
        listing = [s for s in list_path.read_text().splitlines() if s.endswith('.traceg')]
        ok = (all(a['identity'] == 'PASS' for a in selected)
              and listing == [a['member'] for a in selected]
              and actual_set == r['ordered_traceg_set_sha256']
              and actual_list == r['kernelslist_g_sha256']
              and len(selected) == int(r['traceg_members'])
              and sum(a['bytes'] for a in selected) == int(r['traceg_bytes']))
        payloads.append(dict(**r, actual_list_sha256=actual_list, actual_set_sha256=actual_set,
                             audit='PASS' if ok else 'FAIL'))
    table(out / 'PAYLOAD_AUDIT.tsv', payloads)
    accepted = rows(gen / 'fast64_4_cap_resolved_matrix_v1/fast64_4_primary_accepted_matrix_v1.tsv')
    identities = rows(gen / 'fast64_4_cap_resolved_matrix_v1/fast64_4_identity_manifest.tsv')
    accepted_by_key = {(r['workload'], r['mode']): r for r in accepted}
    ledger, metrics = [], []
    metric_keys = ['gpu_tot_sim_cycle', 'gpu_tot_sim_insn', 'L1D_total_cache_accesses',
                   'L1D_total_cache_misses', 'L2_total_cache_accesses', 'L2_total_cache_misses',
                   'gpgpu_n_mem_read_global', 'gpgpu_n_mem_write_global',
                   'DTC_L1_m4_dynamic_loads', 'DTC_L1_m4_bypass_load_admits']
    for r in identities:
        p = root / r['evidence_path']
        d = json.loads(p.read_text())
        ext = d['external_artifacts']
        log = Path(ext['run_dir']) / 'simulator.stdout'
        raw_ok = log.is_file() and sha(log) == ext['simulator_stdout_sha256']
        evidence_ok = sha(p) == r['evidence_sha256']
        current_status = accepted_by_key[(r['workload'], r['mode'])]['acceptance_status']
        host = d.get('host', {})
        ledger.append(dict(workload=r['workload'], mode=r['mode'], historical_acceptance=current_status,
                           evidence_path=r['evidence_path'], evidence_sha256=sha(p),
                           evidence_identity='PASS' if evidence_ok else 'FAIL', raw_log=str(log),
                           raw_log_sha256=ext['simulator_stdout_sha256'], raw_identity='PASS' if raw_ok else 'FAIL',
                           source_core=r['core_sha'], binary_sha256=r['runtime_sha256'],
                           framework=r['scientific_framework_sha'], config_sha256=r['config_sha256'],
                           trace_list_sha256=r['trace_list_sha256'],
                           elapsed_wall=host.get('elapsed_wall', 'UNKNOWN'), max_rss_kb=host.get('max_rss_kb', 'UNKNOWN'),
                           finite_service_reuse='UNQUALIFIED_NEEDS_ROW_EQUIVALENCE',
                           action='PRESERVE_NO_RERUN_FOR_INVENTORY'))
        metrics.append(dict(workload=r['workload'], mode=r['mode'],
                            scope='HISTORICAL_MODEL_ONLY',
                            **{k: d['metrics'].get(k, 'UNAVAILABLE') for k in metric_keys}))
    table(out / 'ROW_REUSE_LEDGER.tsv', ledger)
    table(out / 'HISTORICAL_PATH_METRICS.tsv', metrics)
    tc = []
    for r in rows(root / 'docs/dtc_l1/iscas2027/tc80/CM3_TC80_FAST12_RUN_MANIFEST.tsv'):
        run = Path(r['run_dir'])
        validation = run / 'VALIDATION.json'
        tc.append(dict(**r, validation_present=validation.is_file(),
                       validation_identity='PASS' if validation.is_file() and sha(validation) == r['strict_validation_sha256'] else 'FAIL',
                       finite_service_reuse='UNQUALIFIED_NEEDS_BASELINE_EQUIVALENCE'))
    table(out / 'TC80_REUSE_LEDGER.tsv', tc)
    source = []
    core = Path('/workspace/repos/gpgpu-sim_distribution')
    for commit in ['95ccdb7a056f2d53f740d90869785cac6d4ee0f5',
                   '6587238c60214d99491f4048e28ce8a3458c1509',
                   '6582b9d171330d88b17e8d5294c97704229e3823']:
        for path in ['src/gpgpu-sim/dtc-l1-common.h', 'src/gpgpu-sim/shader.cc',
                     'src/gpgpu-sim/shader.h', 'src/gpgpu-sim/gpu-sim.cc',
                     'src/gpgpu-sim/gpu-cache.cc', 'src/gpgpu-sim/gpu-cache.h']:
            data = subprocess.check_output(['git', '-C', str(core), 'show', f'{commit}:{path}'])
            source.append(dict(core_commit=commit, path=path, sha256=hashlib.sha256(data).hexdigest()))
    table(out / 'SOURCE_HASHES.tsv', source)
    summary = dict(payload_workloads=len(payloads), ordered_members=len(audited),
                   bytes=sum(a['bytes'] for a in audited),
                   payload_failures=sum(r['audit'] != 'PASS' for r in payloads),
                   historical_rows=len(ledger), evidence_failures=sum(r['evidence_identity'] != 'PASS' for r in ledger),
                   raw_failures=sum(r['raw_identity'] != 'PASS' for r in ledger),
                   tc80_rows=len(tc), tc80_receipt_failures=sum(r['validation_identity'] != 'PASS' for r in tc),
                   core_finite_service='NOT_IMPLEMENTED', R1='NOT_QUALIFIED', R2='GATED')
    (out / 'SUMMARY.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
