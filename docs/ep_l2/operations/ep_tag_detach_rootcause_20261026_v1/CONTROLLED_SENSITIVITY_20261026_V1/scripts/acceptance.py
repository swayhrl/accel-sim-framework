#!/usr/bin/env python3
"""Offline terminal acceptance for the finite EP memory-path sensitivity cases."""
import sys
sys.dont_write_bytecode = True
import copy, hashlib, inspect, json, pathlib, re
import experiment_runtime as v
P = pathlib.Path
OLD = P('/root/data/ep_l2_main_vector_r5_20261023_v1')
BASE_UUID = 'a6b61f77-2ff6-45ad-897c-df0812d01ae8'
BASE_OUT = OLD / 'run/results' / BASE_UUID
CORE = '1093d2629e3d6a9130ba25b9dd119b6f3e16c092'
BIN = 'e511cce7d8bcd5a3ebbe6255f42ebe153547484a69c6857ab55f7a8835a2dc33'
FW = '9dd1ee57a83d83b56b7874bc7c716185ab52c8f7'
def need(ok, why):
    if not ok: raise RuntimeError(why)
def canonical(value):
    return ' '.join(str(value).split())
def printed_options(raw):
    result = {}
    for line in P(raw).open(errors='replace'):
        if line.startswith('launching ') or line.startswith('EPL2ROV1|COMMANDLIST_BEGIN'):
            break
        match = re.match(r'^(-[^\s]+)\s+(.*?)\s+#', line)
        if match:
            key, value = match.groups()
            value = canonical(value)
            need(key not in result or result[key] == value, 'conflicting printed option ' + key)
            result[key] = value
    need('-gpgpu_clock_domains' in result and '-gpgpu_cache:dl1' in result, 'printed options missing')
    return result
def permitted_delta(reference, expected, allow_baseline=False):
    delta = {k: {'before':reference.get(k), 'after':expected.get(k)}
             for k in reference.keys() | expected.keys() if reference.get(k) != expected.get(k)}
    if allow_baseline and not delta: return delta
    need(len(delta) == 1, 'exactly one effective option must change: ' + repr(delta))
    if '-gpgpu_clock_domains' in delta:
        before = [float(x) for x in reference['-gpgpu_clock_domains'].split(':')]
        after = [float(x) for x in expected['-gpgpu_clock_domains'].split(':')]
        need(before == [1132.,1132.,1132.,850.] and after == [1132.,1132.,1132.,935.],
             'only E1 DRAM850->935 is authorized')
    elif '-gpgpu_cache:dl1' in delta:
        need(reference['-gpgpu_cache:dl1'] == 'S:4:128:128,L:T:m:L:L,A:512:8,16:0,32' and
             expected['-gpgpu_cache:dl1'] == 'S:4:128:128,L:T:m:L:L,A:512:8,32:0,32',
             'only E2 L1 MissQ16->32 is authorized')
    else: raise RuntimeError('unrecognized sensitivity option ' + repr(delta))
    return delta
def assert_source(source):
    need(source['core_source_commit'] == CORE and source['binary_sha256'] == BIN and
         source['framework_source_commit'] == FW, 'requires exact r5 Core1093/main e511/Framework9dd')
def option_audit(raw, hist, spec, allow_baseline=False):
    historical = {k:canonical(x) for k,x in hist['profile_semantics']['effective_options'].items()}
    expected = dict(historical)
    need(set(spec['expected_effective_options']).issubset(historical), 'unexpected effective option key')
    expected.update({k:canonical(x) for k,x in spec['expected_effective_options'].items()})
    delta = permitted_delta(historical, expected, allow_baseline)
    baseline = printed_options(BASE_OUT/'raw.log')
    actual = printed_options(raw)
    need(set(actual) == set(baseline), 'printed default option population changed')
    actual_delta = {k:{'before':baseline[k], 'after':actual[k]} for k in actual if actual[k] != baseline[k]}
    need(actual_delta == delta, 'actual raw has unexpected/missing option differences: ' + repr(actual_delta))
    for key,value in expected.items():
        need(actual.get(key) == value, 'raw effective option mismatch: ' + key)
    return {'declared_single_option_delta':delta, 'actual_raw_option_delta':actual_delta,
            'printed_option_count':len(actual), 'clock_domains_MHz':actual['-gpgpu_clock_domains'],
            'baseline_raw_sha256':v.sha(BASE_OUT/'raw.log')}
