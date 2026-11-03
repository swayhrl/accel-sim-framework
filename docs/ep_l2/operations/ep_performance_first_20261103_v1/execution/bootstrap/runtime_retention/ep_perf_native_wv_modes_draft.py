"""New EP-only native entry. No import-time actors; all starts consume first."""
import gzip, hashlib, json, os, pathlib, resource, selectors, shutil, signal
import subprocess, sys, time, uuid
from ep_perf_common_v2 import *

ALLOWED_COHORTS = frozenset(('EP_PERF_PF_RET_fastWalshTransform_CLEAN_ONLY_ON_V1', 'EP_PERF_PF_RET_fastWalshTransform_CLEAN_ONLY_OFF_V1', 'EP_PERF_PF_RET_fastWalshTransform_DIRTY_ONLY_ON_V1', 'EP_PERF_PF_RET_fastWalshTransform_DIRTY_ONLY_OFF_V1', 'EP_PERF_PF_RET_GEMM_CLEAN_ONLY_ON_V1', 'EP_PERF_PF_RET_GEMM_CLEAN_ONLY_OFF_V1', 'EP_PERF_PF_RET_GEMM_DIRTY_ONLY_ON_V1', 'EP_PERF_PF_RET_GEMM_DIRTY_ONLY_OFF_V1'))
SCOPED_MODES = {'EP_PERF_PF_RET_fastWalshTransform_CLEAN_ONLY_ON_V1': 'WV_CLEAN_ONLY', 'EP_PERF_PF_RET_fastWalshTransform_CLEAN_ONLY_OFF_V1': 'WV_CLEAN_ONLY', 'EP_PERF_PF_RET_fastWalshTransform_DIRTY_ONLY_ON_V1': 'WV_DIRTY_ONLY', 'EP_PERF_PF_RET_fastWalshTransform_DIRTY_ONLY_OFF_V1': 'WV_DIRTY_ONLY', 'EP_PERF_PF_RET_GEMM_CLEAN_ONLY_ON_V1': 'WV_CLEAN_ONLY', 'EP_PERF_PF_RET_GEMM_CLEAN_ONLY_OFF_V1': 'WV_CLEAN_ONLY', 'EP_PERF_PF_RET_GEMM_DIRTY_ONLY_ON_V1': 'WV_DIRTY_ONLY', 'EP_PERF_PF_RET_GEMM_DIRTY_ONLY_OFF_V1': 'WV_DIRTY_ONLY'}
SCOPED_CELLS = {'EP_PERF_PF_RET_fastWalshTransform_CLEAN_ONLY_ON_V1': {'mode': 'WV_CLEAN_ONLY', 'program': 'fastWalshTransform', 'input_identity_sha256': 'fc3a90622744ba1f63bec264284983747a372e3a34543249c3977d4bd285fe2e', 'observer_variant': 'ON', 'option_ref': {'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_20261103_v1/main/option_candidates/PF_RET_fastWalshTransform_CLEAN_ONLY_ON.json', 'sha256': '21b08cbb2fe8ec8b2ffb93c41a9900d7ceb067d34303ed4b28374b1f79dd093f'}}, 'EP_PERF_PF_RET_fastWalshTransform_CLEAN_ONLY_OFF_V1': {'mode': 'WV_CLEAN_ONLY', 'program': 'fastWalshTransform', 'input_identity_sha256': 'fc3a90622744ba1f63bec264284983747a372e3a34543249c3977d4bd285fe2e', 'observer_variant': 'OFF', 'option_ref': {'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/execution_performance_first_20261103_v1/control/ni_contract_amendment_011/PF_RET_fastWalshTransform_CLEAN_ONLY_OFF_011.json', 'sha256': 'c5327d67f94dc661441dd79b1cb0a8cc38a8dc65f0aeb6a656154a5463476fbe'}}, 'EP_PERF_PF_RET_fastWalshTransform_DIRTY_ONLY_ON_V1': {'mode': 'WV_DIRTY_ONLY', 'program': 'fastWalshTransform', 'input_identity_sha256': 'fc3a90622744ba1f63bec264284983747a372e3a34543249c3977d4bd285fe2e', 'observer_variant': 'ON', 'option_ref': {'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_20261103_v1/main/option_candidates/PF_RET_fastWalshTransform_DIRTY_ONLY_ON.json', 'sha256': 'd045f19e5304b2676d47e154733d3c6faacd9d3bbc38568c2402a4ba517c1a85'}}, 'EP_PERF_PF_RET_fastWalshTransform_DIRTY_ONLY_OFF_V1': {'mode': 'WV_DIRTY_ONLY', 'program': 'fastWalshTransform', 'input_identity_sha256': 'fc3a90622744ba1f63bec264284983747a372e3a34543249c3977d4bd285fe2e', 'observer_variant': 'OFF', 'option_ref': {'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/execution_performance_first_20261103_v1/control/ni_contract_amendment_011/PF_RET_fastWalshTransform_DIRTY_ONLY_OFF_011.json', 'sha256': '78bcc3b5f3f675c753030d3f0fd2af7deb29ae92fd49c18c939d0c077e0fafa5'}}, 'EP_PERF_PF_RET_GEMM_CLEAN_ONLY_ON_V1': {'mode': 'WV_CLEAN_ONLY', 'program': 'GEMM', 'input_identity_sha256': '140f6ed3a5cdb1d7183cd4d2acc37b086224a054893ef12d990fdb2d5ea3659b', 'observer_variant': 'ON', 'option_ref': {'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_20261103_v1/main/option_candidates/PF_RET_GEMM_CLEAN_ONLY_ON.json', 'sha256': 'd49037a41733b0c8f17f4b378ce3161bca029ed8442dd67afda2b355d925a38b'}}, 'EP_PERF_PF_RET_GEMM_CLEAN_ONLY_OFF_V1': {'mode': 'WV_CLEAN_ONLY', 'program': 'GEMM', 'input_identity_sha256': '140f6ed3a5cdb1d7183cd4d2acc37b086224a054893ef12d990fdb2d5ea3659b', 'observer_variant': 'OFF', 'option_ref': {'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/execution_performance_first_20261103_v1/control/ni_contract_amendment_011/PF_RET_GEMM_CLEAN_ONLY_OFF_011.json', 'sha256': '9bfb057dd53ccf65a4024ab9b63d04b723a967f4f20dcd78b2a7aefa02a74a04'}}, 'EP_PERF_PF_RET_GEMM_DIRTY_ONLY_ON_V1': {'mode': 'WV_DIRTY_ONLY', 'program': 'GEMM', 'input_identity_sha256': '140f6ed3a5cdb1d7183cd4d2acc37b086224a054893ef12d990fdb2d5ea3659b', 'observer_variant': 'ON', 'option_ref': {'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_20261103_v1/main/option_candidates/PF_RET_GEMM_DIRTY_ONLY_ON.json', 'sha256': '109dceaaf34077fb8287a804cb24de6b025739563d700e1fa0c9c4b1ae42aec6'}}, 'EP_PERF_PF_RET_GEMM_DIRTY_ONLY_OFF_V1': {'mode': 'WV_DIRTY_ONLY', 'program': 'GEMM', 'input_identity_sha256': '140f6ed3a5cdb1d7183cd4d2acc37b086224a054893ef12d990fdb2d5ea3659b', 'observer_variant': 'OFF', 'option_ref': {'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/execution_performance_first_20261103_v1/control/ni_contract_amendment_011/PF_RET_GEMM_DIRTY_ONLY_OFF_011.json', 'sha256': '215347af582ef59486dafc21a6bcdfaebec0eaabb7b0db8277fc954c213ca042'}}}
NI011_AMENDMENT_REF = {'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/execution_performance_first_20261103_v1/control/NI011_USER_AMENDMENT_AUTHORIZATION.json', 'sha256': '6f03089824a6dd28776c70545e8f9cbb622acfccd6812825157ada193f1a2f1d'}
def authorized_scope_mode(s):
    need(s.get('cohort') in SCOPED_MODES, 'cohort outside exact retention8 scope')
    cell=SCOPED_CELLS[s['cohort']]
    need(s.get('program')==cell['program'] and s.get('input_identity_sha256')==cell['input_identity_sha256'],'exact approved cell input/program')
    need(s.get('expected_effective_options')==exact(cell['option_ref']),'exact approved cell282 options')
    need(s.get('mode') == SCOPED_MODES[s['cohort']] and s.get('T') is False and s.get('M') is False,'exact RO-disabled retention mode required')
    variant='ON' if s['cohort'].endswith('_ON_V1') else 'OFF'
    need(s.get('observer_variant') == variant,'exact retention observer variant')
    if variant=='OFF':need(s.get('ni_contract_amendment_authorization_ref')==NI011_AMENDMENT_REF,'OFF011 requires exact user amendment')
    return s['mode']

