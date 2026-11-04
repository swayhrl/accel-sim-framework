"""New EP-only native entry. No import-time actors; all starts consume first."""
import gzip, hashlib, json, os, pathlib, resource, selectors, shutil, signal
import subprocess, sys, time, uuid
from ep_perf_common_v2 import *

SCOPED_MODES = {'EP_PERF_PFV3_MIDTAG_FWT_S_G32W16_V1': 'S', 'EP_PERF_PFV3_MIDTAG_FWT_WV_ZERO_RO_G32W16_V1': 'WV_ZERO_RO', 'EP_PERF_PFV3_MIDTAG_FWT_S_G64W8_V1': 'S', 'EP_PERF_PFV3_MIDTAG_FWT_WV_ZERO_RO_G64W8_V1': 'WV_ZERO_RO', 'EP_PERF_PFV3_MIDTAG_GEMM_S_G32W16_V1': 'S', 'EP_PERF_PFV3_MIDTAG_GEMM_WV_ZERO_RO_G32W16_V1': 'WV_ZERO_RO', 'EP_PERF_PFV3_MIDTAG_GEMM_S_G64W8_V1': 'S', 'EP_PERF_PFV3_MIDTAG_GEMM_WV_ZERO_RO_G64W8_V1': 'WV_ZERO_RO'}
ALLOWED_COHORTS=frozenset(SCOPED_MODES)
def authorized_scope_mode(s):
    need(s.get('cohort')in SCOPED_MODES and s.get('mode')==SCOPED_MODES[s['cohort']],'outside exact8 midTag scope/mode')
    need(type(s.get('M'))is bool and type(s.get('T'))is bool and(s['M'],s['T'])==((True,True)if s['mode']=='F'else(False,False)),'DRAM scope M/T mismatch')
    return s['mode']

LEDGER = NATIVE / 'control/qualification_ledger'
NATIVE_ROUTE_GUARD_REF={'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v3_20261104_v1/activation_20261104_v1/agent_d_execution/native_route_guard_v3.py', 'sha256': '9df2bab0058b571466998f71bfa487a929b6718a0d7e56d347746e98d6208ca9'}
MODE_CONTRACT_SHA='536260c779795f059aef96d76e28080f8edd1b79d9d24b7151d312255715310b'
NEW_VALIDATOR_SHA='0de4f89cfcdc83b3d4414b8075372448459d4248ce165e518f7f2051ca7bcda1'
def formal_mode_contract(s):
    need(s['mode_contract_ref']['sha256']==MODE_CONTRACT_SHA and s['validation_module_ref']['sha256']==NEW_VALIDATOR_SHA,'unreviewed formal mapper/parser version')
    return module(s['mode_contract_ref'],'private_formal_mode_contract').validate_static(s)


def spec_path(case):
    need(case.startswith('EP_PERF_') and case.replace('_', '').isalnum() and len(case) < 170, 'invalid cohort')
    need(case in ALLOWED_COHORTS, 'not an exact8 midTag cohort')
    return ROOT / 'cases' / case / 'control/FROZEN_SPEC.json'


