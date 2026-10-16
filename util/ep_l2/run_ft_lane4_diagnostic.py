#!/usr/bin/env python3
"""Lane 4 historical-development pilots, using Lane 5's central allocation.

This entry deliberately cannot launch a formal B16 experiment before the
qualified common release is available. Old-parent rows remain separate.
"""
import argparse
import importlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
RESULTS = Path('/workspace/results/ep_l2_ft20261016/lane4')
MODES = {'OFF': (False, False), 'I_META': (True, False), 'I_READ_HIT': (False, True)}
B16_MODES = {'I_WB':{'wb':True,'meta':False,'read_hit':False},
             'I_META':{'wb':False,'meta':True,'read_hit':False},
             'I_READ_HIT':{'wb':False,'meta':False,'read_hit':True},
             'I_WB_META':{'wb':True,'meta':True,'read_hit':False}}
STATS = ['line_mshr_full_block','descriptor_pool_full_block','per_address_cap_block',
         'missq_full_block','l2_to_dram_full_block','wad_full_events',
         'bank_true_conflict_ops','dram_scheduler_full_block','dram_successful_read_bytes',
         'dram_successful_write_bytes']
ALIASES = {k:'c7d_'+k for k in STATS if k != 'bank_true_conflict_ops'}
ALIASES.update(dram_successful_read_bytes='c7e_dram_successful_read_bytes',
               dram_successful_write_bytes='c7e_dram_successful_write_bytes')


def check(condition, detail):
    if not condition: raise ValueError(detail)


def head(p):
    return subprocess.check_output(['git','-C',str(p),'rev-parse','HEAD'],text=True).strip()


def load_tools():
    contract = json.loads(Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text())
    sys.path.insert(0,str(Path(contract['registry_client']).parent))
    registry = importlib.import_module('registry')
    tools = importlib.import_module('run')
    check(tools.digest(contract['registry_client']) == contract['registry_client_sha256'],
          'published Lane 5 client changed')
    return contract, registry, tools


