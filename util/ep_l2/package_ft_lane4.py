#!/usr/bin/env python3
"""Freeze Lane 4 executed evidence without modifying historical inputs."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import socket
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
COORD='6c136e2a56a008695f8c8b815723bf8f1a760db9'
BRANCH='hrl/ep-l2-ft20261016-lane4-v1'


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()


def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args],text=True).strip()
def write(p,value):p.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def csvwrite(p,fields,rows):
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--results',type=Path,required=True);a.add_argument('--audit',type=Path,required=True)
    a.add_argument('--pack',required=True)
    a.add_argument('--core',type=Path,required=True)
    a.add_argument('--parser-log',type=Path,required=True)
    a.add_argument('--candidate-revision',default='r1')
    args=a.parse_args();out=ROOT/'docs/ep_l2/review_packs'/args.pack
    out.mkdir(parents=True,exist_ok=False)
    producer=git('rev-parse','HEAD')
    assert not git('status','--porcelain','--untracked-files=no','--','util/ep_l2'), 'Freeze tooling first'
    rev=args.candidate_revision
    build=json.loads((args.results/f'BUILD_MANIFEST_b16_{rev}.json').read_text())
    tests=json.loads((args.results/f'tests_b16_{rev}/TEST_MANIFEST.json').read_text())
    assert len(tests['tests'])>=8 and all(r['returncode']==0 for r in tests['tests'])
    legality=json.loads((args.results/f'mode_legality_{rev}/RESULTS.json').read_text())
    assert len(legality['cases'])==6 and all(r['status']=='PASS_EXPECTED_REJECTION' for r in legality['cases'])
    attempt_note=args.results/f'mode_legality_{rev}/ATTEMPT_NOTE.json'
    if attempt_note.exists():shutil.copyfile(attempt_note,out/'MODE_LEGALITY_HARNESS_NOTE.json')
    for name in ['REUSE_AUDIT.csv','HISTORY_SEARCH.json']:shutil.copyfile(args.audit/name,out/name)
    for source,name in [(args.results/f'BUILD_MANIFEST_b16_{rev}.json','BUILD_MANIFEST.json'),
                        (args.results/f'tests_b16_{rev}/TEST_MANIFEST.json','PRODUCTION_TEST_MANIFEST.json'),
                        (args.results/f'mode_legality_{rev}/RESULTS.json','MODE_LEGALITY_RESULTS.json'),
                        (args.results/'DUPLICATE_CHECK_r1.json','DUPLICATE_CHECK.json')]:
        shutil.copyfile(source,out/name)
    dependencies=[]
    for lane in (1,5):
        ref=f'origin/hrl/ep-l2-ft20261016-lane{lane}-v1';commit=git('rev-parse',ref)
        rel=f'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane{lane}/RECEIPT.json'
        text=subprocess.check_output(['git','-C',str(ROOT),'show',commit+':'+rel])
        (out/f'LANE{lane}_RECEIPT_SNAPSHOT.json').write_bytes(text)
        dependencies.append({'lane_id':lane,'publication_commit':commit,'receipt_path':rel,
                             'receipt_sha256':sha(out/f'LANE{lane}_RECEIPT_SNAPSHOT.json')})
    baseline=git('show',dependencies[0]['publication_commit']+':docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane1/BASELINE_CONTRACT_V1.json')
    write(out/'LANE1_BASELINE_SNAPSHOT.json',json.loads(baseline))
    baseline_contract=json.loads(baseline)
    assert not baseline_contract.get('independent_qualification'), 'Dependency advanced: consume qualified source instead of freezing a stale pending report'
    assert build['lane1_parent_commit']==baseline_contract['core_source_commit'], 'Update diagnostic integration to the current producer first'
    parent=build['lane1_parent_commit']
    cpp_count=len(tests['tests'])
    import re
    match=re.search(r'Ran (\d+) tests',args.parser_log.read_text())
    assert match and args.parser_log.read_text().rstrip().endswith('OK')
    parser_count=int(match[1])
    normal_check=args.results/'LANE1_NORMAL_BINARY_CHECK_r1.json'
    check=json.loads(normal_check.read_text())
    assert check['binary_sha256']==baseline_contract['binary_sha256']
    assert not any(check['diagnostic_registrations'].values())
    shutil.copyfile(normal_check,out/'LANE1_NORMAL_BINARY_CHECK.json')
    vectors={'B16_BANKED':{'wb':False,'meta':False,'read_hit':False},
             'I_WB':{'wb':True,'meta':False,'read_hit':False},
             'I_META':{'wb':False,'meta':True,'read_hit':False},
             'I_READ_HIT':{'wb':False,'meta':False,'read_hit':True},
             'I_WB_META':{'wb':True,'meta':True,'read_hit':False}}
    write(out/'IDEAL_CONTRACTS.json',{'coordination_commit':COORD,'code_candidate':build,
        'status':'PRODUCTION_TESTED_CANDIDATE_NOT_QUALIFIED_SHARED_B16_RELEASE',
        'vectors':vectors,'default_off':True,'primary_nominal_data_slots_per_slice':1168,
        'wb':{'storage':'dynamic extra WB-only backing; explicitly outside 1168 budget',
              'retained':['WAD128','ordering','source-read/staging-write/lower-read service','4 banks x 1 op/cycle','lower queues','scheduler','DRAM'],
              'proof':'C8/C16 exceed quota; WAD128 still refuses; copy/read/accept and sector versions close'},
        'meta':{'storage':'dynamic descriptor vector and ordinary address-indexed MSHR map; checked unsigned IDs',
                'relaxed':['Line-MSHR count','global descriptor count','per-address count'],
                'retained':['sector coalescing','RAW/WAR/atomic handling','real fills','response retirement','tag/payload capacity','lower system'],
                'proof':'200 lines / 1640 requests / 800 lower sectors drain; allocator workloads 1024 and 2048'},
        'read_hit':{'kind':'optimistic read-miss-cost reference, not implementable EP-L2 speedup or strict mathematical upper bound',
                    'reference':'SASS has no initial/written bytes: explicit byte-address/producer-version symbols; actual byte seeds in production-driven tests',
                    'numeric_application_validation':'NOT_AVAILABLE_FROM_DATALESS_SASS_TRACE',
                    'retained':['normal ROP hit delay','bank arbitration','NoC/real response FIFO','older producer/WAD/MSHR dependencies','ordinary writes and atomics']},
        'I_BANK':'NOT_SELECTED: conditional follow-up only after the first diagnostics identify unexplained real bank contention',
        'formal_run_gate':'Lane1 must integrate the minimal patch; Lane5 independently qualifies the same shared binary and supplies the exact B16 baseline spec. prepare_ft_lane4_b16.py rejects an unqualified/registration-missing common binary.'})
    source_map=f'''# Ideal-mode source and lifecycle map

All source below is the Core candidate in BUILD_MANIFEST.json. Its Lane 1
parent is `{parent}`; the merge retains Lane 1's
production implementation. `CORE_MINIMAL.patch` is the delta from that parent,
not a request to merge every historical branch. Apply this patch after the
exact parent, then build once with all diagnostics OFF; Lane5 owns independent
qualification. Lane4 does not declare itself accepted. The diagnostic read
response uses the parent's actual requester admission/response audit hooks.

| Mode | Producer/consumer path | Preserved boundary |
|---|---|---|
| I_WB | gpu-sim.cc registration -> cache_config -> ep_l2_payload_store constructor -> const preview_free(WB) -> reserve() grows backing only at commit -> inherited ft_access copy phases -> lower_ready -> lower_accepted | Actual copy/read bank grants; WB packet sector versions; data release only after lower acceptance; independent WAD release at set_done |
| I_META | gpu-sim.cc -> mshr_table.m_ideal_meta -> full_reason / ensure_descriptor_available -> ordinary add / needs_lower_read / mark_ready / peek / commit | Capacities alone are non-binding; sector masks, pending atomic/order state and descriptor release after real response enqueue remain |
| I_READ_HIT | gpu-sim.cc -> memory_sub_partition frontend after ordinary ROP delay -> older producer/WAD/MSHR checks -> diagnostic role through same payload-bank arbiter -> ReferenceMemory snapshot -> real L2-to-ICNT FIFO -> pop retirement | No dropped request, synchronous callback, zero hit-delay shortcut, write/atomic bypass, or uninitialized cache-line data |

I_WB extra IDs retain modulo-4 banking. Appended slots are WB-only and
explicitly outside the nominal physical budget. WAD128 naturally bounds live
staging; no C-entry control ceiling is substituted. Diagnostic storage growth
does not grant another bank/port or remove copying.

I_META's dynamic vector updates descriptor accounting and keeps unsigned IDs;
it does not substitute a guessed large constant. Application capacity-full
counters must be zero before calling metadata non-binding. Histograms whose
historic bins stop at configured capacity must not be treated as proof of an
unbounded resource; use exact blockers, peaks and directed lifecycle evidence.

The read reference distinguishes known bytes and opaque cold/version symbols.
SASS performance runs do not prove numerical application output. Tests seed
real bytes, exercise masked stores and RAW/WAR response ordering, and verify
the same queued snapshots. Atomics remain on the ordinary producer path; this
pack does not claim a separate numerical atomic-opcode validation.

Default OFF preserves ordinary APIs. I_WB requires static FT mode 1; I_READ_HIT
cannot combine with WB/META or unified mode 2. Six CLI combinations reject
before workloads execute. The accepted I_WB_META combination is additionally
tested with 50 WB, 160 outstanding lines, 680 requesters and exact retirement.

Historical directed stress fixtures enlarge issue storage only to expose the
metadata allocator under test. The application overlays preserve primary
issue/DRAM/L1 settings. They are different evidence categories.
'''
    (out/'IDEAL_MODE_SOURCE_MAP.md').write_text(source_map)
    patch=subprocess.check_output(['git','-C',str(args.core),
        'diff','--binary',parent,build['core_source_commit']],text=True)
    (out/'CORE_MINIMAL.patch').write_text(patch)
    rows=[];raw_index=[];movement=[];identities=[];input_audits=[]
    for p in sorted((args.results/'historical_diagnostic').glob('*/run_status.json')):
        r=json.loads(p.read_text());identity=r['identity']
        identities.append(identity);input_audits.append(json.loads(p.with_name('input_audit.json').read_text()))
        assert r['status']=='COMPLETE_VALID'
        parsed=json.loads(p.with_name('reparsed_summary_r1.json').read_text());summary=parsed['summary']
        assert parsed['raw_log_sha256']==sha(p.with_name('raw.log'))==r['raw_log_sha256']
        rows.append({'family':'HISTORICAL_DIAGNOSTIC_OLD_D512_STATIC','workload':identity['workload'],'mode':r['mode'],
                     'status':r['status'],'cycles':summary['cycles'],'instructions':summary['instructions'],
                     'speedup_vs_matched_control':'','run_key':r['run_key'],'owner':'lane4','core_source_commit':identity['core_source_commit'],
                     'framework_source_commit':identity['framework_source_commit'],'binary_sha256':identity['binary_sha256'],
                     'runtime_config_sha256':identity['runtime_config_sha256'],'trace_content_sha256':identity['trace_content_sha256'],
                     'result_directory':str(p.parent)})
        raw_index.append({'run_key':r['run_key'],'mode':r['mode'],'status':r['status'],'raw_log':str(p.with_name('raw.log')),
                          'raw_log_sha256':r['raw_log_sha256'],'run_status_sha256':sha(p),'input_spec_sha256':sha(p.with_name('input_spec.json'))})
        for metric,value in summary['limiter_counts'].items():
            movement.append({'family':'HISTORICAL_DIAGNOSTIC_OLD_D512_STATIC','workload':identity['workload'],
                             'mode':r['mode'],'metric':metric,'value':value if value is not None else 'NOT_RETAINED',
                             'semantics':'summed per-slice event/attempt counter; bytes fields are transferred bytes; not global stalled cycles'})
    assert len(rows)==2
    for key in ['core_source_commit','framework_source_commit','binary_sha256','trace_content_sha256','workload','epoch_range','feature_vector','termination_contract']:
        assert identities[0][key]==identities[1][key], 'unmatched historical comparison: '+key
    assert input_audits[0]['configs'][:-1]==input_audits[1]['configs'][:-1]
    assert input_audits[0]['assets']==input_audits[1]['assets'] and input_audits[0]['traces']==input_audits[1]['traces']
    assert rows[0]['instructions']==rows[1]['instructions']==56000000
    control=next(r for r in rows if r['mode']=='OFF')
    for r in rows:r['speedup_vs_matched_control']=control['cycles']/r['cycles']
    for workload in ['convolutionSeparable','FWT_7_21','vectorAdd_4M','sad']:
        for mode in ['B16_BANKED','I_WB','I_META','I_READ_HIT']+(['I_WB_META'] if workload in ['convolutionSeparable','FWT_7_21'] else []):
            rows.append({'family':'B16_FIRST_WAVE','workload':workload,'mode':mode,
                         'status':'NOT_RUN_DEPENDENCY_PENDING_SHARED_RELEASE','owner':'lane5' if mode=='B16_BANKED' else 'lane4'})
    fields=['family','workload','mode','status','cycles','instructions','speedup_vs_matched_control','run_key','owner',
            'core_source_commit','framework_source_commit','binary_sha256','runtime_config_sha256','trace_content_sha256','result_directory']
    csvwrite(out/'CEILING_RESULTS.csv',fields,rows)
    csvwrite(out/'LIMITER_MOVEMENT.csv',['family','workload','mode','metric','value','semantics'],movement)
    csvwrite(out/'RAW_LOG_INDEX.csv',list(raw_index[0]),raw_index)
    log_rows=[]
    for sub in [f'tests_b16_{rev}',f'mode_legality_{rev}']:
        for p in sorted((args.results/sub).glob('*.log')):
            log_rows.append({'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size})
    for name in ['build_r1.log',f'build_b16_{rev}.log']:
        p=args.results/name;log_rows.append({'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size})
    log_rows.append({'path':str(args.parser_log),'sha256':sha(args.parser_log),'bytes':args.parser_log.stat().st_size})
    csvwrite(out/'VALIDATION_LOG_INDEX.csv',['path','sha256','bytes'],log_rows)
    shutil.copyfile(args.parser_log,out/'PARSER_ADAPTER_TESTS.log')
    (out/'VALIDATION_SUMMARY.md').write_text(f'''# Executed validation

- Historical candidate Release build: PASS. VectorAdd all-OFF: 73873 cycles,
  56000000 instructions; exactly matches retained parent equivalence evidence.
- Integrated Lane 1 plus diagnostics Release target: PASS; assertions enabled
  in actual compile_commands (`-O3 -g3`, no `-DNDEBUG`). The producing
  commits are frozen before configure/build and unchanged at the postcheck.
  This candidate consumes Lane1 runtime-ready Core {parent}.
- Latest candidate: {cpp_count} production-driven C++ executable/config invocations
  PASS. This includes the original finite/unified WB suite, ordinary descriptor
  and WAD regressions, I_WB, I_WB_META, metadata pressure, read-reference checks
  and the read-reference checks above actual finite WBUF16, plus four original
  real-partition finite/unified C8/C16 lifetime/response regressions.
- Six illegal CLI configurations: PASS_EXPECTED_REJECTION. No workload ran in
  these expected-abort cases. Exact commands and overlays are retained.
- {parser_count} parser/config adapter tests: PASS. Synthetic parser fixtures are
  parser tests only, not performance or independent model qualification.
- Two full-application historical pilot modes: COMPLETE_VALID, exact pinned
  source/binary/config/trace, native exit and 64-slice terminal closure. One
  exact duplicate claim returned the existing result and launched no process.
- B16 application matrix: NOT_RUN. Own candidate is not a qualified shared
  release and cannot reuse a different binary's B16 row as an exact match.

Raw logs stay at their indexed result roots. Reparse artifacts are separate;
the earlier retained raw/run_status evidence is not overwritten. Early config
lexing and quota refusals did not start a workload and are not performance rows.
The retained illegal-mode harness note explains an initial overly strict log
postcheck (required a literal Assertion word); the exact abort reason and all
six cases were then rechecked. This was not a failed application simulation.
''')
    (out/'README.md').write_text('''# Lane 4 executed audit and ideal-mode candidate

Status: READY_FOR_REVIEW / DEPENDENCY_PENDING_SHARED_B16_RELEASE.

Read IDEAL_CONTRACTS.json, IDEAL_MODE_SOURCE_MAP.md, VALIDATION_SUMMARY.md,
REUSE_AUDIT.csv, CEILING_RESULTS.csv, LIMITER_MOVEMENT.csv, then exact manifests.
The review pack is a source/test/diagnostic candidate, not independent acceptance.

Historical search covers all retained EP-L2 stage refs and known node metadata,
with supplementary earlier LateBind lineage. Search scope and exact matches
are retained in HISTORY_SEARCH.json. No source/config/binary/trace-matched new
B16 ideal row was found. Old shadow WBUF4/8/16, MSHR256 and L1 headroom remain
historical evidence; the earlier ideal_writeback also removed port/data-traffic
constraints and cannot fill I_WB. A plan is not an experiment.

New full-application historical vectorAdd_4M comparison: OFF 73873 versus
I_READ_HIT 42918 cycles, same 56000000 instructions (1.721259x). This is an
OLD_D512_STATIC optimistic read-miss reference with explicit symbolic bytes.
It is NOT new B16 performance, EP-L2 implementable speedup, or a strict bound.
DRAM read bytes change 32000000 -> 0; lower/scheduler pressure also changes.
The measured timing interleaving changes write traffic too; retain both rows.

I_WB and I_META and their combination are implemented and production-tested.
Their B16 application speedups are NOT_RUN, not zero. First-wave baseline rows
are owned by Lane 5. Lane 1 must apply the minimal patch or integrate equivalent
default-OFF diagnostics, then Lane 5 qualifies one common binary and provides
its frozen B16 specs. prepare_ft_lane4_b16.py derives ideal-only overlays and
run_ft_lane4_diagnostic.py consumes the same central registry; a baseline
without these registrations is refused. The normal baseline is never relaunched
under a different identity merely to call it shared reuse.

Next executable command after the common release/spec exists:
`python3 util/ep_l2/prepare_ft_lane4_b16.py --baseline-spec BASE.json --mode I_WB --out IDEAL.json`,
then `python3 util/ep_l2/run_ft_lane4_diagnostic.py --execute-prepared IDEAL.json`.
Repeat only the four first-wave workloads; combination only convolution/FWT.
No new broad calibration, scan, full cross-product, or I_BANK run is claimed.
''')
    tests_dir=args.results/f'tests_b16_{rev}'
    cpp_tests=[{'test':r['test'],'status':'PASS','executable_sha256':sha(Path(r['run_command'][0]))} for r in tests['tests']]
    write(out/'VALIDATION_COUNTS.json',{'cpp_invocations':cpp_tests,'illegal_cli_cases_pass':6,
        'parser_adapter_tests_pass':parser_count,'new_historical_full_application_runs':2,'new_formal_B16_runs':0})
    write(out/'DEPENDENCIES.json',dependencies)
    (out/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(out)}\n' for p in sorted(out.rglob('*')) if p.is_file() and p.name!='SHA256SUMS'))
    status_dir=ROOT/'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane4';status_dir.mkdir(parents=True,exist_ok=True)
    status='READY_FOR_REVIEW_DEPENDENCY_PENDING_SHARED_B16_RELEASE'
    client=json.loads(Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text())
    sys.path.insert(0,str(Path(client['registry_client']).parent))
    from registry import Registry
    actual_registry=Registry(client['canonical_root']).snapshot()
    active=[r for r in actual_registry['runs'].values() if r['owner']=='lane4' and r['status'] in {'RUNNING','RESERVED'}]
    assert not active, 'preserve/report the actual active run before final closeout'
    receipt={'schema_version':1,'lane_id':4,'task_id':'FT20261016_LANE4_V1','coordination_commit':COORD,'status':status,
        'host':socket.gethostname(),'framework_branch':BRANCH,'framework_source_commit':build['framework_source_commit'],
        'framework_tooling_commit':producer,'core_branch':BRANCH,'core_source_commit':build['core_source_commit'],
        'binary_sha256':build['binary_sha256'],'config_sha256':None,'trace_identity':None,
        'feature_vector':{'finite_wbuf':True,'unified_wb':False,'tvd':False,'ro':False,'adaptive_policy':False,'wbuf_entries':16,
                          'payload_capacity_per_slice':1168,'bank_count':4,'ops_per_bank_cycle':1},
        'ideal_vector':None,'tested_ideal_vectors':vectors,'dependency_receipts':dependencies,
        'artifacts':[str(out.relative_to(ROOT))],'validation':{'cpp_invocations_pass':cpp_count,'illegal_cli_rejections_pass':6,
            'parser_adapter_tests_pass':parser_count,'new_historical_full_application_runs':2,'new_formal_B16_runs':0},
        'active_runs':active,'blockers':['Lane1 producer runtime_ready=true but independent qualification is false; published normal binary does not include Lane4 diagnostics.',
            'Lane1 common integration and Lane5 independently qualified same-binary B16 baseline specs are needed; old and different-binary rows cannot fill these cells.'],
        'historical_executed_run_keys':[r['run_key'] for r in raw_index],
        'config_trace_null_reason':'No formal shared B16 performance identity yet; exact historical/test identities are indexed in the review pack.'}
    write(status_dir/'RECEIPT.json',receipt)
    (status_dir/'STATUS.md').write_text(f'''# Lane 4 status

Status: {status}.
Node: {socket.gethostname()}. Branch in both repositories: `{BRANCH}`.
Framework worktree: `{ROOT}`.
Core worktree: `/workspace/worktrees/gpgpu-sim-ep-l2-ft20261016-lane4-v1`.
Producing Core: `{build['core_source_commit']}`; producing Framework:
`{build['framework_source_commit']}`; tooling: `{producer}`.

Completed: bounded historical audit, default-OFF I_WB/I_META/I_READ_HIT and
I_WB_META, release builds, {cpp_count} production-driven C++ invocations, six illegal
mode rejections, {parser_count} parser/adapter tests, two central-registry-controlled
full-application HISTORICAL_DIAGNOSTIC modes, and exact duplicate reuse check.
VectorAdd OFF 73873 -> optimistic read reference 42918 cycles; same 56M
instructions. This is an old-static reference, not B16/EP-L2 speedup.

Formal B16 application rows: NOT_RUN. Lane1 now publishes runtime_ready=true
at {dependencies[0]['publication_commit']} but independent qualification remains
false; the normal binary lacks diagnostic registrations. Lane5 snapshot is
{dependencies[1]['publication_commit']}. Different-source/binary rows are not
called shared baselines. Current own active simulations: zero.
No polling daemon or unreported background continuation is running.

Review pack: `{out.relative_to(ROOT)}`.
Next: Lane1 integrates CORE_MINIMAL.patch against its exact published parent;
Lane5 independently qualifies one common binary including default-OFF ideal
registrations and supplies B16 baseline specs. Derive/run the four first-wave
ideal sets through the central client, with only convolution/FWT combinations.
No Full EP-L2 dependency. Exact consumed publication/receipt hashes are in
DEPENDENCIES.json. This candidate has not self-declared independent acceptance.
''')
    print(json.dumps({'pack':str(out),'status':status,'code_candidate':build['core_source_commit'],'tooling':producer}))


if __name__=='__main__':main()
