"""One-shot independent four-endpoint terminal audit; never an executor/poller.

Read bounded JSON/metadata, existing directory accounting and /proc identities.
No raw/trace content scan, main/archive SHA, launch, acceptance or central write.
Use after terminal notification; IN_PROGRESS explicitly does not infer failure.
"""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,time

HERE=Path(__file__).resolve().parent
PACK=HERE.parent
ROOT=PACK.parents[3]
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c
import runner
import workload_policy as policy

SOURCE_COMMIT='032c7b4135f0ecb9c6f660611a71d9a6fba993c5'
PLAN=PACK/'execution/PRIMARY_FOUR_PLAN.json'
ACTIVE={'RESERVED','START_INTENT_UNRECONCILED','RUNNING'}
TERMINAL={'COMPLETE_VALID','FAILED','TIMEOUT','RESOURCE_LIMIT','INCOMPLETE','FAILED_SPAWN','CANCELLED_BEFORE_START'}
EXPECTED={'FWT_7_21':dict(instructions=791609344,kernels=19),'sgemm':dict(instructions=1658916864,kernels=1)}


def need(ok,message):
    if not ok:raise ValueError(message)


def raw(path,maximum=16*2**20):
    path=Path(path);need(path.stat().st_size<=maximum,'bounded metadata size exceeded: '+str(path))
    return path.read_bytes()


def read(path):return json.loads(raw(path))


def checked(ref):
    value=raw(ref['path']);need(hashlib.sha256(value).hexdigest()==ref['sha256'],'metadata SHA changed: '+ref['path'])
    return json.loads(value)


def published(path,commit=SOURCE_COMMIT):
    path=Path(path);relative=path.relative_to(ROOT).as_posix()
    size=int(subprocess.check_output(['git','cat-file','-s',commit+':'+relative],cwd=ROOT,timeout=15))
    need(size<=16*2**20,'published metadata exceeds bound')
    blob=subprocess.check_output(['git','show',commit+':'+relative],cwd=ROOT,timeout=15)
    need(blob==raw(path),'local metadata differs from published '+relative)
    return dict(commit=commit,path=relative,sha256=hashlib.sha256(blob).hexdigest())


def process_observation(identity):
    if not identity:return dict(recorded_identity=None,same_recorded_process_alive=False,proof='NO_RECORDED_PROCESS')
    need(type(identity.get('pid')) is int and type(identity.get('start_ticks')) is int and bool(identity.get('boot_id')),
         'incomplete PID/start_ticks/boot identity')
    try:current=c.process_identity(identity['pid'])
    except (FileNotFoundError,ProcessLookupError):current=None
    return dict(recorded_identity=identity,current_identity=current,same_recorded_process_alive=current==identity,
                proof='PID_START_TICKS_BOOT_COMPARISON')