LEDGER = NATIVE / 'control/qualification_ledger'
MODE_CONTRACT_SHA='9087d7b8c25e79196c600659f0639b50cc3316f48fff42b309b3a41a505891de'
NEW_VALIDATOR_SHA='19a535d9ddddcf91f9c16f95f4c4746fd8faa5992883eb1f432946cb8c14cbbe'
def formal_mode_contract(s):
    need(s['mode_contract_ref']['sha256']==MODE_CONTRACT_SHA and s['validation_module_ref']['sha256']==NEW_VALIDATOR_SHA,'unreviewed formal mapper/parser version')
    return module(s['mode_contract_ref'],'private_formal_mode_contract').validate_static(s)


def spec_path(case):
    need(case.startswith('EP_PERF_') and case.replace('_', '').isalnum() and len(case) < 170, 'invalid cohort')
    need(case in ALLOWED_COHORTS, 'outside exact8 user-approved retention cohorts')
    return ROOT / 'cases' / case / 'control/FROZEN_SPEC.json'


def spec_for(case):
    path = spec_path(case)
    s = read(path)
    registry, unused = authority()
    q = registry['registered_future_requests'][GOAL]
    need(q['budget'] == len(q['admitted_specs']) and q['remaining'] == q['budget'] - len(q['consumed']), 'fresh scoped budget arithmetic')
    need(q['admitted_specs'][case] == sha(path), 'unregistered or changed exact spec')
    need(s['schema'] == 'EP_FULL_PERF_EXACT_SPEC_V1' and s['goal'] == FRONTEND_GOAL and s.get('science_request_id') == GOAL and s['cohort'] == case, 'spec identity')
    need(s['application_budget'] == 1 and not s['automatic_retry'] and s['source_keep'], 'fresh one-start contract')
    authorization = exact(q['authorization_ref'])
    need(authorization['goal'] == GOAL and authorization['user_request_ref'] == ref(ROOT/'control/USER_REQUEST.txt'), 'user authorization binding')
    eligibility = exact(s['eligibility_ref'])
    need(eligibility['status'] == 'MAIN_REVIEWED_EP_COMPLETE_INPUT_ELIGIBLE', 'input not complete-application qualified')
    need(eligibility['input_identity_sha256'] == s['input_identity_sha256'], 'eligibility different input')
    need(eligibility['source_identity'] == s['source_identity'], 'eligibility different Source')
    need(s['mode'] in eligibility['modes_qualified'], 'mode outside input qualification')
    need(eligibility['ordered_kernel_identity'] == exact(s['input_binding_ref'])['ordered_kernel_identity'], 'eligibility kernel/command closure')
    source = exact(s['source_qualification_ref'])
    need(source['source_identity'] == s['source_identity'], 'source qualification identity')
    need(source['status'] == 'EXACT_ACCEPTED_SOURCE_CPU_EVIDENCE_REUSED_NOT_NEW_APP_ACCEPTED', 'source qualification status')
    old_sourceq = exact(source['prior_sourceq_ref'])
    need(old_sourceq['source_identity'] == s['source_identity'], 'original CPU source identity')
    for item in old_sourceq['evidence_refs'].values():
        need(sha(item['path']) == item['sha256'], 'original CPU source evidence changed')
    authorized_scope_mode(s)
    need(s['source_identity']['core_source_commit'] == '78f4b59e865b136eede74df74c44c210f5b4ca04', 'unqualified new Core')
    for path, digest in s['pinned_files'].items():
        need(sha(path) == digest, 'host/runtime pin drift ' + path)
    need(sha(s['binary_path']) == s['source_identity']['binary_sha256'], 'ELF drift')
    need(sha(s['static_library_path']) == s['source_identity']['archive_sha256'], 'archive drift')
    for config in s['ordered_configs']:
        need(sha(config['path']) == config['sha256'], 'config drift')
    need(len(s['expected_effective_options']) == 282, 'complete effective option contract required')
    need(s['expected_effective_options']['-trace'] == s['trace_entry'], 'input/config identity')
    formal_mode_contract(s)
    anchor_review=exact(s['matched_S_anchor_qualification_ref']);anchor_point=exact(anchor_review['point_ref'])
    need(anchor_review.get('registry_population_request_id')==FRONTEND_GOAL,'anchor population namespace');anchor_row=registry['registered_future_requests'][FRONTEND_GOAL]['consumed'].get(anchor_point['cohort'],{})
    need(anchor_row.get('state')=='CLOSED_ACCEPTED'and anchor_row.get('accepted_point_ref')==anchor_review['point_ref'],'S anchor current official population/point mismatch')
    if not (s['T'] or s['M']):
        need(s['ro_qualification_ref'] is None, 'RO-disabled mode may not inherit certificate authority')
    if s['T'] or s['M']:
        certificate = exact(s['ro_qualification_ref'])
        need(certificate['status'] == 'EXACT_WHOLE_COMMANDLIST_RO_SOURCE_LOADER_QUALIFIED', 'RO source/input qualification')
        need(certificate['input_identity_sha256'] == s['input_identity_sha256'], 'RO different input')
        need(certificate['source_identity'] == s['source_identity'], 'RO different source')
        for key in ['manifest_ref', 'ranges_ref']:
            need(sha(certificate[key]['path']) == certificate[key]['sha256'], 'RO byte drift')
        for kind in ['manifest','ranges']:
            item = certificate[kind+'_ref']
            need(s['expected_effective_options']['-gpgpu_ep_l2_ro_'+kind] == item['path'] and
                 s['expected_effective_options']['-gpgpu_ep_l2_ro_'+kind+'_sha256'] == item['sha256'], 'RO certificate/actual option mismatch')
    need(s['limits']['RSS_bytes'] > 0 and s['limits']['AS_bytes'] >= s['limits']['RSS_bytes'], 'RSS/AS contract')
    need(s['limits']['result_bytes'] > 0 and s['limits']['wall_seconds'] > 0, 'output/wall contract')
    need(s['host_engine_ref'] == ref(__file__) and s['host_common_ref'] == ref(P(__file__).with_name('ep_perf_common_v2.py')), 'entry engine drift')
    need(s['host_engine_ref']['sha256'] in q['runtime_versions'], 'unregistered runtime version')
    need(q['runtime_versions'][s['host_engine_ref']['sha256']] ==
         dict(engine_ref=s['host_engine_ref'], common_ref=s['host_common_ref']), 'runtime version binding')
    return s


