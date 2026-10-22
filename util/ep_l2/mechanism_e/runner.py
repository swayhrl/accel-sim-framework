"""New campaign execution adapter reusing original identity, process and closure tools.

No old scientific pointer is changed. This module can execute only an explicit
E-qualified version and D-preregistered input from the new canonical ledger.
"""
import json
import os
from pathlib import Path
import re
import resource
import shutil
import subprocess
import sys
import time

from coordinator import (Coordinator,CAMPAIGN,OUTPUT,START_DEADLINE,INTAKE_DEADLINE,
 require,digest,run_key,canonical,write_json,local_resources,output_usage,
 retained_tree_bytes,tooling_binding,GIB,SHARED,FIELD,process_identity)
import run as legacy
from headroom_config import options
from validate import validate_summary
from acceptance import load_current_authority,reject_withdrawn,current_manifest
import policy_v2
import capacity_policy
import capacity_validation
import limits_policy
import disk_policy
import durable_exit
import detach_diagnostic_policy as detach_policy
import detach_validation
import immutable_binary_snapshot as binary_sharing


def inspect(spec,coord,launch_check=True):
    tooling_binding()
    item=coord.snapshot();identity=spec['identity'];key=run_key(identity)
    coord.require_no_hold(item,spec['qualification_id'])
    qrow=item['qualifications'][spec['qualification_id']]
    require(digest(qrow['path'])==qrow['sha256'],'E qualification changed')
    q=qrow['qualification'];source=q['source_identity']
    if detach_policy.is_spec(spec):detach_policy.prepare_validator(qrow,spec,digest)
    require(all(identity[n]==source[n] for n in ('core_source_commit','framework_source_commit','binary_sha256')),
            'runtime source/binary identity differs from independent qualification')
    require(spec['vendor_pybind11_commit']==source['vendor_pybind11_commit'],'vendor identity differs')
    require(spec['profile_semantics']==q['supported_profiles'][spec['profile']],'profile scope differs')
    p=spec['profile_semantics']
    require(identity['feature_vector']==p['feature_vector'] and identity['ideal_vector']==p['ideal_vector'],
            'feature/diagnostic vector differs from independently qualified profile')
    require(spec['labels']==p['labels'],'diagnostic/subset/oracle labels differ')
    require(digest(spec['binary'])==identity['binary_sha256'],'binary content changed')
    # Preserve historical withdrawals even though new acceptances have their own ledger.
    reject_withdrawn(identity,current_manifest(load_current_authority()))
    configs=legacy.asset_manifest(spec['configs'],ordered=True)
    assets=legacy.asset_manifest(spec['auxiliary_assets']) if spec['auxiliary_assets'] else []
    traces=legacy.asset_manifest(spec['trace_files'])
    require(legacy.content_hash({'ordered_configs':configs,'auxiliary_assets':assets,
       'environment':spec['environment']})==identity['runtime_config_sha256'],'ordered config/assets/environment changed')
    require(legacy.content_hash(traces)==identity['trace_content_sha256'],'complete trace content changed')
    legacy.validate_config_closure(spec);legacy.validate_trace_closure(spec)
    selection=item['input_selections'][spec['selection_id']]
    require(digest(selection['path'])==selection['sha256'],'D preregistration changed')
    chosen=selection['selection']['full_input_identity']
    require(chosen['trace_content_sha256']==identity['trace_content_sha256'],'different D input')
    require(policy_v2.comparison_allowed(item,chosen,spec,digest),'different D comparison')
    effective=options([x['path'] for x in spec['configs']])
    require(effective==p['effective_options'],'actual final options differ from independent config whitelist')
    # Fixed comparison invariant includes all options except explicitly researched
    # switches, plus environment, aux files, exact runtime, trace and termination.
    changes=p['comparison_variable_options']
    require(all(name.startswith('-gpgpu_ep_l2_') for name in changes),'unexpected non-L2 experimental variable')
    invariant={'source':source,'trace':identity['trace_content_sha256'],'epoch':identity['epoch_range'],
       'termination':identity['termination_contract'],'environment':spec['environment'],'auxiliary_assets':assets,
       'nonresearch_options':{k:v for k,v in effective.items() if k not in changes},
       'comparison_variable_options':sorted(changes)}
    invariant_hash=legacy.content_hash(invariant)
    require(invariant_hash==spec['comparison_invariants_sha256'],'wrong same-condition comparison identity')
    require(spec['parser']==q['terminal_parser'] and digest(spec['parser']['path'])==spec['parser']['sha256'],
            'parser not independently bound to this version')
    timeout=limits_policy.effective_timeout(item,spec)
    require(timeout is None or (type(timeout) is int and 0<timeout<=86400),
            'bounded explicit timeout or exact approved null operational override required')
    intake=capacity_policy.effective_limits(item)['intake_deadline_unix']
    if launch_check and intake is not None:
        require(timeout is not None and time.time()+timeout<=intake,'run could exceed declared result-intake freeze')
    require(all(isinstance(k,str) and isinstance(v,str) for k,v in spec['environment'].items()),'explicit string environment required')
    require(not set(spec['environment']) & {'TMPDIR','TMP','TEMP','XDG_CACHE_HOME'},'temporary/cache destinations are owned workspace output only')
    require(not any(k in spec['environment'] and spec['environment'][k]!='1' for k in
        ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS')),'one CPU must remain one thread')
    return {'identity':identity,'run_key':key,'configs':configs,'auxiliary_assets':assets,'traces':traces,
      'qualification_sha256':qrow['sha256'],'selection_sha256':selection['sha256'],
      'comparison_invariants_sha256':invariant_hash,'comparison_invariants':invariant,
      'effective_options':effective,'expected_full_instructions':chosen['expected_full_instructions'],
      'parser':spec['parser'],'operational_limits':{'effective_timeout_seconds':timeout,
      'effective_intake_deadline_unix':intake,'override':spec.get('operational_limits_override'),
      'frozen_identity_and_qualification_termination_preserved':True}}


def runtime_metrics(raw,expected_options):
    normal=False;metrics={};actual={}
    for line in Path(raw).open(errors='replace'):
        normal|='GPGPU-Sim: *** exit detected ***' in line
        match=re.fullmatch(r'gpu_tot_sim_(cycle|insn)\s*=\s*(\d+)\s*',line)
        if match:metrics[match[1]]=int(match[2])
        match=re.match(r'^\s*(-[A-Za-z0-9_:]+)\s+(.*?)\s*$',line)
        if match and match[1] in expected_options:
            value=match[2].rsplit(' # ',1)[0].strip()
            require(match[1] not in actual or actual[match[1]]==value,'conflicting native option dump')
            actual[match[1]]=value
    require(normal and set(metrics)=={'cycle','insn'},'missing actual complete native exit/counters')
    # All L2 research options and frozen geometry must appear in the native dump.
    scoped={k:v for k,v in expected_options.items() if k.startswith('-gpgpu_ep_l2_') or k in ('-gpgpu_cache:dl2','-gpgpu_cache:dl2_texture_only')}
    require(bool(scoped) and all(actual.get(k)==v for k,v in scoped.items()),'effective native L2 options mismatch/missing')
    return metrics



def validate_terminal_summary(summary,spec,qrow,audit):
    """Only a registered exact new-capacity Q may use the new scoped validator."""
    q=qrow['qualification'];contract=q.get('capacity_diagnostic')
    if detach_policy.is_spec(spec) or q.get('detach_observer_diagnostic') is not None:
        return detach_policy.validation_module(spec).validate_summary(summary,spec,qrow,audit)
    require(not detach_policy.is_scope(summary.get('diagnostic_scope')),'observer summary cannot use legacy validator')
    if contract is None:
        require(not capacity_policy.is_capacity_spec(spec),'capacity spec has no exact new qualification')
        require(summary.get('diagnostic_scope')!='CAPACITY_DIAGNOSTIC_V1','new capacity summary cannot use legacy validator')
        return validate_summary(summary,spec['identity'])
    require(capacity_policy.is_capacity_spec(spec),'capacity qualification requires dedicated diagnostic condition')
    require(spec['qualification_id']==qrow['sha256']==audit['qualification_sha256'] and
            digest(qrow['path'])==qrow['sha256'],'new capacity qualification identity changed')
    capacity_policy.qualification(q,digest)
    scope=contract['validation_scope']
    require(scope['expected_full_instructions']==audit['expected_full_instructions'] and
            scope['input_selection_id']==spec['selection_id'],'capacity exact full input differs')
    return capacity_validation.validate_summary(summary,spec['identity'],scope)

def disable_owned_core_dumps():
    """Bound crash writes of this controller and its children, never other projects."""
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))


