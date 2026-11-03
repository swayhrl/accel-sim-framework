"""Inert Main-only archive daemon installer. Import performs no actions.

No worker/consumer/aging reference is replaced. No authority update API exists
here. A separate Root source-bound approval receipt is mandatory for apply().
"""
import datetime, fcntl, hashlib, importlib.util, json, os, pathlib, sys, threading, time
P=pathlib.Path
ID='DTC_MAIN_NEGATIVE_ARCHIVE_AUTOCLOSE_OWNER_V3'
CERT='DTC_MAIN_NEGATIVE_ARCHIVE_CLOSURE_CERTIFICATE_V2'
MARKER='DTC_STRACE_BROAD_SHARED_PRIVATE_CONSUMER_V1'
REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
ROOT=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
H_SHA='37dc9021ab6cc016acc13017c65b78cacc2a72af413f4497e41356b63eb6904e'
BRIDGE_SHA='33b56779a9451d7fc449f78851475021c989bb4a10b83c95cf0d685953e8c517'
OPS_SHA='a53f4933d2f0a7479a15d0e6dd8aa0501c4762d6b2161363b9467472a43fc1dc'
RESULTS_SHA='6cc6cc30a71740df951327414d094953effb73a406e7036358ad0b702ebb0403'
IO_PUT_PATH=ROOT/'control/operational_amendments/shared_json_io_v1/shared_json_io.py'
IO_PUT_SHA='59d7ea79e05fd26bb23bc46c73e35aff50ce0ea7831ffa9c162cec94c3ed8973'
REQUIRED_PINS={str(ROOT/'tools/l2_results.py'):RESULTS_SHA,str(ROOT/'tools/l2_outbox.py'):'d4b58b362a39c9d198a40e5c252f6eb07ba780e4707ffd79f6724569e349c4a5',str(ROOT/'control/operational_amendments/broad_shared_cpu_v1/consumer_bridge.py'):BRIDGE_SHA,'/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_native_cap1m.py':'fb246ce610a76a21ae86b36730283fa9fdd9f5d21e35fd76e2db17847f2b247d','/root/data/dtc_main_v100_sweep_20261025_v1/tools/runtime_policy_wall90_v1.py':'d1a3f21ce1c9eac89b8428f0732000d81936577d080b7bcf1c48ebe38980f187'}
REQUIRED_PINS[str(IO_PUT_PATH)]=IO_PUT_SHA
INITIAL={'E2-DTCL2MLP-ddb6806316876a85-CH-P0-V1':'98d83595-84a4-43de-8e4b-472df204e8b5','E2-DTCL2MLP-09f94fcc7494a03b-DH-E768-IR1-V1':'eda14f50-7a15-4f54-b038-e5a6a3ddd593'}
def require(v,m):
    if not v:raise RuntimeError(ID+':'+m)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def object_sha(value):return hashlib.sha256((json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()).hexdigest()
def callback_descriptor(callback):
    code=getattr(callback,'__code__',None);require(code is not None,'CALLBACK_CODE_MISSING')
    return dict(file=code.co_filename,sha256=sha(code.co_filename),qualname=callback.__qualname__,freevars=list(code.co_freevars))
def validate_callback_sources(oldarchive,oldput):
    """Allow only the actual qualified 59d7 -> exact original 6cc put chain."""
    archive=callback_descriptor(oldarchive);wrapper=callback_descriptor(oldput)
    require(archive==dict(file=str(ROOT/'tools/l2_results.py'),sha256=RESULTS_SHA,qualname='archive_closed',freevars=[])and oldarchive.__closure__ is None,'ORIGINAL_ARCHIVE_SOURCE')
    require(wrapper==dict(file=str(IO_PUT_PATH),sha256=IO_PUT_SHA,qualname='install_private_module.<locals>.put',freevars=['original_put']),'EXACT_IO_PUT_WRAPPER_SOURCE')
    closure=oldput.__closure__;require(closure is not None and len(closure)==1,'IO_PUT_CLOSURE_SHAPE')
    target=closure[0].cell_contents;leaf=callback_descriptor(target)
    require(leaf==dict(file=str(ROOT/'tools/l2_results.py'),sha256=RESULTS_SHA,qualname='put',freevars=[])and target.__closure__ is None,'ORIGINAL_PUT_TARGET_SOURCE')
    return dict(archive=archive,put_callback_chain=dict(wrapper=wrapper,original_target=leaf))
def callback_certificate_fields(sources):
    chain=sources['put_callback_chain']
    return dict(original_archive_source_sha256=sources['archive']['sha256'],original_put_source_sha256=chain['wrapper']['sha256'],original_put_source_path=chain['wrapper']['file'],original_put_target_source_sha256=chain['original_target']['sha256'],original_put_target_source_path=chain['original_target']['file'],put_callback_chain=chain)
def closure_paths(root,c):
    root=P(root)/'analysis'
    return root/(c+'.NEGATIVE_ARCHIVE_CLOSURE_CERTIFICATE.json'),root/(c+'.POSTPROCESS_PENDING_RESOLUTION.json')
def negative_result(value,c,uuid):
    require(value.get('state')=='FAIL_L2MLP_ARCHIVED_NO_RETRY'and value.get('cohort')==c and value.get('uuid')==uuid and value.get('cycles')is None and value.get('proof',{}).get('performance_accepted')is False,'EXISTING_RESULT_NOT_EXACT_NEGATIVE')
def exclusive(p,v):
    """Durable complete JSON publication; never overwrites a visible target."""
    p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_name('.'+p.name+'.'+os.urandom(8).hex()+'.writing')
    try:
        with tmp.open('x')as f:json.dump(v,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
        os.link(tmp,p);tmp.unlink();fd=os.open(p.parent,os.O_RDONLY)
        try:os.fsync(fd)
        finally:os.close(fd)
    finally:
        if tmp.exists():tmp.unlink()
def refs(main,m):
    f=m['frame'];l=f.f_locals;consumer=m['consumer'];res=l['res'];aging=m['aging'];b=m['bridge']
    values=[m,f,l['engine'],l['consumer'],l['claims'],l['pool'],l['running'],l['post'],res,aging,aging.lock,aging.original,aging.frame_provider,aging.state,aging.state.advance,res.choose_dispatch,res.resources,f.f_globals['worker'],m['wrapper'],b,b['selected'],*b['original_refs'],consumer.safe_finish,consumer.finish_evidence,consumer.put,consumer.archive_closed,consumer.load]
    for k in ['adaptive','registry']: 
        if k in l:values.append(l[k]);values.append(getattr(l[k],'recommend'if k=='adaptive'else'extend'))
    return tuple(id(v)for v in values)
def load(path):
    sp=importlib.util.spec_from_file_location('_negative_archive_pinned_H',path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def validate_approval(cfg,cfg_sha,approval):
    require(approval['schema']==ID+'_ROOT_APPROVAL'and approval['approved']is True,'ROOT_APPROVAL_ABSENT')
    require(approval['configuration_sha256']==cfg_sha and approval['source_sha256']==cfg['source_sha256'],'APPROVAL_SOURCE_CFG_MISMATCH')
    require(approval['request']==REQ and approval['owner']==cfg['owner'],'APPROVAL_OWNER_REQUEST_MISMATCH')
    require(approval['archive_only']is True and approval['new_grants']==0 and approval['model_retries']==0,'APPROVAL_SCOPE')
    require(approval['qualification_sha256']==cfg['qualification_sha256']and approval['source_readback_sha256']==cfg['source_readback_sha256'],'APPROVAL_QA_READBACK')
    require(approval.get('qualification_only')is False,'PRIVATE_APPROVAL_CANNOT_INSTALL')
    require(approval.get('poststage_gates_installed')is True,'POSTSTAGE_GATES_NOT_ATTESTED')
def eligible(root,q,c,selected):
    if q.get('request')!=REQ or c not in q.get('admitted_specs',{}):return False
    row=q.get('consumed',{}).get(c);d=(row or{}).get('execution_receipt')
    if not isinstance(d,dict)or not(d.get('stop_reason')or d.get('launcher_wait_returncode')):return False
    if not d.get('uuid')or d.get('uuid')!=row.get('uuid')or d.get('cohort')!=c:return False
    if c in INITIAL and row['uuid']!=INITIAL[c]:return False
    rp=P(root)/'analysis'/(c+'.RESULT.json')
    if rp.exists():
        value=read(rp)
        if not(value.get('state')=='FAIL_L2MLP_ARCHIVED_NO_RETRY'and value.get('cohort')==c and value.get('uuid')==row['uuid']and value.get('cycles')is None and value.get('proof',{}).get('performance_accepted')is False):return False
    if not(P(root)/'control/qualification_ledger'/(c+'.DONE.json')).is_file():return False
    return bool(selected(c))
def build_state(main,m,helper,cfg,directory,guard,*,qualification_only=False,installation=None):
    """Private tests call this with fake frame and archive; production uses apply."""
    root=P(cfg['root']);directory=P(directory)
    require((root!=ROOT)is qualification_only,'PRIVATE_PRODUCTION_BOUNDARY')
    require(isinstance(installation,dict),'INSTALLATION_CONTEXT_REQUIRED')
    engine=m['engine'];bridge=m['bridge'];saved=refs(main,m)
    oldarchive=bridge['original_refs'][3];oldput=bridge['original_refs'][2];selected=bridge['selected']
    callback_sources=validate_callback_sources(oldarchive,oldput)
    state=dict(phase='PREPARED',root=root,directory=directory,main=main,marker=m,guard=guard,refs=saved,engine=engine,helper=helper,oldarchive=oldarchive,oldput=oldput,selected=selected,qualification_only=qualification_only,stop=threading.Event(),thread=None,sequence=0,cfg=cfg,installation=installation,callback_sources=callback_sources)
    def event(kind,**data):
        state['sequence']+=1
        value=dict(schema=ID,UTC=utc(),kind=kind,sequence=state['sequence'],owner=cfg['owner'],models_started=0,new_grants=0,model_retries=0,**data)
        exclusive(directory/'events'/(str(time.time_ns())+'_'+str(state['sequence'])+'_'+kind+'.json'),value)
        return value
    state['event']=event
    def invariant():
        guard();require(getattr(main,MARKER)is m,'CONSUMER_MARKER_DRIFT');require(refs(main,m)==saved,'ORIGINAL_REFERENCE_DRIFT')
        require(m['consumer'].safe_finish is m['wrapper'],'EXISTING_WRAPPER_DRIFT')
    state['invariant']=invariant
    def certificate(c,value,q):
        """Metadata-only binding after full H/original verification; no raw reread."""
        row=q['consumed'][c];uuid=row['uuid'];negative_result(value,c,uuid)
        intent_path=root/'control/qualification_ledger'/(c+'.INTENT.json');done_path=intent_path.with_name(c+'.DONE.json')
        intent=read(intent_path);out=P(intent['output']);exit_path=out/'NATIVE_EXIT.json'
        require(row['intent_sha256']==sha(intent_path)and read(done_path)==read(exit_path)==row['execution_receipt'],'CERT_IDENTITY_JOIN')
        require(intent['uuid']==uuid and out==root/'DTC/run/results'/uuid,'CERT_SOURCE_UUID')
        archive=value['archive'];receipt=archive['receipt'];verified=archive['additional_strace_bpf_negative_archive_verification']
        require(verified['status']=='NEGATIVE_EVIDENCE_ARCHIVED_AND_NATIVE_RESTORED'and verified['performance_accepted']is False,'H_FULL_VERIFICATION_CERT_MISSING')
        require(receipt['manifest_sha256']==verified['manifest_sha256']and receipt['source_disposition']=='SOURCE_KEEP','CERT_ARCHIVE_MANIFEST')
        restore=P(receipt['native_restore']);device=restore.stat().st_dev
        require(qualification_only or device==root.stat().st_dev==2128,'CERT_NATIVE_DEVICE')
        run_path=P(installation['run_receipt_path'])
        return dict(schema=CERT,cohort=c,uuid=uuid,request=REQ,qualification_only=qualification_only,result_sha256=sha(root/'analysis'/(c+'.RESULT.json')),helper_sha256=H_SHA,collector_source_sha256=cfg['source_sha256'],configuration_sha256=installation['configuration_sha256'],approval_sha256=installation['approval_sha256'],approval_path=installation['approval_path'],configuration_path=installation['configuration_path'],collector_run_path=str(run_path),collector_run_sha256=sha(run_path),main_pid=cfg['owner']['pid'],main_start_ticks=cfg['owner']['start_ticks'],main_thread_ident=installation['main_thread_ident'],archive_thread_ident=threading.get_ident(),archive_thread_name=threading.current_thread().name,**callback_certificate_fields(callback_sources),outbox_source_sha256=REQUIRED_PINS[str(ROOT/'tools/l2_outbox.py')],source_disposition='SOURCE_KEEP',cycles=None,performance_accepted=False,validated_union_authorized=False,scientific_role=value['scientific_role'],primary_statistics_excluded=value['primary_statistics_excluded'],manifest_sha256=receipt['manifest_sha256'],archive_sha256=receipt['archive_sha256'],result_archive_sha256=object_sha(archive),archive_receipt_sha256=object_sha(receipt),archive_target_mount_path=receipt['target_mount_path'],native_restore=str(restore),native_device=device,independently_verified_entries=archive['independently_verified_entries'],H_required_files=verified['required_files'],intent_sha256=sha(intent_path),done_sha256=sha(done_path),exit_sha256=sha(exit_path),execution_receipt_sha256=object_sha(row['execution_receipt']),automatic_retry=False,model_retries=0)
    state['certificate']=certificate
    def process(c):
        lockpath=directory/'cohort_locks'/(c+'.lock');lockpath.parent.mkdir(parents=True,exist_ok=True)
        with lockpath.open('a+b')as lock:
            try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:return 'LOCK_BUSY'
            invariant();q=engine.registered()[2]
            if not eligible(root,q,c,selected):return 'SKIP'
            uuid=q['consumed'][c]['uuid'];pending=root/'analysis'/(c+'.POSTPROCESS_PENDING.json');pending_sha=sha(pending)if pending.exists()else None
            cp,rp=closure_paths(root,c);result_path=root/'analysis'/(c+'.RESULT.json')
            existing=value=read(result_path)if result_path.exists()else None
            complete_at_entry=cp.exists()and rp.exists()
            if cp.exists():
                require(existing is not None,'CERT_WITHOUT_RESULT')
                expected=certificate(c,existing,q);require(read(cp)==expected,'IMMUTABLE_CERT_CONFLICT')
            else:
                event('ARCHIVE_BEGIN',cohort=c,uuid=uuid,pending_sha256=pending_sha,source_disposition='SOURCE_KEEP')
            def authority_provider():
                invariant();return engine.registered()[2]
            def pinned_archive(candidate):
                require(candidate==c,'CROSS_COHORT_ARCHIVE');invariant()
                archived=oldarchive(candidate);invariant();return archived
            def pinned_put(path,value,exclusive_flag=False):
                invariant();require(exclusive_flag is True,'NEGATIVE_WRITES_MUST_BE_EXCLUSIVE')
                return oldput(path,value,True)
            if not cp.exists():
                value=helper.close_negative(c,root,authority_provider,pinned_archive,pinned_put,qualification_only)
                invariant();expected=certificate(c,value,engine.registered()[2])
                exclusive(cp,expected)
            else:value=existing
            require(value['state']==helper.FAIL and value['uuid']==uuid and value['cycles']is None and value['proof']['performance_accepted']is False,'NEGATIVE_RESULT_CONTRACT')
            invariant()
            if pending_sha is not None:require(sha(pending)==pending_sha,'PENDING_ORIGINAL_CHANGED')
            resolution=dict(schema=ID+'_PENDING_RESOLUTION',cohort=c,uuid=uuid,state=value['state'],cycles=None,performance_accepted=False,source_disposition='SOURCE_KEEP',pending_original_retained=True,pending_original_sha256=pending_sha,result_sha256=sha(root/'analysis'/(c+'.RESULT.json')),model_retries=0)
            if rp.exists():require(read(rp)==resolution,'RESOLUTION_CONFLICT')
            else:exclusive(rp,resolution)
            if complete_at_entry:return 'VERIFIED_COMPLETE'
            event('ARCHIVE_CLOSED',cohort=c,uuid=uuid,result_sha256=resolution['result_sha256'],certificate_path=str(cp),certificate_sha256=sha(cp),source_disposition='SOURCE_KEEP')
            return 'CLOSED'
    state['process']=process
    def tick():
        invariant();q=engine.registered()[2];require(q.get('request')==REQ,'WRONG_CURRENT_GOAL')
        cohorts=list(INITIAL)+sorted(set(q.get('consumed',{}))-set(INITIAL))
        counts={}
        for c in cohorts:
            if state['stop'].is_set()or(directory/'STOP').exists():break
            try:
                if not eligible(root,q,c,selected):continue
                outcome=process(c);counts[outcome]=counts.get(outcome,0)+1
            except Exception as e:event('ARCHIVE_HOLD_SOURCE_KEEP',cohort=c,error=repr(e),source_disposition='SOURCE_KEEP')
        event('HEARTBEAT',counts=counts,remaining=q.get('remaining'),consumed_count=len(q.get('consumed',{})))
        return counts
    state['tick']=tick
    def run():
        state['phase']='RUNNING'
        try:
            event('RUN_BEGIN',stop_path=str(directory/'STOP'),source_sha256=cfg['source_sha256'])
            while not state['stop'].is_set()and not(directory/'STOP').exists():
                tick();state['stop'].wait(cfg['poll_seconds'])
            state['phase']='STOPPED';event('RUN_STOPPED',source_disposition='SOURCE_KEEP')
        except BaseException as error:
            state.update(phase='FAILED_SOURCE_KEEP',error=repr(error))
            try:event('RUN_FAILED_SOURCE_KEEP',error=repr(error),source_disposition='SOURCE_KEEP')
            except BaseException:pass
    state['run']=run
    return state
def apply(config_path,approval_path):
    """Root invokes in existing actual Main only after final review/approval."""
    require(threading.current_thread()is threading.main_thread(),'MAIN_THREAD_ONLY')
    cfg_path=P(config_path);cfg=read(cfg_path);approval=read(approval_path)
    require(cfg['schema']==ID and cfg['request']==REQ and cfg['root']==str(ROOT),'CONFIG_SCOPE')
    require(cfg['qualification_only']is False and cfg['owner']==dict(pid=1498278,start_ticks=977758783),'CONFIG_OWNER')
    require(cfg['source_path']==str(P(__file__).resolve())and cfg['source_sha256']==sha(__file__),'INSTALLER_SOURCE')
    require(cfg['source_pins'].get(cfg['source_path'])==cfg['source_sha256'],'INSTALLER_PIN_ABSENT')
    require(all(cfg['source_pins'].get(p)==h for p,h in REQUIRED_PINS.items()),'H_HANDOFF_SOURCE_PINS_INCOMPLETE')
    require(cfg['helper_sha256']==H_SHA and cfg['source_pins'].get(cfg['helper_path'])==H_SHA,'HELPER_PIN')
    require(1<=cfg['poll_seconds']<=300,'POLL_INTERVAL')
    for key in ['qualification','source_readback']:require(sha(cfg[key+'_path'])==cfg[key+'_sha256'],'QA_READBACK_PIN')
    qa=read(cfg['qualification_path']);back=read(cfg['source_readback_path'])
    require(qa['status']=='PASS_NEGATIVE_ARCHIVE_OWNER_V3_CALLBACK_COMPAT_CPU'and qa['source_sha256']==cfg['source_sha256']and qa['helper_sha256']==H_SHA,'QA_MISMATCH')
    require(back['verified']is True and back['source_pins']==cfg['source_pins']and back['qualification_sha256']==cfg['qualification_sha256'],'SOURCE_READBACK_MISMATCH')
    require(back.get('qualification_only')is False,'PRIVATE_READBACK_CANNOT_INSTALL')
    validate_approval(cfg,sha(cfg_path),approval)
    main=sys.modules['__main__'];require(not hasattr(main,ID),'OBSERVE_EXISTING_INSTALL_DO_NOT_DUPLICATE')
    require(not hasattr(main,'DTC_MAIN_NEGATIVE_ARCHIVE_AUTOCLOSE_OWNER_V1'),'V1_DAEMON_ALREADY_PRESENT')
    require(not hasattr(main,'DTC_MAIN_NEGATIVE_ARCHIVE_AUTOCLOSE_OWNER_V2'),'V2_DAEMON_ALREADY_PRESENT')
    m=getattr(main,MARKER);frame=m['frame'];engine=m['engine'];cfg_sha=sha(cfg_path);approval_sha=sha(approval_path)
    def guard():
        require(os.getpid()==1498278,'OWNER_PID')
        require(int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783,'OWNER_BIRTH')
        require(sha(cfg_path)==cfg_sha and sha(approval_path)==approval_sha,'CONFIG_APPROVAL_DRIFT')
        for p,h in cfg['source_pins'].items():require(sha(p)==h,'SOURCE_DRIFT '+p)
        require(sha(__file__)==cfg['source_sha256']and sha(cfg['helper_path'])==H_SHA,'SELF_HELPER_DRIFT')
        require(frame.f_code.co_name=='run_scheduler'and P(frame.f_code.co_filename)==ROOT/'tools/l2_ops.py'and sha(frame.f_code.co_filename)==OPS_SHA,'ACTUAL_SCHEDULER')
        require(frame.f_locals['engine']is engine and frame.f_locals['consumer']is m['consumer'],'ACTUAL_FRAME')
        require(cfg['source_pins'].get(str(P(engine.__file__)))==sha(engine.__file__),'ENGINE_SOURCE_PIN')
        require(m['bridge']['original_refs'][2]is m['consumer'].put and m['bridge']['original_refs'][3]is m['consumer'].archive_closed,'CAPTURED_CALLBACK_IDENTITY')
        validate_callback_sources(m['bridge']['original_refs'][3],m['bridge']['original_refs'][2])
        require(m['source_sha256']==BRIDGE_SHA and sha(m['bridge']['selected'].__code__.co_filename)==BRIDGE_SHA,'BRIDGE_SOURCE')
        require(m['cfg']==read(m['cfg_path'])and sha(m['cfg_path'])==m['cfg_sha256'],'EXISTING_CONSUMER_CONFIG')
        lease=engine.assert_parent_lease();require(lease['pid']==1498278 and lease['start_ticks']==977758783,'OWNER_LEASE')
    guard();helper=load(cfg['helper_path']);directory=P(cfg['run_directory'])
    require(directory.is_absolute()and directory.resolve().is_relative_to(ROOT/'control/operational_amendments'),'RUN_NAMESPACE')
    require(not directory.exists(),'RUN_DIRECTORY_ALREADY_EXISTS')
    with m['aging'].lock:
        guard();require(not hasattr(main,ID),'CONCURRENT_INSTALL')
        directory.mkdir(parents=True)
        installation=dict(configuration_path=str(cfg_path),configuration_sha256=cfg_sha,approval_path=str(approval_path),approval_sha256=approval_sha,run_receipt_path=str(directory/'RUN.json'),main_thread_ident=threading.get_ident())
        state=build_state(main,m,helper,cfg,directory,guard,installation=installation)
        state['invariant']()
        exclusive(directory/'RUN.json',dict(schema=ID,UTC=utc(),configuration_sha256=cfg_sha,approval_path=str(approval_path),approval_sha256=approval_sha,source_sha256=cfg['source_sha256'],helper_sha256=H_SHA,owner=cfg['owner'],preserved_reference_ids=state['refs'],new_grants=0,models_started=0,registration_mode='SEPARATE_ROOT_SOURCE_BOUND_APPROVAL_NO_AUTHORITY_UPDATE'))
        setattr(main,ID,state)
        thread=threading.Thread(target=state['run'],name=ID,daemon=True);state['thread']=thread
        try:thread.start()
        except BaseException as error:state.update(phase='THREAD_START_FAILED_SOURCE_KEEP',error=repr(error));raise
    return dict(schema=ID,status='ARCHIVE_ONLY_DAEMON_STARTED',source_sha256=cfg['source_sha256'],run_directory=str(directory),thread_ident=thread.ident,new_grants=0,models_started=0,model_retries=0,all_original_references_preserved=True)