def parse_terminal(raw, vector, require_ft=False):
    normal = False; cycles = instructions = None
    b0, invariants, ideals, ft, ft_terminal = {}, {}, {}, {}, {}
    with Path(raw).open(errors='replace') as stream:
        for line in stream:
            normal |= 'GPGPU-Sim: *** exit detected ***' in line
            m = re.fullmatch(r'gpu_tot_sim_(cycle|insn)\s*=\s*(\d+)\s*',line)
            if m:
                if m[1] == 'cycle': cycles = int(m[2])
                else: instructions = int(m[2])
            if not line.startswith(('EPL2B0V1|','EPL2IDEALV1|','EPL2FTV1|')): continue
            record = dict(x.split('=',1) for x in line.strip().split('|') if '=' in x)
            if 'slice' not in record: continue
            slice_id = int(record['slice'])
            if line.startswith('EPL2FTV1|SUMMARY|'):
                ft[slice_id]=record
            elif line.startswith('EPL2FTV1|TERMINAL|'):
                ft_terminal[slice_id]=record
            elif line.startswith('EPL2B0V1|INVARIANT|') and record.get('kernel_uid') == str(2**64-1):
                invariants[slice_id] = record
            elif record.get('scope') == 'application':
                (ideals if line.startswith('EPL2IDEALV1|') else b0)[slice_id] = record
    check(normal and cycles is not None and instructions is not None,'no native normal terminal')
    check(set(b0) == set(invariants) == set(range(64)),'incomplete 64-slice terminal')
    for row in invariants.values():
        for field in ['line_mshr_used','descriptor_used','wad_live','resident_pending','bypass_live','bank_pending','payload_double_owner']:
            check(int(row[field]) == 0, 'nonempty terminal resource: '+field)
        check(row['terminal_clean']=='1' and row['resident_tag_payload_consistent']=='1','invalid terminal ownership')
    if any(vector.values()):
        check(set(ideals) == set(range(64)),'missing exact ideal terminal schema')
        for row in ideals.values():
            check(int(row['ideal_meta'])==vector['meta'] and int(row['ideal_read_hit'])==vector['read_hit'], 'ideal vector mismatch')
            check(int(row.get('ideal_wb','0'))==vector['wb'],'unexpected WB ideal bit')
            if require_ft:check('ideal_wb' in row,'FT binary did not emit the complete ideal vector')
            if vector['wb']:
                check(row.get('ideal_wb')=='1' and int(row['wb_data_full'])==0,
                      'I_WB capacity refusal survived or mode not emitted')
            if vector['meta']:
                check(all(int(row[k])==0 for k in ['line_mshr_full','descriptor_full','per_address_full']),
                      'I_META capacity refusal survived')
            check(int(row['reference_responses_live'])==0 and int(row['reference_arrivals_live'])==0,
                  'reference lifetime not drained')
        if vector['read_hit']: check(sum(int(r['reads_served']) for r in ideals.values())>0,'read diagnostic never served')
    else:check(not ideals,'all-OFF result emitted an unexpected ideal stream')
    if require_ft:
        check(set(ft)==set(ft_terminal)==set(range(64)), 'missing real finite-WBUF summary/requester terminal stream')
        for row in ft_terminal.values():
            check(row['requester_exact_once']=='1' and row['hardware_drained']=='1', 'invalid actual requester/response closure')
            check(int(row['unique_requesters'])==int(row['responses']), 'requester/response count mismatch')
            check(all(int(row[k])==0 for k in ['requester_live','pending_lower_reads','pending_returns','pending_responses']), 'live finite-WBUF terminal queue')
        for row in ft.values():
            check(row['mode']=='1' and row['wbuf']=='16', 'not the static primary WBUF16 model')
            check(all(int(row[k])==0 for k in ['wb_live','wb_slots','reserved','read_refs']), 'FT lifecycle not drained')
            check(row['ownership_consistent']=='1','FT ownership invalid')
            check(int(row['copy_lines'])==int(row['staging_reads'])==int(row['wb_lower_accept']), 'WB copy/read/accept did not close')
            if vector['wb']:check(row['wbuf_full']=='0','WB data capacity still refused')
            else:check(row['physical_slots']=='1168','non-I_WB changed the physical budget')
    return {'cycles':cycles,'instructions':instructions,'normal_exit':True,
            'terminal_64_slice_closure':'PASS',
            'nonbinding_meta':'PASS' if vector['meta'] else 'NOT_APPLICABLE',
            'nonbinding_wb_data':'PASS' if vector['wb'] else 'NOT_APPLICABLE',
            'reference_kind':'BYTE_VERSION_SYMBOLS_WITH_OPTIONAL_KNOWN_VALUES' if vector['read_hit'] else 'ORDINARY_PATH',
            'limiter_counts':{k:sum(int(row[ALIASES.get(k,k)]) for row in b0.values())
                              if all(ALIASES.get(k,k) in row for row in b0.values()) else None for k in STATS},
            'ft_counts':{k:sum(int(row[k]) for row in ft.values()) for k in ['accepted','wb_lower_accept','wbuf_full','copy_lines','copy_bytes','staging_reads','version_checks','descriptor_responses']} if ft else {},
            'ideal_counts':{k:sum(int(row[k]) for row in ideals.values()) for k in ['reads_served','dependency_wait_attempts','bank_wait_attempts','response_wait_attempts','symbolic_bytes','known_bytes']} if ideals else {}}


def validate_config_whole_file(spec):
    assets={r['name'] for r in spec['auxiliary_assets']}
    for item in spec['configs']:
        tokens=shlex.split(Path(item['path']).read_text(),comments=True)
        check('-config' not in tokens,'nested configuration must be expanded')
        for token in tokens:
            if token.endswith(('.xml','.icnt','.config')):
                check(token in assets,'unaccounted configuration dependency: '+token)


def inspect_baseline(spec,tools):
    # Narrow parser adapter for the real multiline quoted QV100 timing field.
    # Preserve every independent-release, content-hash and lifecycle gate in
    # Lane 5 inspect(); neither inputs nor its release authority are replaced.
    original=tools.validate_config_closure
    tools.validate_config_closure=validate_config_whole_file
    try:return tools.inspect(spec)
    finally:tools.validate_config_closure=original


