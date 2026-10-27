"""Future-only private native adapter; source import performs no production action."""
import pathlib,json,hashlib,importlib.util,os,sys,uuid,copy,threading,time
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def private_engine(config,native_module=None):
 """Qualified current native module instance may include existing registry journal."""
 core=load('padding_overlay_core',P(__file__).with_name('padding_overlay.py'));native=native_module or load('padding_private_native',R/'tools/l2_native.py');original_resources=native.resources
 def registry():return native.registered()[2]
 overlay=core.PaddingOverlay(R,config['policy_path'],config['certificate_path'],config['policy_sha256'],config['certificate_sha256'],registry,original_resources);assert config['source_sha256']==sha(P(__file__).with_name('padding_overlay.py'));core.validate_active_config(config,native.registered()[2])
 # This is explicitly additional evidence. Native binding() remains untouched.
 original_overlay_resources=overlay.resources
 def checked_resources(spec,fresh_source=False):
  if fresh_source:core.validate_active_config(config,native.registered()[2])
  return original_overlay_resources(spec,fresh_source)
 native.resources=checked_resources;original_prepare=native.prepare;original_engine=native.engine
 def prepare(c):
  assert c not in native.registered()[2]['consumed'];value=original_prepare(c);return dict(value,additional_padding_admission_binding=overlay.binding(),additional_padding_admission_proof=overlay.last_proof)
 native.prepare=prepare
 def engine():
  n=original_engine();old=n.exclusive;fresh=[];effective_binding={};oldresources=n.resources
  def resources(s,fresh_source=False):
   value=oldresources(s,fresh_source)
   if fresh_source:fresh.append(copy.deepcopy(value['additional_padding_admission_proof']))
   return value
  n.resources=resources
  def exclusive(path,obj):
   path=P(path)
   if path.name.endswith('.INTENT.json')or path.name in['NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json']:
    obj=dict(obj,additional_padding_admission_binding=effective_binding or overlay.binding())
    if path.name.endswith('.INTENT.json'):
     out=P(obj['output']);snapshot=dict(binding=overlay.binding(),fresh_preflights=fresh or[overlay.last_proof],policy=overlay.policy,certificate=overlay.certificate);p=out/'PADDING_ADMISSION_EVIDENCE.json'
     with p.open('x')as h:json.dump(snapshot,h,sort_keys=True,indent=2);h.write('\n');h.flush();os.fsync(h.fileno())
     for name,src in [('PADDING_OWNER_SOURCE.py',P(config['owner_path'])),('PADDING_QA.json',P(config['QA_path'])),('PADDING_PUBLICATION_READBACK.json',P(config['readback_path'])),('PADDING_EXTRA_STRICT.py',P(config['extra_strict_path'])),('PADDING_OVERLAY_SOURCE.py',P(__file__).with_name('padding_overlay.py')),('PADDING_FRONTEND_SOURCE.py',P(__file__)),('PADDING_HISTORY_VALIDATOR.py',P(__file__).with_name('history_evidence_validator.py')),('PADDING_POLICY.json',P(config['policy_path'])),('PADDING_CERTIFICATES.json',P(config['certificate_path']))]:
      with(out/name).open('xb')as h:h.write(src.read_bytes());h.flush();os.fsync(h.fileno())
     effective_binding.update(overlay.binding(),fresh_evidence_sha256=sha(p));obj['additional_padding_admission_binding']=dict(effective_binding);obj['additional_padding_admission_evidence_sha256']=sha(p)
     for name,data in [('PADDING_ACTIVATION_CONFIG.json',config),('PADDING_OVERLAY_REGISTRY_RECORD.json',core.validate_active_config(config,native.registered()[2]))]:
      with(out/name).open('x')as h:json.dump(data,h,sort_keys=True,indent=2);h.write('\n');h.flush();os.fsync(h.fileno())
   return old(path,obj)
  n.exclusive=exclusive;return n
 native.engine=engine;return native,overlay

def main(argv):
 assert argv.count('--padding-only-admission-v1')==1;argv=[x for x in argv if x!='--padding-only-admission-v1'];assert '--project'in argv and argv[argv.index('--project')+1]=='DTC_L1'
 assert len(argv)==5 and argv[3:]==['--project','DTC_L1'];cfg=read(R/'control/operational_amendments/padding_only_v1/ACTIVE_FRONTEND.json');assert cfg['status']=='ACTIVE_FUTURE_ONLY'and cfg['request']==REQ;assert len(argv)>=3 and argv[2].startswith('E2-DTCL2MLP-');assert argv[:2]in[['experiment','prepare'],['experiment','inspect'],['experiment','run-native']];assert cfg['frontend_sha256']==sha(__file__);native,overlay=private_engine(cfg);c=argv[2];q=native.registered()[2];assert c in cfg['allowed_cohorts']and c in q['admitted_specs']and c not in q['consumed'];overlay.activation_context=dict(allowed_cohorts_sha256=load('padding_cfg_hash',P(__file__).with_name('padding_overlay.py')).jsonsha(cfg['allowed_cohorts']),extra_strict_sha256=cfg['extra_strict_sha256'],owner_sha256=cfg['owner_sha256'],frontend_sha256=cfg['frontend_sha256'],QA_sha256=cfg['QA_sha256'],readback_sha256=cfg['readback_sha256'])
 if argv[1]in['prepare','inspect']:return native.prepare(c)
 return native.run_native(c)
if __name__=='__main__':
 try:print(json.dumps(main(sys.argv[1:])))
 except Exception as e:print(json.dumps(dict(status='HOLD',reason=repr(e),scientific_starts=0 if 'already consumed'not in str(e)else'UNPROVEN_NO_RETRY')),file=sys.stderr);sys.exit(2)
