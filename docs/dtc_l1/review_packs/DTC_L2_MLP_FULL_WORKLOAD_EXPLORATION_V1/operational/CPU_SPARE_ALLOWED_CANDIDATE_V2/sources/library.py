"""Approved prospective CPU-spare generation; no installation on import.
Old95 and CPU1 sources/records stay unchanged; raw CPU-full remains evidence.
"""
import pathlib,json,hashlib,importlib.util,copy,os,time,sys,contextlib
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
ID='CPU_SPARE_FUTURE_MEMORY_ADMISSION_095_V2'
G=1024**3
ROLES=['library','frontend','owner','extra_strict','joint_padding','joint_io']
POLICY=dict(min_sample_seconds=.5,max_evidence_age_seconds=2.,max_sample_seconds=10.,quota_fraction=.75,prospective_cpu_threads=1,min_spare_physical_cores=4,max_sibling_busy_fraction=.10,only_ignored_reason='cpu_pressure_full',visible_ancestors_only=True,hidden_ancestor_limits_excluded=False)
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def js(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def objsha(v):return hashlib.sha256(js(v)).hexdigest()
def need(v,msg):
 if not v:raise RuntimeError('RESOURCE_HOLD_CPU_SPARE: '+msg)
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
_OLD=load('cpu_spare_unchanged_memory_v2',R/'control/operational_amendments/future_memory_admission_v1/future_memory.py')
def atomic(p,v):return _OLD.atomic(p,v)
def effective_policy(policy=None):return _OLD.effective_policy(policy)
def budget(sample):return _OLD.budget(sample)
def record(cfg):
 keys=['request','overlay_id','scope_mode','memory_utilization_fraction','host_floor_bytes','cgroup_floor_bytes','expected_pins','io_active_sha256','allowed_cohorts',*[r+'_sha256'for r in ROLES],'QA_sha256','readback_sha256','cpu_exception_scope','cpu_spare_policy']
 return dict({k:copy.deepcopy(cfg[k])for k in keys},fallback_v2_config_sha256=objsha(cfg['fallback_v2_config']),previous_cpu_v1_config_sha256=objsha(cfg['previous_cpu_v1_config']),canary_qualification_path=cfg['canary_qualification_path'],canary_qualification_sha256=cfg['canary_qualification_sha256'])
def eligible_cohort(cfg,q,cohort,stage,claims=None):
 if stage=='FRAME':stage='OWNER_FRAME'
 need(stage in['OWNER_CHOOSE','OWNER_FRAME','NATIVE'],'unknown CPU eligibility stage')
 if cfg['cpu_exception_scope']['mode']!='ALL_ALLOWED_ADMITTED_UNSPENT':return False
 if cohort not in cfg['allowed_cohorts']or cohort not in q['admitted_specs']or cohort in q['consumed']or cohort in q.get('sealed',[]):return False
 return not(stage=='OWNER_CHOOSE'and cohort in(claims or{}))
def canary_qualification(cfg,q=None,utf8=None):
 text=P(cfg['canary_qualification_path']).read_text()if utf8 is None else utf8
 need(hashlib.sha256(text.encode()).hexdigest()==cfg['canary_qualification_sha256'],'natural canary receipt SHA mismatch')
 receipt=json.loads(text);previous=cfg['previous_cpu_v1_config'];c=previous['cpu_exception_scope']['allowed_cohorts'];need(len(c)==1,'previous canary scope invalid')
 need(receipt['status']=='PASS_CPU_SPARE_CANARY_NATURAL_STRICT_ARCHIVE_NATIVE_RESTORE'and receipt['production_release_eligible']is True and receipt['original_performance_accepted']is True,'natural canary not accepted for production release')
 need(receipt['cohort']==c[0]and bool(receipt['uuid'])and bool(receipt['input_digest']),'natural canary identity missing/mismatch')
 fixture=receipt.get('qualification_only',False)
 if fixture:need(cfg.get('qualification_only')is True and(q is None or q.get('qualification_only')is True),'CPU stand-in cannot authorize actual Main')
 else:need(not cfg.get('qualification_only',False),'qualification config cannot authorize production')
 if q is not None:
  row=q['consumed'].get(c[0],{});done=row.get('execution_receipt',{});need(row.get('uuid')==receipt['uuid']and done.get('launcher_wait_returncode')==0 and done.get('stop_reason')is None and bool(done),'previous canary lacks actual natural execution receipt')
 return receipt
def validate(cfg,q):
 need(cfg['status']=='ACTIVE_FUTURE_ONLY'and cfg['request']==REQ and cfg['overlay_id']==ID,'CPU memory not active')
 need(cfg['scope_mode']=='ALL_UNSPENT_FUTURE'and cfg['cpu_spare_policy']==POLICY,'CPU spare policy drift')
 scope=cfg['cpu_exception_scope'];need(scope['mode']=='ALL_ALLOWED_ADMITTED_UNSPENT'and 'allowed_cohorts'not in scope,'CPU scope must use one explicit routing allowlist')
 need(set(cfg['allowed_cohorts'])<=set(q['admitted_specs']),'unadmitted CPU memory scope')
 need(len(set(cfg['allowed_cohorts']))==len(cfg['allowed_cohorts'])and cfg['memory_utilization_fraction']==.95 and cfg['host_floor_bytes']==cfg['cgroup_floor_bytes']==10*G,'CPU memory budget drift')
 old=cfg['fallback_v2_config'];_OLD.validate(old,q)
 previous=cfg['previous_cpu_v1_config'];need(objsha(previous)==cfg['previous_cpu_v1_config_sha256']and previous['fallback_v2_config']==old,'previous CPU1 config preimage mismatch')
 previous_lib=load('cpu_spare_frozen_cpu1_lineage',previous['library_path']);need(previous['library_sha256']==sha(previous_lib.__file__)=='5b081e91077d84856f077d3f2fcbbf9f2aee97af6a6ed3297942cae44a304b54','CPU1 source changed');previous_lib.validate(previous,q);canary_qualification(cfg,q)
 need(old['library_sha256']==sha(_OLD.__file__)and set(old['allowed_cohorts'])<=set(cfg['allowed_cohorts']),'old95 fallback route population changed')
 for role in ROLES+['QA','readback']:need(sha(cfg[role+'_path'])==cfg[role+'_sha256'],'CPU generation source/receipt drift '+role)
 need(sha(__file__)==cfg['library_sha256'],'wrong CPU memory library')
 for p,h in cfg['expected_pins'].items():need(sha(p)==h,'frozen dependency drift '+p)
 need(sha(cfg['io_active_path'])==cfg['io_active_sha256'],'old IO config drift')
 sources={r:cfg[r+'_sha256']for r in ROLES};qa=read(cfg['QA_path']);back=read(cfg['readback_path'])
 need(qa['status']=='PASS'and qa['cpu_spare_library_qualified']and qa['native_binding_qualified']and back['verified'],'CPU source not qualified/published')
 need(qa['qualified_sources']==back['qualified_sources']==sources and back['QA_sha256']==cfg['QA_sha256'],'CPU qualification/readback mismatch')
 need(qa['expected_pins']==back['expected_pins']==cfg['expected_pins'],'CPU expected pin mismatch')
 rec=q['additional_operational_overlays'][ID];need(rec['status']=='ACTIVE'and all(rec.get(k)==v for k,v in record(cfg).items()),'CPU memory record mismatch')
 return rec
def _kv(p):return {s[0]:int(s[1])for s in(line.split()for line in P(p).read_text().splitlines())if len(s)==2 and s[1].isdigit()}
def _ranges(s):
 out=[]
 for x in s.strip().split(','):
  if not x:continue
  v=list(map(int,x.split('-')));out.extend(range(v[0],v[-1]+1))
 return out
def _cgroups():
 # Resolve the process's actual cgroup2 path against the visible mount root.
 cg=next(x.split('::',1)[1]for x in P('/proc/self/cgroup').read_text().splitlines()if x.startswith('0::'))
 fields=next(x.split(' - ',1)[0].split()for x in P('/proc/self/mountinfo').read_text().splitlines()if' - cgroup2 'in x)
 root=P(fields[3]);mount=P(fields[4]);relative=P(cg).relative_to(root);leaf=(mount/relative).resolve();need(leaf.is_relative_to(mount.resolve()),'cgroup escaped visible mount')
 nodes=[];p=leaf
 while True:
  quota=(p/'cpu.max').read_text().split();stat=_kv(p/'cpu.stat');nodes.append(dict(path=str(p),quota=quota,stat=stat))
  if p==mount:break
  p=p.parent
 return dict(process_cgroup=cg,mount_root=str(root),mount_point=str(mount),visible=nodes,sample_monotonic=time.monotonic(),hidden_ancestor_status='UNKNOWN',hidden_ancestor_limits_excluded=False)
def _snapshot():
 ticks={}
 for line in P('/proc/stat').read_text().splitlines():
  x=line.split()
  if x and x[0].startswith('cpu')and x[0]!='cpu':ticks[x[0][3:]]=[int(v)for v in x[1:9]]
 stamp=time.monotonic();allowed=sorted(os.sched_getaffinity(0));online=_ranges(P('/sys/devices/system/cpu/online').read_text());top=[]
 for cpu in online:
  p=P('/sys/devices/system/cpu',f'cpu{cpu}','topology');top.append(dict(cpu=cpu,socket=int((p/'physical_package_id').read_text()),core=int((p/'core_id').read_text()),siblings=_ranges((p/'thread_siblings_list').read_text())))
 claims=[];unknown=[];raced=0;scanned=0
 for proc in P('/proc').iterdir():
  if not proc.name.isdigit()or int(proc.name)==os.getpid():continue
  try:tasks=list((proc/'task').iterdir())
  except FileNotFoundError:raced+=1;continue
  except PermissionError:unknown.append(str(proc));continue
  for task in tasks:
   try:
    f=(task/'stat').read_text().rsplit(')',1)[1].split();aff=sorted(os.sched_getaffinity(int(task.name)));scanned+=1
    if f[0]in('Z','X'):continue
    narrow=len(aff)<len(allowed)
    if narrow or f[0]=='R':claims.append(dict(pid=int(proc.name),tid=int(task.name),start_ticks=int(f[19]),state=f[0],processor=int(f[36]),affinity=aff if narrow else None,affinity_width=len(aff),kind='PINNED_AFFINITY_JOB'if narrow else'RUNNING_BROAD_TASK'))
   except(FileNotFoundError,ProcessLookupError):raced+=1
   except(PermissionError,OSError,ValueError):unknown.append(str(task))
 fields=P('/proc/self/stat').read_text().rsplit(')',1)[1].split()
 result=dict(monotonic=stamp,boot_id=P('/proc/sys/kernel/random/boot_id').read_text().strip(),sampler_pid=os.getpid(),sampler_start_ticks=int(fields[19]),sampler_uid=os.getuid(),sampler_ppid=os.getppid(),allowed=allowed,topology=top,cpu_ticks=ticks,cgroups=_cgroups(),other_task_claims=claims,unreadable_tasks=unknown,raced_disappeared_tasks=raced,scanned_tasks=scanned);result['completed_monotonic']=time.monotonic();return result
def sample_cpu_evidence(selected_cpu=None,sample_seconds=.5,prospective_cpu_threads=1):
 need(sample_seconds>=POLICY['min_sample_seconds']and prospective_cpu_threads==1,'CPU sampling policy changed')
 first=_snapshot();time.sleep(sample_seconds);second=_snapshot()
 e=dict(schema=ID+'_CPU_DOUBLE_SAMPLE',policy=copy.deepcopy(POLICY),first=first,second=second,selected_cpu=selected_cpu,prospective_cpu_threads=1,created_monotonic=time.monotonic(),sampler_source_sha256=sha(__file__))
 try:e['assessment']=verify_cpu_evidence(e,selected_cpu);e['eligible']=True
 except Exception as x:e['assessment']=dict(status='HOLD',reason=str(x));e['eligible']=False
 return e
def verify_cpu_evidence(e,selected_cpu=None):
 """Offline verifier. Reads no live state or files."""
 need(e['schema']==ID+'_CPU_DOUBLE_SAMPLE'and e['policy']==POLICY and e['prospective_cpu_threads']==1,'wrong CPU evidence schema/policy')
 if e['selected_cpu']is not None and selected_cpu is not None:need(e['selected_cpu']==selected_cpu,'selected CPU evidence binding differs')
 a=e['first'];b=e['second'];dt=b['monotonic']-a['monotonic'];need(.5<=dt<=POLICY['max_sample_seconds'],'invalid CPU sample duration')
 need(a['boot_id']==b['boot_id']and(a['sampler_pid'],a['sampler_start_ticks'])==(b['sampler_pid'],b['sampler_start_ticks']),'sampler generation/boot changed')
 need((a['sampler_uid'],a['sampler_ppid'])==(b['sampler_uid'],b['sampler_ppid']),'sampler parent/UID changed')
 need(a['allowed']==b['allowed']and a['topology']==b['topology']and not a['unreadable_tasks']and not b['unreadable_tasks'],'unknown affinity/topology observation')
 need(0<=e['created_monotonic']-b['completed_monotonic']<=POLICY['max_evidence_age_seconds'],'CPU evidence collection age invalid')
 for s in [a,b]:need(s['cgroups']['hidden_ancestor_status']=='UNKNOWN'and s['cgroups']['hidden_ancestor_limits_excluded']is False,'hidden ancestors falsely excluded')
 ca=a['cgroups'];cb=b['cgroups'];need(all(ca[k]==cb[k]for k in ['process_cgroup','mount_root','mount_point']),'cgroup namespace changed')
 need([x['path']for x in ca['visible']]==[x['path']for x in cb['visible']],'visible ancestor path changed')
 quota_checks=[];cgdt=cb['sample_monotonic']-ca['sample_monotonic'];need(.5<=cgdt<=POLICY['max_sample_seconds'],'invalid quota sample duration')
 for old,new in zip(ca['visible'],cb['visible']):
  need(old['quota']==new['quota'],'quota changed during sample');s0=old['stat'];s1=new['stat']
  need(all(s1[k]>=s0[k]for k in ['usage_usec','nr_throttled','throttled_usec']),'quota counter reset')
  need(s1['nr_throttled']==s0['nr_throttled']and s1['throttled_usec']==s0['throttled_usec'],'visible quota throttled')
  if new['quota'][0]!='max':
   quota=int(new['quota'][0])/int(new['quota'][1]);used=(s1['usage_usec']-s0['usage_usec'])/(cgdt*1e6);need(used+1<=.75*quota,'used+prospective exceeds .75 quota')
   quota_checks.append(dict(path=new['path'],quota=quota,used_cores=used,prospective_cores=1))
 need(quota_checks,'no visible finite CPU quota evidence')
 top={r['cpu']:r for r in b['topology']};occupied=set()
 for s in [a,b]:
  for row in s['other_task_claims']:occupied.update(row['affinity']if row['affinity']is not None else[row['processor']])
 occupied_cores={(top[c]['socket'],top[c]['core'])for c in occupied if c in top};allowed=set(b['allowed']);spare={};util={}
 for cpu in b['allowed']:
  row=top[cpu];key=(row['socket'],row['core']);siblings=row['siblings']
  if key in occupied_cores or not set(siblings)<=allowed:continue
  good=True
  for sibling in siblings:
   old=a['cpu_ticks'].get(str(sibling));new=b['cpu_ticks'].get(str(sibling));need(old is not None and new is not None,'missing sibling tick evidence')
   delta=[n-o for n,o in zip(new,old)];need(len(delta)==8 and min(delta)>=0,'invalid CPU tick delta');total=sum(delta)
   busy=(total-delta[3]-delta[4])/total if total>0 else 1.;util[str(sibling)]=busy
   if busy>POLICY['max_sibling_busy_fraction']:good=False
  if good:spare[key]=sorted(set(spare.get(key,[]))|set(siblings))
 need(len(spare)>=4,'fewer than4 unoccupied idle physical cores')
 legal=sorted({c for v in spare.values()for c in v})
 if selected_cpu is not None:need(type(selected_cpu)is int and selected_cpu in legal,'selected CPU absent from final legal idle cores')
 return dict(status='PASS_VISIBLE_QUOTA_AND_PHYSICAL_SPARE_ONLY',quota_checks=quota_checks,sample_seconds=dt,spare_physical_core_count=len(spare),eligible_cpu_ids=legal,selected_cpu=selected_cpu,hidden_ancestor_status='UNKNOWN',hidden_ancestor_limits_excluded=False,sibling_busy_fraction=util)
def _raw(base):
 if 'additional_future_memory_admission_proof'in base:
  old=base['additional_future_memory_admission_proof']['base_resource_snapshot'];need(_OLD.objsha(_OLD.project(old))==_OLD.objsha(base),'unrecognized old95 projected resource');return old
 need('additional_cpu_spare_memory_admission_proof'not in base,'CPU generation double projection refused');return base
def project(base,cfg=None):return _OLD.project(_raw(base))
def project_for_candidate(base,cfg,cohort,selected_cpu=None,evidence=None,context=None):
 need(cohort in cfg['allowed_cohorts']and cfg['cpu_exception_scope']['mode']=='ALL_ALLOWED_ADMITTED_UNSPENT'and cfg['cpu_spare_policy']==POLICY,'outside approved CPU allowlist')
 oldbase=copy.deepcopy(_raw(base));old95=_OLD.project(oldbase);evidence=evidence or sample_cpu_evidence(selected_cpu);assessment=verify_cpu_evidence(evidence,selected_cpu)
 need(evidence['second']['boot_id']==oldbase['boot_id'],'CPU and memory sample boot mismatch')
 need(0<=time.monotonic()-evidence['second']['completed_monotonic']<=2.,'CPU evidence no longer fresh')
 raw_reasons=old95['admission_decision']['pressure_reasons'];effective=[x for x in raw_reasons if x!='cpu_pressure_full'];total=old95['total_projected_additional_RAM_bytes'];d=dict(old95['admission_decision'],pressure_reasons=effective,pressure_pause_new=bool(effective),pass_admission=not effective and total<=budget(old95))
 kind=(context or{}).get('kind','NATIVE'if selected_cpu is not None else'OWNER_FRAME');need(kind in['NATIVE','OWNER_FRAME','OWNER_CHOOSE']and(kind!='NATIVE'or type(selected_cpu)is int),'invalid CPU proof context')
 proof=dict(schema=ID,mode='CPU_SPARE_PER_COHORT',config=copy.deepcopy(cfg),context=dict(cohort=cohort,selected_cpu=selected_cpu,kind=kind),base_resource_snapshot=oldbase,old95_resource_snapshot=old95,raw_pressure_reasons=copy.deepcopy(raw_reasons),effective_pressure_reasons=effective,cpu_evidence=copy.deepcopy(evidence),cpu_assessment=assessment,effective_decision=d,growth_unchanged_bytes=total,only_cpu_pressure_full_excepted=True,old_V2_PRESSURE_PASS_claimed=False,created_monotonic=time.monotonic(),canary_qualification_utf8=P(cfg['canary_qualification_path']).read_text())
 out=dict(old95,physical_RAM_pass=d['pass_admission'],admission_decision=d,additional_cpu_spare_memory_admission_proof=proof)
 return out
def project_memory_only(base,cfg,cohort,selected_cpu=None):
 oldbase=copy.deepcopy(_raw(base));old95=_OLD.project(oldbase)
 proof=dict(schema=ID,mode='MEMORY_ONLY_OLD_CPU_RULES',config=copy.deepcopy(cfg),context=dict(cohort=cohort,selected_cpu=selected_cpu,kind='NATIVE'),base_resource_snapshot=oldbase,old95_resource_snapshot=old95,raw_pressure_reasons=copy.deepcopy(old95['admission_decision']['pressure_reasons']),effective_pressure_reasons=copy.deepcopy(old95['admission_decision']['pressure_reasons']),effective_decision=copy.deepcopy(old95['admission_decision']),growth_unchanged_bytes=old95['total_projected_additional_RAM_bytes'],only_cpu_pressure_full_excepted=False,old_V2_PRESSURE_PASS_claimed=False,created_monotonic=time.monotonic(),canary_qualification_utf8=P(cfg['canary_qualification_path']).read_text())
 return dict(old95,additional_cpu_spare_memory_admission_proof=proof)
def verify_memory_proof(p,require_native=False):
 if p.get('schema')!=ID:
  need(not require_native,'old proof cannot stand in for new native generation');return _OLD.verify_memory_proof(p)
 need(p['schema']==ID and p['old_V2_PRESSURE_PASS_claimed']is False,'wrong CPU memory proof')
 cfg=p['config'];c=p['context'];need(cfg['overlay_id']==ID and cfg['cpu_spare_policy']==POLICY and cfg['cpu_exception_scope']['mode']=='ALL_ALLOWED_ADMITTED_UNSPENT','CPU context mismatch');canary_qualification(cfg,utf8=p['canary_qualification_utf8'])
 oldbase=p['base_resource_snapshot'];old95=_OLD.project(oldbase);need(objsha(old95)==objsha(p['old95_resource_snapshot']),'old raw resource/decision modified')
 need(oldbase['source_module_sha256']==cfg['expected_pins'][str(R/'tools/l2_resources.py')]and oldbase['policy_sha256']==cfg['expected_pins'][str(R/'control/RESOURCE_POLICY.json')],'base source/policy mismatch')
 need(type(oldbase['total_projected_additional_RAM_bytes'])is int and oldbase['total_projected_additional_RAM_bytes']>=0,'invalid full growth')
 if 'additional_padding_admission_proof'not in oldbase:
  growth_rows=oldbase['RAM_reservation_entries']+oldbase['own_ram_forecasts'];need(all(type(x['additional_reserved_bytes'])is int and x['additional_reserved_bytes']>=0 for x in growth_rows)and sum(x['additional_reserved_bytes']for x in growth_rows)==oldbase['total_projected_additional_RAM_bytes'],'full peer/own/claim growth sum mismatch')
 else:
  pad=oldbase['additional_padding_admission_proof'];need(pad['effective_total_additional_RAM_bytes']==oldbase['total_projected_additional_RAM_bytes'],'padding growth mismatch')
 if require_native:
  need(c['kind']=='NATIVE'and type(c['selected_cpu'])is int and 'additional_padding_admission_proof'not in oldbase,'OWNER_FRAME/CHOOSE or padding not a new NOFLAG native proof')
  f=p['native_full_forecast'];need(f['forecast']['predicted_peak_RAM_bytes']<=f['canonical_estimated_peak_model_RAM_bytes'],'native canonical forecast underbound')
  candidates=[x for x in oldbase['own_ram_forecasts']if x['cohort']==c['cohort']];need(len(candidates)==1 and candidates[0]['kind']=='CLAIM_OR_CANDIDATE'and candidates[0]['RSS_bytes']==0 and candidates[0]['additional_reserved_bytes']==f['canonical_estimated_peak_model_RAM_bytes'],'native candidate claim RAM absent/duplicated/discounted')
  need(f['cohort']==c['cohort']and f['selected_cpu']==c['selected_cpu']and f['forecast_source_sha256']==cfg['expected_pins'][str(R/'tools/l2_resources.py')],'full forecast identity/source mismatch')
  need(hashlib.sha256(f['history_utf8'].encode()).hexdigest()==f['history_sha256']and hashlib.sha256(f['resource_policy_utf8'].encode()).hexdigest()==f['resource_policy_sha256']==cfg['expected_pins'][str(R/'control/RESOURCE_POLICY.json')],'full forecast history/policy snapshot mismatch')
  forecast_module=load('cpu_spare_offline_full_forecast',R/'tools/l2_resources.py');need(sha(forecast_module.__file__)==f['forecast_source_sha256'],'offline forecast source drift')
  need(forecast_module.forecast(f['forecast_input_spec'],json.loads(f['history_utf8']),json.loads(f['resource_policy_utf8']))==f['forecast']and f['forecast_input_spec']['estimated_peak_model_RAM_bytes']==f['canonical_estimated_peak_model_RAM_bytes'],'offline full forecast recomputation mismatch')
  if p['mode']=='CPU_SPARE_PER_COHORT':need(p['cpu_evidence']['selected_cpu']==c['selected_cpu'],'native final evidence was not sampled for selected CPU')
 raw=old95['admission_decision']['pressure_reasons']
 if p['mode']=='CPU_SPARE_PER_COHORT':
  need(c['cohort']in cfg['allowed_cohorts']and p['only_cpu_pressure_full_excepted'],'not approved per-cohort exception')
  need(c['kind']in['NATIVE','OWNER_FRAME','OWNER_CHOOSE']and(c['kind']!='NATIVE'or type(c['selected_cpu'])is int),'invalid native/owner context')
  assessment=verify_cpu_evidence(p['cpu_evidence'],c['selected_cpu']);need(assessment==p['cpu_assessment'],'CPU assessment changed')
  need(p['cpu_evidence']['sampler_source_sha256']==cfg['library_sha256'],'CPU sampler source mismatch')
  need(p['cpu_evidence']['second']['boot_id']==oldbase['boot_id'],'CPU/memory boot mismatch')
  need(0<=p['created_monotonic']-p['cpu_evidence']['second']['completed_monotonic']<=2.,'native evidence stale at proof')
  effective=[x for x in raw if x!='cpu_pressure_full'];d=dict(old95['admission_decision'],pressure_reasons=effective,pressure_pause_new=bool(effective),pass_admission=not effective and old95['total_projected_additional_RAM_bytes']<=budget(old95))
 else:
  need(p['mode']=='MEMORY_ONLY_OLD_CPU_RULES'and p['only_cpu_pressure_full_excepted']is False and c['cohort']in cfg['allowed_cohorts'],'invalid new memory-only lineage')
  need('cpu_evidence'not in p and 'cpu_assessment'not in p,'CPU exception smuggled into memory-only mode');assessment=None;effective=raw;d=copy.deepcopy(old95['admission_decision'])
 need(p['raw_pressure_reasons']==raw and p['effective_pressure_reasons']==effective,'pressure changed beyond cpu_full')
 need(d==p['effective_decision']and p['growth_unchanged_bytes']==old95['total_projected_additional_RAM_bytes'],'RAM/forecast/growth changed')
 need(d['pass_admission']and old95['physical_disk_pass']and old95['own_write_ceiling_pass'],'other physical gate HOLD')
 need(old95['native_free_bytes']>old95['required_free_bytes']and old95['free_inodes']>=100000,'disk bound HOLD')
 return dict(status='PASS_NEW_CPU_SPARE_MEMORY_AND_ORIGINAL_BOUNDS',mode=p['mode'],old_V2_PRESSURE_PASS_claimed=False,cohort=c['cohort'],selected_cpu=c['selected_cpu'],budget_bytes=budget(old95),unchanged_growth_bytes=p['growth_unchanged_bytes'],cpu_assessment=assessment)
def _invocation():
 a=sys.argv[1:];need(len(a)>=5 and a[:2]in[['experiment','prepare'],['experiment','run-native'],['experiment','inspect']]and a[3:5]==['--project','DTC_L1'],'unbound native invocation')
 return a[2],a
def _native_forecast(native,cohort):
 spec=native.spec_for(cohort);hp=R/'control/HISTORICAL_RSS.json';raw=hp.read_bytes();history=json.loads(raw);policy_raw=(R/'control/RESOURCE_POLICY.json').read_bytes();policy=json.loads(policy_raw);module=load('cpu_spare_original_full_forecast',R/'tools/l2_resources.py');f=module.forecast(spec,history,policy)
 need(f['predicted_peak_RAM_bytes']<=spec['estimated_peak_model_RAM_bytes'],'CANONICAL_FULL_FORECAST_REFRESH_REQUIRED')
 return dict(cohort=cohort,selected_cpu=spec['host_cpu'],canonical_spec_sha256=native.registered()[2]['admitted_specs'][cohort],forecast=f,forecast_input_spec=spec,canonical_estimated_peak_model_RAM_bytes=spec['estimated_peak_model_RAM_bytes'],history_sha256=hashlib.sha256(raw).hexdigest(),history_utf8=raw.decode('utf-8'),resource_policy_sha256=hashlib.sha256(policy_raw).hexdigest(),resource_policy_utf8=policy_raw.decode('utf-8'),forecast_source_sha256=sha(module.__file__))
def install_future_native(native,cfg,padding=False,invocation_cohort=None):
 validate(cfg,native.registered()[2]);parent_lease=copy.deepcopy(native.assert_parent_lease());cohort,argv=_invocation()if invocation_cohort is None else(invocation_cohort,['CPU_FIXTURE_EXPLICIT_INVOCATION',invocation_cohort])
 need(cohort in cfg['allowed_cohorts'],'outside finite memory route')
 cpu_exception=eligible_cohort(cfg,native.registered()[2],cohort,'NATIVE');need(cpu_exception,'CPU cohort spent/sealed/unadmitted')
 need(not padding,'new generation uses original NOFLAG worker')
 need(cohort not in native.registered()[2]['consumed'],'CPU singleton already spent')
 need(not hasattr(native,'_CPU_SPARE_MEMORY_BINDING'),'CPU native overlay already installed')
 original=native.resources;proofs=[];forecasts=[]
 def resources(spec,fresh_source=False):
  if not fresh_source:return original(spec,False)
  validate(cfg,native.registered()[2]);need(cohort not in native.registered()[2]['consumed'],'CPU singleton spent before fresh preflight')
  selected=native.spec_for(cohort)['host_cpu'];need(type(selected)is int,'native selected CPU missing');forecasts.append(_native_forecast(native,cohort))
  value=project_for_candidate(original(spec,True),cfg,cohort,selected_cpu=selected,context=dict(kind='NATIVE'))if cpu_exception else project_memory_only(original(spec,True),cfg,cohort,selected_cpu=selected);value['additional_cpu_spare_memory_admission_proof']['native_full_forecast']=copy.deepcopy(forecasts[-1]);proofs.append(copy.deepcopy(value['additional_cpu_spare_memory_admission_proof']));return value
 native.resources=resources;old_engine=native.engine
 def engine():
  n=old_engine();old=n.exclusive;binding=dict(schema=ID,request=REQ,cohort=cohort,mode='CPU_SPARE_PER_COHORT',padding_optin=False,qualified_sources={r:cfg[r+'_sha256']for r in ROLES},config_sha256=objsha(cfg),QA_sha256=cfg['QA_sha256'],readback_sha256=cfg['readback_sha256'],snapshot_sha256=None,selected_cpu=None,final_cpu_evidence_sha256=None,old_V2_PRESSURE_PASS_claimed=False)
  def exclusive(path,obj):
   path=P(path)
   if path.name.endswith('.INTENT.json'):
    validate(cfg,native.registered()[2]);need(obj['cohort']==cohort and cohort not in native.registered()[2]['consumed'],'wrong native CPU identity')
    resources(native.spec_for(cohort),True);[verify_memory_proof(p,require_native=True)for p in proofs];final=proofs[-1];need(all(p['context']['kind']=='NATIVE'and type(p['context']['selected_cpu'])is int for p in proofs),'OWNER_FRAME/CHOOSE proof forbidden in native strict')
    need(native.assert_parent_lease()==parent_lease,'parent lease changed before INTENT')
    out=P(obj['output']);snapshot=dict(schema=ID,mode=binding['mode'],padding_optin=False,config=cfg,canary_qualification_utf8=P(cfg['canary_qualification_path']).read_text(),record=copy.deepcopy(native.registered()[2]['additional_operational_overlays'][ID]),fresh_preflights=proofs,full_forecast_preflights=forecasts,invocation=dict(argv=argv,cohort=cohort,selected_cpu=final['context']['selected_cpu'],parent_lease=parent_lease,native_source_path=str(native.__file__),native_source_sha256=sha(native.__file__)),source_snapshots={r:dict(sha256=cfg[r+'_sha256'],utf8=P(cfg[r+'_path']).read_bytes().decode('utf-8'))for r in ROLES},QA_utf8=P(cfg['QA_path']).read_text(),readback_utf8=P(cfg['readback_path']).read_text(),io_active_utf8=P(cfg['io_active_path']).read_text())
    atomic(out/'CPU_SPARE_MEMORY_ADMISSION_SNAPSHOT.json',snapshot);binding.update(snapshot_sha256=sha(out/'CPU_SPARE_MEMORY_ADMISSION_SNAPSHOT.json'),selected_cpu=final['context']['selected_cpu'],final_cpu_evidence_sha256=objsha(final['cpu_evidence'])if cpu_exception else None)
   if path.name.endswith('.INTENT.json')or path.name in['NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json']:
    need(binding['snapshot_sha256'],'CPU INTENT snapshot absent');obj=dict(obj,additional_cpu_spare_memory_admission_binding=copy.deepcopy(binding))
   return old(path,obj)
  n.exclusive=exclusive;return n
 native.engine=engine;native._CPU_SPARE_MEMORY_BINDING=dict(source_sha256=sha(__file__),cfg_sha256=objsha(cfg),cohort=cohort);return native