def validate_b16_variant(spec, tools, api):
    """Consume the real Lane 5 baseline spec/release, never invent a baseline."""
    base=spec['baseline_spec'];baseline_audit=inspect_baseline(base,tools)
    check(base.get('owner')=='lane5' and spec.get('owner')=='lane4', 'baseline/diagnostic owner mismatch')
    check(spec.get('campaign_class')=='B16_IDEAL_DIAGNOSTIC', 'not an R1 diagnostic campaign')
    check(spec.get('baseline_qualified_release_sha256')==baseline_audit['qualified_release_sha256'], 'frozen R1 qualification changed')
    identity=spec['identity'];parent=base['identity']
    check(set(identity['ideal_vector'])=={'wb','meta','read_hit'} and
          all(type(v) is bool for v in identity['ideal_vector'].values()), 'ideal vector requires exact boolean fields')
    check(spec['mode'] in B16_MODES and identity['ideal_vector']==B16_MODES[spec['mode']], 'unadmitted ideal vector')
    check(identity['workload'] in {'convolutionSeparable','FWT_7_21','vectorAdd_4M','sad'},'not a first-wave workload')
    check(spec['mode']!='I_WB_META' or identity['workload'] in {'convolutionSeparable','FWT_7_21'},'combination not scheduled for this workload')
    for field in ['core_source_commit','framework_source_commit','binary_sha256','trace_content_sha256','workload','epoch_range','feature_vector','termination_contract']:
        check(identity[field]==parent[field],'unrelated baseline/diagnostic identity change: '+field)
    check(parent['feature_vector']['wbuf_entries']==16 and parent['feature_vector']['finite_wbuf'] and
          not any(parent['feature_vector'][k] for k in ['unified_wb','tvd','ro','adaptive_policy']), 'primary static B16 required')
    check(spec['binary']==base['binary'] and spec['auxiliary_assets']==base['auxiliary_assets'] and
          spec['environment']==base.get('environment',{}) and spec['trace_files']==base['trace_files'], 'baseline physical inputs changed')
    check(spec['configs'][:-1]==base['configs'],'ideal must append one vector overlay to the exact baseline inputs')
    tokens=shlex.split(Path(spec['configs'][-1]['path']).read_text(),comments=True)
    expected={'-gpgpu_ep_l2_ideal_wb':str(int(identity['ideal_vector']['wb'])),
              '-gpgpu_ep_l2_ideal_meta':str(int(identity['ideal_vector']['meta'])),
              '-gpgpu_ep_l2_ideal_read_hit':str(int(identity['ideal_vector']['read_hit']))}
    check(len(tokens)==6 and dict(zip(tokens[::2],tokens[1::2]))==expected,'overlay changes more than ideal bits')
    configs=tools.asset_manifest(spec['configs'],ordered=True)
    assets=tools.asset_manifest(spec['auxiliary_assets']) if spec['auxiliary_assets'] else []
    check(identity['runtime_config_sha256']==tools.content_hash(
        {'ordered_configs':configs,'auxiliary_assets':assets,'environment':spec.get('environment',{})}),
        'derived diagnostic runtime config identity mismatch')
    check(spec['baseline_run_key']==api.run_key(parent),'baseline key binding changed')
    check(all(not v for v in parent['ideal_vector'].values()),'baseline contains an ideal relaxation')
    binary=Path(spec['binary']).read_bytes()
    check(all(flag.encode() in binary for flag in expected),'qualified common binary lacks Lane 4 registrations; request integration first')
    release=json.loads(Path(base['qualified_release']).read_text())
    check(tools.digest(base['qualified_release'])==baseline_audit['qualified_release_sha256'], 'R1 qualification changed during inspection')
    gate=release.get('ideal_gates',{}).get(spec['mode'],{})
    check(gate.get('status')=='PASS' and gate.get('production_driven') is True and
          gate.get('ideal_vector')==identity['ideal_vector'], 'requested ideal mode not independently qualified by Lane5')
    check(tools.digest(gate['evidence_path'])==gate['evidence_sha256'], 'ideal qualification evidence changed')
    return {'baseline_run_key':spec['baseline_run_key'],
            'baseline_identity':parent,
            'qualified_release_sha256':baseline_audit['qualified_release_sha256'],
            'ideal_gate':gate}


