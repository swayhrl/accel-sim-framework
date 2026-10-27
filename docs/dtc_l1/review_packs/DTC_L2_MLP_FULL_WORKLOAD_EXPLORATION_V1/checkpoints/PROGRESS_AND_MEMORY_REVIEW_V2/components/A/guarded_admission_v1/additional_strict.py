"""Candidate consumer gate AFTER unchanged l2_strict.terminal succeeds.

Consumer must install/integrate this gate before any guarded pilot dispatch.
Never substitutes historical accepted or engineering identities.
"""
import hashlib,importlib.util,json,pathlib
P=pathlib.Path;HERE=P(__file__).resolve().parent
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def verify_reservation_math(base,h,d,policy,c,q,forecast):
 """Historical arithmetic only. Never reads historical process liveness."""
 originals=base['own_ram_forecasts'];original_map={r['cohort']:r for r in originals};assert len(original_map)==len(originals)
 changed=d['changed_live_rows'];unchanged=d['unchanged_rows'];allrows=changed+unchanged;actual={r['cohort']:r for r in allrows}
 assert len(actual)==len(allrows)==len(originals)and set(actual)==set(original_map)
 delta=0
 for cohort,row in actual.items():
  b=original_map[cohort];old=b['additional_reserved_bytes'];new=row['guarded_reserved_bytes']
  assert all(row[k]==b[k]for k in ['cohort','kind','RSS_bytes','additional_reserved_bytes'])
  assert row['original_reserved_bytes']==old and type(old)is int and type(new)is int and 0<=new<=old
  if new!=old:
   assert row in changed and b['kind']=='LIVE_MODEL'and cohort!=c and row['reason']=='FRESH_MONITORED_SAME_GENERATION_GROWTH_ENVELOPE'
   own=h.get('own_live_generations',{});obs=own.get(cohort)if isinstance(own,dict)else next((v for v in own if v.get('cohort')==cohort),None)
   if obs is None:obs=next((v for v in h.get('live_generation_states',[])if v.get('cohort')==cohort),None)
   assert obs and obs['uuid']==q['consumed'][cohort]['uuid']and type(obs['pid'])is int and type(obs['start_ticks'])is int
   rss=obs.get('RSS_bytes',obs.get('rss_bytes'));growth=obs.get('growth_reserve_bytes')
   if growth is None:growth=max(policy['minimum_live_growth_reserve_bytes'],int(rss*.1),int(max(0,obs['growth_rate'])*policy['growth_forecast_horizon_seconds']*policy['growth_rate_multiplier']))
   assert type(growth)is int and growth>=policy['minimum_live_growth_reserve_bytes']
   assert new==min(old,max(policy['minimum_live_growth_reserve_bytes'],growth,b['RSS_bytes']-rss))
  else:assert row in unchanged and row['reason']=='ORIGINAL_UNCHANGED'
  if cohort==c:assert new==old and new>=forecast
  delta+=new-old
 original_total=base['total_projected_additional_RAM_bytes'];assert original_total>=sum(r['additional_reserved_bytes']for r in originals)
 assert d['original_total_projected_additional_RAM_bytes']==original_total
 assert d['guarded_total_additional_RAM_bytes']==original_total+delta
 head=h.get('headroom_sample',{});host=min(base['host_MemAvailable_bytes'],head.get('host_available_bytes',base['host_MemAvailable_bytes']));cg=base.get('cgroup_effective_headroom_bytes')
 for value in [head.get('cgroup_effective_headroom_bytes'),head.get('cgroup_raw_headroom_bytes')]:
  if value is not None:cg=min(cg,value)if cg is not None else value
 ceiling=min(host-policy['host_floor_bytes'],cg-policy['cgroup_floor_bytes']if cg is not None else host-policy['host_floor_bytes'])
 assert d['RAM_available_after_10G_floors_bytes']==ceiling and original_total+delta<=ceiling
 assert not d['pressure_reasons']and not base.get('admission_decision',{}).get('pressure_reasons')and base['physical_disk_pass']
 return True
