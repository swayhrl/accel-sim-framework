"""One new-source original11 qualification canary, charged to original E40 contingency.

Uses the original E singleton, central lock, resource gate and atomic Popen
journal. This explicitly pending gate control cannot publish a performance
endpoint or confer its own qualification. No normal application admission is
weakened. Source and the one exact checkpoint must first be published in E CLIENT.
"""
import csv
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import uuid

sys.path.insert(0, '/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/util/ep_l2/mechanism_e')
import coordinator as c
import run as legacy
from runner import disable_owned_core_dumps
from headroom_config import options

CHECKPOINT = Path(__file__).with_name('CHECKPOINT.json')


def reserve(coord, checkpoint, checkpoint_path):
    """A single exact published control; no replay, budget refund or fake q."""
    s = checkpoint
    c.require(time.time() < c.START_DEADLINE, 'original start cutoff')
    with coord.locked() as (data, item):
        c.counts(item)
        c.require(s['source_identity'] == item['final_source_identity'], 'wrong control source/campaign')
        controls = item['native_off_controls_by_binary']
        record = controls[s['source_identity']['binary_sha256']]
        binding = record['binding']
        c.require(binding['path'] == str(checkpoint_path.resolve()) and
                  binding['sha256'] == c.digest(checkpoint_path), 'control checkpoint binding changed')
        c.require(s['campaign_id'] == c.CAMPAIGN and s['prepared_by'] == 'E' and
                  s['source_identity'] == item['final_source_identity'], 'wrong control source/campaign')
        selected = item['input_selections']['D_V2_vectorAdd_4M']
        c.require(c.digest(selected['path']) == selected['sha256'] and
                  selected['selection']['full_input_identity']['trace_content_sha256'] ==
                  s['identity']['trace_content_sha256'], 'different preregistered complete control input')
        c.require(not record.get('attempt'), 'one necessary control already reserved; reconcile retained attempt')
        c.require(item['uncertain_start_intents'] == 0 and item['remaining_start_capacity'] > 0,
                  'original40 or uncertain start boundary')
        used = sum(c.policy_v2.charged_bucket(a, item['reservations']) == 'contingency' and
                   (a.get('actual_start') or a['state'] in ('RESERVED', 'START_INTENT_UNRECONCILED'))
                   for a in item['attempts'])
        c.require(used < item['reservations']['contingency'], 'original contingency8 exhausted')
        key = c.run_key(s['identity'])
        c.require(key == s['run_key'] and key not in data['runs'], 'duplicate or wrong control key')
        c.require(s['scientific_performance_endpoint'] is False and s['actual_start_bucket'] == 'contingency',
                  'control is never a performance condition')
        c.require(s['identity']['feature_vector']['finite_wbuf'] is False and
                  s['identity']['workload'] == 'vectorAdd_4M' and
                  s['expected_metrics'] == {'cycle': 73873, 'insn': 56000000}, 'exact original gate only')
        growth = s['maximum_result_bytes']
        c.require(growth == 384*2**20 and s['memory_bytes'] == 4*c.GIB, 'fixed conservative control reservations')
        c.resource_gate(data, 'simulation', 1, s['memory_bytes'], growth, c.local_resources(), c.output_usage())
        aid = f'E{len(item["attempts"])+1:03d}_{uuid.uuid4().hex[:8]}'
        row = dict(attempt_id=aid, run_key=key, identity=s['identity'], selection_id='D_V2_vectorAdd_4M',
                   qualification_id='PENDING_ALL_OFF_CONTROL_'+binding['sha256'], profile='NATIVE_ALL_OFF_CONTROL',
                   comparison_group='QUALIFICATION_ONLY_NOT_PERFORMANCE', budget_bucket='contingency',
                   labels=dict(diagnostic=False, subset='ORIGINAL_OFF_QUALIFICATION_CONTROL', oracle=False),
                   state='RESERVED', actual_start=False, reserved_unix=time.time(),
                   result_directory=str(c.OUTPUT/aid), maximum_result_bytes=growth,
                   qualification_control=True, control_binding=binding, **c.disk_policy.lease_policy(item))
        item['attempts'].append(row)
        record['attempt'] = aid
        data['runs'][key] = dict(run_key=key, identity=s['identity'], owner='mechanism_E',
            host=item['host'], boot_id=item['boot_id'], lease_id=aid, status='RESERVED',
            cpu_units=1, memory_bytes=s['memory_bytes'], scan=False, result_directory=row['result_directory'],
            disk_growth_bytes=growth, experiment_id=c.CAMPAIGN, process=None,
            qualification_control=True, **c.disk_policy.lease_policy(item))
        return row