def decode(raw, hist, qualification, spec, native_root, sources=OLD/'sources'):
    """Pure reads and in-memory decoding. Never writes acceptance or legacy assets."""
    assert_source(spec['source_identity'])
    source = P(native_root)/'EP/control/parse_main_terminal.py'
    sys.path[:0] = [str(P(native_root)/'EP/src/owner-control/util/ep_l2/mechanism_e'),
                   str(P(native_root)/'EP/src/owner-control/util/ep_l2/ft_lane5')]
    legacy = v.load(source, '_sensitivity_frozen_model_parser')
    old = inspect.getsource(legacy.parse)
    marker = "    require(qualification['campaign_id']"
    need(old.count(marker) == 1 and old.count('    native={};final={};frames={}') == 1,
         'frozen parser splice contract changed')
    first = old[:old.index(marker)].replace('    policy_v2.combination_qualification(qualification,digest)\n','')
    body = old[old.index('    native={};final={};frames={}'):]
    native_gate = ("    require(qualification['qualified_by']=='EP-MAIN' and qualification['status']=='NATIVE_PRELAUNCH_QUALIFIED_NOT_APPLICATION_ACCEPTED','new EP-MAIN Q required')\n"
                   "    require(all(qualification['source_identity'][n]==identity[n] for n in ('core_source_commit','framework_source_commit','binary_sha256')),'native source identity mismatch')\n")
    joined = first + native_gate + body
    namespace = dict(legacy.__dict__)
    exec(compile(joined, 'EP_MEMORY_PATH_NATIVE_AUTHORITY_MODEL_PARSER', 'exec'), namespace)
    model_spec = copy.deepcopy(hist)
    model_spec['profile_semantics']['effective_options'].update(copy.deepcopy(spec['expected_effective_options']))
    model = namespace['parse'](raw, model_spec, qualification)
    need(model['instructions'] == 56000000 and model['hardware_drained'] is True and model['slices'] == 64,
         'full 56M instruction /64slice/drain closure')
    sys.path.insert(0, str(P(sources)/'r5'))
    r5 = v.load(P(sources)/'r5/decoder.py', '_sensitivity_r5_decoder')
    fixed = v.load(P(sources)/'r4/decoder_samecycle_close.py', '_sensitivity_r4_decoder')
    schema = v.read(P(sources)/'r4/SOURCE_BOUND_SCHEMA_r4.json')
    need(v.sha(P(sources)/'r4/decoder_samecycle_close.py') == r5.FIXED_R4_SHA256, 'fixed r4 SHA mismatch')
    feed = r5.Feed(expected_slices=list(range(64)), registered_slice_count=64, expected_kernels=[1],
                   expected_flags={'T':True,'M':True,'ro_runtime':True}, source_binding=spec['source_identity'],
                   old212_decoder_sha256=r5.FIXED_R4_SHA256)
    with P(raw).open('rb') as stream:
        old212 = fixed.Decoder(schema).decode(r5.TappingReader(stream,feed))
    new = feed.finish(old212)
    need(new['status'] == 'VALID_R5_OBSERVER_DECLARATIONS_ONLY', 'invalid r5 ' + str(new.get('reason')))
    r5.audit_normalized_result(new, old212)
    need(old212['final_cycle'] == new['final_cycle'] == model['cycles'], 'terminal clocks disagree')
    need(new['raw_log_sha256'] == model['raw_log_sha256'] == v.sha(raw), 'decoder raw SHA disagreement')
    ro = model['mechanism_metrics']['full_mechanism_records']['readonly']
    for sid in range(64):
        row = ro.get(sid, ro.get(str(sid)))
        close, prior = row['closure'], row['summary']
        need(close['epoch_closed'] == 1 and
             close['ro_live'] == close['shared_descriptor_used'] == close['shared_line_used'] == prior['live'] == 0,
             'RO closure not drained')
        need(prior['detached'] == old212['slice_counters'][str(sid)]['detach_success'], 'detach syntax/authoritative mismatch')
    ctas = []
    kernels = []
    for line in P(raw).open(errors='replace'):
        match = re.fullmatch(r'gpu_tot_issued_cta\s*=\s*(\d+)\s*', line)
        if match: ctas.append(int(match[1]))
        match = re.fullmatch(r'kernel_name\s*=\s*(\S+)\s*', line)
        if match: kernels.append(match[1])
    need(ctas and ctas[-1] == 15625, 'actual terminal CTA missing/wrong')
    need(new['global_record']['kernel_catalog'] == [1], 'actual kernel catalog must be one UID1')
    authority = {'frozen_parser_sha256':v.sha(source),
                 'frozen_numeric_body_sha256':hashlib.sha256(body.encode()).hexdigest(),
                 'native_authority_parser_sha256':hashlib.sha256(joined.encode()).hexdigest(),
                 'change':'E-controller-only authority preamble replaced; profile/model/numeric body retained; expected case options supplied explicitly',
                 'old_E_qualification_modified':False,
                 'historical_data_scope':'conditional frozen trace-model correctness evidence only; no inherited application acceptance',
                 'numeric_SASS_output_validated':False}
    model['native_authority_binding'] = authority
    model['source_map']['data'] = 'New exact EP-MAIN prelaunch Q plus unchanged conditional trace-model evidence; no E/native application signature inherited'
    return model, old212, new, authority