def fresh_input(s):
    p = exact(s['input_binding_ref'])
    need(p['input_identity_sha256'] == s['input_identity_sha256'], 'input binding identity')
    mount = json.loads(subprocess.check_output(['findmnt', '-J', '-T', s['trace_entry']], text=True))['filesystems'][0]
    need(mount['source'] == 'admin-wcx@10.208.130.164:/home/shared' and mount['fstype'] == 'fuse.sshfs', 'not genuine164')
    need(s['trace_entry'].startswith('/root/share/mnt164/'), 'large inputs must use genuine164')
    rows = []
    for item in p['members']:
        path = P(item['path'])
        st = path.stat()
        need(st.st_size == item['size'] and st.st_mtime_ns == item['mtime_ns'], 'frozen member stat changed')
        need(str(path.resolve()) == item['resolved_path'], 'member storage identity changed')
        rows.append(dict(path=str(path), size=st.st_size, mtime_ns=st.st_mtime_ns,
                         recorded_sha256=item['sha256'], body_rehashed=False))
    need(sha(s['trace_entry']) == p['literal_commandlist_sha256'], 'small whole commandlist changed')
    return dict(status='RECORDED_CONTENT_AND_CURRENT_STORAGE_BINDING_PASS', mount=mount, members=rows,
                literal_commandlist_sha256=sha(s['trace_entry']), no_large_body_rehash=True)


