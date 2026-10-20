"""Package retained producer evidence. Never compile, simulate, or write E state."""
import datetime
import difflib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess

ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / 'docs/ep_l2/review_packs/MS20261020_A2_FORMAL_WAD_PRODUCER_RELEASE_r1'
E = Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
EPACK = E / 'docs/ep_l2/review_packs/MS20261020_E_WAD_ROLLBACK_NATIVE_REPAIR_r1'
RESULTS = Path('/workspace/ep_l2_ms20261019_e_results')
SHARED = Path('/workspace/ep_l2_ms20261019_shared')
REGISTRY = Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json')
CORE = Path('/workspace/worktrees/gpgpu-sim-ep-l2-ms20261020-a-r39-own-pending-v1')
R42 = Path('/workspace/worktrees/gpgpu-sim-ep-l2-ms20261020-a-r42-wad-fixtures-v1')
FW = Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-a-r2-ro-runtime-v1')
VENDOR = FW / 'gpu-simulator/extern/pybind11'
AHEAD = 'cf8679faef667f0dc58cf3c2571d1cd4b4aa8fcd'
EHEAD = '2a42d1079aa2c076762fc8642bf0e5fd5fd1d917'
IDENTITY = dict(core_source_commit='d010911e3174a3764791183cd108fe4664ba8731',
    framework_source_commit='9dd1ee57a83d83b56b7874bc7c716185ab52c8f7',
    vendor_pybind11_commit='f90c430c3a1ce8f08c09942a5a1c3a797bb2295b',
    binary_sha256='61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5')
MAIN = Path('/workspace/build/ep-l2-ms20261020-a-wad-pending-r41/accel-sim.out')
ARCHIVE = Path('/workspace/build/ep-l2-ms20261020-a-wad-pending-r40/libgpgpusim.a')
ARCHIVE_SHA = '3c6ce15b88ae16c17c30718618aedc769495168d6e3d0c371270ba95b7b0aca8'


def command(*args, cwd=None):
    return subprocess.check_output(args, cwd=cwd)


def git(path, *args):
    return command('git', '-C', str(path), *args).decode().strip()


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def ref(path):
    p = Path(path)
    return dict(path=str(p), sha256=digest(p), bytes=p.stat().st_size)


def load(path):
    return json.loads(Path(path).read_text())


def write(name, data):
    (PACK / name).write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')


def check_pin(path, sha):
    assert digest(path) == sha, f'Changed evidence: {path}'


def tree_check(path, commit, prefixes=()):
    entries = command('git', '-C', str(path), 'ls-tree', '-rz', commit, '--', *prefixes).split(b'\0')
    checked = []
    for item in entries:
        if not item:
            continue
        meta, name = item.split(b'\t')
        mode, kind, oid = meta.split()
        if kind != b'blob':
            continue
        file = path / os.fsdecode(name)
        content = os.readlink(file).encode() if mode == b'120000' else file.read_bytes()
        assert hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest() == oid.decode(), str(file)
        checked.append(dict(path=os.fsdecode(name), git_blob=oid.decode(), sha256=hashlib.sha256(content).hexdigest()))
    return checked