def preflight(s):
    c.tooling_binding()
    client = json.loads((c.HANDOFF/'CLIENT_CONTRACT.json').read_text())
    b = client['native_off_qualification_controls_by_binary'][s['source_identity']['binary_sha256']]
    c.require(b['entry'] == str(Path(__file__).resolve()) and b['entry_sha256'] == c.digest(__file__) and
              b['checkpoint_sha256'] == c.digest(CHECKPOINT), 'exact E published canary consumer required')
    blob = subprocess.check_output(['git', 'show', b['publication_commit']+':'+b['git_path']],
                                   cwd=client['execution_worktree'])
    c.require(c.digest(__file__) == __import__('hashlib').sha256(blob).hexdigest(), 'canary source publication mismatch')
    c.require(c.digest(s['binary']) == s['source_identity']['binary_sha256'], 'official binary changed')
    c.require(all(s['source_identity'][k] == s['identity'][k] for k in
                  ('core_source_commit','framework_source_commit','binary_sha256')), 'wrong source/binary identity')
    c.require(legacy.asset_manifest(s['configs'], ordered=True) == s['config_manifest'] and
              legacy.asset_manifest(s['trace_files']) == s['trace_manifest'], 'complete control assets changed')
    c.require(legacy.content_hash(s['trace_manifest']) == s['identity']['trace_content_sha256'] and
              legacy.content_hash(dict(ordered_configs=s['config_manifest'], auxiliary_assets=[],
                                       environment=s['environment'])) == s['identity']['runtime_config_sha256'],
              'control identity formula mismatch')
    legacy.validate_config_closure(dict(s, auxiliary_assets=[])); legacy.validate_trace_closure(s)
    effective = options([r['path'] for r in s['configs']])
    c.require(effective.get('-gpgpu_ep_l2_ft_mode', '0') == '0', 'all-OFF FTmode0 required')
    for name in ('tvd_clean', 'tvd_dirty', 'ro_tag_detach', 'ro_line_mshr_bypass', 'diag_copy_free',
                 'diag_l2_data_free', 'ms_observer', 'mq2', 'rg1', 'static_s64'):
        c.require(effective.get('-gpgpu_ep_l2_'+name, '0') == '0', 'new mechanism not OFF: '+name)
    base = Path(s['baseline_directory'])
    c.require(c.digest(base/'run_status.json') == s['baseline_status_sha256'] and
              c.digest(base/'raw.log') == s['baseline_raw_sha256'], 'frozen baseline changed')
    for name, sha in s['csv_sha256'].items(): c.require(c.digest(base/name) == sha, 'baseline CSV changed')
    c.require(len(s['csv_sha256']) == 7 and c.digest(s['parser']['path']) == s['parser']['sha256'], 'exact seven CSV/parser')
    n = s['independent_native_receipt']
    c.require(c.digest(n['path']) == n['sha256'], 'independent current native evidence changed')
    evidence = json.loads(Path(n['path']).read_text())
    c.require(evidence['source_identity'] == s['source_identity'] and len(evidence['tests']) == 24 and
              evidence['status'] == 'E_24_AFFECTED_NATIVE_EXECUTIONS_PASS_PENDING_GATE_REVIEW' and
              all(t['execution_expectation'] == 'PASS' and c.digest(t['raw_log']) == t['raw_log_sha256']
                  for t in evidence['tests']), 'current independent affected24 required')
    review=s['new_producer_identity_review']
    c.require(c.digest(review['path']) == review['sha256'], 'new producer review changed')
    reviewed=json.loads(Path(review['path']).read_text())
    c.require(reviewed['source_identity'] == s['source_identity'] and reviewed['build_logs_and_archive_members_verified']
              and reviewed['old_OFF_not_new_gate'], 'independent exact producer review required')
    old=s['retained_independent_unaffected_native']
    c.require(c.digest(old['path']) == old['sha256'], 'retained independent native changed')
    prior=json.loads(Path(old['path']).read_text())
    c.require(len(prior['tests']) == 40 and all(t['execution_expectation']=='PASS' and
              c.digest(t['raw_log'])==t['raw_log_sha256'] for t in prior['tests']),
              'retained independent40 raw evidence required; does not replace new OFF')