def put_once(path, obj):
    if P(path).exists(): need(v.read(path) == obj, 'immutable output conflict: ' + str(path))
    else: v.put(path,obj)
def acceptance(case):
    v.bind(case)
    B,N = P(v.B),P(v.N)
    s = v.pins()
    q = v.read(B/'control/NATIVE_PRELAUNCH_QUALIFICATION.json')
    need(q['status'] == 'NATIVE_PRELAUNCH_QUALIFIED_NOT_APPLICATION_ACCEPTED' and q['qualified_by'] == 'EP-MAIN' and
         q['cohort'] == case and q['spec_sha256'] == v.sha(B/'control/FROZEN_SPEC.json'),
         'new exact native prelaunch qualification required')
    assert_source(s['source_identity'])
    need(q['source_identity'] == s['source_identity'], 'Q source mismatch')
    baseline = v.read(BASE_OUT/'CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json')
    need(baseline['uuid'] == BASE_UUID and baseline['status'] == 'EP_NATIVE_VECTOR_R5_DIAGNOSTIC_ACCEPTED',
         'samebinary accepted baseline identity absent')
    assert_source(baseline['source_identity'])
    need(v.sha(BASE_OUT/'raw.log') == baseline['raw_sha256'], 'baseline raw changed')
    oldspec = v.read(OLD/'control/FROZEN_SPEC.json')
    oldenv = {P(path).name:h for path,h in oldspec['env_hashes'].items()}
    for path,h in s['env_hashes'].items():
        if not P(path).name.startswith('config-'):
            need(oldenv.get(P(path).name) == h, 'nonconfig semantic input changed: ' + path)
    need(s['input_trace_composite_sha256'] == oldspec['input_trace_composite_sha256'], 'input composite changed')
    done = v.read(v.LED/(case+'.DONE.json'))
    out = P(done['output'])
    need(out.resolve() == (B/'run/results'/done['uuid']).resolve() and out.resolve() != BASE_OUT.resolve(),
         'output outside exact new case UUID')
    need(v.read(out/'NATIVE_EXIT.json') == done, 'exit receipt differs from ledger DONE')
    need(done['cohort'] == case and done['launcher_wait_returncode'] == 0 and done['stop_reason'] is None and
         done['native_simulator_observed'], 'execution incomplete or stopped')
    need(v.sha(out/'raw.log') == done['raw_sha256'], 'closed raw changed')
    pid = v.read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')
    try:
        need(v.info(pid['pid'])['start_ticks'] != pid['start_ticks'], 'same simulator still alive')
    except FileNotFoundError: pass
    actual = v.read(out/'NATIVE_LAUNCH.json')
    need(actual['source_identity'] == s['source_identity'] and
         actual['spec_sha256'] == v.sha(B/'control/FROZEN_SPEC.json'), 'actual source/spec mismatch')
    for path,h in s['env_hashes'].items():
        need(v.sha(out/P(path).name) == h, 'actual env/input/config changed: ' + path)
    header = (out/'raw.log').open(errors='replace').read(32768)
    need('gpgpu-sim_git-commit-1093d262' in header and 'accelsim-commit-9dd1ee57' in header,
         'actual raw producer build mismatch')
    trace = (out/'actual_file_process_network.log').read_text()
    need('kernel-1.traceg' in trace and 'kernelslist.g' in trace, 'trace-file-open proof missing')
    need('connect(' not in trace and all('ssh' not in x for x in actual['argv']), 'unexpected scientific remote execution')
    need(actual['environment']['EPL2_DETACH_DIAG'] == actual['environment']['EPL2_TAGPRESSURE_DIAG'] == '1',
         'r4/r5 observers not actually enabled')
    histpath = P(s.get('historical_spec_path', B/'control/HISTORICAL_VECTOR_SPEC.json'))
    hist = v.read(histpath)
    opts = option_audit(out/'raw.log', hist, s)
    model,old212,new,authority = decode(out/'raw.log',hist,q,s,N)
    summary = {'schema':'EP_MEMORY_PATH_SENSITIVITY_INDEPENDENT_TERMINAL_JOIN_V1',
               'status':'EP_MEMORY_PATH_SENSITIVITY_CASE_ACCEPTED','cohort':case,'uuid':done['uuid'],
               'source_identity':s['source_identity'],'baseline_uuid':BASE_UUID,'pair':False,
               'native_spec_sha256':v.sha(B/'control/FROZEN_SPEC.json'),
               'historical_spec_reference_only_sha256':v.sha(histpath),
               'raw_sha256':done['raw_sha256'],'cycles':model['cycles'],'instructions':model['instructions'],
               'CTA':15625,'CTA_proof':'actual terminal gpu_tot_issued_cta','slices':64,'kernel_count':1,
               'hardware_drained':True,'effective_option_audit':opts,
               'wall_seconds':done['elapsed_seconds'],'source_disposition':'SOURCE_KEEP',
               'cycles_or_detach_expected_value':False,'writeback_bytes_may_change':True,
               'old_main61_speedup_claim':False,'numeric_SASS_output_validation':'UNKNOWN',
               'qualification_scope':'new finite sensitivity case; same r5 binary/model, no inherited E acceptance'}
    for name,obj in [('MODEL_PARSER_AUTHORITY_REBIND.json',authority),('ACTUAL_EFFECTIVE_OPTION_AUDIT.json',opts),
                     ('terminal_summary.json',model),('R4_212_TERMINAL.json',old212),('R5_TAGPRESSURE_TERMINAL.json',new)]:
        put_once(out/name,obj)
    summary.update(model_summary_sha256=v.sha(out/'terminal_summary.json'),
                   old212_summary_sha256=v.sha(out/'R4_212_TERMINAL.json'),
                   r5_summary_sha256=v.sha(out/'R5_TAGPRESSURE_TERMINAL.json'))
    put_once(out/'CURRENT_ACCEPTED_DIAGNOSTIC_POINT.json',summary)
    put_once(B/'control'/('SCIENCE_QUALIFICATION_'+case+'.json'),summary)
    return summary