def dispatch_binding(case):
    p = ROOT / 'control/dispatch_bindings' / (case + '.json')
    binding = read(p)
    need(binding['cohort'] == case and binding['spec_sha256'] == sha(spec_path(case)), 'dispatch/spec mismatch')
    need(type(binding['host_cpu']) is int and binding['host_cpu'] in os.sched_getaffinity(0), 'CPU not available')
    return binding


def prepare(case):
    need(os.environ.get('EP_FULL_PERF_NATIVE_ENTRY') == '1', 'native sole entry required')
    route=read(ROOT/'control/NATIVE_ENTRY_ROUTE.json')
    need(route['goal']==GOAL and route['status']=='MAIN_INSTALLED_ADDITIVE_NATIVE_EP_PERF_ROUTE','native route qualification missing')
    prior=P(route['prior_entry_ref']['path']).read_bytes()
    need(sha(route['prior_entry_ref']['path'])==route['prior_entry_ref']['sha256'],'prior native entry evidence changed')
    entry=route['entry_ref']
    registry,_=authority()
    need(registry['registered_future_requests'][GOAL]['native_entry_ref']==entry,'entry outside registered scoped sole-entry')
    need(P(entry['path'])==ROOT.parent/'bin/native' and sha(entry['path'])==entry['sha256'],'scoped native entry path/content drift')
    need((NATIVE/'bin/native').read_bytes()==prior,'foreign global native bytes changed; requalification required')
    current=P(entry['path']).read_bytes()
    need(current.endswith(prior) and route['own_prelude'].encode() in current,'native route or peer suffix changed')
    s = spec_for(case)
    input_proof = fresh_input(s)
    for name, commit_field in [('core', 'core_source_commit'), ('framework', 'framework_source_commit')]:
        repo = s['source_worktrees'][name]
        need(subprocess.check_output(['git', '-C', repo, 'rev-parse', 'HEAD'], text=True).strip() == s['source_identity'][commit_field], 'source HEAD drift')
        need(not subprocess.check_output(['git', '-C', repo, 'status', '--porcelain', '--untracked-files=no'], text=True).strip(), 'tracked Source dirty')
    qualification = exact(s['host_qualification_ref'])
    need(qualification['status'] == 'HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED', 'host qualification missing')
    for item in qualification['modules']:
        need(sha(item['path']) == item['sha256'], 'host qualification pin changed')
    receipt = dict(status='EP_PERF_PREPARE_PASS_NO_START', cohort=case, input=input_proof,
                   source_identity=s['source_identity'], spec_sha256=sha(spec_path(case)),
                   host_qualification_ref=s['host_qualification_ref'], science_starts=0,
                   formal_mode=s['mode'],mode_contract_ref=s['mode_contract_ref'],
                   validation_module_ref=s['validation_module_ref'],
                   mode_cpu_qualification_ref=s.get('mode_cpu_qualification_ref'))
    path = ROOT/'cases'/case/'control/NATIVE_PRELAUNCH_QUALIFICATION.json'
    if path.exists():
        need(read(path) == receipt, 'prelaunch qualification changed')
    else:
        put(path, receipt, True)
    return receipt


