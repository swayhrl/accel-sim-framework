"""Finite closed-receipt analysis; does not import or execute any project code."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess

WT = Path('/workspace/worktrees/accel-sim-iscas2027-dtc-ag6-io-diagnosis-174-v1')
OUT = Path('/workspace/dtc-ag6-io-diagnosis-174-v1/evidence')
BASE = Path('docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution')
ATT = BASE / 'ag6_actual_cohort_stop_v2/AE_GEMM'
ANCHOR = 'd9c192544622579a93d3efad98f56f82536c2fbe'
def read(p):
    return json.loads((WT / p).read_text())
def put(n, x):
    (OUT / n).write_text(json.dumps(x, indent=2) + '\n')
def git(*args):
    return subprocess.check_output(['git', '-C', str(WT), *args])
def counters(raw):
    return {line.split()[0]: {k:int(v) for k,v in (s.split('=') for s in line.split()[1:])}
            for line in raw.splitlines()}
start, terminal, summary = read(ATT/'RUN_START.json'), read(ATT/'RUN_TERMINAL.json'), read(BASE/'ag6_actual_cohort_stop_v2/STOP_SUMMARY.json')
baseline = read(ATT/'FINAL_PRE_FORK.json')['snapshot']
expected = {(r['pid'],r['start_ticks']) for r in terminal['engine']['owned_process_exit_instances']}
controller = (1086556, 918077690)
rows, detail, hashes = [], [], []
last_check = None
counts = {'host':0, 'cgroup':0}
digest = hashlib.sha256()
previous_t = None
with (WT/ATT/'RESOURCE_MONITOR.jsonl').open('rb') as stream:
    for line_no, line in enumerate(stream, 1):
        digest.update(line)
        r=json.loads(line); s=r['snapshot']; t=s['monotonic_ns']
        assert previous_t is None or t > previous_t
        qualified = last_check is None or t-last_check >= 30_000_000_000
        hp=s['pressure']; cp=s['cgroup_pressure_parsed']
        if qualified:
            for domain,pressure in [('host',hp),('cgroup',cp)]:
                counts[domain] = counts[domain]+1 if float(pressure['io']['full']['avg10'])>25 else 0
            last_check=t
        for domain in counts:
            assert counts[domain] == r['decision']['domains'][domain]['io_PSI_samples']
        own=[p for p in s['processes'] if (p['pid'],p['start_ticks']) in expected]
        manager=[p for p in s['processes'] if (p['pid'],p['start_ticks'])==controller]
        row=dict(line=line_no, utc=s['utc'], monotonic_ns=t,
                 elapsed_from_first_s=round((t-(rows[0]['monotonic_ns'] if rows else t))/1e9,6),
                 sample_gap_s='' if previous_t is None else round((t-previous_t)/1e9,6),
                 host_io_full_avg10=hp['io']['full']['avg10'],cgroup_io_full_avg10=cp['io']['full']['avg10'],
                 host_io_total_us=hp['io']['full']['total'],cgroup_io_total_us=cp['io']['full']['total'],
                 host_memory_full_avg10=hp['memory']['full']['avg10'],cgroup_memory_full_avg10=cp['memory']['full']['avg10'],
                 psi_qualification=qualified,host_io_run=counts['host'],cgroup_io_run=counts['cgroup'],
                 decision=r['decision']['decision'],warnings=';'.join(r['decision']['domains']['cgroup']['warnings']),
                 disk_free_bytes=s['disk_free_bytes'],host_MemAvailable_bytes=s['host_MemAvailable_bytes'],
                 cgroup_headroom_bytes=int(s['cgroup']['memory.max'])-int(s['cgroup']['memory.current']),
                 cgroup_swap_bytes=int(s['cgroup']['memory.swap.current']),pswpin=s['pswpin'],pswpout=s['pswpout'],
                 host_oom_kill=s['host_oom_kill'],cgroup_oom=s['cgroup']['events']['oom'],cgroup_oom_kill=s['cgroup']['events']['oom_kill'],
                 root_state=r['own']['state'] if r['own'] else 'UNAVAILABLE',
                 root_majflt=r['own']['majflt'] if r['own'] else 'UNAVAILABLE',
                 owned_instances=len(own),authority=r['authority']['status'],
                 provenance=str(ATT/'RESOURCE_MONITOR.jsonl')+':'+str(line_no))
        rows.append(row)
        detail.append(dict(line=line_no,utc=s['utc'],monotonic_ns=t,io_stat=counters(s['cgroup']['io.stat']),
                           diskstats=s['diskstats'],own=own,manager=manager,
                           cgroup_keys=list(s['cgroup']), cgroup_membership=s['cgroup_membership']))
        previous_t=t
assert rows[-1]['decision']=='STOP' and counts=={'host':0,'cgroup':3}
qualified_rows=[r for r in rows if r['psi_qualification'] and r['cgroup_io_run']>0]
assert [(r['utc'],r['monotonic_ns'],r['cgroup_io_full_avg10']) for r in qualified_rows] == [(r['utc'],r['monotonic_ns'],r['cgroup_io_full_avg10']) for r in summary['qualified_IO_samples']]
with (OUT/'STOP_RECONSTRUCTION.tsv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
put('CLOSED_EXTRACT.json',detail)
put('RECOMPUTATION.json',dict(rows=len(rows),monitor_sha256=digest.hexdigest(),qualified_matches_published=True,
    first=rows[0],last=rows[-1],qualified=qualified_rows,
    min_disk_bytes=min(r['disk_free_bytes'] for r in rows),
    max_host_io=max(float(r['host_io_full_avg10']) for r in rows),
    max_cgroup_io=max(float(r['cgroup_io_full_avg10']) for r in rows),
    min_host_memory=min(r['host_MemAvailable_bytes'] for r in rows),
    min_cgroup_memory=min(r['cgroup_headroom_bytes'] for r in rows)))
manifest_path=BASE/'AG6_EXECUTABLE_PREREGISTRATION_V2.json'
manifest_bytes=git('show',start['publication_head']+':'+str(manifest_path))
assert hashlib.sha256(manifest_bytes).hexdigest()==start['executable_manifest_sha256']
manifest=json.loads(manifest_bytes)
source_proof=[]
for absolute,sha in manifest['source_sha256'].items():
    rel=absolute.split('accel-sim-iscas2027-dtc-closure-exec-174-v1/')[1]
    data=git('show',start['publication_head']+':'+rel)
    assert hashlib.sha256(data).hexdigest()==sha
    assert (WT/rel).read_bytes()==data
    source_proof.append(dict(path=rel,publication=start['publication_head'],blob=git('rev-parse',start['publication_head']+':'+rel).decode().strip(),sha256=sha,bytes=len(data),matches_diagnostic_checkout=True))
put('EXECUTED_SOURCE_PROOF.json',dict(publication_head=start['publication_head'],manifest_sha256=start['executable_manifest_sha256'],files=source_proof))
required=[BASE/'CURRENT_ROLE_STATUS_AFTER_DISK_AUTHORIZATION_20261020.json',BASE/'AG6_SINGLE_WORKER_RELEASE_REVIEW_V2.json',BASE/'AG6_BUDGET_LEDGER.json',BASE/'SELECTION_V2.json',BASE/'ag6_actual_cohort_stop_v2/STOP_SUMMARY.json',BASE.parent/'CURRENT_STATE.md']
required+=list(ATT/p for p in ['RUN_START.json','RUN_TERMINAL.json','WRAPPER_EXCEPTION.json','STRICT.json','RESOURCE_FINAL.json','FINAL_PRE_FORK.json','RESOURCE_MONITOR.jsonl','ENGINE/CHILD.json','ENGINE/FORK_CHILD.json','ENGINE/START.json','ENGINE/TERMINAL.json'])
for rel in required:
    data=(WT/rel).read_bytes() if rel.name!='RESOURCE_MONITOR.jsonl' else None
    sha=hashlib.sha256(data).hexdigest() if data is not None else digest.hexdigest()
    assert git('rev-parse',ANCHOR+':'+str(rel))==git('hash-object',str(WT/rel))
    hashes.append(dict(path=str(rel),anchor=ANCHOR,blob=git('rev-parse',ANCHOR+':'+str(rel)).decode().strip(),sha256=sha,bytes=(WT/rel).stat().st_size))
assert next(x['sha256'] for x in hashes if x['path'].endswith('/RUN_START.json'))==read(BASE/'AG6_BUDGET_LEDGER.json')['run_start_receipts'][0]['sha256']
put('PRIMARY_PROVENANCE.json',hashes)
raw=Path(summary['raw_evidence']['path'])
stdout_proof=next(x for x in summary['raw_evidence']['files'] if x['path']=='ENGINE/stdout')
stdout=(raw/'ENGINE/stdout').read_bytes()
assert len(stdout)==stdout_proof['bytes'] and hashlib.sha256(stdout).hexdigest()==stdout_proof['sha256']
put('STDOUT_FINDINGS.json',dict(**stdout_proof,closed_source=str(raw/'ENGINE/stdout'),
    last_lines=stdout.decode(errors='replace').splitlines()[-24:]))
print(json.dumps(json.loads((OUT/'RECOMPUTATION.json').read_text()),indent=2))
print('source files verified',len(source_proof))
print('stdout tail',stdout.decode(errors='replace').splitlines()[-24:])
