"""Explicit Main callback. Never import this module to register or dispatch."""
import pathlib,json,hashlib,importlib.util,os,sys,threading,copy,datetime,traceback
P=pathlib.Path
ROOT=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
MARKER='DTC_MAIN_BPF_ENGINEERING_CANARIES_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):
    spec=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def put(p,value):
    p=P(p)
    with p.open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def apply(directory):
    d=P(directory);cfg=read(d/'OWNER_CONFIG.json');main=sys.modules['__main__']
    assert threading.current_thread()is threading.main_thread()
    assert os.getpid()==cfg['owner']['pid']==1498278
    assert int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==cfg['owner']['start_ticks']==977758783
    assert not hasattr(main,MARKER),'OBSERVE_PRIOR_INSTALLATION_DO_NOT_REPEAT'
    for p,h in cfg['source_pins'].items():assert sha(p)==h,p
    frame=sys._current_frames()[main.DTC_L2_MLP_ADDON_THREAD.ident]
    while frame and not(frame.f_code.co_name=='run_scheduler'and P(frame.f_code.co_filename)==ROOT/'tools/l2_ops.py'):frame=frame.f_back
    assert frame is not None
    engine=frame.f_locals['engine'];engine.assert_parent_lease()
    memory=main.DTC_FUTURE_MEMORY_ADMISSION_095_FLOOR10_V1
    aging=memory['aging'];sync=main.DTC_FUTURE_MEMORY_PRIMARY_SCOPE_SYNC_V1;tiny=main.DTC_FUTURE_MEMORY_AGING_FACADE_095_V1
    assert engine is memory['engine']and aging is frame.f_locals['res'].DTC_LARGE_JOB_AGING_INSTALLED and sync.frame is frame
    assert not hasattr(main,'DTC_STRACE_FUTURE_DISPATCH_V2')and not hasattr(main,'DTC_STRACE_BPF_PRIVATE_CONSUMER_V2')
    modules={k:load('main_bpf_'+k,p)for k,p in cfg['modules'].items()}
    scope=modules['scope'].CanaryScope(read(cfg['draft_plan_path']))
    state=dict(frame=frame,engine=engine,memory=memory,aging=aging,sync=sync,modules=modules,
               phase='PREFLIGHT',directory=str(d),new_grants=0,model_starts_by_callback=0)
    setattr(main,MARKER,state)
    originals={};priority_installed=consumer_installed=worker_installed=view_installed=False
    try:
        with aging.lock:
            engine.assert_parent_lease();sync.stable_memory();tiny.guard()
            q=engine.registered()[2]
            assert not any(c not in q['consumed']for c in frame.f_locals['claims']),'DRAIN_PREEXEC_CLAIMS_BEFORE_INSTALL'
            before_q=copy.deepcopy(q);before_scope=sha(ROOT/'control/SCOPE.json');before_matrix=sha(ROOT/'control/MATRIX_CURRENT.json')
            ids={k:id(frame.f_locals[k])for k in ['pool','claims','running','post','registry']}
            protected=aging.state.protected;tokens=copy.deepcopy(aging.state.pending_releases)
            entry_cfg=read(cfg['entry_config_path']);registration_cfg=read(cfg['registration_config_path'])
            store=modules['registration'].EngineeringCanaryRegistry(ROOT,engine,frame,registration_cfg)
            state['store']=store
            authorization=store.expected_authorization();put(d/'MAIN_AUTHORIZATION.json',authorization)
            prepared=store.prepare(authorization);put(d/'REGISTRATION_PREPARED_RECEIPT.json',prepared)
            registration=store.register(authorization);state.update(phase='REGISTERED_EXACT4',new_grants=registration['new_grants'])
            put(d/'REGISTRATION_RECEIPT.json',registration)
            transaction=modules['scope_transaction'].ScopeTransaction(sync,scope,cfg['exclusion_contract_path'],modules['priority'],cfg['source_pins'],cfg['owner'],d/'memory_scope_transactions')
            state['memory_scope_transaction']=transaction
            prepared_memory=transaction.prepare();state['memory_scope_prepared']=str(prepared_memory)
            memory_ack=transaction.apply(prepared_memory);put(d/'MEMORY_SCOPE_RECEIPT.json',memory_ack)
            sync.stable_memory();tiny.guard()
            assert aging.state.protected==protected and aging.state.pending_releases==tokens
            priority_cfg=read(cfg['priority_config_path'])
            producer=modules['producer'];priority_module=modules['priority']
            records={producer.ID:dict(producer.record(entry_cfg),status='ACTIVE',runtime_installation='PENDING_MAIN_SAME_OWNER_CALLBACK'),priority_module.ID:priority_module.record(priority_cfg)}
            def add_overlays(reg):
                row=reg['registered_future_requests'][engine.REQ];old=copy.deepcopy(row)
                for key,value in records.items():assert key not in row['additional_operational_overlays'];row['additional_operational_overlays'][key]=value
                expected=copy.deepcopy(old);expected['additional_operational_overlays'].update(copy.deepcopy(records));assert row==expected
            engine.update_authority(add_overlays);producer.validate(entry_cfg,engine.registered()[2])
            state['phase']='OPERATIONAL_RECORDS_REGISTERED'
            consumer=modules['consumer'];consumer_receipt=consumer.install_on_frame(frame,cfg['entry_config_path'],cfg['exclusion_contract_path'],cfg['exclusion_contract_sha256'],engine.assert_parent_lease)
            consumer_installed=True
            worker_receipt=producer.install_owner_dispatch(frame,cfg['entry_config_path'],consumer.consumer_check)
            worker_installed=True
            adapter=priority_module.Priority(frame,priority_cfg,tiny.coupling['gate'],memory,scope,producer)
            state['priority']=adapter;priority_receipt=priority_module.install(adapter);priority_installed=True
            assert consumer.consumer_check(frame,entry_cfg)is True
            originals=dict(read=frame.f_globals['read'],recommend=frame.f_locals['adaptive'].recommend)
            def current_sources():
                def canonical(c):return engine.canonical(c),sha(ROOT/'control/specs'/(c+'.json'))
                return read(ROOT/'control/MATRIX_CURRENT.json'),read(ROOT/'control/SCOPE.json'),engine.registered()[2],canonical
            reader=modules['scope'].make_dispatch_reader(originals['read'],scope,current_sources,ROOT/'control/MATRIX_CURRENT.json')
            adaptive=modules['scope'].wrap_primary_adaptive(originals['recommend'],scope,current_sources)
            view=reader(ROOT/'control/MATRIX_CURRENT.json');assert reader.last_issue is None
            assert len(view['points'])==len(read(ROOT/'control/MATRIX_CURRENT.json')['points'])+5
            summary=read(ROOT/'analysis/AUTO_SUMMARY.json');history=read(ROOT/'control/SEARCH_HISTORY.json')
            shadow=adaptive(summary,view,history)
            assert adaptive.last_issue is None and not shadow.get('proposals')and shadow.get('scientific_stage_complete')is not True and shadow.get('adoption_ready')is not True
            # The sole live scheduler sees the additional engineering rows only
            # after all physical/consumer/worker/role gates are installed.
            frame.f_globals['read']=reader;frame.f_locals['adaptive'].recommend=adaptive;view_installed=True
            state.update(phase='INSTALLED_PENDING_NATIVE_CANARY',scope=scope,read=reader,adaptive=adaptive,originals=originals,shadow=shadow)
            assert ids=={k:id(frame.f_locals[k])for k in ids}
            assert sha(ROOT/'control/SCOPE.json')==before_scope and sha(ROOT/'control/MATRIX_CURRENT.json')==before_matrix
            assert aging.state.protected==protected and aging.state.pending_releases==tokens
            after=engine.registered()[2];assert after['budget']==before_q['budget']+4 and after['remaining']==before_q['remaining']+4
            assert after['consumed']==before_q['consumed']and all(after['admitted_specs'][c]==h for c,h in before_q['admitted_specs'].items())
            sync.stable_memory();tiny.guard();adapter.active()
            for p,h in cfg['source_pins'].items():assert sha(p)==h
            ack=dict(schema='MAIN_BPF_ENGINEERING_CANARY_OWNER_INSTALL_V1',status=state['phase'],UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner=cfg['owner'],same_runtime_objects=ids,
                budget_before=before_q['budget'],budget_after=after['budget'],new_grants=4,model_starts_by_callback=0,
                private_dispatch_points=len(view['points']),primary_points=len(read(ROOT/'control/MATRIX_CURRENT.json')['points']),primary_matrix_sha256=before_matrix,primary_scope_sha256=before_scope,
                engineering_cohorts=sorted(scope.rows),primary_rollout_policy='NONE',validated_union_authorized=False,
                registration=registration,memory_scope=memory_ack,consumer=consumer_receipt,worker=worker_receipt,priority=priority_receipt,
                source_readback_kind='ACTUAL_164_AND_NATIVE_BYTES_NOT_HTTPS',source_pins=cfg['source_pins'],all_old_consumed_UUIDs_and_specs_preserved=True,
                original_models_signaled=0,protected_R_and_release_tokens_unchanged=True,adaptive_shadow_state=shadow.get('state'),
                next_required='Actual paired native canary activation/full original strict/natural completion/true164 archive/native restore/cycle and host-impact comparison')
            put(d/'ACK.json',ack);put(d/'ADAPTIVE_SHADOW.json',shadow)
            return ack
    except BaseException:
        error=traceback.format_exc();restored=[]
        with aging.lock:
            if view_installed:
                frame.f_globals['read']=originals['read'];frame.f_locals['adaptive'].recommend=originals['recommend'];restored.append('optional engineering dispatch/scientific wrappers')
            if priority_installed:modules['priority'].restore(state['priority']);restored.append('priority')
            if worker_installed:modules['producer'].restore_owner_dispatch();restored.append('future worker')
            if consumer_installed:modules['consumer'].restore_in_owner(engine.assert_parent_lease);restored.append('private consumer')
            state.update(phase='INSTALL_ENGINEERING_HOLD_PRESERVE',error=error,restored=restored)
            put(d/'ERROR.json',dict(traceback=error,restored=restored,new_grants=state['new_grants'],refunds=0,model_starts_by_callback=0,automatic_retry=False,scope_append_preserved=True))
        raise