def resource_gate(s, binding):
    """Fresh passive resource admission, serialized with this Goal's claims."""
    resources = module(s['resource_module_ref'], 'ep_perf_resource_admission')
    policy = exact(s['resource_policy_ref'])
    snapshot = resources.snapshot()
    claims = read(ROOT/'control/DISPATCH_CLAIMS.json')['claims']
    own = claims.get(s['cohort'])
    need(own is not None and own['state'] == 'CLAIMED' and own['spec_sha256'] == sha(spec_path(s['cohort'])) and
         own['host_cpu'] == binding['host_cpu'], 'own exact unspent dispatch claim missing/mismatched')
    additional = 0
    writes = 0
    for case, row in claims.items():
        # The resource module accounts for foreign tasks; this population is EP only.
        rss = 0
        model = row.get('model_pid')
        if model:
            try:
                parts = (P('/proc')/str(model)/'stat').read_text().rsplit(')',1)[1].split()
                need(int(parts[19]) == row['model_start_ticks'] and parts[0] not in ['Z','X'], 'own PID generation changed; admission HOLD')
                status = (P('/proc')/str(model)/'status').read_text().splitlines()
                rss = int(next(v.split()[1] for v in status if v.startswith('VmRSS:')))*1024
            except (OSError, StopIteration):
                pass
        if row['state'] in ['CLAIMED', 'RUNNING']:
            additional += max(0, row['estimated_peak_RAM_bytes'] - rss)
        writes += max(0, row['remaining_write_bytes'])
    writes += max([read(ROOT/'cases'/case/'control/FROZEN_SPEC.json')['limits']['result_bytes'] for case in claims] or [0]) + 2*M
    decision = resources.admit(snapshot, additional, writes, policy=policy)
    need(decision['pass_admission'], 'RESOURCE_ADMISSION_HOLD:' + json.dumps(decision, separators=(',', ':')))
    receipt = dict(utc=now(), binding=binding, snapshot=snapshot, admission=decision,
                   own_additional_RAM_bytes=additional, own_remaining_write_bytes=writes)
    put(ROOT/'control/admission_receipts'/(s['cohort']+'.'+str(uuid.uuid4())+'.json'), receipt, True)
    return receipt


def verify_actual(h, info, s, args, env):
    need(info['cmdline'] == [x.encode() for x in args] and info['environment'] == {k.encode(): v.encode() for k, v in env.items()}, 'actual model argv/environment')
    need(info['affinity'] == [s['host_cpu']] and info['nice'] == 10, 'actual CPU/nice')
    need(info['boot_id'] == s['native_boot_id'] and info['mnt_namespace'] == s['native_mount_namespace'], 'native domain changed')
    need(s['binary_path'] in info['maps'], 'new model ELF not mapped')
    allowed = {s['binary_path']: s['source_identity']['binary_sha256']}
    allowed.update({p: digest for p, digest in s['pinned_files'].items() if '/env/lib/' in p or '/common-lib/' in p})
    mapped = {}
    for line in info['maps'].splitlines():
        fields = line.split(maxsplit=5)
        if len(fields) == 6 and fields[5].startswith('/'):
            path = fields[5]
            need(path in allowed and sha(path) == allowed[path], 'unqualified mapped library ' + path)
            mapped[path] = allowed[path]
    line = next(v for v in info['limits'].splitlines() if v.startswith('Max address space'))
    need(line.split()[3:5] == [str(s['limits']['AS_bytes'])] * 2, 'actual AS limit mismatch')
    need('/root/data/ep_l2_dtc_l1_native_v2/EP/src/' not in info['maps'], 'protected old Core mapped')
    return dict(mapped_file_sha256=mapped, actual_environment_exact=True,
                actual_AS_limit_bytes=s['limits']['AS_bytes'], actual_RSS_monitor_limit_bytes=s['limits']['RSS_bytes'])