def spec_for(case, require_release=True):
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
    need(authorization.get('explicit_user_approval')is True and authorization.get('approved_launches')==8 and authorization.get('allowed_cohorts')==sorted(ALLOWED_COHORTS),'fresh exact eight user scope approval')
    need(authorization.get('Source5')==s['source_identity'],'authorization Source5 binding')
    need(s.get('Main_scientific_launch_authorization')==q['authorization_ref'],'exact authorization/spec binding')
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
    need(s.get('native_route_guard_ref')==NATIVE_ROUTE_GUARD_REF,'spec route guard binding')
    for anchor_field in ['absolute_REF850_S_anchor_qualification_ref','absolute_REF850_EP_anchor_qualification_ref']:
        anchor_review=exact(s[anchor_field]);anchor_point=exact(anchor_review['point_ref'])
        need(anchor_review.get('registry_population_request_id')==FRONTEND_GOAL,'anchor old850 population namespace')
        anchor_row=registry['registered_future_requests'][FRONTEND_GOAL]['consumed'].get(anchor_point['cohort'],{})
        need(anchor_row.get('state')=='CLOSED_ACCEPTED'and anchor_row.get('accepted_point_ref')==anchor_review['point_ref'],'old absolute850 official accepted population')
    peer_case=s['same_background_peer_cohort']
    peer_path=spec_path(peer_case)
    need(peer_case in q['admitted_specs'] and sha(peer_path)==q['admitted_specs'][peer_case],'sameclock S/EP peer not registered exact')
    module(s['mode_contract_ref'],'service_fair_pair_contract').validate_fair_pair(s,read(peer_path))
    scope=module(s['mode_contract_ref'],'service_release_contract')
    family_row=scope.family_row(s)
    # Preparation can overlap; consumption of any GEMM waits for all four FWT closures.
    if require_release and '_GEMM_' in case:
        prerequisite=[x for x in ALLOWED_COHORTS if '_FWT_' in x]
        need(len(prerequisite)==4,'exact four FWT predecessor cells')
        stage=read(ROOT/'control/FWT4_ACCEPTED_STAGE_REVIEW.json')
        need(stage.get('schema')=='EP_MAIN_PFV3_MIDTAG_FWT4_ACCEPTED_STAGE_REVIEW_V1' and stage.get('status')=='MAIN_REVIEWED_FWT4_CLOSED_ACCEPTED_ARCHIVED_TWO_RESTORES' and stage.get('approved_by')=='EP-MAIN' and stage.get('request_id')==GOAL,'Main FWT4 stage receipt missing/mismatched')
        need(set(stage.get('accepted_point_refs',{}))==set(prerequisite) and set(stage.get('archive_receipt_refs',{}))==set(prerequisite),'Main FWT4 stage population')
        exact(stage['controller_manifest_ref'])
        for fwt in prerequisite:
            row=q['consumed'].get(fwt,{})
            need(stage['accepted_point_refs'][fwt]==row.get('accepted_point_ref') and stage['archive_receipt_refs'][fwt]==row.get('archive_receipt_ref'),'Main stage/current accepted identities differ')
            need(row.get('state')=='CLOSED_ACCEPTED','FWT four accepted/archive gate before GEMM')
            pt=exact(row['accepted_point_ref']);ar=exact(row['archive_receipt_ref'])
            need(pt.get('cohort')==fwt and pt.get('status')=='EP_FULL_PERF_APPLICATION_ACCEPTED' and pt.get('hardware_drained')is True,'FWT accepted input/drain')
            need(pt.get('spec_ref')==ref(spec_path(fwt)) and pt.get('source_identity')==s['source_identity'],'FWT exact Source/spec')
            need(ar.get('cohort')==fwt and ar.get('uuid')==row.get('uuid')==pt.get('uuid') and ar.get('status')=='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS' and ar.get('source_keep')is True,'FWT archive closure')
            rs=ar.get('native_restores',[])
            need(len(rs)==2 and len({r['target']for r in rs})==2 and all(r.get('status')=='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS' and r.get('archive_sha256')==ar['archive_ref']['sha256']for r in rs),'FWT two independent restores')
    if family_row['stage']=='CONDITIONAL_COMBINATION' and require_release:
        scope.validate_combo_release(s, registry, ROOT/'control/conditional_release'/(case+'.json'), data_root=ROOT)
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
    # No installed receipt => HOLD before spec consumption, resource claims or fork.
    route=read(ROOT/'control/NATIVE_ENTRY_ROUTE_V3.json')
    need(route['goal']==GOAL and route['status']=='MAIN_INSTALLED_ADDITIVE_NATIVE_EP_PERF_ROUTE','native route not Main installed')
    need(route.get('approved_by')=='EP-MAIN' and route.get('scientific_scope_activated')is True,'scope not activated')
    # Immutable exact shared Native pin. Any future route change HOLDs.
    need(route.get('guard_module_ref')==NATIVE_ROUTE_GUARD_REF,'pinned route guard mismatch')
    guard=module(route['guard_module_ref'],'midtag_formal_native_route_guard')
    guard.validate_current(str(ROOT/'control/NATIVE_ENTRY_ROUTE_V3.json'))
    entry=route['entry_ref'];registry,_=authority()
    need(registry['registered_future_requests'][GOAL]['native_entry_ref']==entry,'registered sole-entry mismatch')
    need(P(entry['path'])==ROOT.parent/'bin/native_midtag_v3' and sha(entry['path'])==entry['sha256'],'scoped entry mismatch')
    need(route.get('exact_cohorts')==sorted(ALLOWED_COHORTS),'Native cohort scope mismatch')
    s = spec_for(case, require_release=False)
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
    decision = resources.admit(snapshot, additional, writes, policy=dict(policy,requested_host_cpu=binding['host_cpu'],requested_cohort=s['cohort'],requested_request_id=GOAL))
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


def run_native(case):
    prepare(case)
    s = spec_for(case)
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
        with locked(GLOBAL_MAIN_ADMISSION_LOCK):
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
            with locked(GLOBAL_MAIN_ADMISSION_LOCK):
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
