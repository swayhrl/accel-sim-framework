"""Publish exact incremental producer evidence; no new compile/native/app or E acceptance."""
from pathlib import Path
import collections
import datetime
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
A = ROOT/'docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/a'
BASE = A/'full_system_v2'
PACK = ROOT/'docs/ep_l2/review_packs/MS20261020_A_RO_ORIGIN_PRODUCTION_RELEASE_r28'
RESULTS = Path('/workspace/ep_l2_ms20261019_e_results')
CORE = Path('/workspace/worktrees/gpgpu-sim-ep-l2-ms20261020-a-r25-ro-origin-v1')
NEW = '27ec10bda848e4929181c60a7cbb40d6b007945c'
UTC = datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(4*2**20), b''):
            h.update(chunk)
    return h.hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def put(path, data):
    Path(path).write_text(json.dumps(data, indent=2)+'\n')


def git(*args):
    return subprocess.check_output(['git','-C',str(ROOT),*args])


def main():
    assert not PACK.exists()
    r26p = RESULTS/'A_RO_ORIGIN_INCREMENTAL_r26/RECEIPT.json'
    r27p = RESULTS/'A_RO_ORIGIN_AFFECTED_r27/RECEIPT.json'
    r26, r27 = load(r26p), load(r27p)
    assert r26['status'] == 'OLD_RED_NEW_GREEN_MAIN_COMPILED_PENDING_AFFECTED_QUALIFICATION'
    assert r27['status'] == 'AFFECTED_RO20_ACTUAL_PASS_PENDING_E_QUALIFICATION'
    assert r26['lease_released'] and r27['lease_released']
    assert r26['retained_assets_unchanged'] and r27['retained_assets_unchanged']
    assert r26['core_source_commit'] == r27['core_source_commit'] == NEW
    assert r26['binary_sha256'] == r27['binary_sha256'] == sha(r26['binary'])
    assert len(r26['tests']) == 6 and len(r27['tests']) == 20
    assert all(t['expectation_verified'] for t in r26['tests']+r27['tests'])
    assert [t['actual_exit'] for t in r26['tests']] == [0,-11,0,0,0,0]
    assert all(t['actual_exit'] == 0 for t in r27['tests'])
    assert r27['observer_semantics'][0]['line'] == r27['observer_semantics'][1]['line']
    assert [n for n,v in r26['archive_members'].items() if v['old_sha256'] != v['new_sha256']] == ['gpu-cache.cc.o']
    central = load('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json')
    campaign = central['mechanism_study_20261019_v1']
    assert all(central['resource_leases'][r['lease_id']]['status']=='RELEASED' for r in (r26,r27))
    assert campaign['t0_unix'] == 1792414193 and campaign['maximum_actual_starts'] == 40
    for r in (r26,r27):
        assert r['E_central_admission'] == 'GRANTED_BY_PUBLISHED_RESERVE_WORK'
        assert r['resource_allocation']['disk_floor_bytes'] == 5*2**30
        for t in r['tests']:
            assert sha(t['raw_log']) == t['raw_log_sha256']
            assert sha(t['command'][0]) == t['binary_sha256']
    for name in ('RO_ORIGIN_INCREMENTAL_SPEC_r26.json','RO_ORIGIN_AFFECTED_SPEC_r27.json'):
        for path,digest in load(BASE/name)['retained_files_sha256'].items():
            assert sha(path) == digest
    old_release_bytes = git('show','75707624b980df5e3bbb809c76a31cf1b34501a1:'+str((A/'RELEASE.json').relative_to(ROOT)))
    assert (A/'RELEASE.json').read_bytes() == old_release_bytes
    old_release = json.loads(old_release_bytes)
    previous_path = Path(old_release['producer_test_manifest']['path'])
    assert sha(previous_path) == old_release['producer_test_manifest']['sha256']
    previous = load(previous_path)
    assert r27['observer_semantics'][0]['line'] == previous['observer_pairs_unchanged']['F_observer'][0]['line']
    fresh = {t['case']:t for t in r27['tests']}
    rows = []
    for prior in previous['tests']:
        name = prior['case']
        if name in fresh:
            t = fresh[name]
            assert t['command'][1:] == prior['native_command'][1:]
            assert t['actual_exit'] == prior['actual_exit'] == 0
            assert t['required_terminal'] == prior['required_terminal']
            row = dict(prior, evidence_origin='NEW_RO_ORIGIN_AFFECTED27_NATIVE',
                receipt=t['evidence'], receipt_SHA256=t['sha256'],
                native_binary=t['command'][0], native_binary_SHA256=t['binary_sha256'],
                native_command=t['command'], raw_log=t['raw_log'], raw_SHA256=t['raw_log_sha256'])
            assert sha(t['evidence']) == t['sha256']
        else:
            assert sha(prior['native_binary']) == prior['native_binary_SHA256']
            assert sha(prior['raw_log']) == prior['raw_SHA256']
            assert sha(prior['receipt']) == prior['receipt_SHA256']
            row = dict(prior, evidence_origin='REUSED_UNCHANGED_SOURCE_DISJOINT_FROM_RO_ISSUE',
                not_executed_on_new_archive=True)
        assert row['required_terminal'] in Path(row['raw_log']).read_text()
        rows.append(row)
    assert len(rows) == 64 and len(fresh) == 20
    assert collections.Counter(r['suite'] for r in rows) == dict(main=55,diagnostics=9)
    assert collections.Counter(t['suite'] for t in r27['tests']) == dict(main=19,diagnostics=1)
    for gate in previous['r14_gates']:
        detail = gate['actual_native_detail']
        assert sha(detail['raw_log']) == detail['raw_log_sha256']
        assert sha(detail['command'][0]) == detail['binary_sha256']
    PACK.mkdir(parents=True)
    old = BASE/'frozen_producer_75707624'
    assert not old.exists()
    old.mkdir()
    (old/'RELEASE.json').write_bytes(old_release_bytes)
    for name in ('SUPPORTED_PROFILES.json','LATEST_SOURCE.json','STATUS.md','RECEIPT.json'):
        shutil.copy2(A/name, old/name)
    for n,p in [('R26_RECEIPT.json',r26p),('R27_RECEIPT.json',r27p)]:
        shutil.copy2(p, PACK/n)
    for r in (r26,r27):
        for t in r['tests']:
            name = t['case']
            shutil.copy2(t['evidence'],PACK/(name+'.native.json'))
            shutil.copy2(t['raw_log'],PACK/(name+'.raw.log'))
    source_identity = dict(core_source_commit=NEW,
        framework_source_commit=r26['framework_source_commit'],
        vendor_pybind11_commit=r26['vendor'],binary_sha256=r26['binary_sha256'])
    manifest_path = BASE/'RO_ORIGIN_NATIVE_EVIDENCE_MANIFEST_r28.json'
    manifest = dict(schema='A_INCREMENTAL_RO_ORIGIN_NATIVE_EVIDENCE_R28',UTC=UTC,
        status='AFFECTED20_AND_DETAILED4_ACTUAL_PASS_PENDING_E',source_identity=source_identity,
        main=55,diagnostics=9,composite_original64=True,all64_fresh_new_archive=False,
        fresh_affected_original_cases=20,reused_unchanged_source_cases=44,
        new_detailed_mode_cases=4,old_source_control_and_real_SIGSEGV_cases=2,
        source_reuse_boundary='Only RO lowerread origin allocator changed. No other production source/header differs; reused44 do not exercise this productionallocator. Three originalR14 TVD-only gates retain exact evidence. This is incremental producer evidence, not fresh64 on newbinary or E acceptance.',
        previous_manifest=dict(path=str(previous_path),sha256=sha(previous_path)),
        old_red_new_green=dict(path=str(r26p),sha256=sha(r26p)),
        affected_native=dict(path=str(r27p),sha256=sha(r27p)),
        observer_equality=dict(F_observer=r27['observer_semantics'],
            S_U_reused_source_disjoint={k:previous['observer_pairs_unchanged'][k] for k in ('native_S','native_U')}),
        F_semantic_signature_matches_retained_old_source=True,
        original_r14_gates_reused=previous['r14_gates'],tests=rows,
        independent_E_qualification=False,application_acceptance=False)
    put(manifest_path,manifest)
    fixtures = {p:h for p,h in old_release['compiled_fixture_sha256'].items()
                if Path(p).name not in r27['fixture_binary_sha256']}
    fixtures.update({str(Path(r27['build_directory'])/t):h for t,h in r27['fixture_binary_sha256'].items()})
    fixtures[str(Path(r26['build_directory'])/'ep_l2_ro_detailed_origin_new')] = r26['new_native_sha256']
    archives = dict(old_release['fixture_archive_sha256'])
    archives.pop('/workspace/build/ep-l2-ms20261019-a-common-native-r1/gpgpu-sim/src/gpgpu-sim/libgpgpusim.a')
    archives[str(Path(r26['build_directory'])/'libgpgpusim.a')] = r26['new_archive_sha256']
    profiles = load(A/'SUPPORTED_PROFILES.json')
    profiles.update(schema='A_INCREMENTAL_SUPPORTED_PROFILES_R28',Core=NEW,runtime_producer_Core=NEW,
        fixture_current_Core=NEW,binary_SHA256=r26['binary_sha256'],
        status='PRODUCER_AFFECTED20_DETAILED4_VERIFIED_PENDING_E',
        native_qualified_profiles=[],independent_E_qualification=False,
        evidence=str(manifest_path.relative_to(A)))
    profiles['profile_aliases']['S_WB64'] = 'STATIC_WB64'
    for profile in profiles['source_supported'].values():
        profile['status'] = 'INCREMENTAL_PRODUCER_VERIFIED_NOT_E_QUALIFIED'
    put(A/'SUPPORTED_PROFILES.json',profiles)
    release = dict(old_release)
    release.update(schema='EP_L2_A_INCREMENTAL_RO_ORIGIN_PRODUCER_RELEASE_R28',UTC=UTC,
        status='COMPILED_INCREMENTAL_RO_ORIGIN_REPAIR_AFFECTED_NATIVE_PASS_PENDING_E',
        source_identity=source_identity,binary_path=r26['binary'],runtime_producer_Core=NEW,
        fixture_source_Core=NEW,fixture_generated_banner_Core='97fd7a3d872f572818afee1f99343368f89b7ed9',
        production_tree_ids={p:subprocess.check_output(['git','-C',str(CORE),'rev-parse',NEW+':'+p],text=True).strip()
                             for p in ('src','libcuda','CMakeLists.txt')},
        fixture_archive_sha256=archives,compiled_fixture_sha256=fixtures,
        producing_build_receipt=dict(path=str(r26p),sha256=sha(r26p)),
        producer_test_manifest=dict(path=str(manifest_path),sha256=sha(manifest_path)),
        E_policy_publication=r26['E_source_publication'],
        producer_finite_main55_and_diag9_predicates=True,
        predicate_scope='INCREMENTAL:20new affected+44exact unchanged; threeoriginalR14 reused; fournew detailedDRAM modes. NOT all64fresh currentarchive.',
        independent_E_qualification=False,producer_runtime_ready=True,
        application_start_authorization=False,qualified_profiles=[],
        E_actual_starts=campaign['actual_starts'],original_T0=campaign['t0_unix'],
        fixture_note='Onlygpu-cache.cc recompiled;22archive members,21unchanged. Newmain reuses exactfrontendobjects/other7archives. ThreeROfixtures relink unchangedobjects against repairedarchive; other16nativeELFs unchanged. Generated97fd hostbanner deliberatelyretained and is NOT currentproducingCore. Exact external identity above governs.',
        publication_identity='CURRENT_A_BRANCH_COMMIT_CONTAINING_THIS_ARTIFACT; exact SHA in remote-readback handoff',
        supported_profiles_manifest=dict(path=str(A/'SUPPORTED_PROFILES.json'),sha256=sha(A/'SUPPORTED_PROFILES.json')),
        profile_aliases=profiles['profile_aliases'],
        prior_producer=dict(commit='75707624b980df5e3bbb809c76a31cf1b34501a1',
            release_path=str(old/'RELEASE.json'),release_sha256=sha(old/'RELEASE.json'),
            status='HISTORICAL_FINITE_PRODUCER_CURRENT_F_SOURCE_HOLD_ALL_DATA_RETAINED'),
        E_scope_review_required=['Independent affected-native acceptance and new detailedDRAM regression.',
            'New-source all-OFF gate disposition; existing E001 CSVcontrol belongs oldmain67fd only.',
            'Rebind exact source/profile/input/parser identity; keep oldqualifications/holds intact.',
            'E alone launches necessarynewcanary/SF underoriginal40/T0/32+8; never crossbinaryanchors.'],
        old_red_new_green=dict(path=str(r26p),sha256=sha(r26p),old_exit=-11,new_modes_exit0=4,
            old_native_sha256=r26['old_native_sha256'],new_native_sha256=r26['new_native_sha256']),
        affected_native=dict(path=str(r27p),sha256=sha(r27p),exit0=20),
        new_CPP_translation_units=2,new_CMake_configurations=0,new_A_full_applications=0,
        policy_control_tests='E153resourcecontrols unchanged; not native science evidence')
    put(A/'RELEASE.json',release)
    put(BASE/'RO_ORIGIN_RELEASE_r28.json',release)
    binding = load(BASE/'FINAL_PROFILE_INPUT_BINDINGS_r24.json')
    binding.update(schema='A_FINAL_PROFILE_INPUT_BINDINGS_R28',UTC=UTC,
        status='EXACT_OLD_OVERLAYS_NEW_PRODUCER_BINDING_PENDING_E_INPUT_PROFILE_ACCEPTANCE',
        official_producer_publication=release['publication_identity'],
        official_release=dict(path=str(A/'RELEASE.json'),sha256=sha(A/'RELEASE.json')),
        runtime_source_identity=source_identity,binary_path=r26['binary'],
        native_producer_manifest=dict(path=str(manifest_path),sha256=sha(manifest_path)),
        actual_full_starts_at_binding=campaign['actual_starts'],
        current_qualification_state='NEW_SOURCE_NOT_E_QUALIFIED_OLD_SOURCE_HOLDS_PRESERVED',
        current_E_input_scope_holds=campaign.get('input_scope_holds',{}),
        new_CPP_native_or_application_runs='Binding itself none; actualr26 twoobjects/6native+r27link3/20native recordedseparately')
    for condition in binding['conditions']:
        if condition.get('overlay'):
            assert sha(condition['overlay']['path']) == condition['overlay']['sha256']
        condition['scientific_qualification'] = False
        condition['application_start_authorization'] = False
    put(BASE/'FINAL_PROFILE_INPUT_BINDINGS_r28.json',binding)
    source = load(A/'SOURCE_REVISIONS.json')
    source['full_system_v2_r28_actual_RO_origin_repair'] = dict(source_identity,
        control_build_commit=r26['control_source_commit'],affected_control_commit=r27['control_source_commit'],
        producer_release=str(BASE/'RO_ORIGIN_RELEASE_r28.json'),producer_release_sha256=sha(BASE/'RO_ORIGIN_RELEASE_r28.json'),
        old_red_new_green6=str(r26p),affected20=str(r27p),old_source_held=True,
        old_snapshots_preserved=True,full_application_starts_by_A=0)
    put(A/'SOURCE_REVISIONS.json',source)
    latest = dict(schema='A_LATEST_SOURCE_R28',UTC=UTC,
        status=release['status'],runtime_source_identity=source_identity,
        official_release_path=str(A/'RELEASE.json'),official_release_sha256=sha(A/'RELEASE.json'),
        producer_manifest=dict(path=str(manifest_path),sha256=sha(manifest_path)),
        current_supported_profiles=dict(path=str(A/'SUPPORTED_PROFILES.json'),sha256=sha(A/'SUPPORTED_PROFILES.json')),
        final_profile_input_bindings=dict(path=str(BASE/'FINAL_PROFILE_INPUT_BINDINGS_r28.json'),sha256=sha(BASE/'FINAL_PROFILE_INPUT_BINDINGS_r28.json')),
        previous_official_release=str(old/'RELEASE.json'),independent_qualification=False,
        full_application_starts_by_A=0,E_actual_starts_snapshot=campaign['actual_starts'])
    put(A/'LATEST_SOURCE.json',latest)
    receipt = dict(schema='A_RO_ORIGIN_PRODUCTION_RELEASE_RECEIPT_R28',UTC=UTC,
        campaign_id=release['campaign_id'],authority=release['authority_commit'],status=release['status'],
        source_identity=source_identity,binary=r26['binary'],new_A_CPP_translation_units=2,
        new_native_executions=26,new_current_source_exit0=24,old_source_control_exit0=1,old_source_SIGSEGV=1,
        historical_A_native_executions=53,A_cumulative_native_executions=79,
        affected_original_cases_passed=20,new_detailed_modes_passed=4,
        original64_scope='20fresh+44unchanged; not allfreshnewbinary',all64_fresh_new_archive=False,
        new_main_and_fixtures_built=True,old_builds_ELFs_archives_inputs_unchanged=True,
        leases=[dict(id=r['lease_id'],state='RELEASED',receipt_sha256=sha(p)) for r,p in ((r26,r26p),(r27,r27p))],
        r26_build_peak_bytes=r26['own_build_bytes_peak'],r27_build_peak_bytes=r27['own_build_bytes_peak'],
        main_old_sha256=r26['retained_main_sha256'],main_new_sha256=r26['binary_sha256'],
        independent_E_qualification=False,application_start_authorization=False,
        full_applications_by_A=0,E_actual_starts=campaign['actual_starts'],E_total_limit=40,original_T0=campaign['t0_unix'],
        accepted_pairs=len(campaign['accepted_pairs']),accepted_points=len(campaign['accepted_results']),
        E_policy_source=r26['E_source_publication'],E_policy=r26['E_workspace_disk_policy'],
        admission='Actual E published reserve_work API grant; no manual approval file manufactured; no central policy mutation',
        prior_f_failure='E003_af8fc7e6 SIGSEGV remains frozen; original 67fd qualifications held',
        E_next=release['E_scope_review_required'],unsupported=profiles['unsupported_controls'])
    put(A/'RECEIPT.json',receipt)
    status = f'''# A r28: repaired production main and affected native evidence ready for E

Actual source repair is Core `{NEW}`; runtime Framework `{r26['framework_source_commit']}`, vendor `{r26['vendor']}`. New main `{r26['binary_sha256']}` lives at `{r26['binary']}`. Old main67fd and all oldELFs/archives/raw/config/input files remain byte-identical. Frozen priorRELEASE75707624 is copied with its exactSHA under full_system_v2/frozen_producer_75707624 and preserved in Git.

Real old-red/new-green: the SAME finitefixture linked to the immutable oldlibrary reproduces SIGSEGV(-11) with lowerread wid/sid/tpc=4294967295 through actualdetailedDRAM/stats14; oldnative T0M0 passes. Only RO issue originfields inherit demand IDs. Onegpu-cache.cc productionobject and one newfixtureobject compiled with originalO3/g3/assertionsON; copiedarchive has22members and onlygpu-cache.cc.o changed. Fournew T/M modes actually pass exactonce, originidentity, drain/backpressure/P1. NewT0M0 raw bytes equaloldnativecontrol. No statistics disablement, H0change or queue/resource/lifecycle workaround.

ThreeexistingRO fixtures were separately relinked to the newarchive without recompilation/mainrelink; all20affected originalcases pass. Fobserver on/off semanticlines are equal. Original64 evidence is explicitly composite20fresh+44source-disjointunchanged; threeoriginalR14 gates reuse exactold evidence, not a fresh64claim. Actualnewnative executions26=24newsource exit0+oneoldcontrol exit0+oneoldSIGSEGV. A cumulative79 includes allhistoric failures. Fullapplications byA remain0.

Both realE ordinary5GiB API leases263b4a79/0a4df92e are RELEASED. TwoGiB monitor, .2ssampling, ownedgroup protection and exactsource bindings were active; r26buildpeak{r26['own_build_bytes_peak']}B, r27buildpeak{r27['own_build_bytes_peak']}B stayed within reserves. The earlier manualfilewait was an unnecessary Aentry layer and is superseded; no Eauthority code/policy was changed and no Eapprovalfile was fabricated.

E actualstarts{campaign['actual_starts']}/40; originalT0/32+8/deadlines/6GiBnew/20GiBtotal/Share40GiB/RAM64GiB/globalCPUandconcurrency remain. OldF E003failure and holds remain; oldS E002 is untouched. No acceptedS/Fpair exists at this snapshot. The completed originalallOFF E001 belongs old67fd only. E independentlyaccepts newsource/affectednative and decides necessarynewOFFqualificationcanary before sameNEWbinary S/F/mechanism dispatch. No crossbinaryanchors. Existingoverlays/oracles/researchswitches are unchanged; btreeinputhold is not waived. F-minus-W/fullfixed64dirtyRO remain unsupported.
'''
    (A/'STATUS.md').write_text(status)
    for name in ('STATUS.md','RECEIPT.json','RELEASE.json','SUPPORTED_PROFILES.json','LATEST_SOURCE.json'):
        shutil.copy2(A/name,PACK/name)
    shutil.copy2(manifest_path,PACK/manifest_path.name)
    shutil.copy2(BASE/'RO_ORIGIN_RELEASE_r28.json',PACK/'RO_ORIGIN_RELEASE_r28.json')
    put(PACK/'FILES_SHA256.json',{p.name:sha(p) for p in PACK.iterdir() if p.is_file()})
    print('R28_PRODUCER_READY_PENDING_E',r26['binary_sha256'], 'fresh20/reused44/detailed4',
          'reviewpack_bytes',sum(p.stat().st_size for p in PACK.iterdir() if p.is_file()))


if __name__ == '__main__':
    main()
