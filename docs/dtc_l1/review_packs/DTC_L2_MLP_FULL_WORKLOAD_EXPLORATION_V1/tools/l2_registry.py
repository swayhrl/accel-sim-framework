"""Coordinator-only additive parameter-family grants. Existing spent specs never change."""
import pathlib,json,hashlib,copy,importlib.util,math,datetime,os
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');G=1024**3;M=1024**2
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,f):
 s=importlib.util.spec_from_file_location(n,R/'tools'/f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(p,v):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name('.'+p.name+'.L2REG');tmp.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n');tmp.replace(p)
def refresh_pending_resource_spec(c,history):
 e=load('l2_resource_amend_engine','l2_native.py');s=e.canonical(c)
 if(R/'control/dispatch_bindings'/(c+'.json')).exists():return
 f=load('l2_resource_amend_prediction','l2_resources.py').forecast(s,history)
 # Unknown CUTCP first point keeps its explicitly qualified wide envelope.
 if s['program']=='cutcp'and not f['history_records']:return
 predicted=f['predicted_peak_RAM_bytes'];hard=f['proposed_process_tree_rss_cap_bytes']
 if predicted==s['estimated_peak_model_RAM_bytes']and hard==s['limits']['max_process_tree_rss_bytes']:return
 old=copy.deepcopy(s);s['estimated_peak_model_RAM_bytes']=predicted;s['limits']=dict(s['limits'],max_process_tree_rss_bytes=hard,max_process_tree_vms_bytes=max(2*hard,hard+8*G))
 def amend(reg):
  q=reg['registered_future_requests'][e.REQ];assert c not in q['consumed'];p=R/'control/specs'/(c+'.json');oldsha=sha(p);assert q['admitted_specs'][c]==oldsha
  h=R/'control/resource_spec_history'/c/(oldsha+'.json');h.parent.mkdir(parents=True,exist_ok=True)
  if not h.exists():h.write_bytes(p.read_bytes())
  put(p,s);put(R/'control'/(c+'_SPEC.json'),s);q['admitted_specs'][c]=sha(p)
  record=dict(cohort=c,old_sha256=oldsha,new_sha256=sha(p),reason='ratified dynamic host RSS/AS only; scientific input/config/source unchanged',forecast=f,UTC=datetime.datetime.now(datetime.timezone.utc).isoformat());put(R/'control/resource_spec_history'/c/(sha(p)+'.AMENDMENT.json'),record)
  stable=lambda x:{k:v for k,v in x.items()if k not in ['estimated_peak_model_RAM_bytes','limits']}
  assert stable(old)==stable(s)and old['limits']['timeout_seconds']==s['limits']['timeout_seconds']and old['limits']['max_result_directory_bytes']==s['limits']['max_result_directory_bytes']
 e.update_authority(amend)
def extend(proposal):
 e=load('l2_extend_engine','l2_native.py');gen=load('l2_extend_generator','l2_config_generator.py');matrix=read(R/'control/MATRIX_CURRENT.json');history=read(R/'control/SEARCH_HISTORY.json');pid=proposal['proposal_id']
 if pid in history['proposal_ids']:return []
 profile=proposal['profile'];assert profile and all(c.isalnum()or c=='_'for c in profile);parameters=gen.normalize(proposal['parameters']);new=[]
 for want in proposal['new_cells']:
  # E emits either explicit cells or digest/design records; accept only the frozen domain.
  digest=want.get('input_digest',want.get('workload'));cell=want.get('cell',want.get('design'))
  assert cell in ['CH','DH'];basepoint=next(p for p in matrix['points']if p['input_digest']==digest and p['cell']==cell and p['profile']=='P0');base=read(R/'control/specs'/(basepoint['cohort']+'.json'))
  c='E2-DTCL2MLP-'+digest[:16]+'-'+cell+'-'+profile+'-V1'
  if any(p['cohort']==c for p in matrix['points']):continue
  texts=[P(x['path']).read_text()for x in base['configs']];after,manifest=gen.generate(texts,parameters);cfg=[]
  for i,text in enumerate(after):
   path=R/'DTC/env'/(cell+'_'+profile)/('config-'+str(i)+'.config');path.parent.mkdir(parents=True,exist_ok=True)
   if path.exists():assert path.read_text()==text
   else:path.write_text(text)
   cfg.append(dict(path=str(path),sha256=sha(path)))
  s=copy.deepcopy(base);s.update(cohort=c,downstream_profile=profile,profile=profile,configs=cfg,host_cpu=None)
  opt=gen.effective_options(after)
  for key in ['-gpgpu_cache:dl2','-gpgpu_frfcfs_dram_sched_queue_size']:s['expected_options'][key]=[opt[key]]
  s['native_simulator_argv']=[base['native_simulator_argv'][0],'-trace',base['native_simulator_argv'][2]]
  for x in cfg:s['native_simulator_argv']+=['-config',x['path']]
  put(R/'control/specs'/(c+'.json'),s);put(R/'control'/(c+'_SPEC.json'),s);new.append(dict(basepoint,cohort=c,profile=profile))
 if new:
  def register(reg):
   q=reg['registered_future_requests'][e.REQ]
   for point in new:
    c=point['cohort'];assert c not in q['admitted_specs'];q['admitted_specs'][c]=sha(R/'control/specs'/(c+'.json'));q['admitted_inputs'][point['input_digest']]['specs'].append(c)
   q['budget']+=len(new);q['remaining']+=len(new);q['state']='RUNNING';q.setdefault('authorized_extensions',[]).append(dict(proposal_id=pid,profile=profile,parameters=parameters,new_starts=len(new)))
  e.update_authority(register);matrix['points']+=new;matrix['revision']+=1;put(R/'control/matrix_revisions'/(str(matrix['revision']).zfill(5)+'.json'),dict(proposal=proposal,new_points=new,base_scope_sha256=matrix['base_scope_sha256']));put(R/'control/MATRIX_CURRENT.json',matrix)
 history['proposal_ids'].append(pid);history['profiles'][profile]={'parameters':parameters};put(R/'control/SEARCH_HISTORY.json',history);return new
