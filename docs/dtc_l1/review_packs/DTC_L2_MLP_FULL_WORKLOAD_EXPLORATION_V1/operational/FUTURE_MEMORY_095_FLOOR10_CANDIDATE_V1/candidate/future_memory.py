"""Private future-only .95/10GiB admission. Import never installs anything."""
import pathlib,json,hashlib,importlib.util,copy,os,uuid
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1';ID='FUTURE_ONLY_MEMORY_ADMISSION_095_FLOOR10_V1';G=1024**3;ROLES=['library','frontend','owner','extra_strict','joint_padding','joint_io']
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def js(x):return(json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
def objsha(x):return hashlib.sha256(js(x)).hexdigest()
def need(x,msg):
 if not x:raise RuntimeError(msg)
def load(name,path):s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def atomic(path,obj):
 p=P(path);tmp=p.with_name('.'+p.name+'.future-memory-'+uuid.uuid4().hex)
 try:
  with tmp.open('xb')as f:f.write(js(obj));f.flush();os.fsync(f.fileno())
  os.link(tmp,p);tmp.unlink();fd=os.open(p.parent,os.O_RDONLY)
  try:os.fsync(fd)
  finally:os.close(fd)
 finally:
  if tmp.exists():tmp.unlink()
def record(cfg):return {k:copy.deepcopy(cfg[k])for k in ['request','overlay_id','scope_mode','memory_utilization_fraction','host_floor_bytes','cgroup_floor_bytes','expected_pins','io_active_sha256','allowed_cohorts',*[r+'_sha256'for r in ROLES], 'QA_sha256','readback_sha256']}
def validate(cfg,q):
 need(cfg['status']=='ACTIVE_FUTURE_ONLY'and cfg['request']==REQ and cfg['overlay_id']==ID,'future memory not active');need(cfg['scope_mode']in['FINITE_CANARY','ALL_UNSPENT_FUTURE']and len(set(cfg['allowed_cohorts']))==len(cfg['allowed_cohorts'])and bool(cfg['allowed_cohorts']),'unknown memory scope');need(cfg['scope_mode']!='FINITE_CANARY'or len(cfg['allowed_cohorts'])==1,'canary must contain exactlyone allowedcohort');need(set(cfg['allowed_cohorts'])<=set(q['admitted_specs']),'unadmitted memory scope');need(cfg['memory_utilization_fraction']==.95 and cfg['host_floor_bytes']==cfg['cgroup_floor_bytes']==10*G,'future memory policy changed')
 for role in ROLES+['QA','readback']:need(sha(cfg[role+'_path'])==cfg[role+'_sha256'],'future memory source/receipt drift '+role)
 need(sha(__file__)==cfg['library_sha256'],'wrong loaded memory library');qualified={r:cfg[r+'_sha256']for r in ROLES};qa=read(cfg['QA_path']);back=read(cfg['readback_path']);need(qa['status']=='PASS'and qa['native_prefix_qualified']and qa['joint_strict_qualified']and back['verified'],'future memory not qualified');need(qa['qualified_sources']==back['qualified_sources']==qualified and qa['expected_pins']==back['expected_pins']==cfg['expected_pins'],'qualification/readback mismatch')
 for path,digest in cfg['expected_pins'].items():need(sha(path)==digest,'old dependency changed '+path)
 need(sha(cfg['io_active_path'])==cfg['io_active_sha256'],'IO activation config changed');r=q['additional_operational_overlays'][ID];need(r['status']=='ACTIVE'and all(r[k]==v for k,v in record(cfg).items()),'Main future-memory authority record mismatch');return r
def effective_policy(policy=None):return dict(policy or{},memory_utilization_fraction=.95,min_host_headroom_bytes=10*G,min_cgroup_headroom_bytes=10*G)
def budget(sample):
 h=max(0,sample['host_MemAvailable_bytes']-10*G);cg=sample['cgroup_effective_headroom_bytes'];return int(min(h,max(0,cg-10*G))*.95)if cg is not None else int(h*.95)
def verify_memory_proof(p):
 need(p['schema']==ID and p['fresh_source']is True,'not a fresh memory proof');need(p['memory_utilization_fraction']==.95 and p['host_floor_bytes']==p['cgroup_floor_bytes']==10*G,'memory proof policy mismatch');base=p['base_resource_snapshot'];need(base['source_module_sha256']==p['base_source_sha256']and base['policy_sha256']==p['base_policy_sha256'],'base source mismatch');need(all(base.get(k)==v for k,v in p['sample'].items()),'sample changed');need(base['admission_decision']==p['base_decision']and base['admission_decision']['pressure_reasons']==p['pressure_reasons'],'base pressure/decision changed');need(p['no_new_clean_cache_credit']and p['canonical_candidate_and_claim_costs_unchanged'],'claim/cache rule changed');need(base['total_projected_additional_RAM_bytes']==p['growth_unchanged_bytes'],'base growth changed')
 if p['legacy_padding_proof_sha256']is None:need(sum(x['additional_reserved_bytes']for x in base['RAM_reservation_entries'])+sum(x['additional_reserved_bytes']for x in base['own_ram_forecasts'])==p['growth_unchanged_bytes'],'full noFlag peer/own growth not retained')
 else:need(objsha(base['additional_padding_admission_proof'])==p['legacy_padding_proof_sha256']and base['additional_padding_admission_proof']['effective_total_additional_RAM_bytes']==p['growth_unchanged_bytes'],'full padding growth changed')
 b=budget(p['sample']);need(b==p['effective_decision']['admission_RAM_budget_bytes'],'memory budget mismatch');need(p['growth_unchanged_bytes']==p['effective_decision']['additional_reserved_RAM_bytes'],'growth was reduced');need(p['effective_decision']['pass_admission']is(not p['pressure_reasons']and p['growth_unchanged_bytes']<=b),'memory pass mismatch');need(not p['pressure_reasons']and p['effective_decision']['pass_admission'],'future memory HOLD');need(p['disk_and_own_bound_pass']==bool(base['physical_disk_pass']and base['own_write_ceiling_pass'])and p['disk_and_own_bound_pass']and p['sample']['native_free_bytes']>p['sample']['required_free_bytes']and p['sample']['free_inodes']>=100000,'disk/write safety changed');return dict(status='PASS_EXACT_FUTURE_MEMORY_ARITHMETIC',budget_bytes=b,unchanged_growth_bytes=p['growth_unchanged_bytes'])
def project(base):
 pressure=copy.deepcopy(base['admission_decision']['pressure_reasons']);total=base['total_projected_additional_RAM_bytes'];b=budget(base);d=dict(base['admission_decision'],memory_utilization_fraction=.95,effective_usable_bytes=min(max(0,base['host_MemAvailable_bytes']-10*G),max(0,base['cgroup_effective_headroom_bytes']-10*G))if base['cgroup_effective_headroom_bytes']is not None else max(0,base['host_MemAvailable_bytes']-10*G),admission_RAM_budget_bytes=b,additional_reserved_RAM_bytes=total,pass_admission=not pressure and total<=b);sample={k:base.get(k)for k in ['host_MemAvailable_bytes','cgroup_effective_headroom_bytes','cgroup_memory_max','cgroup_memory_current','cgroup_reclaimable_clean_inactive_file_credit_bytes','native_free_bytes','required_free_bytes','free_inodes','monotonic','utc']};proof=dict(schema=ID,fresh_source=True,memory_utilization_fraction=.95,host_floor_bytes=10*G,cgroup_floor_bytes=10*G,base_decision=copy.deepcopy(base['admission_decision']),effective_decision=d,growth_unchanged_bytes=total,pressure_reasons=pressure,disk_and_own_bound_pass=bool(base['physical_disk_pass']and base['own_write_ceiling_pass']),sample=sample,legacy_padding_proof_sha256=objsha(base['additional_padding_admission_proof'])if'additional_padding_admission_proof'in base else None,base_source_sha256=base['source_module_sha256'],base_policy_sha256=base['policy_sha256'],no_new_clean_cache_credit=True,canonical_candidate_and_claim_costs_unchanged=True)
 proof['base_resource_snapshot']=copy.deepcopy(base);return dict(base,physical_RAM_pass=d['pass_admission'],admission_decision=d,host_floor_bytes=10*G,cgroup_floor_bytes=10*G,additional_future_memory_admission_proof=proof)
def wrap_resources(original,guard=None,proofs=None):
 def resources(spec,fresh_source=False):
  if not fresh_source:return original(spec,False)
  if guard:guard()
  value=project(original(spec,True))
  if proofs is not None:proofs.append(copy.deepcopy(value['additional_future_memory_admission_proof']))
  return value
 return resources
def install_future_native(native,cfg,padding=False):
 validate(cfg,native.registered()[2]);need(not hasattr(native,'_FUTURE_MEMORY_BINDING'),'native memory overlay already installed');proofs=[];native.resources=wrap_resources(native.resources,lambda:validate(cfg,native.registered()[2]),proofs);oldengine=native.engine
 def engine():
  n=oldengine();old=n.exclusive;binding=dict(schema=ID,request=REQ,qualified_sources={r:cfg[r+'_sha256']for r in ROLES},config_sha256=objsha(cfg),QA_sha256=cfg['QA_sha256'],readback_sha256=cfg['readback_sha256'],padding_optin=bool(padding),snapshot_sha256=None)
  def exclusive(path,obj):
   path=P(path)
   if path.name.endswith('.INTENT.json'):
    validate(cfg,native.registered()[2]);need(obj['cohort']in cfg['allowed_cohorts']and obj['cohort']not in native.registered()[2]['consumed'],'cohort not a future unspent approved point');need(proofs,'no complete passing memory preflights');[verify_memory_proof(p)for p in proofs];out=P(obj['output']);snapshot=dict(schema=ID,config=cfg,record=copy.deepcopy(native.registered()[2]['additional_operational_overlays'][ID]),fresh_preflights=proofs,padding_optin=bool(padding),source_snapshots={r:dict(sha256=cfg[r+'_sha256'],utf8=P(cfg[r+'_path']).read_bytes().decode('utf-8'))for r in ROLES},QA_utf8=P(cfg['QA_path']).read_bytes().decode('utf-8'),readback_utf8=P(cfg['readback_path']).read_bytes().decode('utf-8'),io_active_utf8=P(cfg['io_active_path']).read_bytes().decode('utf-8'));atomic(out/'FUTURE_MEMORY_ADMISSION_SNAPSHOT.json',snapshot);binding['snapshot_sha256']=sha(out/'FUTURE_MEMORY_ADMISSION_SNAPSHOT.json')
   if path.name.endswith('.INTENT.json')or path.name in['NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json']:need(binding['snapshot_sha256'],'missing memory INTENT snapshot');obj=dict(obj,additional_future_memory_admission_binding=copy.deepcopy(binding))
   return old(path,obj)
  n.exclusive=exclusive;return n
 native.engine=engine;native._FUTURE_MEMORY_BINDING=dict(source_sha256=sha(__file__),cfg_sha256=objsha(cfg));return native
