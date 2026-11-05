"""New EP-only native entry. No import-time actors; all starts consume first."""
import gzip, hashlib, json, os, pathlib, resource, selectors, shutil, signal
import subprocess, sys, time, uuid
from ep_perf_common_v2 import *
_SCHEMA_REFS={'contract_ref': {'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v4_20261104_v1/track_b/private_runtime/RUNTIME_FULL_43_CONTRACT_V4.json', 'sha256': '29cb1d6a3a70917e2ce478b3ab38b11532c1072d8f05151ae71c619dfe9ea6f0'}, 'closure_ref': {'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v4_20261104_v1/track_a/private_main_integration/SOURCE78_NATIVE_CLOSURE.json', 'sha256': '1db6b7339c39696989767a6d8de8f10ccd90f0c52f9296bbd6ec66cd365662a5'}, 'extra_dependencies_ref': {'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v4_20261104_v1/track_a/private_main_integration/SOURCE78_HELPER_DEPENDENCIES.json', 'sha256': '139d1c8cf914b0e6667ea20e4054a42e16f5e29cdedcda2f5789f82858822767'}}
_SCHEMA_MODULE={'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v4_20261104_v1/track_b/private_runtime/runtime_monitor_schema_v4_strict.py', 'sha256': '540feb2cd00044dd9d62b8a0858181a2c026cb82ac63cb0be1e9bdb65ab8126b'}
def validate_spec_contract(s,require_bound_cpu=False):
    return module(_SCHEMA_MODULE,'source78_strict43').validate_spec_contract(s,**_SCHEMA_REFS,require_bound_cpu=require_bound_cpu,check_current_domain=True,check_current_dependencies=True)
def engineering_spec_for(case):
    s=read(spec_path(case));validate_spec_contract(s)
    need(s['schema']=='EP_FULL_PERF_EXACT_SPEC_V1'and s['goal']==FRONTEND_GOAL and s['science_request_id']==GOAL and s['cohort']==case,'spec identity')
    need(s['host_engine_ref']==ref(__file__)and s['host_common_ref']==ref(P(__file__).with_name('ep_perf_common_v2.py')),'entry engine drift')
    authorized_scope_mode(s);formal_mode_contract(s)
    eligibility=exact(s['eligibility_ref']);binding=exact(s['input_binding_ref'])
    need(eligibility['status']=='MAIN_REVIEWED_EP_COMPLETE_INPUT_ELIGIBLE'and eligibility['source_identity']==s['source_identity']and eligibility['input_identity_sha256']==s['input_identity_sha256']and s['mode']in eligibility['modes_qualified'],'input/mode eligibility')
    need(eligibility['ordered_kernel_identity']==binding['ordered_kernel_identity'],'eligibility kernel closure')
    source=exact(s['source_qualification_ref']);need(source['source_identity']==s['source_identity'],'Source qualification identity')
    prior_source=exact(source['prior_source_qualification_ref']);need(prior_source['source_identity']==s['source_identity'],'prior source identity')
    old_source=exact(prior_source['prior_sourceq_ref']);need(old_source['source_identity']==s['source_identity'],'original CPU Source5')
    for r in old_source['evidence_refs'].values():need(sha(r['path'])==r['sha256'],'original Source CPU evidence changed')
    for p,h in s['pinned_files'].items():need(sha(p)==h,'host/runtime pin drift '+p)
    need(sha(s['binary_path'])==s['source_identity']['binary_sha256']and sha(s['static_library_path'])==s['source_identity']['archive_sha256'],'Source78 ELF/archive drift')
    return s
def fresh_science_authorization(s):
    a=exact(s['Main_scientific_launch_authorization'])
    need(a.get('explicit_user_approval')is True and a.get('approved_launches')==3 and a.get('allowed_cohorts')==sorted(ALLOWED_COHORTS)and a.get('goal')==GOAL and a.get('Source5')==s['source_identity'],'MISSING_FRESH_EXACT_REQUEST3_SCIENTIFIC_AUTHORIZATION')
    need(a.get('request_ref')==ref(ROOT/'control/EXACT_REQUEST.json'),'fresh request identity drift')
    return a
def preclaim_schema(case,binding=None):
    s=engineering_spec_for(case)
    if binding is not None:
        need(binding.get('cohort')==case and binding.get('spec_sha256')==sha(spec_path(case)),'preclaim binding identity')
        s=dict(s,host_cpu=binding['host_cpu']);validate_spec_contract(s,require_bound_cpu=True)
    fresh_science_authorization(s)
    return s


SCOPED_MODES = {'EP_PERF_PFV4_A2_3MM_S_G64W8_V1': 'S', 'EP_PERF_PFV4_A2_3MM_WV_ZERO_RO_G64W8_V1': 'WV_ZERO_RO', 'EP_PERF_PFV4_A2_3MM_WV_ZERO_RO_REF32W8_V1': 'WV_ZERO_RO'}
ALLOWED_COHORTS=frozenset(SCOPED_MODES)
def authorized_scope_mode(s):
    need(s.get('cohort')in SCOPED_MODES and s.get('mode')==SCOPED_MODES[s['cohort']],'outside independent exact2 Source78 scope/mode')
    need(type(s.get('M'))is bool and type(s.get('T'))is bool and(s['M'],s['T'])==((True,True)if s['mode']=='F'else(False,False)),'DRAM scope M/T mismatch')
    return s['mode']