def execute():
    def interrupted(signum, frame):
        raise KeyboardInterrupt('owned qualification control interrupted')
    signal.signal(signal.SIGTERM, interrupted)
    s = json.loads(CHECKPOINT.read_text()); preflight(s)
    disable_owned_core_dumps(); coord = c.Coordinator(); proc = None
    with coord.unique_controller():
        a = reserve(coord, s, CHECKPOINT); out = Path(a['result_directory'])
        status = 'INCOMPLETE'; detail = 'prelaunch incomplete'; peak = 0; start = time.monotonic()
        result = dict(attempt_id=a['attempt_id'], run_key=a['run_key'], identity=a['identity'],
            source_identity=s['source_identity'], qualification_control=True,
            scientific_performance_endpoint=False, independent_acceptance='NOT_A_PERFORMANCE_ACCEPTANCE')
        try:
            out.mkdir(exist_ok=False); c.write_json(out/'input_checkpoint.json', s)
            shutil.copy2(s['binary'], out/'accel-sim.out')
            cmd = [str(out/'accel-sim.out')]
            for i, asset in enumerate(s['configs']):
                dst = out/f'config-{i}.config'; shutil.copyfile(asset['path'], dst)
                c.require(c.digest(dst) == s['config_manifest'][i]['sha256'], 'snapshot config changed')
                cmd += ['-config', str(dst)]
            cmd += ['-trace', next(x['path'] for x in s['trace_files'] if x['name'] == s['entry_trace_name'])]
            (out/'tmp').mkdir(); (out/'cache').mkdir()
            env = dict(os.environ, **s['environment'], TMPDIR=str(out/'tmp'), TMP=str(out/'tmp'),
                       TEMP=str(out/'tmp'), XDG_CACHE_HOME=str(out/'cache'))
            preflight(s)
            with (out/'raw.log').open('xb') as log:
                proc = coord.start_application(a['attempt_id'], cmd, out, env, log, subprocess.Popen)
                c.require(proc is not None, 'native spawn failed')
                result.update(process=c.process_identity(proc.pid), command=cmd)
                c.write_json(out/'ACTUAL_RUNNING.json', dict(result, state='RUNNING'))
                while proc.poll() is None:
                    live = c.local_resources(); usage = c.output_usage()
                    peak = max(peak, legacy.process_tree_rss(proc.pid))
                    incident = c.disk_policy.stop_detail(live, a)
                    if (incident or live['share_disk_free_bytes'] < 40*c.GIB or
                        live['available_memory_bytes'] < 64*c.GIB or peak > s['memory_bytes'] or
                        c.retained_tree_bytes(out) >= s['maximum_result_bytes'] or
                        usage['new_bytes'] >= 6*c.GIB or usage['total_bytes'] >= 20*c.GIB):
                        status='RESOURCE_LIMIT'; detail='own canary resource guard'
                        result['resource_limit'] = dict(incident or {}, resources=live, output_usage=usage,
                            process=result['process'], source_identity=s['source_identity'], run_key=a['run_key'],
                            attempt_id=a['attempt_id'], lease_id=a['attempt_id'], stop_scope='OWNED_PROCESS_GROUP_ONLY')
                        c.write_json(out/'RESOURCE_LIMIT.json', result['resource_limit']); legacy.terminate_owned(proc); break
                    if time.monotonic()-start > s['timeout_seconds'] or time.time() >= c.INTAKE_DEADLINE:
                        status='TIMEOUT'; detail='original bounded control timeout'; legacy.terminate_owned(proc); break
                    time.sleep(a['monitor_interval_seconds'])
            if status not in ('RESOURCE_LIMIT', 'TIMEOUT'):
                c.require(proc.returncode == 0, 'native all-OFF nonzero exit')
                c.require('GPGPU-Sim: *** exit detected ***' in (out/'raw.log').read_text(errors='replace'), 'missing native exit')
                parsed = subprocess.run([sys.executable, s['parser']['path'], str(out/'raw.log'), '--out', str(out),
                    '--framework-commit', s['source_identity']['framework_source_commit'], '--core-commit',
                    s['source_identity']['core_source_commit'], '--source-log', str(out/'raw.log')],
                    cwd=out, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
                (out/'parser.stdout').write_bytes(parsed.stdout); (out/'parser.stderr').write_bytes(parsed.stderr)
                c.require(parsed.returncode == 0, 'frozen native B0 parser failed')
                summary = next(csv.DictReader((out/'target_summary.csv').open()))
                c.require(all(summary[n] == '1' for n in ('invariants_terminal_clean','invariants_payload_consistent')) and
                          summary['slice_count'] == summary['terminal_invariant_records'] == '64', 'all64 closure failed')
                import re
                metrics={}
                for line in (out/'raw.log').open(errors='replace'):
                    m=re.fullmatch(r'gpu_tot_sim_(cycle|insn)\s*=\s*(\d+)\s*',line)
                    if m: metrics[m[1]]=int(m[2])
                result['actual_metrics']=metrics
                c.require(metrics == s['expected_metrics'], 'original all-OFF cycle/instruction regression')
                result['seven_csv_sha256']={name:c.digest(out/name) for name in s['csv_sha256']}
                c.require(result['seven_csv_sha256'] == s['csv_sha256'], 'original all-OFF CSV regression')
                preflight(s); status='COMPLETE_VALID'; detail='original all-OFF native gate PASS, not performance endpoint'
                result['old_all_off_equivalence']='PASS'
        except BaseException as error:
            if status not in ('RESOURCE_LIMIT','TIMEOUT'): status='FAILED'
            detail=repr(error)
        finally:
            if proc: legacy.terminate_owned(proc)
            result.update(status=status, detail=detail, wall_seconds=time.monotonic()-start, peak_rss_bytes=peak,
                          raw_log_sha256=c.digest(out/'raw.log') if (out/'raw.log').exists() else None,
                          exit_code=proc.returncode if proc else None)
            if 'resource_limit' in result:
                result['resource_limit'].update(exit_code=result['exit_code'], raw_log_sha256=result['raw_log_sha256'],
                                                owned_process_retired=proc.poll() is not None)
                c.write_json(out/'RESOURCE_LIMIT.json', result['resource_limit'])
            c.write_json(out/'run_status.json', result)
            with coord.locked() as (data,item):
                row=next(x for x in item['attempts'] if x['attempt_id']==a['attempt_id'])
                c.require(not proc or proc.poll() is not None, 'own child still alive')
                row.update(state=status if row.get('actual_start') else 'CANCELLED_BEFORE_START',
                    finished_unix=time.time(), receipt_path=str(out/'run_status.json'), receipt_sha256=c.digest(out/'run_status.json'))
                data['runs'][a['run_key']].update(status=row['state'], detail=detail, raw_log_sha256=result['raw_log_sha256'])
                item['native_off_controls_by_binary'][s['source_identity']['binary_sha256']]['result']=dict(path=str(out/'run_status.json'),sha256=c.digest(out/'run_status.json'),status=status)
            c.write_json(c.HANDOFF/'events/E_NEW773_ALL_OFF_QUALIFICATION_CONTROL_r1.json', result)
    print(json.dumps(dict(status=status,attempt_id=a['attempt_id'],detail=detail)))


if __name__ == '__main__': execute()