def verify(c,e=None):
 g=load('additional_guard_rules',HERE/'guarded_native.py')
 e=e or load('additional_guard_base',g.R/'tools/l2_native.py')
 i=e.read(e.R/'control/qualification_ledger'/(c+'.INTENT.json'))
 reg,ep,q,plan=e.registered()
 if 'resource_overlay_binding'not in i:
  assert not any(v.get('cohort')==c for v in q.get('resource_admission_token_history',{}).values()),'Guard-selected cohort cannot omit its additional binding'
  return {'status':'NO_OVERLAY_ORIGINAL_STRICT_ONLY','original_strict_unmodified':True}
 binding=i['resource_overlay_binding'];record=q['resource_admission_overlays'][binding['overlay_id']]
 assert binding['request']==e.REQ and binding['cohort']==c and binding['overlay_id']==g.OVERLAY_ID
 assert binding['registry_overlay_record_sha256']==g.jsonsha(record)
 assert record['original_engine_sha256']==e.sha(e.__file__) and record['original_binding_sha256']==g.jsonsha(e.binding())
 assert binding['base_provider_sha256']==e.sha(e.R/'tools/l2_resources.py')
 for k in ['overlay_source','policy','monitor_source','additional_strict_source','cpu_native_prefix_qualification','publication_readback']:
  assert e.sha(record[k]['path'])==record[k]['sha256']
 assert binding['overlay_source_sha256']==record['overlay_source']['sha256']
 assert binding['policy_sha256']==record['policy']['sha256'] and binding['monitor_source_sha256']==record['monitor_source']['sha256']
 assert binding['cpu_native_prefix_qualification_sha256']==record['cpu_native_prefix_qualification']['sha256']
 assert binding['additional_strict_source_sha256']==record['additional_strict_source']['sha256']==e.sha(__file__)
 assert binding['publication_readback_sha256']==record['publication_readback']['sha256']
 pub=e.read(record['publication_readback']['path']);assert pub['status']=='READBACK_VERIFIED'and len(pub['commit'])==40
 assert all(pub['source_sha256'][k]==record[k]['sha256']for k in ['overlay_source','policy','monitor_source','additional_strict_source','cpu_native_prefix_qualification'])
 assert binding['original_l2_execution_binding_unmodified']and binding['scientific_spec_and_limits_unmodified']and binding['base_forecast_fields_are_not_the_effective_admission_gate']
 policy=e.read(record['policy']['path']);out=P(i['output']);spec=e.spec_for(c)
 assert q['consumed'][c]['intent_sha256']==e.sha(e.R/'control/qualification_ledger'/(c+'.INTENT.json'))
 for obj in [i,e.read(out/'NATIVE_LAUNCH.json'),e.read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')]:
  assert obj['resource_overlay_binding']==binding and obj['l2_mlp_execution_binding']==e.binding()
  v=obj['resource_overlay_admission_evidence'];decision=v['decision'];token=v['owner_selected_token']
  assert decision['pass_admission']and decision['candidate_estimate_unchanged']and decision['RSS_AS_caps_unchanged']and decision['foreign_and_unresolved_reservations_unchanged']
  assert v['owner_selected_token_sha256']==binding['owner_selected_token_sha256']
  history=q['resource_admission_token_history'][token['nonce']];assert history['cohort']==c and history['sha256']==v['owner_selected_token_sha256']==e.sha(history['path'])
  assert e.read(history['path'])==token and token['nonce']==binding['owner_selected_token_nonce']
  assert token['canonical_spec_sha256']==e.sha(e.R/'control/specs'/(c+'.json'))
  assert token['dispatch_binding_sha256']==e.sha(out/'DISPATCH_BINDING.json')
  raw=v['heartbeat_raw_utf8'].encode();assert hashlib.sha256(raw).hexdigest()==v['heartbeat_sha256'];h=json.loads(raw)
  assert h['policy_sha256']==binding['policy_sha256'] and h['monitor_source_sha256']==binding['monitor_source_sha256']
  assert h['registry_overlay_record_sha256']==binding['registry_overlay_record_sha256']and h['epoch']==token['epoch']==2
  assert h['boot_id']==token['boot_id']and h['warmup_complete']and not h['pause_new_admission']
  assert h['shadow_mode']is False and h['signals_enabled']is True and h['healthy']is True and h['fault']is None and h['fresh_admission_allowed']is True
  assert h['aggressive_admission_armed']is True
  assert h['active_admission_token_sha256']==binding['owner_selected_token_sha256']
  assert all(h[k]==v for k,v in binding['guard_identity'].items())
  assert h['monitor_pid']==h['owner_pid']and h['monitor_start_ticks']==h['owner_start_ticks']and h['guard_tid']!=h['owner_pid']
  assert h['pause_journal_path']==record['pause_journal_path']and h['guard_token']==record['guard_token']
  assert g.journal_prefix_hash(h['pause_journal_path'],h['pause_journal_prefix_bytes'])==h['pause_journal_sha256']
  assert h['handle_state_sha256']==g.jsonsha(h['paused_handles'])
  assert 0<=v['heartbeat_age_seconds']<=policy['heartbeat_max_age_seconds']
  assert token['issued_monotonic']<=h['monotonic']+v['heartbeat_age_seconds']<=token['expires_monotonic']
  assert decision['guarded_total_additional_RAM_bytes']<=decision['RAM_available_after_10G_floors_bytes']
  base=v['base_resource_receipt'];candidate=[r for r in decision['unchanged_rows']if r['cohort']==c and r['kind']in ['CLAIM_OR_CANDIDATE','SPENT_UNRESOLVED_GENERATION']]
  verify_reservation_math(base,h,decision,policy,c,q,spec['estimated_peak_model_RAM_bytes'])
  assert candidate and candidate[0]['guarded_reserved_bytes']>=spec['estimated_peak_model_RAM_bytes']
  assert base['source_module_sha256']==binding['base_provider_sha256']
 journal=P(record['pause_journal_path']).read_bytes();end=journal.rfind(b'\n')+1;prefix=journal[:end];events=[]
 native=e.read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')
 for line in prefix.splitlines():
  row=json.loads(line)
  if row.get('cohort')!=c:continue
  assert row['request']==e.REQ and row['epoch']==2 and row['guard_token']==record['guard_token']
  assert row['owner_pid']==binding['guard_identity']['owner_pid']and row['source_sha256']==binding['monitor_source_sha256']
  assert row['uuid']==q['consumed'][c]['uuid']and row['pid']==native['pid']and row['start_ticks']==native['start_ticks']
  assert not row['event'].startswith('SHADOW_');events.append(row)
 return {'status':'PASS_ADDITIONAL_GUARDED_ADMISSION_BINDING','overlay_id':g.OVERLAY_ID,'cohort':c,'binding':binding,'original_strict_unmodified':True,'pause_journal_verified_prefix_bytes':end,'pause_journal_verified_prefix_sha256':hashlib.sha256(prefix).hexdigest(),'target_generation_pause_events':events}
def terminal(c):
 g=load('guarded_strict_rules',HERE/'guarded_native.py');s=load('unchanged_l2_terminal',g.R/'tools/l2_strict.py')
 original=s.terminal(c);extra=verify(c)
 return {'original_strict_result':original,'additional_resource_overlay_validation':extra}
