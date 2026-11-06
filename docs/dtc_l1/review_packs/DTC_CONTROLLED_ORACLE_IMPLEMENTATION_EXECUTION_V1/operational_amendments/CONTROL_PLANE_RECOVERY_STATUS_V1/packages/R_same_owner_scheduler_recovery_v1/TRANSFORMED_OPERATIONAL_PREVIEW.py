def recovery_dispatch_loop():
 owner();assert threading.current_thread()is not threading.main_thread()
 main=sys.modules['__main__'];state=getattr(main,MARKER,None)
 if state is None:attach_registered_request(str(R));state=getattr(main,MARKER)
 with state['lock']:
  assert state['thread_ident']==_RECOVERY['cap']['original_thread_ident'];state[_RECOVERY['generation']]['thread_ident']=threading.get_ident()
 first=state['contexts'][str(BASE/'initial8')];mask=set(first['plan']['new_dispatcher_cpu_allowance'])
 assert mask and not mask&set(first['plan']['protected_cpu_ids']);os.sched_setaffinity(0,mask)
 running=dict(_RECOVERY['cap']['running']);post=dict(_RECOVERY['cap']['post']);reviews=dict(_RECOVERY['cap']['reviews']);dispatch_index=_RECOVERY['cap']['dispatch_index']
 def key(ctx,c):return ctx['request']+':'+c
 def event(ctx,kind,**data):put(ctx['root']/'events'/(str(time.time_ns())+'_'+kind+'.json'),dict(UTC=stamp(),kind=kind,request=ctx['request'],**data),True)
 def saveclaims():
  state[_RECOVERY['generation']]['reservation_sync_pending']=True
  with state['lock']:
   for ctx in state['contexts'].values():put(ctx['root']/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims={v['cohort']:v for v in state['claims'].values()if v['request']==ctx['request']}))
   put(BASE/'control/SHARED_POOL_DISPATCH_RESERVATIONS.json',dict(schema='DTC_CONTROLLED_ORACLE_SHARED_POOL_CLAIMS_V1',owner_pid=1498278,owner_start_ticks=977758783,claims=state['claims'],requests={c['request']:str(c['root'])for c in state['contexts'].values()}))
   for ctx in state['contexts'].values():sync_stage_reservation(ctx,{v['cohort']:v for v in state['claims'].values()if v['request']==ctx['request']})
  state[_RECOVERY['generation']]['reservation_sync_pending']=False
 state['saveclaims']=saveclaims
 def pause(ctx,c,value):
  p=BASE/'control/ENGINEERING_PAUSE_NEW.json'
  if not p.exists():
   try:put(p,dict(request=ctx['request'],cohort=c,UTC=stamp(),result=value,no_healthy_model_signals=True,model_retries=0),True)
   except FileExistsError:pass
 work=_RECOVERY['cap']['work'];review=_RECOVERY['cap']['review']
 with _RECOVERY['cap']['held_duplicate']as held:
  state[_RECOVERY['generation']]['reservation_sync_pending']=True
  with _PlainPool(max_workers=min(128,len(mask)),thread_name_prefix='DTC_ORACLE_RECOVERY_MODEL')as workers,_PlainPool(max_workers=1,thread_name_prefix='DTC_ORACLE_RECOVERY_ARCHIVE')as archives,_PlainPool(max_workers=1,thread_name_prefix='DTC_ORACLE_RECOVERY_REVIEW')as review_pool:
   while True:
    try:
     if not state[_RECOVERY['generation']].get('loop_observed'):_RECOVERY['running_ack']();state[_RECOVERY['generation']]['loop_observed']=True
     _RECOVERY['cleanup'](running,post,reviews)
     with state['lock']:contexts=list(state['contexts'].values())
     for ctx in contexts:ctx['e'].assert_parent_lease()
     for future,(ctx,c)in list(running.items()):
      if not future.done():continue
      value=_RECOVERY['harvest'](future,running,ctx,c,'MODEL')
      if value is None:continue
      event(ctx,'MODEL_WORKER_RETURN',cohort=c,result=value)
      if value['state']=='EXECUTION_CLOSED':
       _closed_receipt(ctx,c)
       with state['lock']:state['claims'].pop(key(ctx,c),None);saveclaims()
       post[archives.submit(ctx['consumer'].safe_finish,c)]=(ctx,c)
      elif c not in ctx['e'].registered()[2]['consumed']:
       _unused_identity(ctx,c)
       with state['lock']:state['claims'].pop(key(ctx,c),None);saveclaims()
       ctx['cool'][c]=time.monotonic()+30;ctx['errors'][c]=value
       if any(reason in value.get('error','')for reason in ['RESOURCE_HOLD','REGISTRY_SHARED_LOCK_BUSY','REGISTRY_EX_BUSY','REGISTRY_BUSY','WAIT_MODE_GATE2','WAIT_INDEPENDENT_ACTUAL_QUALIFIER_REVIEW']):event(ctx,'EXPECTED_ADMISSION_DEFERRAL_ZERO_START',cohort=c,error=value.get('error'))
       else:pause(ctx,c,value)
      else:ctx['errors'][c]=value;pause(ctx,c,value) # spent uncertain generation retains claim
     for future,(ctx,c)in list(post.items()):
      if not future.done():continue
      value=_RECOVERY['harvest'](future,post,ctx,c,'POST')
      if value is None:continue
      event(ctx,'RESULT_CONSUMED',cohort=c,state=value['state']);saveclaims()
      if value['state']==PASS and c in set(ctx['plan']['initial_qualifiers'].values()):reviews[review_pool.submit(review,ctx,c)]=(ctx,c);ctx['cool']['review:'+c]=time.monotonic()+60
      elif value['state']not in[PASS,NEG]:ctx['errors'][c]=value;pause(ctx,c,value)
     for future,(ctx,c)in list(reviews.items()):
      if not future.done():continue
      try:event(ctx,'INDEPENDENT_QUALIFIER_REVIEW_RETURN',**future.result())
      except BaseException as error:ctx['errors'][c]=dict(reason='INDEPENDENT_REVIEW_ENGINEERING',error=repr(error));event(ctx,'FAMILY_RELEASE_HELD',cohort=c,error=repr(error))
      reviews.pop(future)
     sample=first['res'].sample_system();all_pending=[];states_by_request={};snapshots={}
     for ctx in contexts:
      q=ctx['e'].registered()[2];snapshots[ctx['request']]=q;root=ctx['root'];busy={key(k,c)for k,c in list(running.values())+list(post.values())};reviewbusy={key(k,c)for k,c in reviews.values()}
      for c,row in q['consumed'].items():
       claim=state['claims'].get(key(ctx,c))
       if claim:claim['uuid']=row['uuid']
       if row.get('execution_receipt')and key(ctx,c)not in busy and not(root/'analysis'/(c+'.RESULT.json')).exists()and time.monotonic()>=ctx['cool'].get('post:'+c,0):post[archives.submit(ctx['consumer'].safe_finish,c)]=(ctx,c);ctx['cool']['post:'+c]=time.monotonic()+60
       if c in set(ctx['plan']['initial_qualifiers'].values())and key(ctx,c)not in reviewbusy and(root/'analysis'/(c+'.RESULT.json')).exists()and rd(root/'analysis'/(c+'.RESULT.json'))['state']==PASS and not(root/'control/actual_qualification_reviews'/(c+'.json')).exists()and time.monotonic()>=ctx['cool'].get('review:'+c,0):reviews[review_pool.submit(review,ctx,c)]=(ctx,c);ctx['cool']['review:'+c]=time.monotonic()+60
      if ctx['plan']['stage']=='initial8':
       for mode in ctx['plan']['qualified_modes']:
        subject='MODE:'+mode;members=[p for p in ctx['points']if p['mode']in[mode,'OFF_MATCHED']]
        if key(ctx,subject)in reviewbusy or P(ctx['plan']['mode_gate2_reviews'][mode]).exists()or time.monotonic()<ctx['cool'].get('review:'+subject,0):continue
        if len(members)==16 and all((root/'analysis'/(p['cohort']+'.RESULT.json')).exists()and rd(root/'analysis'/(p['cohort']+'.RESULT.json'))['state']==PASS for p in members)and all((root/'control/actual_qualification_reviews'/(ctx['plan']['initial_qualifiers'][m]+'.json')).exists()for m in[mode,'OFF_MATCHED']):
         reviews[review_pool.submit(review,ctx,subject)]=(ctx,subject);ctx['cool']['review:'+subject]=time.monotonic()+60
      gates={}
      if not(BASE/'control/ENGINEERING_PAUSE_NEW.json').exists()and not(BASE/'control/POOL_STOP_NEW.json').exists():
       for point in ctx['points']:
        c=point['cohort']
        if c in q['consumed']or key(ctx,c)in state['claims']or time.monotonic()<ctx['cool'].get(c,0):continue
        try:
         spec=ctx['e'].canonical(c)
         if ctx['res'].admission_hold(q,spec)is not None:gates[c]='TYPED_MODE_HOLD';continue
         gates[c]=ctx['res'].verify_initial_runtime_gate(ctx['plan'],c,q);all_pending.append((ctx,spec))
        except ctx['res'].WaitInitialRuntimeGate as wait:gates[c]=str(wait)
        except BaseException as error:gates[c]=repr(error);ctx['errors'][c]=dict(reason='MODE_QUALIFICATION_GATE_FAILED',error=repr(error))
      states={p['cohort']:rd(root/'analysis'/(p['cohort']+'.RESULT.json'))['state']if(root/'analysis'/(p['cohort']+'.RESULT.json')).exists()else'PENDING'for p in ctx['points']};states_by_request[ctx['request']]=states
      put(root/'analysis/BATCH_STATE.json',dict(UTC=stamp(),request=ctx['request'],budget=q['budget'],consumed=len(q['consumed']),remaining=q['remaining'],running=[c for k,c in running.values()if k is ctx],postprocess=[c for k,c in post.values()if k is ctx],independent_reviews=[c for k,c in reviews.values()if k is ctx],states=states,gates=gates,errors=ctx['errors'],same_owner_shared_pool=True,no_extra_model_retries=True))
     callback=state.get('extension_callback')
     if callback is not None:
      if callback.snapshot()['state']=='ARMED':
       for mode in first['plan']['qualified_modes']:
        try:
         evidence=first['res'].verify_mode_extension_receipt(first['plan'],mode)
         queue=callback.queue_once();event(first,'AUTHORIZED_GATE2_MAINTHREAD_HANDOFF_QUEUED',mode=mode,evidence=evidence,queue=queue);break
        except first['res'].WaitInitialRuntimeGate:pass
      put(BASE/'control/EXTENSION_CALLBACK_STATUS.json',callback.snapshot())
     # One global pending list and RAM/CPU claim dictionary across both requests.
     if state[_RECOVERY['generation']].get('reservation_sync_pending')or not _launch_phase_ready(running):all_pending=[]
     for _ in range(min(1,max(0,min(128,len(mask))-len(running)))):
      if not all_pending or(BASE/'control/ENGINEERING_PAUSE_NEW.json').exists()or(BASE/'control/POOL_STOP_NEW.json').exists():break
      decision=first['res'].choose_dispatch([s for _,s in all_pending],sample,state['claims'],policy=rd(first['root']/'control/RESOURCE_POLICY.json'),dispatch_index=dispatch_index)
      if decision is None:break
      ctx,spec=next((k,s)for k,s in all_pending if s['cohort']==decision['cohort']);c=spec['cohort'];fresh=_RECOVERY['resource'](ctx,spec,False)
      if fresh is None:continue
      if not all(fresh[k]for k in ['physical_RAM_pass','physical_disk_pass','admission_disk_pass','admission_pressure_pass']):event(ctx,'RESOURCE_HOLD_NO_START',cohort=c,sample=fresh);all_pending=[(k,s)for k,s in all_pending if s['cohort']!=c];continue
      cpu=decision['host_cpu'];db=ctx['root']/'control/dispatch_bindings'/(c+'.json')
      if db.exists():
       b=rd(db);assert b['canonical_spec_sha256']==sha(ctx['root']/'control/specs'/(c+'.json'))
       if b['host_cpu']not in mask or b['host_cpu']in({x['host_cpu']for x in state['claims'].values()}|{cpu for x in sample['observed_affinity_claims']for cpu in x['cpus']}):all_pending=[(k,s)for k,s in all_pending if s['cohort']!=c];continue
       cpu=b['host_cpu']
      else:put(db,dict(cohort=c,canonical_spec_sha256=sha(ctx['root']/'control/specs'/(c+'.json')),host_cpu=cpu,resolved_spec_sha256=ctx['e'].jsonsha(dict(spec,host_cpu=cpu))),True)
      with state['lock']:
       state['claims'][key(ctx,c)]=dict(request=ctx['request'],execution_root=str(ctx['root']),cohort=c,host_cpu=cpu,uuid=None,workload=spec['workload'],predicted_peak_RAM_bytes=decision['predicted_peak_RAM_bytes'],result_cap_bytes=spec['limits']['max_result_directory_bytes'],RAM_cap_bytes=spec['limits']['max_process_tree_rss_bytes'],observed_model=False);saveclaims()
      charged=_RECOVERY['resource'](ctx,spec,True)
      if charged is None:
       _unused_identity(ctx,c)
       with state['lock']:state['claims'].pop(key(ctx,c),None);saveclaims()
       continue
      if not all(charged[k]for k in ['physical_RAM_pass','physical_disk_pass','admission_disk_pass','admission_pressure_pass']):
       _unused_identity(ctx,c)
       with state['lock']:state['claims'].pop(key(ctx,c),None);saveclaims()
       event(ctx,'POSTCLAIM_RESOURCE_HOLD_ZERO_CONSUME',cohort=c,resource_sample=charged);all_pending=[(k,s)for k,s in all_pending if s['cohort']!=c];continue
      _unused_identity(ctx,c);running[workers.submit(work,ctx,c)]=(ctx,c);dispatch_index+=1;event(ctx,'DISPATCH_AUTHORIZED_UNUSED_IDENTITY',cohort=c,cpu=cpu);all_pending=[(k,s)for k,s in all_pending if s['cohort']!=c];sample=first['res'].sample_system()
     put(BASE/'control/SHARED_POOL_STATUS.json',dict(UTC=stamp(),owner_pid=1498278,owner_start_ticks=977758783,requests={k:dict(budget=q['budget'],remaining=q['remaining'],consumed=len(q['consumed']))for k,q in snapshots.items()},running=[dict(request=k['request'],cohort=c)for k,c in running.values()],archive_jobs=len(post),independent_reviews=len(reviews),claims=len(state['claims']),single_dispatcher=True))
     terminal=not running and not post and not reviews and all(q['remaining']==0 and all(v in[PASS,NEG]for v in states_by_request[k].values())for k,q in snapshots.items())
     if terminal and(len(contexts)==2 or(BASE/'control/POOL_STOP_NEW.json').exists()):put(BASE/'control/SHARED_POOL_EXECUTION_TERMINAL.json',dict(status='ALL_ATTACHED_REGISTERED_ORACLE_IDENTITIES_TERMINAL',UTC=stamp(),states=states_by_request,independent_final_closeout_pending=True),True);return
     time.sleep(2)
    except BaseException as recovery_error:
     _RECOVERY['cycle_error'](recovery_error)
     time.sleep(2)