LEDGER = NATIVE / 'control/qualification_ledger'
NATIVE_ROUTE_GUARD_REF={'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v5_20261105_v1/track_d_workloads/three_mm/runtime/native_route_guard_v3.py', 'sha256': 'a915ced04a8ba7aea39eb7cdb055cacd3861244597e837094544471a7111a12d'}
MODE_CONTRACT_SHA='d95d06f07beaf3c469ca1ab0462c942473d19626ad321b2bc906bbbd1ea3858f'
NEW_VALIDATOR_SHA='f6ddde64d52fdd23aefd3ac6432e18d4fedc1e9756f03ad4af0afbe46f795237'
def formal_mode_contract(s):
    need(s['mode_contract_ref']['sha256']==MODE_CONTRACT_SHA and s['validation_module_ref']['sha256']==NEW_VALIDATOR_SHA,'unreviewed formal mapper/parser version')
    return module(s['mode_contract_ref'],'private_formal_mode_contract').validate_static(s)


def spec_path(case):
    need(case.startswith('EP_PERF_') and case.replace('_', '').isalnum() and len(case) < 170, 'invalid cohort')
    need(case in ALLOWED_COHORTS, 'outside exact independent request2 cohort')
    return ROOT / 'cases' / case / 'control/FROZEN_SPEC.json'


def spec_for(case,require_release=True):
   s=engineering_spec_for(case);fresh_science_authorization(s)
   registry,unused=authority();q=registry['registered_future_requests'].get(GOAL)
   need(q is not None,'FRESH_REQUEST2_NOT_REGISTERED')
   need(q['budget']==3==len(q['admitted_specs'])and q['remaining']==3-len(q['consumed']),'fresh exact request2 budget arithmetic')
   need(q['admitted_specs'].get(case)==sha(spec_path(case))and q['authorization_ref']==s['Main_scientific_launch_authorization'],'registered Spec/approval binding')
   need(q['runtime_versions'].get(s['host_engine_ref']['sha256'])==dict(engine_ref=s['host_engine_ref'],common_ref=s['host_common_ref']),'runtime version binding')
   scope=module(s['mode_contract_ref'],'request2_fair_pair');scope.validate_fair_pair(s,read(scope.family_row(s)['peer_accepted_spec_ref']['path'])if scope.family_row(s)['peer_accepted_spec_ref']else read(spec_path(s['same_background_peer_cohort'])))
   for row in scope.family_scope()['points']:
       r=row['accepted_same_mode_ref']
       if r is None:continue
       point=exact(r['accepted_point_ref']);namespace=r.get('request')or point.get('goal',FRONTEND_GOAL)
       accepted=registry['registered_future_requests'][namespace]['consumed'].get(r['cohort'],{})
       need(accepted.get('state')=='CLOSED_ACCEPTED'and accepted.get('accepted_point_ref')==r['accepted_point_ref'],'exact official accepted REF population')
   validate_spec_contract(s)
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
    candidate=engineering_spec_for(case)
    fresh_science_authorization(candidate)
    # No installed receipt => HOLD before spec consumption, resource claims or fork.
    route=read(ROOT/'control/NATIVE_ENTRY_ROUTE_V4.json')
    need(route['goal']==GOAL and route['status']=='MAIN_INSTALLED_ADDITIVE_NATIVE_EP_PERF_ROUTE','native route not Main installed')
    need(route.get('approved_by')=='EP-MAIN' and route.get('scientific_scope_activated')is True,'scope not activated')
    # Immutable exact shared Native pin. Any future route change HOLDs.
    need(route.get('guard_module_ref')==NATIVE_ROUTE_GUARD_REF,'pinned route guard mismatch')
    guard=module(route['guard_module_ref'],'midtag_formal_native_route_guard')
    guard.validate_current(str(ROOT/'control/NATIVE_ENTRY_ROUTE_V4.json'))
    entry=route['entry_ref'];registry,_=authority()
    need(registry['registered_future_requests'][GOAL]['native_entry_ref']==entry,'registered sole-entry mismatch')
    need(P(entry['path'])==P(__file__).with_name('native_request3') and sha(entry['path'])==entry['sha256'],'scoped entry mismatch')
    need(route.get('exact_cohorts')==sorted(ALLOWED_COHORTS),'Native cohort scope mismatch')
    s = spec_for(case, require_release=False)
    input_proof = fresh_input(s)
    for name, commit_field in [('core', 'core_source_commit'), ('framework', 'framework_source_commit')]:
        repo = s['source_worktrees'][name]
        need(subprocess.check_output(['git', '-C', repo, 'rev-parse', 'HEAD'], text=True).strip() == s['source_identity'][commit_field], 'source HEAD drift')
        need(not subprocess.check_output(['git', '-C', repo, 'status', '--porcelain', '--untracked-files=no'], text=True).strip(), 'tracked Source dirty')
    qualification = exact(s['host_qualification_ref'])
    need(qualification['status'] == 'PRIVATE_MAIN_INTEGRATION_ENGINEERING_REVIEW_CANDIDATE', 'host qualification missing')
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
    validate_spec_contract(s,require_bound_cpu=True)
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