def endpoint(state,row,attempt,coord):
    result=dict(condition_id=row['condition_id'],attempt_id=attempt['attempt_id'],profile=row['profile'],
      workload=row['workload'],state=attempt['state'],actual_start=attempt['actual_start'],charged_without_refund=True,
      result_directory=attempt['result_directory'])
    spec=checked(row['spec']);qrow=state['qualifications'][row['qualification_id']];q=checked(qrow)
    need(q==qrow['qualification'] and q['status']=='INDEPENDENTLY_QUALIFIED','qualification not exact independent seal')
    need(q['source_identity']==policy.SOURCE and q['input_selection_id']==spec['selection_id'],'wrong input-specific main61 Q')
    need(attempt['qualification_id']==row['qualification_id']==spec['qualification_id'],'Q identity mismatch')
    need(attempt['identity']==spec['identity'] and attempt['run_key']==row['run_key'],'attempt/source/input spec mismatch')
    need(policy.scope_allowed(state,spec),'full approved spec binding no longer valid')
    result['published_spec']=published(row['spec']['path']);result['published_qualification']=published(qrow['path'])
    result['qualified_labels']=spec['labels'];result['selection_id']=spec['selection_id'];result['comparison_group']=spec['comparison_group']
    result['processes']={name:process_observation(attempt.get(key)) for name,key in
      (('native','process'),('collector','exit_collector_process'))}
    if attempt['state'] in ACTIVE:
        result.update(audit_status='IN_PROGRESS',native_exit_inferred=False);return result
    need(attempt['state'] in TERMINAL,'unknown endpoint lifecycle state')
    directory=Path(attempt['result_directory']);receipt_path=attempt.get('receipt_path')
    result['actual_result_directory_bytes']=c.retained_tree_bytes(directory)
    result['endpoint_hard_cap_bytes']=attempt['maximum_result_bytes']
    if not receipt_path:
        result.update(audit_status='TERMINAL_INCOMPLETE_NO_REGISTERED_RECEIPT',native_exit_inferred=False)
        return result
    receipt=checked(dict(path=receipt_path,sha256=attempt['receipt_sha256']))
    need(receipt['attempt_id']==attempt['attempt_id'] and receipt['run_key']==attempt['run_key'] and
      receipt['identity']==attempt['identity'] and receipt['status']==attempt['state'],'terminal receipt registration mismatch')
    snapshot=read(directory/'input_spec.json');need(policy.spec_sha(snapshot)==policy.spec_sha(spec),
      'execution snapshot differs from exact approved spec')
    need(snapshot['operational_limits_override']==policy.operational_override(spec),'runtime override changed')
    audit=receipt['input_audit'];need(audit['identity']==attempt['identity'],'input audit identity mismatch')
    target=EXPECTED[row['workload']]
    need(audit['expected_full_instructions']==target['instructions'],'full-input expected instruction mismatch')
    need(audit['qualification_sha256']==qrow['sha256'],'input audit wrong own qualification')
    need(audit['effective_options']==spec['profile_semantics']['effective_options'] and
      spec['labels']==spec['profile_semantics']['labels'],'configuration/profile/labels closure mismatch')
    need(audit['parser']==q['terminal_parser']==spec['parser'],'version-specific parser binding mismatch')
    need(hashlib.sha256(raw(spec['parser']['path'])).hexdigest()==spec['parser']['sha256'],'bound parser source changed')
    for index,config in enumerate(audit['configs']):
        need(hashlib.sha256(raw(directory/f'config-{index}.config')).hexdigest()==config['sha256'],
             'executed configuration snapshot changed')
    for asset in audit['auxiliary_assets']:
        need(hashlib.sha256(raw(directory/asset['name'])).hexdigest()==asset['sha256'],
             'executed bounded auxiliary snapshot changed')
    selection=state['input_selections'][spec['selection_id']]
    need(audit['selection_sha256']==selection['sha256'] and checked(selection)==selection['selection'],
         'input selection preregistration binding mismatch')
    declared_traces=[t for t in audit['traces'] if t['name'].startswith('kernel-') and '.trace' in t['name']]
    need(len(declared_traces)==target['kernels'],'closed complete trace manifest kernel count mismatch')
    result.update(receipt=dict(path=receipt_path,sha256=attempt['receipt_sha256']),
      expected_full_instructions=target['instructions'],declared_complete_trace_kernel_count=len(declared_traces),
      kernel_completion_basis='Closed full-input manifest + exact full instructions + normal native exit + all_kernels termination + existing validator; legacy parser has no separate kernel UID completion array',
      native_exit_inferred=False,detail=receipt.get('detail'),wall_seconds=receipt.get('wall_seconds'))
    native_path=directory/'NATIVE_EXIT.json'
    native=None
    if native_path.exists():
        native=read(native_path)
        need(hashlib.sha256(raw(native_path)).hexdigest()==receipt.get('native_exit_receipt_sha256') and
          receipt.get('native_exit_evidence')==native,'durable native exit receipt content mismatch')
        need(native['native_process']==attempt['process'] and native['guardian_process']==attempt['exit_collector_process'],
          'native/collector actual owner identity mismatch')
        need(native['native_ppid']==native['guardian_process']['pid'],'native was not collector direct child')
        ready=read(directory/'NATIVE_EXECUTION_READY.json')
        for key in ('native_process','guardian_process','controller_process','native_ppid','binding'):
            need(ready[key]==native[key],'durable readiness/exit identity mismatch: '+key)
        binding=native['binding']
        need(binding['attempt_id']==attempt['attempt_id'] and binding['run_key']==attempt['run_key'] and
          binding['identity']==attempt['identity'] and binding['qualification_id']==spec['qualification_id'],
          'native exit binding mismatch')
        need(native['controller_process']['boot_id']==native['native_process']['boot_id']==native['guardian_process']['boot_id'],
          'native/collector/controller boot identity mismatch')
        result['processes']['controller']=process_observation(native['controller_process'])
        result['native_exit']=dict(exit_code=native['exit_code'],wait_status=native['wait_status'],
          stop_reason=native['stop_reason'],signal=native.get('signal'),exited_normally=native.get('exited_normally'),
          collection_method=native['collection_method'],released_to_native=native['released_to_native'],
          native_process=native['native_process'],collector=native['guardian_process'],controller=native['controller_process'])
        need(receipt.get('exit_code')==native['exit_code'],'receipt and true native exit disagree')
    if attempt['state'] in ('FAILED','TIMEOUT','RESOURCE_LIMIT'):
        need(native is not None,'actual failed/resource/time exit receipt missing; no exit inferred')
    if attempt['state']!='COMPLETE_VALID':
        need(attempt['attempt_id'] not in state['accepted_results'],'failed endpoint must not be accepted')
        result.update(audit_status='TERMINAL_NEGATIVE_OR_INCOMPLETE_PRESERVED',independent_acceptance=receipt.get('independent_acceptance'),
          resource_limit=receipt.get('resource_limit'),native_exit_receipt_present=native is not None)
        return result
    coord.require_no_hold(state,spec['qualification_id'])
    pointer=state['accepted_results'][attempt['attempt_id']];need(pointer['path']==receipt_path and
      pointer['sha256']==attempt['receipt_sha256'],'accepted receipt pointer mismatch')
    need(receipt['independent_acceptance']=='PASS' and receipt['complete_input_verified'] is True,'not independently accepted')
    need(result['actual_result_directory_bytes']<=attempt['maximum_result_bytes']<=384*2**20,'accepted endpoint hard cap exceeded')
    need(native is not None and native['exit_code']==native['wait_status']==0 and native['stop_reason'] is None and
      native['released_to_native'] is True and native['exited_normally'] is True,'no proven unguarded native exit0')
    summary=receipt['summary'];need(read(directory/'terminal_summary.json')==summary,'terminal summary snapshot mismatch')
    need(summary['instructions']==target['instructions'] and summary['slices']==64 and summary['hardware_drained'] is True,
      'incomplete instruction/slice/hardware drain closure')
    need(summary['workload_termination']['all_kernels'] is True and summary['workload_termination']['normal_exit'] is True,
      'full application termination not closed')
    need(summary['raw_log_sha256']==receipt['raw_log_sha256'],'recorded terminal raw SHA differs; no raw rehash performed')
    validation=runner.validate_terminal_summary(summary,snapshot,qrow,audit)
    need(validation==receipt['validation'] and validation['status']=='PASS','independent existing validator mismatch')
    result.update(audit_status='VERIFIED_ACCEPTED_ENDPOINT',cycles=summary['cycles'],instructions=summary['instructions'],
      slices=64,hardware_drained=True,validation=validation,source_identity=q['source_identity'],
      mechanism_metrics=receipt.get('mechanism_metrics',{}),raw_sha_recorded_not_recomputed=receipt['raw_log_sha256'])
    return result


