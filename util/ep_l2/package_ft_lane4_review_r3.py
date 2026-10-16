#!/usr/bin/env python3
"""Freeze review_r3 source audit and scientific veto evidence without rebuilding."""
import argparse
import csv
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
RESULTS=Path('/workspace/results/ep_l2_ft20261016/lane4')
REVIEW='a41bfb55934303a4d4a342762f74a16d137d0316'


def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def git(*a):return subprocess.check_output(['git','-C',str(ROOT),*a],text=True).strip()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pack',required=True);a=p.parse_args()
    out=ROOT/'docs/ep_l2/review_packs'/a.pack;out.mkdir(parents=True,exist_ok=False)
    producer=git('rev-parse','HEAD');assert not git('status','--porcelain','--untracked-files=no','--','util/ep_l2')
    audit=RESULTS/'review_r3_source_audit_r2';reject=RESULTS/'review_r3_rejection_checks_r1'
    for src in audit.iterdir():
        if src.is_file():shutil.copyfile(src,out/src.name)
    for name in ['RESULTS.json','CONSUMED_TOOL_CLOSURE.json']:
        shutil.copyfile(reject/name,out/('REJECTION_CHECKS.json' if name=='RESULTS.json' else name))
    for src in reject.glob('*.log'):shutil.copyfile(src,out/src.name)
    for source,name,count in [(RESULTS/'review_r3_acceptance_tests_r2.log','SCIENTIFIC_ACCEPTANCE_TESTS.log',21),
                              (RESULTS/'review_r3_binding_regression_r3.log','R1_BINDING_REGRESSION.log',20)]:
        text=source.read_text();assert f'Ran {count} tests' in text and text.rstrip().endswith('OK');shutil.copyfile(source,out/name)
    dependencies=[]
    for lane in [1,5]:
        commit=git('rev-parse',f'origin/hrl/ep-l2-ft20261016-lane{lane}-v1')
        prefix=f'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane{lane}/'
        receipt='RECEIPT.json'
        if lane==1:
            names=git('ls-tree','--name-only',commit,prefix+'RECEIPT_REVIEW_R3.json')
            if names:receipt='RECEIPT_REVIEW_R3.json'
        raw=subprocess.check_output(['git','show',commit+':'+prefix+receipt],cwd=ROOT)
        dest=out/f'LANE{lane}_RECEIPT_SNAPSHOT.json';dest.write_bytes(raw)
        dependencies.append(dict(lane_id=lane,publication_commit=commit,receipt_path=prefix+receipt,receipt_sha256=digest(dest)))
        if lane==5:
            for name in ['APPLICATION_ACCEPTANCE.json','SCIENTIFIC_HOLD.json','VALIDATION_MATRIX.json']:
                (out/('LANE5_'+name)).write_bytes(subprocess.check_output(['git','show',commit+':'+prefix+name],cwd=ROOT))
    write(out/'DEPENDENCIES.json',dependencies)
    rejection=json.loads((out/'REJECTION_CHECKS.json').read_text());assert len(rejection['production_cli_rejections'])==4 and len(rejection['old_actual_application_rows_rejected'])==6
    write(out/'SCIENTIFIC_SUPERSESSION.json',dict(review_commit=REVIEW,
        authority_publication=dependencies[1]['publication_commit'],
        supersedes=['prior R0/R1 application acceptance','Lane4 review_r2 wording that frozen R0 could immediately proceed'],
        scientific_status='OLD_FT_APPLICATION_QUALIFICATION_WITHDRAWN',
        original_execution_status='PRESERVED_NO_REGISTRY_MUTATION',
        retained_fixture_scope='Only previously tested local invariants; no repaired application acceptance',
        legacy_read_reference='73873->42918 (1.721259x) historical OLD_STATIC only; not automatically falsified by this FT defect and not a repaired ceiling',
        accepted_R1_1_application_rows=0,unrun_R1_1_cells=18,
        official_R0_1_release=None,official_R1_1_release=None))
    preserved=[]
    for name in ['FT20261016_LANE4_IDEAL_DIAGNOSTICS_r2','FT20261016_LANE4_OFF_EQUIVALENCE_r1','FT20261016_LANE4_R1_HANDOFF_r1']:
        old=ROOT/'docs/ep_l2/review_packs'/name
        subprocess.run(['sha256sum','-c','--quiet','SHA256SUMS'],cwd=old,check=True)
        preserved.append(dict(path=str(old.relative_to(ROOT)),checksums_sha256=digest(old/'SHA256SUMS'),status='UNCHANGED'))
    raw_rows=[]
    for p in sorted((RESULTS/'historical_diagnostic').glob('*/run_status.json')):
        r=json.loads(p.read_text());assert r['status']=='COMPLETE_VALID'
        assert digest(p.with_name('raw.log'))==r['raw_log_sha256']
        raw_rows.append(dict(run_key=r['run_key'],classification='HISTORICAL_DIAGNOSTIC_NOT_FORMAL_R1_1',
            original_terminal=r['status'],identity=r['identity'],run_status=str(p),run_status_sha256=digest(p),
            raw_log=str(p.with_name('raw.log')),raw_log_sha256=r['raw_log_sha256']))
    assert len(raw_rows)==3
    raw_rows+=rejection['old_actual_application_rows_rejected']
    write(out/'PRESERVATION_INDEX.json',dict(frozen_packs=preserved,raw_rows=raw_rows,raw_deleted=0,binary_overwrites=0,old_terminals_rewritten=0))
    client=json.loads(Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text())
    assert digest(client['registry_client'])==client['registry_client_sha256']
    sys.path.insert(0,str(Path(client['registry_client']).parent))
    from registry import Registry,local_resources
    snapshot=Registry(client['canonical_root']).snapshot();host=next(iter(snapshot['hosts'].values()))
    active=[dict(r,key=k) for k,r in snapshot['runs'].items() if r['status'] in ['RUNNING','RESERVED']]
    assert not [r for r in active if r['owner']=='lane4']
    live=local_resources()
    write(out/'RESOURCE_CHECK.json',dict(observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),resources=live,
        registry_updated_at=snapshot['updated_at'],active_runs=active,
        active_leases=[r for r in snapshot['resource_leases'].values() if r['status']!='RELEASED'],
        disk_floor_bytes=host['min_disk_free_bytes'],memory_floor_bytes=host['min_available_memory_bytes'],
        builds=0,simulations=0,admission_attempts=0,cleanup_actions=0,floor_changed=False,
        disk_below_floor=live['disk_free_bytes']<host['min_disk_free_bytes']))
    fields=['family','workload','mode','owner','status','cycles','instructions','core_source_commit','framework_source_commit','binary_sha256','runtime_config_sha256','trace_content_sha256','run_key']
    with (out/'R1_1_CEILING_RESULTS.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for workload in ['convolutionSeparable','FWT_7_21','vectorAdd_4M','sad']:
            for mode in ['B16_BANKED','I_WB','I_META','I_READ_HIT']+(['I_WB_META'] if workload in ['convolutionSeparable','FWT_7_21'] else []):
                w.writerow(dict(family='R1_1_REPAIRED_MATCHED_DIAGNOSTIC',workload=workload,mode=mode,
                    owner='lane5' if mode=='B16_BANKED' else 'lane4',status='NOT_RUN_REPAIRED_RELEASE_QUALIFICATION_AND_MATCHED_SPEC_PENDING'))
    write(out/'VALIDATION_COUNTS.json',dict(producing_tool_commit=producer,new_scientific_acceptance_tests_pass=21,
        binding_regression_tests_pass=20,actual_old_R1_CLI_rejections=4,actual_old_R0_rows_rejected=6,
        private_index_repair_replays_pass=2,repaired_runtime_production_tests=0,new_simulations=0,
        repaired_binary=None,trace=None,runtime_config=None,scope='SOURCE_AND_RUNNER_ONLY_NO_REPAIRED_RUNTIME_PASS'))
    (out/'README.md').write_text('''# Lane4 review_r3 — repaired R1.1 audit and withdrawal veto

Current status: SCIENTIFIC_HOLD for old FT application releases; repaired
R1.1 producer/binary/independent qualification/matched B16 specs pending.
R0.1 repair is Lane1's first priority and is not blocked by this diagnostic lane.
No compiler, simulator, cleanup or quota admission was launched here.

Read SCIENTIFIC_SUPERSESSION.json and the exact Lane5 authority snapshots first.
Old normal execution terminals remain frozen; old R0/R1 application PASS is
superseded. Three own historical application runs and all earlier packs/raw/
binaries are preserved. The old-static 1.721x reference is historical only.

New checks: 21 withdrawal tests, 20 binding regressions, rejection of all four
actual stale R1 prepared specs before registry claim, and rejection of six
actual old R0 complete rows by scientific intake. These are runner checks,
not repaired-model qualification. Latest published authority and qualification
bytes have veto; a copied old PASS cannot override withdrawal. Repaired runs
also require physical_bank_clock, memcpy_payload_identity and requested ideal
mode gates. Execution eligibility never implies CURRENT_ACCEPTED result.

SOURCE_REPAIR_AUDIT and REVIEW_FINDINGS record two conflict-free private-index
replays. Both repaired runtime trees match. The additional one-call ideal Tag
timestamp delta is an uncompiled candidate; physical bank time is unchanged.
Warmup dirty-victim, partial-sector/reinitialization and actual chosen-Tag/
handle agreement still require official producer validation. Apply success is
not runtime success. No official R1.1 source or binary is invented here.

The 18 repaired R1.1 cells are explicitly NOT_RUN with blank identity/metrics;
no old R0/R1/OLD_STATIC cell is substituted. Future execution needs Lane1's
separate official R1.1 freeze, Lane5's repaired/per-mode qualification and exact
same-binary B16 specs, then the unchanged central quota/registry.
''')
    (out/'SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.relative_to(out)}\n' for p in sorted(out.rglob('*')) if p.is_file() and p.name!='SHA256SUMS'))
    print(json.dumps(dict(pack=str(out),producer=producer,new_simulations=0,tests=41,source_replays=2,CLI_rejections=4,withdrawn_rows_rejected=6)))


if __name__=='__main__':main()