def stage_release_gate(s):
    if s['program'] != 'GEMM':return dict(status='INITIAL_FWT_SCOPE')
    path=ROOT.parent/'control/STAGE_RELEASE_RETENTION_GEMM.json'
    need(path.exists(),'GEMM_CONDITIONAL_STAGE_HOLD_MISSING_MAIN_RELEASE')
    release=read(path)
    need(release.get('schema')=='EP_MAIN_PF_RETENTION_GEMM_STAGE_RELEASE_V1' and release.get('status')=='RELEASED_AFTER_FWT_TWO_MODE_MS_NI_PASS' and release.get('approved_by')=='EP-MAIN' and release.get('science_request_id')==GOAL,'GEMM exact Main stage release')
    need(release.get('ni_contract_amendment_authorization_ref')==NI011_AMENDMENT_REF,'GEMM stage NI amendment')
    refs=release.get('ni_comparison_refs',[]);need(len(refs)==2,'two FWT mode NI comparisons required')
    registry,_=authority();request=registry['registered_future_requests'][GOAL];modes=set()
    criterion=exact(release.get('criterion_review_ref'))
    need(criterion.get('status')=='MAIN_REVIEWED_RETENTION_PERFORMANCE_CRITERION_PASS' and criterion.get('approved_by')=='EP-MAIN' and criterion.get('criterion_satisfied') is True,'GEMM Main performance criterion review missing')
    need(criterion.get('source_identity')==s['source_identity'] and criterion.get('input_identity_sha256')=='fc3a90622744ba1f63bec264284983747a372e3a34543249c3977d4bd285fe2e','GEMM criterion Source/FWT input')
    def accepted_point(rr,mode,own=False):
        point=exact(rr);need(point.get('mode')==mode and point.get('source_identity')==s['source_identity'] and point.get('input_identity_sha256')==criterion['input_identity_sha256'] and point.get('hardware_drained') is True,'criterion point Source/input/mode/drain')
        owners=[request] if own else registry['registered_future_requests'].values();found=False
        for owner in owners:
            consumed=owner.get('consumed',{})
            if type(consumed) is not dict:continue
            row=consumed.get(point['cohort'],{})
            if row.get('state')=='CLOSED_ACCEPTED' and row.get('accepted_point_ref')==rr:found=True;break
        need(found,'criterion point not current official CLOSED_ACCEPTED')
        return point
    old=accepted_point(criterion['old_WV_point_ref'],'WV_ZERO_RO')
    partial_refs=criterion.get('partial_point_refs',[]);need(len(partial_refs)==2,'criterion must retain both partial ON results')
    partials=[];pmodes=set()
    for rr in partial_refs:
        point=exact(rr);mode=point.get('mode');need(mode in ('WV_CLEAN_ONLY','WV_DIRTY_ONLY') and mode not in pmodes,'criterion two distinct partials');pmodes.add(mode)
        point=accepted_point(rr,mode,True);need(SCOPED_CELLS.get(point['cohort'],{}).get('observer_variant')=='ON','NI control cannot enter performance criterion');partials.append(point)
    def victim_reads(point):
        bundle=exact(point['validation_ref']);need(bundle.get('source_identity')==s['source_identity'],'criterion bundle Source')
        records=bundle['model']['mechanism_metrics']['full_mechanism_records']['victim']
        need(set(records)==set(str(i) for i in range(64)),'criterion exact64slice Victim population')
        vals=[records[str(i)]['read_responses'] for i in range(64)];need(all(type(v) is int and v>=0 for v in vals),'criterion Victim read units')
        return sum(vals)
    old_reads=victim_reads(old)
    speed=any(type(point.get('cycles')) is int and point['cycles']*200<=old['cycles']*199 for point in partials)
    service=old_reads>0 and any(abs(victim_reads(point)-old_reads)*10>=old_reads for point in partials)
    need(speed or service,'GEMM frozen criterion false: neither>=0.5pct fewer cycles nor>=10pct absolute relative Victim read-service change')

    required={'cycles','instructions','CTA','kernel_count','hardware_drained','ordered_kernel_identity','FT_TVD_resource_closure'}
    for rr in refs:
        q=exact(rr);mode=q.get('mode');need(mode in ('WV_CLEAN_ONLY','WV_DIRTY_ONLY') and mode not in modes,'two distinct FWT NI modes');modes.add(mode)
        need(q.get('schema')=='EP_MAIN_PF_RETENTION_MS_APPLICATION_NI_V1' and q.get('status')=='PASS_MS_ONLY_APPLICATION_NI','FWT exact MS NI not PASS')
        need(q.get('source_identity')==s['source_identity'] and q.get('input_identity_sha256')=='fc3a90622744ba1f63bec264284983747a372e3a34543249c3977d4bd285fe2e','FWT NI Source/input scope')
        need(set(q.get('equal_fields',[])) >= required,'FWT NI incomplete closure/ordered kernel equality')
        for field,variant in [('primary_point_ref','ON'),('off_point_ref','OFF')]:
            point=exact(q[field]);cohort=point['cohort'];cell=SCOPED_CELLS.get(cohort,{})
            need(cell.get('program')=='fastWalshTransform' and cell.get('mode')==mode and cell.get('observer_variant')==variant,'FWT NI wrong formal point')
            row=request['consumed'].get(cohort,{})
            need(row.get('state')=='CLOSED_ACCEPTED' and row.get('accepted_point_ref')==q[field],'FWT NI point outside current closed official population')
            archive=exact(row['archive_receipt_ref'])
            need(archive.get('status')=='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS' and len(archive.get('native_restores',[]))==2 and all(t.get('status')=='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS' for t in archive['native_restores']),'FWT NI archive/two native restores not closed')
    return dict(status='MAIN_RELEASED_GEMM_AFTER_TWO_FWT_MS_NI',release_ref=ref(path))