def prepare(args, client, api, tools):
    # Reuse the original frozen trace roster without modifying its source tree.
    sys.path.insert(0,str(ROOT/'util/ep_l2'))
    history = importlib.import_module('run_target_baseline')
    trace = dict(history.ROSTER)[args.workload]
    core = Path(args.core).resolve()
    build_manifest = json.loads(Path(args.build_manifest).read_text())
    subprocess.run(['git','-C',str(core),'diff','--exit-code',
                    build_manifest['core_source_commit'],'HEAD','--','src','libcuda','libopencl'],check=True)
    check(build_manifest['binary_sha256'] == tools.digest(args.binary), 'binary/build manifest mismatch')
    # Evidence/runner commits may follow the producing commit; simulator source
    # must still be identical. Keep runner and compiled source identities separate.
    subprocess.run(['git','-C',str(ROOT),'diff','--exit-code',
                    build_manifest['framework_source_commit'],'HEAD','--','gpu-simulator'],check=True)
    mode = MODES[args.mode]
    check(not subprocess.check_output(['git','-C',str(core),'status','--porcelain','--untracked-files=no'],text=True), 'dirty Core source')
    check(not subprocess.check_output(['git','-C',str(ROOT),'status','--porcelain','--untracked-files=no'],text=True), 'dirty Framework source')
    subprocess.run(['git','-C',str(core),'merge-base','--is-ancestor','1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e',head(core)],check=True)
    check('-gpgpu_ep_l2_ft_mode' not in (core/'src/gpgpu-sim/gpu-sim.cc').read_text(),
          'historical-only adapter cannot silently operate a new finite-WBUF source')
    config_paths = [core/'configs/tested-cfgs/SM7_QV100/gpgpusim.config',
                    ROOT/'gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config',
                    ROOT/'tests/ep_l2/b0_banked_d512_850.config',
                    ROOT/'tests/ep_l2/ft_lane4'/({'OFF':'ideal_off','I_META':'ideal_meta','I_READ_HIT':'ideal_read_hit'}[args.mode]+'.config')]
    configs = [{'name':f'config-{i}.config','path':str(p)} for i,p in enumerate(config_paths)]
    assets = {}
    for p in config_paths:
        # The actual QV100 config has a quoted DRAM-timing value spanning two
        # physical lines. Tokenize the complete file, as the config parser does.
        tokens = shlex.split(p.read_text(),comments=True)
        check('-config' not in tokens,'nested configuration requires explicit expansion')
        for token in tokens:
            if not token.endswith(('.xml','.icnt','.config')): continue
            q = next((root/token for root in [p.parent,core/'configs/tested-cfgs/SM7_QV100',ROOT/'gpu-simulator/configs/tested-cfgs/SM7_QV100'] if (root/token).is_file()),None)
            check(q is not None,'missing auxiliary input '+token)
            assets[token]={'name':token,'path':str(q.resolve())}
    files = [{'name':trace.name,'path':str(trace)}]
    for line in trace.read_text().splitlines():
        line=line.strip()
        if line.startswith('kernel-'): files.append({'name':line,'path':str(trace.parent/line)})
    environment={'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
    spec={'binary':str(Path(args.binary).resolve()),'configs':configs,'auxiliary_assets':list(assets.values()),
          'trace_files':files,'entry_trace_name':trace.name,'environment':environment,
          'campaign_class':'HISTORICAL_DIAGNOSTIC','mode':args.mode,'timeout_seconds':args.timeout,
          'lane5_dependency':client,'core_worktree':str(core),'owner':'lane4'}
    spec['build_manifest'] = build_manifest
    spec['runner_source_commit'] = head(ROOT)
    cm=tools.asset_manifest(configs,ordered=True);am=tools.asset_manifest(spec['auxiliary_assets']) if assets else []
    tm=tools.asset_manifest(files)
    spec['identity']={'core_source_commit':build_manifest['core_source_commit'],
        'framework_source_commit':build_manifest['framework_source_commit'],
        'binary_sha256':tools.digest(spec['binary']),
        'runtime_config_sha256':tools.content_hash({'ordered_configs':cm,'auxiliary_assets':am,'environment':environment}),
        'trace_content_sha256':tools.content_hash(tm),'workload':args.workload,
        'epoch_range':{'scope':'full_application','campaign_class':'HISTORICAL_DIAGNOSTIC'},
        'feature_vector':{'finite_wbuf':False,'unified_wb':False,'tvd':False,'ro':False,'adaptive_policy':False,
                          'wbuf_entries':0,'payload_capacity_per_slice':1152,'bank_count':4,'ops_per_bank_cycle':1},
        'ideal_vector':{'wb':False,'meta':mode[0],'read_hit':mode[1]},
        'termination_contract':{'normal_exit':True,'hardware_resource_drain':'64-slice B0 and ideal response/arrival closure',
                                'numeric_application_validation':'NOT_AVAILABLE_FROM_SASS_DATALESS_TRACE'}}
    tools.validate_trace_closure(spec)
    return spec, {'configs':cm,'assets':am,'traces':tm}


def execute(spec,audit,client,api,tools):
    formal=spec['campaign_class']=='B16_IDEAL_DIAGNOSTIC'
    qualification=validate_b16_variant(spec,tools,api) if formal else None
    if not formal:
        check(spec['campaign_class']=='HISTORICAL_DIAGNOSTIC' and
              spec['identity']['feature_vector']['finite_wbuf'] is False,
              'unknown campaign cannot fill a B16 cell')
    check(tools.digest(spec['binary'])==spec['identity']['binary_sha256'],'prepared binary changed')
    check(tools.asset_manifest(spec['configs'],ordered=True)==audit['configs'],'prepared configs changed')
    check(tools.asset_manifest(spec['trace_files'])==audit['traces'],'prepared traces changed')
    check((tools.asset_manifest(spec['auxiliary_assets']) if spec['auxiliary_assets'] else [])==audit['assets'],'prepared auxiliary inputs changed')
    key=api.run_key(spec['identity']);directory=RESULTS/('b16_diagnostic' if formal else 'historical_diagnostic')/key
    registry=api.Registry(client['canonical_root'])
    try:
        fresh,row=registry.claim(spec['identity'],'lane4',directory)
    except ValueError as error:
        return {'status':'NOT_RUN_QUOTA_OR_ADMISSION','detail':str(error),
                'run_key':key,'identity':spec['identity'],'reserved':False}
    if not fresh: return {'status':'DUPLICATE_NOT_LAUNCHED','existing':row}
    process=None;status='INCOMPLETE';detail='not launched';started=time.monotonic();result={
        'identity':spec['identity'],'run_key':key,'campaign_class':spec['campaign_class'],'mode':spec['mode'],
        'runner_execution_commit':head(ROOT),'parser_source_sha256':tools.digest(__file__)}
    if formal:result['matched_baseline']=qualification
    try:
        directory.mkdir(parents=True,exist_ok=False)
        api.write_json(directory/'input_spec.json',spec);api.write_json(directory/'input_audit.json',audit)
        binary=directory/'accel-sim.out';shutil.copyfile(spec['binary'],binary);binary.chmod(0o755)
        check(tools.digest(binary)==spec['identity']['binary_sha256'],'binary snapshot mismatch')
        command=[str(binary)]
        for item in spec['configs']:
            target=directory/item['name'];shutil.copyfile(item['path'],target);command+=['-config',str(target)]
            check(tools.digest(target)==next(r['sha256'] for r in audit['configs'] if r['name']==item['name']),'config snapshot mismatch')
        for item in spec['auxiliary_assets']:
            target=directory/item['name'];shutil.copyfile(item['path'],target)
            check(tools.digest(target)==next(r['sha256'] for r in audit['assets'] if r['name']==item['name']),'auxiliary snapshot mismatch')
        trace=next(r['path'] for r in spec['trace_files'] if r['name']==spec['entry_trace_name'])
        command+=['-trace',trace];api.write_json(directory/'COMMAND.json',command)
        env=os.environ.copy();env.update(spec['environment'])
        policy=registry.snapshot()['hosts'][row['host']];peak=0
        with (directory/'raw.log').open('xb') as log:
            process=subprocess.Popen(command,cwd=directory,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            registry.update(key,row['lease_id'],'RUNNING',process=api.process_identity(process.pid))
            while process.poll() is None:
                peak=max(peak,tools.process_tree_rss(process.pid));live=api.local_resources()
                if time.monotonic()-started>spec['timeout_seconds']:
                    status='TIMEOUT';detail='own diagnostic deadline';tools.terminate_owned(process);break
                if (peak>row['memory_bytes'] or (directory/'raw.log').stat().st_size>policy['default_run_output_limit_bytes'] or
                    tools.tree_bytes(tools.RESULT_ROOT)>policy['max_result_bytes'] or live['disk_free_bytes']<policy['min_disk_free_bytes'] or
                    live['available_memory_bytes']<policy['min_available_memory_bytes']):
                    status='RESOURCE_LIMIT';detail='shared policy threshold';tools.terminate_owned(process);break
                time.sleep(1)
        result.update(exit_code=process.returncode,peak_rss_bytes=peak)
        if status not in {'TIMEOUT','RESOURCE_LIMIT'}:
            check(process.returncode==0,'nonzero process exit')
            result['summary']=parse_terminal(directory/'raw.log',spec['identity']['ideal_vector'],require_ft=formal)
            check(tools.digest(spec['binary'])==spec['identity']['binary_sha256'],'original binary changed')
            check(tools.asset_manifest(spec['configs'],ordered=True)==audit['configs'],'config changed')
            check(tools.asset_manifest(spec['trace_files'])==audit['traces'],'trace content changed')
            check((tools.asset_manifest(spec['auxiliary_assets']) if spec['auxiliary_assets'] else [])==audit['assets'],'auxiliary content changed')
            if formal:validate_b16_variant(spec,tools,api)
            status='COMPLETE_VALID';detail='B16_IDEAL_DIAGNOSTIC; not implementation speedup or strict mathematical bound' if formal else 'HISTORICAL_DIAGNOSTIC_ONLY; never a B16 result'
    except BaseException as error:
        if process is not None:tools.terminate_owned(process)
        status='FAILED';detail=f'{type(error).__name__}: {error}'
    finally:
        result.update(status=status,detail=detail,wall_seconds=time.monotonic()-started,result_directory=str(directory))
        if directory.exists():
            if (directory/'raw.log').exists():result['raw_log_sha256']=tools.digest(directory/'raw.log')
            api.write_json(directory/'run_status.json',result)
        registry.update(key,row['lease_id'],status,detail=detail,exit_code=process.returncode if process else None,raw_log_sha256=result.get('raw_log_sha256'))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--core');p.add_argument('--binary')
    p.add_argument('--build-manifest')
    p.add_argument('--workload',choices=['convolutionSeparable','FWT_7_21','vectorAdd_4M','sad'])
    p.add_argument('--mode',choices=MODES);p.add_argument('--timeout',type=int,default=1800)
    p.add_argument('--prepare-only',action='store_true')
    p.add_argument('--execute-prepared',type=Path)
    a=p.parse_args();client,api,tools=load_tools()
    if a.execute_prepared:
        frozen=json.loads(a.execute_prepared.read_text());spec,audit=frozen['spec'],frozen['audit']
    else:
        check(all([a.core,a.binary,a.build_manifest,a.workload,a.mode]),'prepare needs core/binary/build-manifest/workload/mode')
        spec,audit=prepare(a,client,api,tools)
    if a.prepare_only:print(json.dumps({'run_key':api.run_key(spec['identity']),'spec':spec,'audit':audit},indent=2));return
    result=execute(spec,audit,client,api,tools);print(json.dumps(result,indent=2))
    if result['status'] not in {'COMPLETE_VALID','DUPLICATE_NOT_LAUNCHED'}:raise SystemExit(1)


if __name__=='__main__':main()