def main():
    assert socket.gethostname() == 'huangrulin-174'
    lock = (SHARED / 'A_BUILD.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    assert not PACK.exists(), 'Preserve previous publication; use an explicit new revision'
    before = REGISTRY.read_bytes()
    central = json.loads(before)
    state = central['mechanism_study_20261019_v1']
    assert state['actual_starts'] == 7 and state['maximum_actual_starts'] == 40
    assert state['t0_unix'] == 1792414193
    active = {group: {k:v for k,v in central[group].items() if v['status'] in ('RESERVED','RUNNING')}
              for group in ('runs','resource_leases')}
    assert not any(active.values()), 'Active E work: inspect before publication'
    assert shutil.disk_usage('/workspace').free > 7 * 2**30
    # Process evidence is captured, without starting any registry/controller API.
    processes = []
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit() or int(proc.name) == os.getpid():
            continue
        try:
            argv = (proc / 'cmdline').read_bytes().split(b'\0')
            if not argv or not argv[0]:
                continue
            executable = Path(os.fsdecode(argv[0])).name
            cwd = os.readlink(proc / 'cwd')
            if executable in ('cc1plus','cc1','make','gmake','ninja','c++','g++','accel-sim.out') or executable.startswith('ep_l2_'):
                processes.append(dict(pid=int(proc.name), executable=executable, cwd=cwd,
                                      argv=[os.fsdecode(x) for x in argv if x]))
        except (OSError, ProcessLookupError):
            pass
    assert not [p for p in processes if 'ms202610' in p['cwd'] or any('ms202610' in a for a in p['argv'])], processes
    worktrees = {}
    for p in (ROOT,E,CORE,R42,FW,VENDOR,Path('/workspace/worktrees/gpgpu-sim-ep-l2-ms20261019-a-core-v1')):
        worktrees[str(p)] = dict(head=git(p,'rev-parse','HEAD'), status=git(p,'status','--porcelain=v1'))
    assert worktrees[str(CORE)]['head'] == IDENTITY['core_source_commit']
    assert worktrees[str(FW)]['head'] == IDENTITY['framework_source_commit']
    assert worktrees[str(VENDOR)]['head'] == IDENTITY['vendor_pybind11_commit']
    assert all(not v['status'] for k,v in worktrees.items() if k != str(ROOT)), worktrees
    remote = git(ROOT,'ls-remote','origin','refs/heads/hrl/ep-l2-ms20261019-a-core-v1','refs/heads/hrl/ep-l2-ms20261019-e-eval-v1')
    assert AHEAD in remote and EHEAD in remote
    sources = dict(core=tree_check(CORE,IDENTITY['core_source_commit']),
                   framework=tree_check(FW,IDENTITY['framework_source_commit']),
                   vendor=tree_check(VENDOR,IDENTITY['vendor_pybind11_commit']))
    r42_production = tree_check(R42, IDENTITY['core_source_commit'], ('src','libcuda','CMakeLists.txt','linux-so-version.txt'))
    assert git(CORE,'diff','--name-only','27ec10bda848e4929181c60a7cbb40d6b007945c',IDENTITY['core_source_commit']) == 'src/gpgpu-sim/gpu-cache.cc'
    assert git(CORE,'rev-parse',IDENTITY['core_source_commit']+':src') == git(R42,'rev-parse','HEAD:src')
    # Check all declared prior pins, not merely the top-level new binary digest.
    spec = load(ROOT/'docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/a/full_system_v2/WAD_PENDING_REPAIR_SPEC_r42.json')
    for path, sha in spec['retained_files_sha256'].items():
        check_pin(path, sha)
    espec = load(EPACK/'SPEC.json')
    for path, sha in espec['pins'].items():
        check_pin(path, sha)
    check_pin(MAIN,IDENTITY['binary_sha256']); check_pin(ARCHIVE,ARCHIVE_SHA)
    manifest = load(EPACK/'INDEPENDENT_NATIVE_RESULT.json')
    request = load(EPACK/'REQUEST_A_FORMAL_RELEASE_AFTER_E_NATIVE_PASS.json')
    check_pin(EPACK/'INDEPENDENT_NATIVE_RESULT.json',request['E_native_manifest_sha256'])
    check_pin(EPACK/'ACTUAL_NATIVE_RECEIPT.json',request['E_actual_receipt_sha256'])
    assert manifest['candidate_source_identity'] == IDENTITY
    tests = manifest['tests']
    assert len(tests) == 17 and sum(len(x['terminal_checks']) for x in tests) == 26
    for t in tests:
        check_pin(t['receipt_path'],t['receipt_sha256']); check_pin(t['raw_log'],t['raw_log_sha256'])
        check_pin(t['command'][0],t['binary_sha256'])
        receipt = load(t['receipt_path'])
        assert receipt['command'] == t['command'] and receipt['actual_exit'] == t['actual_exit'] == 0
        assert receipt['expectation_verified'] and all(t['terminal_checks'].values())
        raw = Path(t['raw_log']).read_text()
        assert all(s in raw for s in t['terminal_checks'])
    # Inspect real archive members; only gpu-cache differs from the Core27 parent.
    parent = Path('/workspace/build/ep-l2-ms20261020-a-ro-origin-r26/libgpgpusim.a')
    names = command('ar','t',str(ARCHIVE)).decode().splitlines()
    assert names == command('ar','t',str(parent)).decode().splitlines() and len(names) == 22
    members = {}
    r40 = load(RESULTS/'A_WAD_PENDING_INCREMENTAL_r40/RECEIPT.json')
    for name in names:
        old = hashlib.sha256(command('ar','p',str(parent),name)).hexdigest()
        new = hashlib.sha256(command('ar','p',str(ARCHIVE),name)).hexdigest()
        members[name] = dict(old_sha256=old,new_sha256=new)
        assert members[name] == r40['archive_members'][name]
    assert [k for k,v in members.items() if v['old_sha256'] != v['new_sha256']] == ['gpu-cache.cc.o']
    obj = ARCHIVE.parent/'gpu-cache.cc.o'
    check_pin(obj,members['gpu-cache.cc.o']['new_sha256'])
    build_commands = []
    retained_inputs = {}
    history = []
    historical_native = []
    for attempt in ('A_WAD_PENDING_INCREMENTAL_r39','A_WAD_PENDING_INCREMENTAL_r40','A_WAD_PENDING_CONTINUE_r41','A_WAD_PENDING_REMAINING_r42'):
        receipt_path = RESULTS/attempt/'RECEIPT.json'
        receipt = load(receipt_path)
        history.append(dict(attempt=attempt,receipt=ref(receipt_path),status=receipt['status'],error=receipt.get('error'),
                            historical_retained_assets_unchanged=receipt['retained_assets_unchanged'],
                            interpretation='Historical failed wrapper is retained verbatim; this new release does not rewrite its success flag.'))
        for c in receipt['commands']:
            if c['command'][0] in ('/usr/bin/c++','/usr/bin/ar'):
                check_pin(c['log'],c['log_sha256']); assert c['exit_code'] == 0
                build_commands.append(dict(attempt=attempt,**c))
                for arg in c['command']:
                    if arg.endswith(('.a','.o')) and Path(arg).is_file(): retained_inputs[arg] = ref(arg)
        for path in (RESULTS/attempt).glob('*.json'):
            if path.name != 'RECEIPT.json':
                history.append(dict(attempt=attempt,artifact=ref(path)))
                native = load(path)
                if 'raw_log' in native and 'binary_sha256' in native:
                    check_pin(native['raw_log'], native['raw_log_sha256'])
                    check_pin(native['command'][0], native['binary_sha256'])
                    historical_native.append(dict(attempt=attempt,receipt=ref(path),
                        raw_log=ref(native['raw_log']),binary=ref(native['command'][0]),
                        actual_exit=native['actual_exit'],expected_exit=native['expected_exit'],
                        expectation_verified=native['expectation_verified']))
    # The main link was successful even though the later r41 fixture stopped the wrapper.
    links = [c for c in build_commands if c['log'].endswith('/new_main_link.log')]
    assert len(links) == 1 and str(ARCHIVE) in links[0]['command']
    assert str(MAIN) in links[0]['command'] and links[0]['exit_code'] == 0
    compile_cmd = next(c for c in build_commands if c['log'].endswith('/changed_gpu_cache_compile.log'))
    assert not any('NDEBUG' in x for x in compile_cmd['command'])
    for flag in ('-O3','-g3','-std=gnu++17','-DGPGPUSIM_POWER_MODEL','-DTRACING_ON=1'):
        assert flag in compile_cmd['command']
    old_red = RESULTS/'A_WAD_PENDING_INCREMENTAL_r39/core27_old_dirty_expected_assert.native.json'
    old = load(old_red)
    assert old['actual_exit'] == -6 and old['expectation_verified']
    check_pin(old['raw_log'],old['raw_log_sha256']); check_pin(old['command'][0],old['binary_sha256'])
    historical = []
    for attempt in ('E006_789c1a95','E007_6f906272'):
        for name in ('run_status.json','raw.log','ABORT_STATE.json','gdb.log'):
            p = RESULTS/attempt/name
            if p.exists(): historical.append(ref(p))
    assert digest(RESULTS/'E006_789c1a95/raw.log') == digest(RESULTS/'E007_6f906272/raw.log')
    PACK.mkdir(parents=True)
    (PACK/'E_independent').mkdir()
    for p in EPACK.iterdir():
        if p.is_file() and (p.name in ('INDEPENDENT_NATIVE_RESULT.json','ACTUAL_NATIVE_RECEIPT.json',
                'REQUEST_A_FORMAL_RELEASE_AFTER_E_NATIVE_PASS.json','SPEC.json','test_potential_a1_injected_read.cc',
                'independent_fixture_compile.log','independent_fixture_link.log') or p.name.startswith('new_')):
            shutil.copyfile(p,PACK/'E_independent'/p.name)
            check_pin(PACK/'E_independent'/p.name,digest(p))
    prior_fixture = R42/'tests/ep_l2/test_potential_a1.cc'
    fixed_fixture = EPACK/'test_potential_a1_injected_read.cc'
    (PACK/'E_TEST_ONLY_REPAIR.patch').write_text(''.join(difflib.unified_diff(
        prior_fixture.read_text().splitlines(True),fixed_fixture.read_text().splitlines(True),
        fromfile='a/tests/ep_l2/test_potential_a1.cc',tofile='b/tests/ep_l2/test_potential_a1.cc')))
    write('SOURCE_FILE_IDENTITIES.json',dict(**sources,r42_production=r42_production))
    write('BUILD_PROVENANCE.json',dict(schema='A2_RETAINED_BUILD_PROVENANCE_V1',
        commands=build_commands,retained_inputs=retained_inputs,archive_members=members,
        changed_object=ref(obj),main=ref(MAIN),archive=ref(ARCHIVE),
        production_compilation_this_release=0,main_relinks_this_release=0,
        provenance='r40 one production TU + one archive-member replacement; r41 existing frontend objects and seven other archives relinked. No rebuild by A2. Successful individual commands remain valid despite later test wrapper failure.',
        generated_banner_note='Inherited generated version banner is historical; external exact source/tree/object identity governs. No banner rewrite.'))
    write('NATIVE_EVIDENCE_MANIFEST.json',dict(schema='A2_CONSUMED_E_INDEPENDENT_NATIVE_EVIDENCE_V1',
        source_identity=IDENTITY,E_publication=EHEAD,E_manifest=ref(EPACK/'INDEPENDENT_NATIVE_RESULT.json'),
        E_actual_receipt=ref(EPACK/'ACTUAL_NATIVE_RECEIPT.json'),tests=tests,
        terminal_expectation_count=26,independent_native_pass_count=17,
        A2_new_native_invocations=0,A2_full_application_starts=0,
        producer_prior_old_red=ref(old_red),
        old_red_new_green=dict(old_core='27ec10bda848e4929181c60a7cbb40d6b007945c',old_exit=-6,
            old_binary_sha256=old['binary_sha256'],new_core=IDENTITY['core_source_commit'],
            new_dirty_case=next(t for t in tests if t['case']=='new_dirty_WAD128_drain'),
            same_fixture_object_retained_in_r40=True,
            note='The exact old fixture is linked against Core27 for old red and d010 archive for r40 green. E independently rechecks the four dirty terminals with its retained r41 fixture; E fixture repairs do not modify production code.'),
        scope='17 affected finite production-path commands / 26 expected checks; symbolic version data; no full-application correctness or performance acceptance. Older native results keep their original binary/archive scope.'))
    write('HISTORY_PRESERVATION.json',dict(failed_A_attempts=history,original_E_failures=historical,
        prior_release=ref(ROOT/'docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/a/full_system_v2/RO_ORIGIN_RELEASE_r30.json'),
        E006_E007='E006 main773 SIGABRT -6; E007 same-binary/full-input forensic replay reproduced byte-identical abort and captured stack/pending UID3006216. Final -9 was GDB cleanup after observed SIGABRT. Both remain FAILED and counted. No application PASS inferred.',
        r39='Expected old-source assertion verified; wrapper TypeError stopped before compiling production.',
        r40='Production object/archive succeeded; three dirty/clean cases passed; obsolete --repair-gates expectation failed. Preserved, not renamed PASS.',
        r41='Main relink succeeded; supported warm/FT_OFF/legacy rollback passed; TVD rollback fixture failed.',
        r42='Test-only retry still left injected RESPONSE grant selected; frontend write never reached rollback. E fixed consumption through public arbiter and independently passed; original failed ELF and logs remain.',
        B_C_joint='r35 joint fixture failure and later B/C replacement fixture remain separate and unaccepted; six finite existing RO interactions do not qualify that joint scenario.',
        old_773='Prior release/qualification, E005 S native0 under HOLD, E006 F failure and withdrawals are immutable; no main773 result transfers to main61.',
        causal_review=ref('/workspace/ep_l2_ms20261019_a_common_v1/E006_B_R5_SAME_CAUSE_CONFIRMED_r43.json')))
    write('HISTORICAL_NATIVE_IDENTITIES.json',dict(schema='A2_UNMODIFIED_A_NATIVE_HISTORY_IDENTITIES_V1',
        evidence=historical_native,no_old_status_rewritten=True))
    profiles = load(ROOT/'docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/a/SUPPORTED_PROFILES.json')
    write('SUPPORTED_PROFILES.json',dict(schema='A2_WAD_PRODUCER_SOURCE_PROFILES_V1',source_identity=IDENTITY,
        source_supported={k:dict(research_switches=v['research_switches'],status='SOURCE_SUPPORTED_INCREMENTAL_AFFECTED_NATIVE_SCOPE_ONLY_E_QUALIFICATION_REQUIRED') for k,v in profiles['source_supported'].items()},
        unsupported_controls=profiles['unsupported_controls'],profile_aliases=profiles['profile_aliases'],
        independently_qualified_profiles=[],application_qualified_profiles=[],
        R_certification=profiles['R_certification'],static_WB64=profiles['static_WB64'],
        same_final_binary_required=True,no_per_input_best_subset=True,
        joint_B_C_status='FAILED_OR_PENDING_NOT_UPGRADED',
        topology=dict(resident_tags=1024,data_slots=1168,line_bytes=128,shared_wad_tvd=128,descriptors=512,line_mshrs=128,banks=4,bank_ops=1)))
    write('IDENTITY_AUDIT.json',dict(schema='A2_ORIGINAL174_PHYSICAL_IDENTITY_AUDIT_V1',
        at_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),host=socket.gethostname(),
        boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),worktrees=worktrees,
        fetched_remote_refs=remote,build_lock_acquired=True,active_global=active,relevant_native_build_processes=processes,
        central_registry_before_sha256=hashlib.sha256(before).hexdigest(),
        central_read_only=True,actual_starts=7,maximum_actual_starts=40,t0_unix=1792414193,
        start_deadline_unix=state['start_deadline_unix'],workspace_free_bytes=shutil.disk_usage('/workspace').free,
        workspace_floor_bytes=5*2**30,monitor_reserve_bytes=2*2**30,
        r42_retained_pins_checked=len(spec['retained_files_sha256']),E_pins_checked=len(espec['pins']),
        build_directories={str(p):dict(git_managed=False,files=[ref(f) for f in p.iterdir() if f.is_file()]) for p in (ARCHIVE.parent,MAIN.parent,Path('/workspace/build/ep-l2-ms20261020-a-wad-pending-r42'))},
        no_reset_clean_or_history_overwrite=True))
    assert REGISTRY.read_bytes() == before, 'Concurrent E state changed; preserve audit and review latest state'
    # Entry is written last, only after every producer identity and receipt check succeeds.
    write('RELEASE.json',dict(schema='EP_L2_A2_FORMAL_WAD_OWN_PENDING_PRODUCER_RELEASE_V1',
        status='FORMALLY_RELEASED_BY_A2_FOR_E_INDEPENDENT_ACCEPTANCE',producer='Lane A2 (continuation of Lane A)',
        campaign_id='EPL2_MECHANISM_STUDY_20261019_V1',authority_commit='b2e5328aca825d6e9ebfe09e46fa208957834636',
        source_identity=IDENTITY,binary_path=str(MAIN),binary_sha256=IDENTITY['binary_sha256'],
        production_archive=ref(ARCHIVE),production_object=ref(obj),
        production_source_path=str(CORE),runtime_framework_path=str(FW),vendor_path=str(VENDOR),
        production_tree_ids={p:git(CORE,'rev-parse',IDENTITY['core_source_commit']+':'+p) for p in ('src','libcuda','CMakeLists.txt')},
        build_log=ref(PACK/'BUILD_PROVENANCE.json'),producer_test_manifest=ref(PACK/'NATIVE_EVIDENCE_MANIFEST.json'),
        supported_profiles_manifest=ref(PACK/'SUPPORTED_PROFILES.json'),identity_audit=ref(PACK/'IDENTITY_AUDIT.json'),
        history=ref(PACK/'HISTORY_PRESERVATION.json'),E_independent_native_publication=EHEAD,
        E_test_only_fixture_source=ref(fixed_fixture),E_test_only_patch=ref(PACK/'E_TEST_ONLY_REPAIR.patch'),
        producer_runtime_ready=True,producer_release_complete=True,
        E_affected_native_17_consumed=True,E_affected_terminal_expectations=26,
        independent_E_full_application_qualification=False,qualified_profiles=[],
        application_start_authorization=False,A2_new_compiles=0,A2_new_native_invocations=0,A2_full_application_starts=0,
        original_budget=dict(actual_starts=7,maximum_actual_starts=40,allocation='32+8 unchanged',
            t0_unix=1792414193,start_deadline_unix=1792576800,intake_deadline_unix=1792591200,
            contingency_used=5,contingency_remaining=3,accepted_pairs=0),
        release_semantics='Formal A producer publication is complete. E owns independent identity acceptance, source-specific OFF qualification and same-main61 Conv S/F under the existing controller. No old hold is cleared here.',
        E_next_entry=ref(EPACK/'NEXT_OFF_AND_CONV_BOUNDARY.json'),
        publication_identity='Exact containing Git commit is supplied by REMOTE_READBACK and HANDOFF_A2; control publication commit is distinct from runtime Framework.'))
    print(json.dumps(dict(status='FORMAL_RELEASE_PACKAGED',release=ref(PACK/'RELEASE.json'),
        archive_members=22,unchanged_archive_members=21,native_commands_consumed=17,terminal_checks=26)))


if __name__ == '__main__':
    main()