def offline_regression():
    """No writes, no new acceptance. Re-decode only the immutable accepted850 raw."""
    oldspec = v.read(OLD/'control/FROZEN_SPEC.json')
    hist = v.read(OLD/'control/HISTORICAL_VECTOR_SPEC.json')
    spec = dict(oldspec,expected_effective_options=hist['profile_semantics']['effective_options'])
    audit = option_audit(BASE_OUT/'raw.log',hist,spec,allow_baseline=True)
    model,_,r5,_ = decode(BASE_OUT/'raw.log',hist,v.read(OLD/'control/NATIVE_PRELAUNCH_QUALIFICATION.json'),
                          spec,P('/root/data/ep_l2_dtc_l1_native_v2'))
    need(model['cycles'] == v.read(BASE_OUT/'terminal_summary.json')['cycles'], 'offline baseline numeric regression')
    return {'status':'OFFLINE_BASELINE_DECODER_REGRESSION_ONLY','new_acceptance_granted':False,
            'cycles':model['cycles'],'r5_status':r5['status'],'raw_sha256':v.sha(BASE_OUT/'raw.log'),
            'option_audit':audit}
if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case',nargs='?')
    parser.add_argument('--offline-regression',action='store_true')
    args=parser.parse_args()
    print(json.dumps(offline_regression() if args.offline_regression else acceptance(args.case),indent=2))