def execute(spec,coord):
    disable_owned_core_dumps()
    # Called only by the one live E controller after an explicit ready event.
    item=coord.snapshot();limits=capacity_policy.effective_limits(item)
    require(limits_policy.deadline_open(limits['start_deadline_unix']),'no new complete applications after cutoff')
    timeout=limits_policy.effective_timeout(item,spec)
    audit=inspect(spec,coord);spec=dict(spec,input_audit=audit)
    attempt=coord.reserve_application(spec);directory=Path(attempt['result_directory'])
    created=False;process=None;status='INCOMPLETE';detail='prelaunch snapshot incomplete';result={
      'attempt_id':attempt['attempt_id'],'run_key':attempt['run_key'],'identity':spec['identity'],
      'source_identity':coord.snapshot()['qualifications'][spec['qualification_id']]['qualification']['source_identity'],
      'qualification_id':spec['qualification_id'],'selection_id':spec['selection_id'],
      'profile':spec['profile'],'labels':spec['labels'],'comparison_group':spec['comparison_group'],
      'comparison_invariants_sha256':audit['comparison_invariants_sha256'],'input_audit':audit,
      'status':status,'independent_acceptance':'NOT_ACCEPTED','complete_input_verified':False}
    if detach_policy.is_spec(spec):result['scientific_scope']=spec['scientific_scope']
    started=time.monotonic()
    try:
        directory.mkdir(parents=True,exist_ok=False);created=True
        write_json(directory/'input_spec.json',spec);write_json(directory/'input_audit.json',audit)
        if binary_sharing.enabled(spec):
            binary_sharing.snapshot(coord,spec,attempt,directory,write_json)
        else:
            shutil.copy2(spec['binary'],directory/'accel-sim.out')
        require(digest(directory/'accel-sim.out')==spec['identity']['binary_sha256'],'binary snapshot changed')
        command=[str(directory/'accel-sim.out')]
        for i,asset in enumerate(spec['configs']):
            path=directory/f'config-{i}.config';shutil.copyfile(asset['path'],path)
            require(digest(path)==audit['configs'][i]['sha256'],'config snapshot changed')
            command+=['-config',str(path)]
        for asset in spec['auxiliary_assets']:
            target=directory/asset['name'];require(not target.exists() and target.resolve().is_relative_to(directory),'asset collision/escape')
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(asset['path'],target)
            require(digest(target)==next(v['sha256'] for v in audit['auxiliary_assets'] if v['name']==asset['name']),'aux snapshot changed')
        entry=next(a['path'] for a in spec['trace_files'] if a['name']==spec['entry_trace_name'])
        command+=['-trace',str(Path(entry).resolve())]
        tmp=directory/'tmp';tmp.mkdir();cache=directory/'cache';cache.mkdir()
        environment=os.environ.copy();environment.update(TMPDIR=str(tmp),TMP=str(tmp),TEMP=str(tmp),XDG_CACHE_HOME=str(cache),
           OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1');environment.update(spec['environment'])
        # Every actual launch remains in this single controller process. The
        # journal and real process identity are written while holding original lock.
        with (directory/'raw.log').open('xb') as log:
            process=coord.start_application(attempt['attempt_id'],command,directory,environment,log,
                durable_exit.popen_factory(spec,attempt,audit))
            require(process is not None,'OS refused simulator spawn; failed attempt retained, not charged')
            status='RUNNING';peak=0
            result['execution_stage']='NATIVE_EXECUTION'
            result['process']=process_identity(process.pid)
            while process.poll() is None:
                if durable_exit.STOP.is_set():
                    status,detail='INCOMPLETE','controller termination requested; owned native stop with durable exit receipt'
                    legacy.terminate_owned(process);break
                peak=max(peak,legacy.process_tree_rss(process.pid));resources=local_resources();usage=output_usage()
                disk_stop=disk_policy.stop_detail(resources,attempt)
                if ((timeout is not None and time.monotonic()-started>timeout) or
                    not limits_policy.deadline_open(limits['intake_deadline_unix'])):
                    status,detail='TIMEOUT','predeclared timeout/intake freeze';legacy.terminate_owned(process);break
                if (disk_stop is not None or resources['share_disk_free_bytes']<40*GIB
                    or resources['available_memory_bytes']<64*GIB or peak>spec.get('memory_bytes',8*GIB)
                    or retained_tree_bytes(directory)>=attempt['maximum_result_bytes']
                    or usage['new_bytes']>=limits['additional_results_max_bytes'] or usage['total_bytes']>=limits['old_plus_new_results_max_bytes']):
                    status,detail='RESOURCE_LIMIT','own run stopped at physical/RAM/output guard';
                    result['resource_limit']=disk_stop or dict(status='RESOURCE_LIMIT',reason='RAM_SHARE_OR_RESULT_LIMIT',resources=resources)
                    result['resource_limit'].update(attempt_id=attempt['attempt_id'],lease_id=attempt['attempt_id'],
                        run_key=attempt['run_key'],process=result['process'],source_identity=result['source_identity'],
                        resources=resources,output_usage=usage,stop_scope='OWNED_PROCESS_GROUP_ONLY',
                        native_scientific_acceptance=False)
                    write_json(directory/'RESOURCE_LIMIT.json',result['resource_limit']);legacy.terminate_owned(process)
                    result['resource_limit'].update(exit_code=process.returncode,owned_process_retired=process.poll() is not None,
                        raw_log_sha256=digest(directory/'raw.log'),terminated_unix=time.time())
                    write_json(directory/'RESOURCE_LIMIT.json',result['resource_limit']);break
                time.sleep(attempt.get('monitor_interval_seconds',2))
        result.update(exit_code=process.returncode,peak_process_tree_rss_bytes=peak)
        result['native_exit_evidence']=process.exit_evidence()
        result['native_exit_receipt_sha256']=digest(directory/'NATIVE_EXIT.json')
        native_stop=result['native_exit_evidence'].get('stop_reason')
        if status=='RUNNING' and native_stop:
            status=native_stop['kind'] if native_stop['kind'] in ('TIMEOUT','RESOURCE_LIMIT') else 'INCOMPLETE'
            detail=native_stop['reason']
        if status not in ('TIMEOUT','RESOURCE_LIMIT','INCOMPLETE'):
            require(process.returncode==0,'nonzero actual simulator exit')
            result['execution_stage']='TERMINAL_VALIDATION'
            native=runtime_metrics(directory/'raw.log',audit['effective_options'])
            with (directory/'parser.log').open('xb') as log:
                parsed=subprocess.run([sys.executable,spec['parser']['path'],'--raw',str(directory/'raw.log'),
                    '--out',str(directory/'terminal_summary.json')],cwd=directory,stdout=log,stderr=subprocess.STDOUT,timeout=120)
            require(parsed.returncode==0,'independent terminal parser failed')
            summary=json.loads((directory/'terminal_summary.json').read_text())
            require(summary['cycles']==native['cycle'] and summary['instructions']==native['insn'],'parser/native terminal mismatch')
            require(native['insn']==audit['expected_full_instructions'],'full input instruction closure mismatch')
            qrow=coord.snapshot()['qualifications'][spec['qualification_id']]
            result['validation']=validate_terminal_summary(summary,spec,qrow,audit)
            require(inspect(spec,coord,launch_check=False)==audit,'runtime/source/trace/qualification changed while executing')
            result.update(summary=summary,mechanism_metrics=summary.get('mechanism_metrics',{}),complete_input_verified=True,independent_acceptance='PASS')
            status,detail='COMPLETE_VALID','E accepted exact full input, qualified version and hardware closure'
    except BaseException as error:
        if process is not None:
            try:legacy.terminate_owned(process)
            except Exception as cleanup:result['cleanup_error']=str(cleanup)
        if status not in ('RESOURCE_LIMIT','TIMEOUT'):
            status='INCOMPLETE' if isinstance(error,durable_exit.ExitEvidenceMissing) else 'FAILED'
        detail=f'{type(error).__name__}: {error}'
    finally:
        result.update(status=status,detail=detail,wall_seconds=time.monotonic()-started)
        if created:
            result['raw_log_sha256']=digest(directory/'raw.log') if (directory/'raw.log').exists() else None
            write_json(directory/'run_status.json',result)
        # A failed prelaunch snapshot frees only its own reservation. It is not an
        # actual start and is never silently deleted or overwritten on retry.
        current=next(a for a in coord.snapshot()['attempts'] if a['attempt_id']==attempt['attempt_id'])
        if current['state']=='RUNNING':
            coord.finish_application(attempt['attempt_id'],status,directory/'run_status.json')
            if status=='FAILED':
                # Treat a real native/terminal failure as review-required for
                # that exact version, never as evidence that all science failed.
                # E may subsequently classify an ordinary parser/tool issue and
                # clear this with explicit evidence, without replaying valid raw.
                coord.place_scientific_hold(spec['qualification_id'],attempt['attempt_id'],detail,directory/'run_status.json')
        elif current['state']=='RESERVED':
            with coord.locked() as (data,item):
                row=next(a for a in item['attempts'] if a['attempt_id']==attempt['attempt_id'])
                row.update(state='CANCELLED_BEFORE_START',detail=detail)
                data['runs'][attempt['run_key']].update(status='FAILED',detail=detail)
    return result


def accept_pair(coord,left_id,right_id,pair_id,mechanism="UNSPECIFIED"):
    with coord.locked() as (data,item):
        require(pair_id not in item['accepted_pairs'],'pair already published')
        records=[]
        for attempt_id in (left_id,right_id):
            entry=item['accepted_results'][attempt_id]
            require(digest(entry['path'])==entry['sha256'],'accepted endpoint changed')
            record=json.loads(Path(entry['path']).read_text())
            require(record['status']=='COMPLETE_VALID' and record['independent_acceptance']=='PASS','endpoint not accepted')
            if 'native_exit_evidence' in record:
                native=record['native_exit_evidence'];path=Path(entry['path']).parent/'NATIVE_EXIT.json'
                require(digest(path)==record['native_exit_receipt_sha256'] and
                        json.loads(path.read_text())==native,'accepted native exit evidence changed')
                require(native['exit_code']==0 and native['wait_status']==0 and native['stop_reason'] is None,
                        'accepted native exit is not an unguarded normal exit0')
            require(not detach_policy.is_scope(record.get('scientific_scope')),'observer diagnostic point cannot be S/F pair')
            coord.require_no_hold(item,record['qualification_id'])
            qualified=item['qualifications'][record['qualification_id']]
            require(digest(qualified['path'])==qualified['sha256'],'current qualification withdrawn/changed')
            records.append(record)
        a,b=records
        require(left_id!=right_id and a['profile']!=b['profile'],'two distinct conditions required')
        for name in ('source_identity','selection_id','comparison_group','comparison_invariants_sha256'):
            require(a[name]==b[name],'pair mismatch: '+name)
        require(a['summary']['instructions']==b['summary']['instructions'],'pair complete instructions differ')
        row={'pair_id':pair_id,'campaign_id':CAMPAIGN,'accepted_by':'E','accepted_unix':time.time(),
          'status':'CURRENT_ACCEPTED','baseline_attempt_id':left_id,'variant_attempt_id':right_id,
          'mechanism':mechanism,'comparison_group':a['comparison_group'],'nonresearch_config_equal':True,
          'endpoints':{side:{'attempt_id':rid,**item['accepted_results'][rid]} for side,rid in [('left',left_id),('right',right_id)]},
          'cycles_left':a['summary']['cycles'],'cycles_right':b['summary']['cycles'],
          'ratio_left_over_right':a['summary']['cycles']/b['summary']['cycles'],
          'scope':'same binary/input/nonresearch options/termination; diagnostic/subset/oracle labels retained'}
        item['accepted_pairs'][pair_id]=row
        write_json(coord.handoff/'events'/f'E_TO_D_PAIR_{pair_id}.json',row)
        return row