def audit():
    start=time.time();coord=c.Coordinator();central=read(c.SHARED/'RUN_REGISTRY.json');state=central[c.FIELD]
    errors=[];result=dict(schema='E2_MAIN61_PRIMARY_FOUR_INDEPENDENT_FINAL_AUDIT_V1',at_unix=start,
      status='IN_PROGRESS',audit_errors=errors,original_T0=state['t0_unix'],actual_starts=state['actual_starts'],
      new_application_native_build_goal_or_controller_starts=0,no_registry_lease_or_acceptance_mutation=True,
      no_raw_or_trace_body_read=True,no_main_archive_or_trace_SHA_recomputed=True,peer_ACK_not_inferred=True)
    plan=read(PLAN);result['published_plan']=published(PLAN)
    adoption=read(PACK/'central_adoption/ADOPTION_RECEIPT.json')
    try:
        need(policy.active(state),'approved four-start scope absent')
        need(state['t0_unix']==plan['T0']==1792414193 and state['actual_starts']==50,'original T0 or50 actual charges mismatch')
        new=state['attempts'][46:];need(len(new)==4 and all(a.get('actual_start') is True for a in new),'four actual starts not closed')
        need({a['condition_id'] for a in new}==set(policy.CONDITIONS),'duplicate/extra/missing new condition')
        need(sum(a.get('actual_start') is True for a in state['attempts'])==50,'actual charged recount mismatch')
        need(plan['source_identity']==policy.SOURCE,'same exact main61 source missing')
        need(adoption['runtime_source_binding']==SOURCE_COMMIT,'unexpected central runtime source binding')
        for oldid in ('E011_618407f0','E012_63be0bb4'):
            need(next(a for a in state['attempts'][:46] if a['attempt_id']==oldid)['state']=='INCOMPLETE','old FWT INCOMPLETE changed')
        result.update(old46_prefix_original_matrix_buckets_HOLD_accepted_preserved=True,
          original_contingency_allocation=state['reservations']['contingency'],
          separate_new_batch_charges={b:len(v['attempt_ids']) for b,v in state[policy.FIELD]['batches'].items()})
        source_contract=read(c.HANDOFF/'CLIENT_CONTRACT.json')
        need(source_contract['source_publication_commit']==SOURCE_COMMIT,'active CLIENT publication changed')
        result['CLIENT_source_publication_commit']=SOURCE_COMMIT
    except (ValueError,KeyError,StopIteration) as error:errors.append(dict(scope='central_invariants',error=str(error)))
    endpoints=[]
    for row in plan['conditions']:
        try:
            matches=[a for a in state['attempts'][46:] if a.get('condition_id')==row['condition_id']]
            need(len(matches)==1,'one unique actual attempt required')
            endpoints.append(endpoint(state,row,matches[0],coord))
        except (ValueError,KeyError,FileNotFoundError) as error:
            endpoints.append(dict(condition_id=row['condition_id'],audit_status='AUDIT_EVIDENCE_ERROR',error=str(error)))
            errors.append(dict(scope=row['condition_id'],error=str(error)))
    result['endpoints']=endpoints;pairs=[]
    for wanted in plan['pairs']:
        row=dict(pair_id=wanted['pair_id'],workload=wanted['workload'],status='NOT_CURRENT_ACCEPTED')
        pair=state['accepted_pairs'].get(wanted['pair_id'])
        if pair:
            try:
                need(pair['status']=='CURRENT_ACCEPTED' and pair['nonresearch_config_equal'] is True,'pair not currently accepted')
                need({v['run_key'] for v in pair['endpoints'].values()}=={wanted['left_run_key'],wanted['right_run_key']},'pair endpoint mismatch')
                need(all(v['identity']['binary_sha256']==policy.MAIN61 for v in pair['endpoints'].values()),'mixed binary pair')
                need(all(next(e for e in endpoints if e.get('attempt_id')==pair[k])['audit_status']=='VERIFIED_ACCEPTED_ENDPOINT'
                  for k in ('baseline_attempt_id','variant_attempt_id')),'pair endpoint not independently proven')
                artifact_path=PACK/'execution'/(wanted['pair_id']+'_ACCEPTED_PAIR.json');artifact=read(artifact_path)
                need(artifact['accepted_pair']==pair,'published accepted pair projection differs')
                delivery=read(PACK/'execution'/(wanted['pair_id']+'_D_DELIVERY_RECEIPT.json'))
                need(delivery['status']=='DELIVERED_AFTER_REMOTE_READBACK_NOT_CONSUMPTION_CLAIM' and len(delivery['channels'])==3,'real D delivery proof absent')
                row.update(status='VERIFIED_CURRENT_ACCEPTED_AND_D_DELIVERED',cycles_S=pair['cycles_left'],cycles_F=pair['cycles_right'],
                  ratio_S_over_F=pair['ratio_left_over_right'],publication=published(artifact_path,delivery['remote_publication']),delivery=delivery,
                  analysis_cohort='ORIGINAL_MAIN61_FWT_RESTORATION' if wanted['workload']=='FWT_7_21' else 'INDEPENDENT_SGEMM_EXPLORATION_NOT_ORIGINAL_MAIN_OR_CAPACITY')
            except (ValueError,KeyError,StopIteration,FileNotFoundError) as error:
                row.update(status='PAIR_AUDIT_EVIDENCE_ERROR',error=str(error));errors.append(dict(scope=wanted['pair_id'],error=str(error)))
        pairs.append(row)
    result['pairs']=pairs
    active={g:[r for r in central[g].values() if r.get('experiment_id')==c.CAMPAIGN and r['status'] in c.ACTIVE]
            for g in ('runs','resource_leases')}
    result.update(controller=state['controller'],active_owned_runs_and_leases=active,
      controller_process=process_observation(state['controller'].get('process')))
    usage=c.output_usage();resources=c.local_resources();baseline=read(PACK/'PROPOSAL.json')['baseline']
    result['resource_account']=dict(current=resources,result_usage=usage,
      actual_new_result_growth_since_proposal_bytes=usage['new_bytes']-baseline['new_result_bytes'],
      actual_total_result_growth_since_proposal_bytes=usage['total_bytes']-baseline['total_result_bytes'],
      four_endpoint_result_bytes=sum(e.get('actual_result_directory_bytes',0) for e in endpoints),
      four_endpoint_cap_bytes=1536*2**20,total_approved_proposal_growth_cap_bytes=1778384896,
      new_limit_bytes=10*2**30,total_limit_bytes=24*2**30,
      remaining_new_bytes=state['additional_results_max_bytes']-usage['new_bytes'],
      remaining_total_bytes=state['old_plus_new_results_max_bytes']-usage['total_bytes'],
      cumulative_generation_not_reset_by_migration=True)
    final_states=all(a['state'] in TERMINAL for a in state['attempts'][46:]) and len(state['attempts'][46:])==4
    controller_closed=state['controller']['state']=='STOPPED' and not any(active.values()) and not result['controller_process']['same_recorded_process_alive']
    processes_retired=all(not obs['same_recorded_process_alive'] for e in endpoints for role,obs in e.get('processes',{}).items())
    if final_states and controller_closed:
        if not processes_retired:errors.append(dict(scope='process_retirement',error='recorded native/collector/controller still alive'))
        if usage['new_bytes']>10*2**30 or usage['total_bytes']>24*2**30:
            errors.append(dict(scope='result_generation_budget',error='actual cumulative generated result budget exceeded'))
        result['status']=('TERMINAL_EVIDENCE_ERROR' if errors else 'COMPLETE_PROVEN' if
          all(e['audit_status']=='VERIFIED_ACCEPTED_ENDPOINT' for e in endpoints) and
          all(p['status']=='VERIFIED_CURRENT_ACCEPTED_AND_D_DELIVERED' for p in pairs)
          else 'TERMINAL_NEGATIVE_OR_INCOMPLETE_PRESERVED')
    result.update(all_four_terminal=final_states,controller_and_E_leases_closed=controller_closed,
      all_recorded_processes_retired=processes_retired,elapsed_audit_seconds=time.time()-start)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,default=HERE/'AUDIT.json');args=parser.parse_args()
    need(args.out.resolve().parent==HERE,'audit output must stay in own final_audit directory')
    value=audit();args.out.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:value[k] for k in ('status','actual_starts','all_four_terminal','controller_and_E_leases_closed','audit_errors')}))