def run_native(case):
    prepare(case)
    s = spec_for(case)
    stage_release_gate(s)
    binding = dispatch_binding(case)
    s = dict(s, host_cpu=binding['host_cpu'])
    h = module(s['helpers_ref'], 'ep_perf_helpers')
    output_module = module(s['output_module_ref'], 'ep_perf_output')
    out = ROOT / 'cases' / case / 'run' / str(uuid.uuid4())
    uid = out.name
    env = dict(PATH='/usr/bin:/bin', LANG='C', LC_ALL='C', CUDA_VISIBLE_DEVICES='',
               LD_LIBRARY_PATH=str(NATIVE/'common-lib'), OMP_NUM_THREADS='1',
               OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1',
               TMPDIR=str(out/'tmp'), XDG_CACHE_HOME=str(out/'cache'), **s['observer_env'])
    args, launcher = h.command(s, out), h.launch_command(s, out)
    with locked(ROOT/'control'/('CPU_' + str(s['host_cpu']) + '.lock'), True), locked(ROOT/'cases'/case/'control/RUN.lock', True):
        def consume(registry):
            request = registry['registered_future_requests'][GOAL]
            need(case not in request['consumed'] and request['remaining'] > 0, 'already consumed; new allowance needed')
            need(not (LEDGER/(case+'.INTENT.json')).exists(), 'intent exists; never retry')
            out.mkdir(parents=True)
            (out/'tmp').mkdir()
            (out/'cache').mkdir()
            intent = dict(goal=GOAL, cohort=case, uuid=uid, utc=now(), output=str(out),
                          source_identity=s['source_identity'], spec_ref=ref(spec_path(case)),
                          dispatch_binding_ref=ref(ROOT/'control/dispatch_bindings'/(case+'.json')),
                          launcher_argv=launcher, model_argv=args, environment=env,
                          consumed_before_launcher_fork=1, automatic_retry=False)
            intent_ref = put(LEDGER/(case+'.INTENT.json'), intent, True)
            request['consumed'][case] = dict(uuid=uid, output=str(out), intent_ref=intent_ref,
                                              state='CONSUMED_BEFORE_FORK', consumed=1, remaining=0)
            request['remaining'] -= 1
            request['state'] = 'RUNNING'
        with locked(ROOT.parent/'control/ADMISSION.lock'):
            resource_gate(s, binding)
            transaction('CONSUME_EXACT_ONE_BEFORE_FORK_NO_REFUND', consume)
        began = time.monotonic()
        p = None
        observed = None
        failure = None
        returncode = None
        peak_rss = peak_hot = 0
        raw_receipt = None
        capsule = {}
        def update_claim(changes):
            with locked(ROOT.parent/'control/ADMISSION.lock'):
                path = ROOT/'control/DISPATCH_CLAIMS.json'
                value = read(path)
                need(case in value['claims'], 'live own claim missing')
                previous = dict(value['claims'][case])
                value['claims'][case].update(changes)
                put(path, value)
                current = value['claims'][case]
                if (current['state'] != previous['state'] or
                    abs(current['remaining_write_bytes']-previous['remaining_write_bytes']) >= 4*M):
                    publish_own_write_carrier(value['claims'])
        def limits():
            os.setsid()
            os.sched_setaffinity(0, {s['host_cpu']})
            os.setpriority(os.PRIO_PROCESS, 0, 10)
            resource.setrlimit(resource.RLIMIT_AS, (s['limits']['AS_bytes'],)*2)
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
            resource.setrlimit(resource.RLIMIT_FSIZE, (s['limits']['result_bytes'],)*2)
        try:
            copies = {P(c['path']).name: c['path'] for c in s['ordered_configs']}
            copies.update({'FROZEN_SPEC.json': str(spec_path(case)),
                           'NATIVE_PRELAUNCH_QUALIFICATION.json':str(ROOT/'cases'/case/'control/NATIVE_PRELAUNCH_QUALIFICATION.json'),
                           'USER_AUTHORIZATION.json':str(ROOT/'control/USER_AUTHORIZATION.json'),
                           'SOURCE_QUALIFICATION.json':s['source_qualification_ref']['path'],
                           'INPUT_ELIGIBILITY.json':s['eligibility_ref']['path'],
                           'INPUT_BINDING.json':s['input_binding_ref']['path']})
            if s['T'] or s['M']:
                certificate = exact(s['ro_qualification_ref'])
                copies.update({'RO_QUALIFICATION.json':s['ro_qualification_ref']['path'],
                               'RO_MANIFEST.json':certificate['manifest_ref']['path'],
                               'RO_RANGES.csv':certificate['ranges_ref']['path']})
            for name, source in copies.items():
                digest = sha(source)
                shutil.copy2(source, out/name)
                need(sha(out/name) == digest == sha(source), 'sealed copy changed')
                capsule[name] = ref(out/name)
            with output_module.RawGzipWriter(out/'raw.log.gz') as raw, (out/'RESOURCE_SAMPLES.jsonl').open('xb') as samples:
                p = subprocess.Popen(launcher, cwd=out, env=env, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, preexec_fn=limits, bufsize=0)
                update_claim(dict(state='RUNNING', launcher_pid=p.pid, output=str(out), uuid=uid))
                os.set_blocking(p.stdout.fileno(), False)
                select = selectors.DefaultSelector()
                select.register(p.stdout, selectors.EVENT_READ)
                put(out/'NATIVE_LAUNCH.json', dict(utc=now(), launcher_pid=p.pid,
                    launcher_start_ticks=h.info(p.pid)['start_ticks'], launcher_argv=launcher,
                    model_argv=args, environment=env, source_identity=s['source_identity'],
                    spec_sha256=sha(spec_path(case)), dispatch_binding=binding,
                    launch_capsule=capsule, native_engine_ref=ref(__file__)), True)
                eof = False
                last_sample = -10
                while p.poll() is None or not eof:
                    for key, unused in select.select(.05):
                        data = os.read(key.fileobj.fileno(), 65536)
                        if not data:
                            eof = True
                            select.unregister(key.fileobj)
                            break
                        raw.write(data)
                    if observed is None:
                        for pid in h.process_tree(p.pid):
                            try:
                                info = h.info(pid)
                                if pid != p.pid and s['binary_path'] in info['maps']:
                                    proof = verify_actual(h, info, s, args, env)
                                    observed = dict(h.serializable_info(info), **proof)
                                    put(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json', observed, True)
                                    update_claim(dict(model_pid=observed['pid'], model_start_ticks=observed['start_ticks']))
                                    break
                            except (FileNotFoundError, ProcessLookupError):
                                pass
                    elapsed = time.monotonic() - began
                    if elapsed - last_sample >= 2:
                        last_sample = elapsed
                        rss = sum(h.rss(pid) for pid in h.process_tree(p.pid))
                        hot = h.footprint(out)
                        peak_rss, peak_hot = max(peak_rss, rss), max(peak_hot, hot)
                        sample = dict(elapsed_seconds=elapsed, process_tree_RSS_bytes=rss, allocated_hot_bytes=hot)
                        samples.write(encoded(sample))
                        samples.flush()
                        update_claim(dict(observed_RSS_bytes=rss, observed_hot_bytes=hot,
                                          estimated_peak_RAM_bytes=max(s['estimated_peak_RAM_bytes'], min(s['limits']['RSS_bytes'], int(rss*1.1))),
                                          remaining_write_bytes=max(0,s['limits']['result_bytes']-hot)+2*M))
                        if rss > s['limits']['RSS_bytes']:
                            failure = 'ACTUAL_PROCESS_TREE_RSS_HARD_LIMIT'
                        if hot > s['limits']['result_bytes']:
                            failure = 'ACTUAL_RESULT_HARD_LIMIT'
                        # Admission forecasts and transient peer snapshots never kill a healthy model.
                        if shutil.disk_usage(ROOT).free < 128*M:
                            failure = 'PHYSICAL_ENOSPC_EMERGENCY_128M'
                    if elapsed > s['limits']['wall_seconds']:
                        failure = 'EXACT_WALL_LIMIT'
                    if (ROOT/'cases'/case/'control/ABORT').exists():
                        failure = 'EXPLICIT_OWN_ABORT'
                    if failure:
                        break
                if failure and p.poll() is None:
                    os.killpg(p.pid, signal.SIGTERM)
                try:
                    returncode = p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(p.pid, signal.SIGKILL)
                    returncode = p.wait()
                select.close()
                p.stdout.close()
            raw_receipt = raw.receipt
        except BaseException as exc:
            failure = failure or ('LAUNCH_OR_MONITOR_EXCEPTION:' + type(exc).__name__ + ':' + str(exc))
        finally:
            if p is not None and p.poll() is None:
                os.killpg(p.pid, signal.SIGKILL)
                returncode = p.wait()
        raw_ref = ref(out/'raw.log.gz') if (out/'raw.log.gz').exists() else None
        syscall = None
        if returncode == 0 and failure is None and observed:
            try:
                syscall = h.syscall_proof(out/'actual_file_process_network.log', s, observed['pid'])
                need(not h.pid_generation_live(observed), 'model generation still live')
            except Exception as exc:
                failure = 'SYSCALL_OR_PROCESS_CLOSURE:' + str(exc)
        closed_refs = {name:ref(out/name) for name in ['NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json','actual_file_process_network.log'] if (out/name).exists()}
        done = dict(schema='EP_FULL_PERF_NATIVE_DONE_V1', goal=GOAL, cohort=case, uuid=uid,
                    output=str(out), source_identity=s['source_identity'], spec_ref=ref(spec_path(case)),
                    launcher_wait_returncode=returncode, stop_reason=failure, native_simulator_observed=observed is not None,
                    raw_compressed_ref=raw_ref, raw_stream_receipt=raw_receipt,
                    syscall_proof=syscall, closed_artifact_refs=closed_refs, new_attempt_consumed=1,
                    automatic_retry=False, elapsed_seconds=time.monotonic()-began,
                    peak_process_tree_RSS_bytes=peak_rss, peak_hot_bytes=peak_hot, source_keep=True)
        put(out/'NATIVE_EXIT.json', done, True)
        done_ref = put(LEDGER/(case+'.DONE.json'), done, True)
        def finish(registry):
            row = registry['registered_future_requests'][GOAL]['consumed'][case]
            need(row['uuid'] == uid, 'consumed row changed')
            row.update(state='NATURAL_COMPLETE_PENDING_VALIDATION' if returncode == 0 and failure is None and observed else 'UNACCEPTED_ENGINEERING_FAILURE', done_ref=done_ref,
                       remaining_future_model_RAM_bytes=0)
        transaction('RECORD_TERMINAL_NO_REFUND', finish)
        update_claim(dict(state='TERMINAL_PENDING_VALIDATION', estimated_peak_RAM_bytes=0,
                          observed_RSS_bytes=0, remaining_write_bytes=2*M))
        return done


def main(args):
    need(len(args) == 5 and args[0] == 'experiment' and args[3:] == ['--project','EP_L2'], 'exact EP native command required')
    op, case = args[1:3]
    if op in ('prepare', 'inspect'):
        return prepare(case)
    if op == 'run-native':
        return run_native(case)
    raise RuntimeError('unsupported operation')


if __name__ == '__main__':
    try:
        print(json.dumps(main(sys.argv[1:])))
    except Exception as exc:
        print(json.dumps(dict(status='HOLD', reason=str(exc), automatic_retry=False)), file=sys.stderr)
        sys.exit(2)
